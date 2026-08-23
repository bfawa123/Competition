"""
数据访问层
"""
import json
import os
import threading
from typing import List, Optional
from models.schemas import Book, Memory


class Database:
    """简单的 JSON 文件数据库"""

    def __init__(self, books_path: str, memories_path: str):
        self.books_path = books_path
        self.memories_path = memories_path
        self._ensure_files()
        self._memory_lock = threading.Lock()

    def _ensure_files(self):
        """确保数据文件存在"""
        os.makedirs(os.path.dirname(self.books_path), exist_ok=True)

        if not os.path.exists(self.books_path):
            self._init_books_data()

        if not os.path.exists(self.memories_path):
            with open(self.memories_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _init_books_data(self):
        """初始化示例书目数据"""
        sample_books = [
            {
                "id": 1,
                "title": "机器学习实战",
                "topic": "machine_learning",
                "difficulty": "beginner",
                "pages": 350,
                "language": "zh",
                "case_ratio": 0.7,
                "theory_ratio": 0.3,
                "prerequisites": ["Python基础"],
                "goals": ["入门机器学习", "实战项目"],
                "keywords": ["Scikit-learn", "监督学习", "Kaggle"],
                "availability": True,
                "description": "以Python为工具，深入浅出地介绍机器学习核心算法"
            },
            {
                "id": 2,
                "title": "深度学习入门",
                "topic": "deep_learning",
                "difficulty": "intermediate",
                "pages": 280,
                "language": "zh",
                "case_ratio": 0.5,
                "theory_ratio": 0.5,
                "prerequisites": ["机器学习基础", "Python"],
                "goals": ["理解深度学习原理", "神经网络"],
                "keywords": ["神经网络", "反向传播", "PyTorch"],
                "availability": True,
                "description": "基于Python的深度学习原理与实践"
            },
            {
                "id": 3,
                "title": "Python编程：从入门到实践",
                "topic": "python",
                "difficulty": "beginner",
                "pages": 459,
                "language": "zh",
                "case_ratio": 0.8,
                "theory_ratio": 0.2,
                "prerequisites": [],
                "goals": ["掌握Python基础", "编程入门"],
                "keywords": ["Python", "编程基础", "项目实战"],
                "availability": True,
                "description": "以项目驱动的方式学习Python编程"
            }
        ]

        with open(self.books_path, "w", encoding="utf-8") as f:
            json.dump(sample_books, f, ensure_ascii=False, indent=2)

    # ============ 书目操作 ============

    def get_all_books(self) -> List[Book]:
        """获取所有书目"""
        with open(self.books_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Book(**book) for book in data]

    def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """根据ID获取书目"""
        books = self.get_all_books()
        for book in books:
            if book.id == book_id:
                return book
        return None

    def search_books(self, filters: dict) -> List[Book]:
        """根据条件筛选书目"""
        books = self.get_all_books()

        # 主题筛选
        if filters.get("topic"):
            books = [b for b in books if b.topic == filters["topic"]]

        # 难度筛选
        if filters.get("difficulty"):
            difficulties = filters["difficulty"]
            if isinstance(difficulties, (list, tuple, set)):
                books = [b for b in books if b.difficulty in difficulties]
            else:
                books = [b for b in books if b.difficulty == difficulties]

        # 语言筛选
        if filters.get("language"):
            books = [b for b in books if b.language == filters["language"]]

        # 最大页数筛选
        if filters.get("max_pages"):
            books = [b for b in books if b.pages <= filters["max_pages"]]

        # 最小案例占比
        if filters.get("min_case_ratio"):
            books = [b for b in books if b.case_ratio >= filters["min_case_ratio"]]

        # 馆藏状态
        if filters.get("availability") is not None:
            books = [b for b in books if b.availability == filters["availability"]]

        return books

    def add_book(self, book: Book):
        """添加书目"""
        books = self.get_all_books()
        books.append(book)
        with open(self.books_path, "w", encoding="utf-8") as f:
            json.dump([b.model_dump() for b in books], f, ensure_ascii=False, indent=2)

    # ============ 记忆操作 ============

    def get_all_memories(self) -> dict:
        """获取所有记忆（按 user_id 组织）"""
        with open(self.memories_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_user_memories(self, user_id: str) -> List[Memory]:
        """获取指定用户的所有记忆"""
        all_memories = self.get_all_memories()
        user_data = all_memories.get(user_id, [])
        return [Memory(**mem) for mem in user_data]

    def save_memory(self, memory: Memory):
        """保存记忆"""
        with self._memory_lock:
            all_memories = self.get_all_memories()
            user_id = memory.user_id
            if user_id not in all_memories:
                all_memories[user_id] = []

            existing_idx = next(
                (idx for idx, mem in enumerate(all_memories[user_id]) if mem["field"] == memory.field),
                None,
            )
            mem_dict = memory.model_dump(mode="json")
            if existing_idx is not None:
                all_memories[user_id][existing_idx] = mem_dict
            else:
                all_memories[user_id].append(mem_dict)

            temp_path = f"{self.memories_path}.{os.getpid()}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(all_memories, f, ensure_ascii=False, indent=2, default=str)
            os.replace(temp_path, self.memories_path)

    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """删除记忆"""
        with self._memory_lock:
            all_memories = self.get_all_memories()
            if user_id not in all_memories:
                return False

            user_memories = all_memories[user_id]
            all_memories[user_id] = [m for m in user_memories if m["id"] != memory_id]

            temp_path = f"{self.memories_path}.{os.getpid()}.delete.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(all_memories, f, ensure_ascii=False, indent=2, default=str)
            os.replace(temp_path, self.memories_path)

            return True


# 全局数据库实例
db: Optional[Database] = None


def init_db(books_path: str, memories_path: str):
    """初始化数据库"""
    global db
    db = Database(books_path, memories_path)


def get_db() -> Database:
    """获取数据库实例"""
    if db is None:
        raise RuntimeError("Database not initialized")
    return db
