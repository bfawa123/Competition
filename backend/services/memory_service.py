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
        confidence = min(1.0, max(0.0, float(compressed.get("confidence", 0.8))))
        memory = Memory(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            user_id=user_id,
            type=MemoryType(compressed["type"]),
            field=compressed["field"],
            value=compressed["value"],
            confidence=confidence,
            source=compressed.get("source", feedback),
            created_at=datetime.now()
        )

        # 4. 存储
        self.db.save_memory(memory)

        # 5. 保存 embedding 缓存
        self._save_embeddings_cache()

        return memory

    @staticmethod
    def _compute_similarities(query: str, texts: List[str]) -> List[float]:
        """
        用"字符 n-gram TF-IDF"计算 query 与每条记忆的余弦相似度。

        原实现依赖一个只在 5 条假文档上拟合的向量器，任何真实文本都会得到
        零向量、相似度恒为 0。这里改成拿"查询 + 当前用户的记忆"现拟合，
        中文（按字符切）和英文都能得到有意义的相似度。
        """
        if not texts:
            return []
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity as sk_cosine

            corpus = [query] + list(texts)
            vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(1, 3), max_features=4096)
            matrix = vectorizer.fit_transform(corpus)
            sims = sk_cosine(matrix[0:1], matrix[1:]).ravel()
            return [float(s) for s in sims]
        except Exception as exc:
            print(f"[WARN] 记忆相似度计算失败，回退按置信度排序: {exc}")
            return [0.0] * len(texts)

    def retrieve_memory(self, user_id: str, query: str, top_k: int = None) -> List[Memory]:
        """
        检索相关记忆（向量相似度 + 关键词回退）

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

        # 2. 用真实文本现拟合 TF-IDF 计算相似度（含反馈原文，便于命中"太厚/太难"等说法）
        mem_texts = [f"{m.field}: {m.value} {m.source or ''}".strip() for m in user_memories]
        similarities = self._compute_similarities(query, mem_texts)

        # 3. 只保留达到阈值的记忆，用 相似度 × 置信度 加权
        scored_memories = [
            (memory, similarity * memory.confidence)
            for memory, similarity in zip(user_memories, similarities)
            if similarity >= settings.memory_similarity_threshold
        ]

        # 4. 回退：如果没有明显相关的记忆，返回用户所有记忆（按置信度排序）
        if not scored_memories:
            scored_memories = [(m, m.confidence) for m in user_memories]

        # 5. 按分数排序，取 Top-K
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_memories = [mem for mem, score in scored_memories[:top_k]]

        # 6. 更新使用统计
        for memory in top_memories:
            memory.usage_count = max(0, memory.usage_count) + 1
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

        # 无 LLM 时使用规则降级
        if llm is None:
            return self._rule_based_compress(feedback, context)

        prompt = f"""请将以下用户反馈压缩为结构化记忆，用于个性化推荐。

用户反馈: "{feedback}"

当前推荐上下文: {json.dumps(context, ensure_ascii=False) if context else "无"}

请输出 JSON 格式（不要输出其他内容）：
{{
  "type": "preference | task_feedback | fixed_profile",
  "field": "difficulty | time | language | pages | format | topic",
  "value": "从规范值里选最贴近的一个：prefer_short | prefer_long | prefer_easier | prefer_harder | prefer_chinese | prefer_english | prefer_cases | prefer_theory；确实无法归类时才用简短中文短语",
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

        try:
            response = llm.chat([
                {"role": "system", "content": "你是记忆压缩专家，专门把用户反馈转为结构化数据。"},
                {"role": "user", "content": prompt}
            ], temperature=0.3)

            # 解析 LLM 输出
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                compressed = json.loads(json_match.group(0))
                compressed["source"] = feedback  # 保存原文
                return compressed
        except Exception as e:
            print(f"LLM compress failed, using rule-based: {e}")

        # 降级：规则
        return self._rule_based_compress(feedback, context)

    def _rule_based_compress(self, feedback: str, context: Optional[Dict] = None) -> Dict:
        """基于规则的反馈压缩（无 LLM 时的降级方案）"""
        feedback_lower = feedback.lower()

        # 规则匹配
        if any(kw in feedback for kw in ["太厚", "太长", "页数多", "篇幅"]):
            return {"type": "preference", "field": "pages", "value": "prefer_short", "confidence": 0.85, "source": feedback}
        # 注意：前端快捷按钮是「难度太高」，必须匹配"太高"（原来只认"太难"，按钮会变成无效的 general 记忆）
        if any(kw in feedback for kw in ["太难", "太高", "偏难", "看不懂", "太硬", "太难懂"]):
            return {"type": "preference", "field": "difficulty", "value": "prefer_easier", "confidence": 0.85, "source": feedback}
        if any(kw in feedback for kw in ["太简单", "太浅", "太基础"]):
            return {"type": "preference", "field": "difficulty", "value": "prefer_harder", "confidence": 0.8, "source": feedback}
        if any(kw in feedback for kw in ["中文", "Chinese", "中文版"]):
            return {"type": "preference", "field": "language", "value": "prefer_chinese", "confidence": 0.9, "source": feedback}
        if any(kw in feedback for kw in ["英文", "English", "原版"]):
            return {"type": "preference", "field": "language", "value": "prefer_english", "confidence": 0.9, "source": feedback}
        if any(kw in feedback for kw in ["案例", "实战", "项目"]):
            return {"type": "preference", "field": "format", "value": "prefer_cases", "confidence": 0.85, "source": feedback}
        if any(kw in feedback for kw in ["理论", "原理", "推导"]):
            return {"type": "preference", "field": "format", "value": "prefer_theory", "confidence": 0.85, "source": feedback}
        if any(kw in feedback for kw in ["读过", "看过了", "已经"]):
            return {"type": "task_feedback", "field": "rejected_book", "value": feedback[:50], "confidence": 0.9, "source": feedback}
        if any(kw in feedback for kw in ["每天", "每日", "分钟"]):
            return {"type": "fixed_profile", "field": "time", "value": feedback[:50], "confidence": 0.75, "source": feedback}

        # 默认
        return {
            "type": "preference",
            "field": "general",
            "value": feedback[:50],
            "confidence": 0.5,
            "source": feedback,
            "reasoning": "规则匹配降级处理"
        }


# 全局服务实例
memory_service = MemoryService()
