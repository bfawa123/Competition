"""
评分工具函数
"""
import math
from typing import Dict, List
from models.schemas import Book, UserInput, Memory


def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """归一化到 0-1"""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def calculate_time_score(pages: int, daily_minutes: int) -> float:
    """
    计算时间适配分数

    假设：
    - 慢速读者：10页/30分钟
    - 快速读者：20页/30分钟
    - 推荐阅读周期：14天
    """
    daily_pages_slow = daily_minutes / 3
    daily_pages_fast = daily_minutes / 1.5

    ideal_pages = pages / 14

    if daily_pages_slow <= ideal_pages <= daily_pages_fast:
        return 1.0
    elif daily_pages_slow * 0.5 <= ideal_pages <= daily_pages_fast * 1.5:
        return 0.7
    else:
        return 0.4


def calculate_difficulty_score(book_difficulty: str, user_difficulty: str) -> float:
    """计算难度匹配分数"""
    difficulty_order = {"beginner": 1, "intermediate": 2, "advanced": 3}
    book_level = difficulty_order.get(book_difficulty, 2)
    user_level = difficulty_order.get(user_difficulty, 2)

    diff = abs(book_level - user_level)
    if diff == 0:
        return 1.0
    elif diff == 1:
        return 0.6
    else:
        return 0.2


def check_rejection(book: Book, memories: List[Memory]) -> float:
    """检查是否被用户拒绝"""
    for mem in memories:
        if mem.field in ["rejected_book", "too_thick", "too_difficult"]:
            # 检查是否匹配
            if str(book.id) in str(mem.value):
                return 1.0
            if book.title in str(mem.value):
                return 1.0
            if any(kw.lower() in str(mem.value).lower() for kw in book.keywords):
                return 0.8
    return 0.0


# 记忆值的规范词表映射。
# LLM 压缩出来的 value 可能是 prefer_basic / prefer_thin / 中文短语等，
# 而评分器只认少数几个规范值，这里统一兜住同义词，避免"记忆写了但排序不动"。
_VALUE_SYNONYMS = [
    ("prefer_short", ["short", "thin", "brief", "fewer", "短", "薄", "少页"]),
    ("prefer_long", ["long", "thick", "more pages", "长", "厚", "多页"]),
    ("prefer_easier", ["easier", "easy", "basic", "simple", "lower", "beginner", "简", "容易", "基础", "入门"]),
    ("prefer_harder", ["harder", "hard", "advanced", "complex", "deeper", "难", "高级", "深入"]),
    ("prefer_chinese", ["chinese", "zh", "中文", "汉语"]),
    ("prefer_english", ["english", "en", "英文", "英语"]),
    ("prefer_cases", ["case", "example", "practice", "案例", "实例", "实战", "练习"]),
    ("prefer_theory", ["theory", "principle", "proof", "理论", "原理", "推导"]),
]


def normalise_memory_value(value) -> str:
    """把记忆里的 value 归一到评分器认识的标准值；认不出时原样返回小写字符串。"""
    text = str(value).lower()
    for canonical, keywords in _VALUE_SYNONYMS:
        if any(k in text for k in keywords):
            return canonical
    return text
