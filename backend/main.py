"""
FastAPI 主应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config import settings
from models.schemas import (
    UserInput,
    RecommendationRequest,
    RecommendationResponse,
    MemoryCreate,
    MemoryRetrieve,
    BookSearchFilters
)
from services.agent import agent
from services.memory_service import memory_service
from services.book_service import book_service
from models.database import init_db

from typing import Dict, Any


# ============ 生命周期管理 ============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时初始化数据库"""
    print("[LAUNCH] 启动知遇AI馆员服务...")
    init_db(settings.books_data_path, settings.memories_data_path)
    print("[OK] 数据库初始化完成")
    yield
    print("[BYE] 服务关闭")


# ============ FastAPI 应用 ============

app = FastAPI(
    title="知遇 AI 馆员 API",
    description="基于反馈记忆的个性化学习阅读路线助手",
    version="1.0.0",
    lifespan=lifespan
)

# 允许跨域（前端调用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 封面图片静态服务（books.json 中 cover 字段指向 /covers/{id}.jpeg）
import os
_COVERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "covers")
if os.path.isdir(_COVERS_DIR):
    app.mount("/covers", StaticFiles(directory=_COVERS_DIR), name="covers")


# ============ 健康检查 ============

@app.get("/")
async def root():
    """健康检查"""
    return {
        "service": "知遇 AI 馆员",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查详情"""
    return {
        "status": "healthy",
        "config": {
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
            "memory_top_k": settings.memory_top_k
        }
    }


# ============ 推荐接口 ============

@app.post("/api/agent/recommend", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest):
    """
    Agent 推荐接口

    流程：
    1. retrieve_memory - 加载用户相关记忆
    2. search_books - 检索候选书目
    3. recommend - 评分排序
    4. 生成推荐说明
    """
    try:
        response = agent.run(request.user_input, request.user_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agent/trace/{user_id}")
async def get_agent_trace(user_id: str):
    """获取Agent执行轨迹"""
    return {
        "user_id": user_id,
        "trace": agent.get_trace()
    }


# ============ 记忆接口 ============

@app.post("/api/memory/write")
async def write_memory(request: MemoryCreate):
    """
    写入记忆 - 压缩用户反馈

    返回压缩后的结构化记忆
    """
    try:
        memory = memory_service.write_memory(request.user_id, request.feedback, request.context)
        return {
            "success": True,
            "memory": memory.model_dump(mode="json"),
            "message": f"记忆已保存：{memory.field} = {memory.value}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/retrieve")
async def retrieve_memory(query: str, user_id: str, top_k: int = 5):
    """
    检索相关记忆（向量相似度检索）

    返回按相似度排序的记忆列表
    """
    try:
        memories = memory_service.retrieve_memory(user_id, query, top_k)
        return {
            "query": query,
            "user_id": user_id,
            "memories": [m.model_dump(mode="json") for m in memories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory/list/{user_id}")
async def list_memories(user_id: str):
    """获取用户所有记忆"""
    try:
        memories = memory_service.get_all_memories(user_id)
        return {
            "user_id": user_id,
            "memories": [m.model_dump(mode="json") for m in memories]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/memory/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    """删除记忆"""
    try:
        success = memory_service.delete_memory(user_id, memory_id)
        if success:
            return {"success": True, "message": "记忆已删除"}
        else:
            raise HTTPException(status_code=404, detail="记忆不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 书目接口 ============

@app.get("/api/books/search")
async def search_books(
    query: str = None,
    topic: str = None,
    difficulty: str = None,
    language: str = None,
    max_pages: int = None,
    min_case_ratio: float = None,
    availability: bool = True
):
    """检索书目（query 为关键词，匹配书名/主题/简介/关键词/馆藏位置）"""
    try:
        filters = {
            "topic": topic,
            "difficulty": difficulty,
            "language": language,
            "max_pages": max_pages,
            "min_case_ratio": min_case_ratio,
            "availability": availability
        }
        # 过滤 None
        filters = {k: v for k, v in filters.items() if v is not None}

        books = book_service.search(filters, query=query or "")
        return {
            "count": len(books),
            "books": [b.model_dump(mode="json") for b in books]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/books/{book_id}")
async def get_book(book_id: int):
    """获取单本书详情"""
    book = book_service.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="书籍不存在")
    return book.model_dump(mode="json")


# ============ 演示接口 ============

@app.get("/api/demo/compare/{user_id}")
async def demo_compare(user_id: str):
    """
    前后对比演示接口

    模拟用户第一次推荐（无记忆）vs 第二次推荐（有记忆）
    """
    from models.schemas import UserInput, DifficultyLevel, Language

    # 第一次推荐（无记忆）
    first_request = RecommendationRequest(
        user_input=UserInput(
            goal="machine_learning",
            difficulty=DifficultyLevel.BEGINNER,
            time_per_day=30,
            language=Language.ZH
        ),
        user_id=user_id
    )
    first_result = agent.run(first_request.user_input, f"{user_id}_first")

    # 模拟用户反馈
    feedback = "这本书太厚了，我每天只有30分钟，而且偏好中文案例"
    memory = memory_service.write_memory(user_id, feedback)

    # 第二次推荐（有记忆）
    second_request = RecommendationRequest(
        user_input=UserInput(
            goal="machine_learning",
            difficulty=DifficultyLevel.BEGINNER,
            time_per_day=30,
            language=Language.ZH
        ),
        user_id=user_id
    )
    second_result = agent.run(second_request.user_input, user_id)

    # 清理演示记忆
    memory_service.delete_memory(user_id, memory.id)

    return {
        "user_id": user_id,
        "feedback": feedback,
        "memory_saved": memory.model_dump(mode="json"),
        "first_recommendation": {
            "books": [bs.model_dump(mode="json") for bs in first_result.books[:3]],
            "explanation": first_result.explanation,
            "memories_used": len(first_result.memories_used)
        },
        "second_recommendation": {
            "books": [bs.model_dump(mode="json") for bs in second_result.books[:3]],
            "explanation": second_result.explanation,
            "memories_used": len(second_result.memories_used)
        },
        "comparison": {
            "memory_added": memory.field,
            "impact": "推荐结果已根据反馈调整" if second_result.memories_used else "无记忆影响"
        }
    }


# ============ 启动 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
