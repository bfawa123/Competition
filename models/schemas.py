"""
数据模型定义
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============ 枚举类型 ============

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MemoryType(str, Enum):
    FIXED_PROFILE = "fixed_profile"  # 固定画像
    PREFERENCE = "preference"  # 偏好记忆
    TASK_FEEDBACK = "task_feedback"  # 任务反馈


class Language(str, Enum):
    ZH = "zh"
    EN = "en"


# ============ 书目模型 ============

class Book(BaseModel):
    id: int
    title: str
    topic: str  # 主题：machine_learning, python, deep_learning, nlp, etc.
    difficulty: DifficultyLevel
    pages: int
    language: Language
    case_ratio: float  # 0-1，案例占比
    theory_ratio: float  # 0-1，理论占比
    prerequisites: List[str]  # 前置知识
    goals: List[str]  # 适用目标
    keywords: List[str]  # 关键词
    availability: bool = True  # 馆藏状态
    description: Optional[str] = None


class BookSearchFilters(BaseModel):
    topic: Optional[str] = None
    difficulty: Optional[DifficultyLevel] = None
    language: Optional[Language] = None
    max_pages: Optional[int] = None
    min_case_ratio: Optional[float] = None
    availability: bool = True


# ============ 记忆模型 ============

class Memory(BaseModel):
    id: str
    user_id: str
    type: MemoryType
    field: str  # difficulty | time | language | pages | format | ...
    value: Any  # 具体值或分类
    confidence: float  # 0-1
    source: str  # 来源描述
    created_at: datetime
    last_used: Optional[datetime] = None
    usage_count: int = 0


class MemoryCreate(BaseModel):
    user_id: str
    feedback: str
    context: Optional[Dict[str, Any]] = None


class MemoryRetrieve(BaseModel):
    query: str
    user_id: str
    top_k: int = 5


# ============ 用户输入模型 ============

class UserInput(BaseModel):
    goal: str  # 学习目标：machine_learning, deep_learning, etc.
    difficulty: DifficultyLevel
    time_per_day: int  # 每日可用时间（分钟）
    language: Language = Language.ZH
    additional_constraints: Optional[str] = None


# ============ 推荐模型 ============

class BookScore(BaseModel):
    book: Book
    total_score: float
    topic_score: float
    difficulty_score: float
    time_score: float
    preference_score: float
    explanation: str


class RecommendationResponse(BaseModel):
    books: List[BookScore]
    memories_used: List[Memory]
    explanation: str
    agent_trace: List[Dict[str, Any]]


class RecommendationRequest(BaseModel):
    user_input: UserInput
    user_id: str
    compare_with: Optional[str] = None  # 用于前后对比
