"""
推荐评分引擎
"""
from typing import List, Dict
from models.schemas import Book, BookScore, UserInput, Memory
from config import settings


class Recommender:
    """推荐引擎：基于评分公式的可解释推荐"""

    def __init__(self):
        pass

    def recommend(
        self,
        books: List[Book],
        user_input: UserInput,
        memories: List[Memory]
    ) -> List[BookScore]:
        """
        推荐评分

        评分公式：
        book_score = topic_match * W1 + difficulty_match * W2 + time_match * W3 + preference_match * W4 - rejection_penalty

        Args:
            books: 候选书目
            user_input: 用户输入
            memories: 相关记忆

        Returns:
            排序后的 BookScore 列表
        """
        scored_books = []

        for book in books:
            scores = self._calculate_scores(book, user_input, memories)

            # 检查是否被拒绝
            rejection_penalty = self._check_rejection(book, memories)

            # 计算总分
            total = (
                scores["topic"] * settings.weight_topic +
                scores["difficulty"] * settings.weight_difficulty +
                scores["time"] * settings.weight_time +
                scores["preference"] * settings.weight_preference -
                rejection_penalty * settings.rejection_penalty
            )

            # 生成解释
            explanation = self._generate_explanation(book, scores, rejection_penalty, memories)

            scored_books.append(BookScore(
                book=book,
                total_score=round(total, 2),
                topic_score=round(scores["topic"], 2),
                difficulty_score=round(scores["difficulty"], 2),
                time_score=round(scores["time"], 2),
                preference_score=round(scores["preference"], 2),
                explanation=explanation
            ))

        # 排序
        scored_books.sort(key=lambda x: x.total_score, reverse=True)

        return scored_books

    def _calculate_scores(self, book: Book, user_input: UserInput, memories: List[Memory]) -> Dict[str, float]:
        """计算各项评分（0-1）"""

        # 1. 主题匹配度（0-1）
        topic_score = self._score_topic(book, user_input.goal)

        # 2. 难度匹配度（0-1）
        difficulty_score = self._score_difficulty(book, user_input.difficulty)

        # 3. 时间匹配度（0-1）
        time_score = self._score_time(book, user_input.time_per_day)

        # 4. 偏好匹配度（0-1）
        preference_score = self._score_preference(book, user_input, memories)

        return {
            "topic": topic_score,
            "difficulty": difficulty_score,
            "time": time_score,
            "preference": preference_score
        }

    def _score_topic(self, book: Book, user_goal: str) -> float:
        """主题匹配评分"""
        # 精确匹配
        if book.topic == user_goal:
            return 1.0

        # 关键词匹配
        goal_keywords = {
            "machine_learning": ["机器学习", "ml", "machine learning", "监督", "无监督"],
            "deep_learning": ["深度学习", "神经网络", "deep learning", "神经网络"],
            "python": ["python", "编程", "代码"],
            "nlp": ["自然语言", "nlp", "文本处理"],
            "computer_vision": ["计算机视觉", "图像", "cv"]
        }

        keywords = goal_keywords.get(user_goal, [user_goal])
        book_text = f"{book.title} {book.description or ''} {' '.join(book.keywords)}".lower()

        matches = sum(1 for kw in keywords if kw.lower() in book_text)
        if matches > 0:
            return 0.7 + 0.3 * min(matches / len(keywords), 1.0)

        return 0.0

    def _score_difficulty(self, book: Book, user_difficulty: str) -> float:
        """难度匹配评分"""
        difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
        book_level = difficulty_order.get(book.difficulty, 2)
        user_level = difficulty_order.get(user_difficulty, 2)

        # 完全匹配
        if book.difficulty == user_difficulty:
            return 1.0

        # 差一级
        if abs(book_level - user_level) == 1:
            return 0.6

        # 差两级
        return 0.2

    def _score_time(self, book: Book, daily_minutes: int) -> float:
        """时间适配评分"""
        # 估算阅读速度：慢速读者 10页/30min，快速 20页/30min
        daily_pages_slow = daily_minutes / 3  # 30分钟10页
        daily_pages_fast = daily_minutes / 1.5  # 30分钟20页

        # 推荐阅读天数：7-30天
        ideal_days = 14
        ideal_pages = book.pages / ideal_days

        # 判断是否在合理范围内
        if daily_pages_slow <= ideal_pages <= daily_pages_fast:
            return 1.0
        elif daily_pages_slow * 0.5 <= ideal_pages <= daily_pages_fast * 1.5:
            return 0.7
        else:
            return 0.4

    def _score_preference(self, book: Book, user_input: UserInput, memories: List[Memory]) -> float:
        """偏好匹配评分"""
        score = 0.5  # 基础分

        # 语言偏好
        if book.language == user_input.language:
            score += 0.2
        else:
            score -= 0.1

        # 案例驱动偏好
        case_pref = next((m for m in memories if m.field == "prefer_cases"), None)
        if case_pref and book.case_ratio >= 0.6:
            score += 0.15

        # 理论偏好
        theory_pref = next((m for m in memories if m.field == "prefer_theory"), None)
        if theory_pref and book.theory_ratio >= 0.6:
            score += 0.15

        return max(0.0, min(1.0, score))

    def _check_rejection(self, book: Book, memories: List[Memory]) -> float:
        """检查是否被拒绝（返回惩罚分数）"""
        rejection_memories = [m for m in memories if m.field in ["rejected_book", "too_thick", "too_difficult"]]

        for mem in rejection_memories:
            # 如果记忆提到这本书的ID或关键词
            if str(book.id) in str(mem.value):
                return 1.0

            # 关键词匹配
            if any(kw.lower() in str(mem.value).lower() for kw in book.keywords):
                return 0.8

            if book.title in str(mem.value):
                return 1.0

        return 0.0

    def _generate_explanation(self, book: Book, scores: Dict, rejection: float, memories: List[Memory]) -> str:
        """生成推荐解释"""
        parts = []

        if scores["topic"] >= 0.7:
            parts.append(f"✓ 主题匹配：{book.topic}")
        if scores["difficulty"] >= 0.7:
            parts.append(f"✓ 难度合适：{book.difficulty}")
        if scores["time"] >= 0.7:
            parts.append(f"✓ 时间适配：{book.pages}页")
        if scores["preference"] >= 0.7:
            parts.append(f"✓ 符合偏好")

        if rejection > 0:
            parts.append(f"⚠ 您曾反馈过类似书籍{'不适合' if rejection > 0.5 else '可能不太适合'}")

        if not parts:
            parts.append("一般匹配")

        return "；".join(parts)


# 全局服务实例
recommender = Recommender()
