"""
书目检索服务
"""
from typing import List, Dict, Optional
from models.schemas import Book, BookSearchFilters
from models.database import get_db
from config import settings


class BookService:
    """书目检索服务"""

    def __init__(self):
        self._db = None

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
        books = self.db.search_books(filters)

        # 如果有关键词，进一步筛选
        if query:
            query_lower = query.lower()
            books = [
                b for b in books
                if query_lower in b.title.lower()
                or (query_lower in b.description.lower() if b.description else False)
                or any(query_lower in kw.lower() for kw in b.keywords)
            ]

        return books

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
