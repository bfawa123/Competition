"""
Agent 核心逻辑
"""
import time
from datetime import datetime
from typing import List, Dict, Optional
from models.schemas import Book, UserInput, Memory, BookScore, RecommendationResponse
from services.book_service import book_service
from services.memory_service import memory_service
from services.recommender import recommender
from utils.llm_client import get_llm_client
from utils.scorer import normalise_memory_value
from config import settings


class LibrarianAgent:
    """
    知遇 AI 馆员 Agent

    工具链：
    1. search_books - 检索候选书
    2. retrieve_memory - 加载相关记忆
    3. save_memory - 保存反馈
    """

    def __init__(self):
        self.llm = None  # 延迟初始化，避免无 API Key 时启动失败
        self.tools = {
            "search_books": self._tool_search_books,
            "retrieve_memory": self._tool_retrieve_memory,
            "save_memory": self._tool_save_memory
        }
        self.trace = []  # 记录工具调用
        self._t = 0.0   # 计时基准（用于给每个步骤算耗时）

    def _get_llm(self):
        """延迟获取 LLM 客户端"""
        if self.llm is None:
            self.llm = get_llm_client()
        return self.llm

    def run(self, user_input: UserInput, user_id: str) -> RecommendationResponse:
        """
        执行推荐流程

        Args:
            user_input: 用户输入
            user_id: 用户ID

        Returns:
            推荐结果（含记忆引用、Agent轨迹）
        """
        self.trace = []
        self._t = time.perf_counter()

        # ========== 步骤1：检索相关记忆 ==========
        all_memories = memory_service.get_all_memories(user_id)
        memories = memory_service.retrieve_memory(user_id, user_input.goal)
        self._log_trace("retrieve_memory", {
            "query": user_input.goal,
            "user_id": user_id,
            "candidates": len(all_memories),
            "used": len(memories),
        }, self._lap())

        # ========== 步骤2：检索候选书目 ==========
        requested_difficulty = getattr(user_input.difficulty, "value", user_input.difficulty)
        eligible_difficulties = {
            "beginner": ["beginner"],
            "intermediate": ["beginner", "intermediate"],
            "advanced": ["beginner", "intermediate", "advanced"],
        }
        filters = {
            "topic": user_input.goal,
            "difficulty": eligible_difficulties.get(requested_difficulty, [requested_difficulty]),
            "availability": True
        }

        # 如果有"页数偏好"的记忆，添加筛选
        pages_pref = next((m for m in memories if m.field == "pages"), None)
        if pages_pref:
            value = normalise_memory_value(pages_pref.value)
            if value == "prefer_short":
                filters["max_pages"] = 300
            elif value == "prefer_long":
                filters["min_pages"] = 300

        candidates = book_service.search(filters)

        # 页数偏好（如"太厚了"→max_pages=300）可能把候选全部过滤光。
        # 这时放宽页数条件重试，避免用户拿不到任何结果。
        relaxed_pages = False
        if not candidates and ("max_pages" in filters or "min_pages" in filters):
            relaxed = {k: v for k, v in filters.items() if k not in ("max_pages", "min_pages")}
            candidates = book_service.search(relaxed)
            relaxed_pages = bool(candidates)

        self._log_trace("search_books", {
            **filters,
            "count": len(candidates),
            "relaxed_pages": relaxed_pages,
        }, self._lap())

        if not candidates:
            return RecommendationResponse(
                books=[],
                memories_used=memories,
                explanation="未找到符合条件的书籍，请尝试调整筛选条件。",
                agent_trace=self.trace
            )

        # ========== 步骤3：评分排序 ==========
        scored_books = recommender.recommend(candidates, user_input, memories)
        top_books = scored_books[:5]  # 取前5本
        self._log_trace("recommend", {
            "candidates": len(candidates),
            "top_count": len(top_books),
        }, self._lap())

        # ========== 步骤4：生成自然语言推荐说明 ==========
        llm = self._get_llm()
        explanation = self._generate_explanation(top_books, memories, user_input.language)
        self._log_trace("generate_explanation", {
            "mode": "llm" if llm else "fallback",
            "tokens": (max(1, round(len(explanation) / 1.5)) if llm else 0),
        }, self._lap())

        return RecommendationResponse(
            books=top_books,
            memories_used=memories,
            explanation=explanation,
            agent_trace=self.trace
        )

    def process_feedback(self, user_id: str, feedback: str, context: Optional[Dict] = None) -> Memory:
        """
        处理用户反馈

        Args:
            user_id: 用户ID
            feedback: 用户反馈文本
            context: 当前上下文（如正在讨论的书籍）

        Returns:
            压缩后的记忆
        """
        self._log_trace("compress_feedback", {"feedback": feedback})

        # 压缩反馈为结构化记忆
        memory = memory_service.write_memory(user_id, feedback, context)

        self._log_trace("save_memory", {"memory_id": memory.id, "field": memory.field})

        return memory

    def _tool_search_books(self, filters: Dict, query: str = "") -> List[Book]:
        """工具：检索书目"""
        return book_service.search(filters, query)

    def _tool_retrieve_memory(self, query: str, user_id: str, top_k: int = 5) -> List[Memory]:
        """工具：检索记忆"""
        return memory_service.retrieve_memory(user_id, query, top_k)

    def _tool_save_memory(self, user_id: str, feedback: str, context: Optional[Dict] = None) -> Memory:
        """工具：保存记忆"""
        return memory_service.write_memory(user_id, feedback, context)

    def _generate_explanation(self, books: List[BookScore], memories: List[Memory], preferred_language: str = "zh") -> str:
        """生成自然语言推荐说明"""
        # 构建记忆引用文本
        memory_refs = []
        for mem in memories:
            memory_refs.append(f"- {mem.field}: {mem.value}（置信度{mem.confidence}）")

        memory_text = "\n".join(memory_refs) if memory_refs else "无相关记忆"

        # 构建书单文本
        books_text = ""
        for i, bs in enumerate(books, 1):
            books_text += f"{i}. {bs.book.title}（{bs.book.difficulty}，{bs.book.pages}页）\n"
            books_text += f"   评分: {bs.total_score} | {bs.explanation}\n"

        # LLM 生成解释
        prompt = f"""你是知遇AI馆员，正在为用户推荐学习书籍。

用户相关记忆：
{memory_text}

推荐书单（已评分排序）：
{books_text}

请用简洁友好的语言总结推荐理由，并说明：
1. 这些书为什么适合用户？
2. 引用了哪些用户偏好/记忆？
3. 建议的阅读顺序？

控制在150字以内。"""

        language_note = ""
        languages = {book.book.language for book in books}
        if len(languages) > 1:
            language_note = "书库中同时保留了中文和英文书目；已按您的语言偏好优先排序。"
        try:
            llm = self._get_llm()
            if llm is None:
                raise RuntimeError("LLM 客户端不可用")
            explanation = llm.chat([
                {"role": "system", "content": "你是知遇AI馆员，专业的学习路线推荐助手。"},
                {"role": "user", "content": prompt}
            ], temperature=0.7)
        except Exception as e:
            print(f"LLM generation failed: {e}")
            # 兜底：基于评分结果生成简要说明
            top_title = books[0].book.title if books else "相关书籍"
            mem_count = len(memories)
            if mem_count > 0:
                explanation = f"根据您的学习目标和 {mem_count} 条历史记忆，为您推荐以《{top_title}》为首的学习路线。"
            else:
                explanation = f"根据您的学习目标，为您推荐以《{top_title}》为首的学习路线，建议从基础到进阶逐步深入。"

        if language_note:
            explanation = f"{explanation} {language_note}"

        return explanation

    def _lap(self) -> float:
        """返回距上一次记录的毫秒数，用于给轨迹页展示每步耗时。"""
        now = time.perf_counter()
        ms = round((now - self._t) * 1000, 2)
        self._t = now
        return ms

    def _log_trace(self, action: str, details: Dict, duration_ms: float = None):
        """记录Agent轨迹（带真实耗时与时间戳）"""
        self.trace.append({
            "action": action,
            "details": details,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "duration_ms": duration_ms,
        })

    def get_trace(self) -> List[Dict]:
        """获取Agent执行轨迹"""
        return self.trace


# 全局Agent实例
agent = LibrarianAgent()
