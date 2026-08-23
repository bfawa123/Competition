"""
书目检索服务
"""
from typing import List, Dict, Optional
import re
from models.schemas import Book, BookSearchFilters
from models.database import get_db
from config import settings
from utils.embedding import EmbeddingManager


class BookService:
    """书目检索服务"""

    def __init__(self):
        self._db = None
        self._semantic_model = None

    @property
    def db(self):
        """延迟获取数据库连接"""
        if self._db is None:
            self._db = get_db()
        return self._db

    def search(self, filters: Dict, query: str = "") -> List[Book]:
        """
        检索书目

        Args:
            filters: 筛选条件 {topic, difficulty, language, max_pages, min_case_ratio, availability}
            query: 关键词查询（可用于扩展）

        Returns:
            符合条件的书目列表
        """
        topic = filters.get("topic")
        if topic:
            # 用户输入可能是“Python”“Python入门”等自然表达，
            # 不应要求它和数据库的标准主题完全相等。
            relaxed_filters = dict(filters)
            relaxed_filters.pop("topic", None)
            books = self.db.search_books(relaxed_filters)
            books = self._filter_by_topic_relevance(books, topic)
        else:
            books = self.db.search_books(filters)

        # 如果有关键词，进一步筛选（匹配书名/作者/主题/简介/关键词/馆藏位置）
        if query:
            query_lower = query.lower()
            books = [
                b for b in books
                if query_lower in b.title.lower()
                or (query_lower in (b.author or "").lower())
                or query_lower in b.topic.lower()
                or (query_lower in b.description.lower() if b.description else False)
                or (query_lower in (b.location or "").lower())
                or any(query_lower in kw.lower() for kw in b.keywords)
            ]

        return books

    @staticmethod
    def _normalise(text: str) -> str:
        return re.sub(r"[\s punctuation，。！？、；：“”‘’（）()【】\[\]·]", "", (text or "").lower())

    def _filter_by_topic_relevance(self, books: List[Book], topic: str) -> List[Book]:
        """主题召回：优先标准主题，其次标题/简介/关键词包含匹配。"""
        query = self._normalise(topic)
        if not query:
            return books

        def searchable(book: Book) -> str:
            return self._normalise(" ".join([
                book.topic, book.title, book.description or "", " ".join(book.keywords)
            ]))

        exact = [book for book in books if self._normalise(book.topic) == query]
        if exact:
            return exact + [book for book in books if book not in exact and query in searchable(book)]

        matched = [book for book in books if query in searchable(book) or searchable(book) in query]
        if matched:
            return matched

        # 中文自然语言输入的轻量语义兜底，真正的向量模型可通过
        # SEMANTIC_MODEL 配置启用；没有模型时也不能让书目变成空白。
        aliases = {
            "python": ["python基础", "编程", "程序设计"],
            "机器学习": ["machinelearning", "深度学习", "人工智能", "算法"],
            "深度学习": ["机器学习", "人工智能", "神经网络"],
            "人工智能": ["机器学习", "深度学习", "算法"],
        }
        terms = aliases.get(query, [])
        alias_matches = [book for book in books if any(term in searchable(book) for term in terms)]
        if alias_matches:
            return alias_matches

        # 可选的真正语义召回：安装 sentence-transformers 后自动使用
        # BAAI/bge-m3；模型不可用时保持上面的规则兜底，不影响离线启动。
        try:
            if self._semantic_model is None:
                self._semantic_model = EmbeddingManager(force_tfidf=False)
            if not self._semantic_model.use_tfidf:
                texts = [f"{book.title}。主题：{book.topic}。{book.description or ''}" for book in books]
                query_vector = self._semantic_model.get_embedding(topic)
                book_vectors = self._semantic_model.batch_embed(texts)
                ranked = sorted(
                    zip(books, book_vectors),
                    key=lambda item: self._semantic_model.cosine_similarity(query_vector, item[1]),
                    reverse=True,
                )
                semantic_matches = [book for book, vector in ranked[:10]
                                    if self._semantic_model.cosine_similarity(query_vector, vector) >= settings.semantic_similarity_threshold]
                if semantic_matches:
                    return semantic_matches
        except Exception as exc:
            print(f"Semantic book retrieval unavailable, using lexical fallback: {exc}")
        return []

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """根据ID获取书目"""
        return self.db.get_book_by_id(book_id)

    def get_by_topic(self, topic: str) -> List[Book]:
        """根据主题获取书目"""
        return self.search({"topic": topic})

    def get_recommended_by_difficulty(self, difficulty: str) -> List[Book]:
        """根据难度获取推荐书目"""
        return self.search({"difficulty": difficulty})


# 全局服务实例
book_service = BookService()
