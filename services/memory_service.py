"""
记忆管理服务 - 核心：压缩、存储、检索
"""
import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional
from models.schemas import Memory, MemoryType, MemoryCreate, MemoryRetrieve
from models.database import get_db
from config import settings
from utils.embedding import EmbeddingManager


class MemoryService:
    """记忆管理服务"""

    def __init__(self):
        self._db = None
        self.embedding_mgr = EmbeddingManager(force_tfidf=True)  # 强制使用 TF-IDF 避免网络问题
        self._load_embeddings_cache()

    @property
    def db(self):
        """延迟获取数据库连接"""
        if self._db is None:
            self._db = get_db()
        return self._db

    def _load_embeddings_cache(self):
        """加载 embedding 缓存"""
        from pathlib import Path
        cache_path = Path(settings.embeddings_cache_path)
        if cache_path.exists():
            with open(cache_path, "r", encoding="utf-8") as f:
                self.embeddings_cache = json.load(f)
        else:
            self.embeddings_cache = {}

    def _save_embeddings_cache(self):
        """保存 embedding 缓存"""
        from pathlib import Path
        cache_path = Path(settings.embeddings_cache_path)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(self.embeddings_cache, f)

    def write_memory(self, user_id: str, feedback: str, context: Optional[Dict] = None) -> Memory:
        """
        写入记忆 - 压缩反馈为结构化记忆

        流程：
        1. 调用 LLM 压缩反馈
        2. 生成 embedding
        3. 存储到数据库
        """
        # 1. 压缩反馈
        compressed = self._compress_feedback(feedback, context)

        # 2. 生成 embedding
        text_for_embedding = f"{compressed['field']}: {compressed['value']}"
        embedding = self.embedding_mgr.get_embedding(text_for_embedding)
        self.embeddings_cache[text_for_embedding] = embedding

        # 3. 创建 Memory 对象
        memory = Memory(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            type=MemoryType(compressed["type"]),
            field=compressed["field"],
            value=compressed["value"],
            confidence=compressed.get("confidence", 0.8),
            source=compressed.get("source", feedback),
            created_at=datetime.now()
        )

        # 4. 存储
        self.db.save_memory(memory)

        # 5. 保存 embedding 缓存
        self._save_embeddings_cache()

        return memory

    def retrieve_memory(self, user_id: str, query: str, top_k: int = None) -> List[Memory]:
        """
        检索相关记忆（向量相似度检索）

        Args:
            user_id: 用户ID
            query: 查询文本
            top_k: 返回Top-K

        Returns:
            相关记忆列表（按相似度排序）
        """
        if top_k is None:
            top_k = settings.memory_top_k

        # 1. 获取用户所有记忆
        user_memories = self.db.get_user_memories(user_id)
        if not user_memories:
            return []

        # 2. 生成查询 embedding
        query_embedding = self.embedding_mgr.get_embedding(query)

        # 3. 计算相似度
        scored_memories = []
        for memory in user_memories:
            # 构建记忆文本
            mem_text = f"{memory.field}: {memory.value}"
            mem_embedding = self.embeddings_cache.get(mem_text)

            if mem_embedding is None:
                # 缓存中没有，动态生成
                mem_embedding = self.embedding_mgr.get_embedding(mem_text)
                self.embeddings_cache[mem_text] = mem_embedding

            # 计算余弦相似度
            similarity = self.embedding_mgr.cosine_similarity(query_embedding, mem_embedding)

            # 应用置信度权重
            weighted_score = similarity * memory.confidence

            if similarity >= settings.memory_similarity_threshold:
                scored_memories.append((memory, weighted_score))

        # 4. 按分数排序，取 Top-K
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_memories = [mem for mem, score in scored_memories[:top_k]]

        # 5. 更新使用统计
        for memory in top_memories:
            memory.usage_count += 1
            memory.last_used = datetime.now()
            self.db.save_memory(memory)

        return top_memories

    def get_all_memories(self, user_id: str) -> List[Memory]:
        """获取用户所有记忆"""
        return self.db.get_user_memories(user_id)

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """删除记忆"""
        return self.db.delete_memory(user_id, memory_id)

    def _compress_feedback(self, feedback: str, context: Optional[Dict] = None) -> Dict:
        """
        压缩反馈为结构化记忆（调用 LLM）

        这是记忆系统的核心：把自然语言反馈转为结构化数据
        """
        from utils.llm_client import get_llm_client

        llm = get_llm_client()

        prompt = f"""请将以下用户反馈压缩为结构化记忆，用于个性化推荐。

用户反馈: "{feedback}"

当前推荐上下文: {json.dumps(context, ensure_ascii=False) if context else "无"}

请输出 JSON 格式（不要输出其他内容）：
{{
  "type": "preference | task_feedback | fixed_profile",
  "field": "difficulty | time | language | pages | format | topic",
  "value": "具体值或分类（如 prefer_chinese, daily_30min, too_thick）",
  "confidence": 0.0-1.0,
  "reasoning": "压缩理由"
}}

规则：
1. type 选择：
   - fixed_profile: 用户的基本属性（如时间、难度基础）
   - preference: 用户偏好（如喜欢中文、偏好案例驱动）
   - task_feedback: 对特定书籍/任务的反馈（如"这本书太难"）
2. field 选择最合适的维度
3. value 要简洁、可量化
4. confidence 根据反馈明确程度给出（0.5-1.0）
"""

        response = llm.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "你是记忆压缩专家，专门把用户反馈转为结构化数据。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        # 解析 LLM 输出
        try:
            import re
            content = response.choices[0].message.content
            # 提取 JSON
            json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
            if json_match:
                compressed = json.loads(json_match.group(0))
                compressed["source"] = feedback  # 保存原文
                return compressed
        except Exception as e:
            print(f"Failed to parse LLM output: {e}")

        # 降级：简单规则
        return {
            "type": "preference",
            "field": "general",
            "value": feedback[:50],
            "confidence": 0.5,
            "source": feedback,
            "reasoning": "LLM解析失败，降级处理"
        }


# 全局服务实例
memory_service = MemoryService()
