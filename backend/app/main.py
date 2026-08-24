"""
FastAPI 主应用
"""
import sys
from pathlib import Path

# 确保 backend 目录在 sys.path 中，支持从 app/ 导入时找到其他模块
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

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
    BookSearchFilters,
    AssistantChatRequest,
    AssistantReply
)
from services.agent import agent
from services.memory_service import memory_service
from services.book_service import book_service
from models.database import init_db

import re
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


# ============ 灵犀助手接口 ============

@app.post("/api/assistant/chat", response_model=AssistantReply)
async def assistant_chat(request: AssistantChatRequest):
    """
    灵犀学习助手 - 智能问答

    结合用户上下文（学习目标、路线书籍、个人偏好记忆）回答用户问题。

    使用场景：
    - 在"我的路线"页面询问学习建议
    - 询问为什么这样安排学习路线
    - 询问如何调整学习计划
    """
    try:
        # 构建上下文信息
        context_parts = []

        # 1. 用户基本信息
        context_parts.append(f"用户：{request.context.userName}")

        # 2. 学习目标
        goal = request.context.input.goal
        difficulty = request.context.input.difficulty.value if hasattr(request.context.input.difficulty, 'value') else request.context.input.difficulty
        time_per_day = request.context.input.time_per_day
        language = request.context.input.language.value if hasattr(request.context.input.language, 'value') else request.context.input.language
        context_parts.append(f"学习目标：{goal}，难度：{difficulty}，每日时间：{time_per_day}分钟，语言偏好：{language}")

        # 3. 路线书籍信息
        if request.context.books:
            context_parts.append("\n当前学习路线包含以下书籍：")
            for i, book_score in enumerate(request.context.books, 1):
                book = book_score.book
                context_parts.append(
                    f"{i}. 《{book.title}》- {book.difficulty}，{book.pages}页，"
                    f"语言：{book.language}，评分：{book_score.total_score:.1f}"
                )
                if book.keywords:
                    context_parts.append(f"   关键词：{', '.join(book.keywords[:5])}")
        else:
            context_parts.append("当前还没有选择任何书籍。")

        # 4. 相关记忆
        memories = memory_service.retrieve_memory(
            user_id=request.context.userName,
            query=request.question,
            top_k=3
        )
        if memories:
            context_parts.append("\n用户历史偏好记忆：")
            for mem in memories:
                context_parts.append(f"- {mem.field}: {mem.value}（置信度：{mem.confidence}）")

        context_text = "\n".join(context_parts)

        # 构建 prompt
        prompt = f"""你是灵犀学习助手，一位专业的学习顾问。请根据以下用户上下文信息，回答用户的问题。

{context_text}

用户问题：{request.question}

请提供有帮助、具体且可操作的建议。如果问题与当前学习路线无关，请礼貌地引导用户关注他们的学习计划。
回答要简洁友好，控制在200字以内。如果提供具体建议，请说明理由。"""

        # 调用 LLM
        try:
            llm = agent._get_llm()
            if llm is None:
                raise RuntimeError("LLM 客户端不可用")

            answer = llm.chat([
                {
                    "role": "system",
                    "content": "你是灵犀学习助手，专门帮助用户优化学习路线、解答学习问题、提供学习建议。"
                },
                {"role": "user", "content": prompt}
            ], temperature=0.7, max_tokens=500)

            # 去除 markdown 格式
            answer = _remove_markdown(answer)

        except Exception as llm_error:
            print(f"[WARN] LLM 调用失败: {llm_error}")
            # 兜底回复
            answer = _generate_fallback_answer(request.context, request.question)

        return AssistantReply(answer=answer)

    except Exception as e:
        print(f"[ERROR] 灵犀助手接口错误: {e}")
        raise HTTPException(status_code=500, detail=f"灵犀助手暂时无法回答: {str(e)}")


def _generate_fallback_answer(context: 'AssistantContext', question: str) -> str:
    """生成兜底回复（LLM 不可用时）"""
    books = context.books
    if not books:
        return "我注意到你还没有选择任何书籍。建议你先完成学习目标设置，获取个性化推荐后再来咨询学习路线问题。"

    book_count = len(books)
    total_pages = sum(bs.book.pages for bs in books)
    time_per_day = context.input.time_per_day
    estimated_days = max(1, total_pages // time_per_day)

    if "顺序" in question or "怎么学" in question or "计划" in question:
        return f"根据你的学习目标，建议按以下顺序学习：\n1. 先学习《{books[0].book.title}》（主线书）\n2. 穿插阅读补充书籍\n预计完成时间：约{estimated_days}天。你可以点击【每日阅读安排】查看详细的7天计划。"
    elif "太难" in question or "调整" in question or "修改" in question:
        return "如果觉得当前路线太难，可以：\n1. 增加每日学习时间\n2. 选择更基础的书籍\n3. 返回推荐页调整难度设置\n你还可以在书籍详情中提供反馈，我会记住你的偏好并优化推荐。"
    elif "为什么" in question:
        return f"这条路线包含{book_count}本书，总计{total_pages}页。主线书《{books[0].book.title}》负责搭建知识框架，补充书提供案例和练习。这样的组合可以帮助你系统性地掌握{context.input.goal}。"
    else:
        return f"你当前的学习路线包含{book_count}本书。如果需要调整，可以返回推荐页修改偏好设置，或者告诉我你的具体需求，我会尽力帮你优化学习计划。"


def _remove_markdown(text: str) -> str:
    """
    去除 markdown 格式符号，返回纯文本

    处理：
    - **加粗** → 纯文本
    - *斜体* → 纯文本
    - `代码` → 纯文本
    - [链接](url) → 纯文本
    - # 标题 → 纯文本
    - --- 分隔线 → 移除
    - > 引用 → 纯文本
    - 列表标记 → 保留文本
    """
    if not text:
        return text

    # 1. 移除加粗 **text** 或 __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)

    # 2. 移除斜体 *text* 或 _text_（避免与加粗冲突，先处理加粗）
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.*?)_(?!_)', r'\1', text)

    # 3. 移除行内代码 `code`
    text = re.sub(r'`(.*?)`', r'\1', text)

    # 4. 移除代码块 ```code```
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # 5. 移除链接 [text](url)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # 6. 移除图片 ![alt](url)
    text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)

    # 7. 移除标题标记 # ## ### 等
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # 8. 移除引用标记 >
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # 9. 移除水平线 --- 或 ***
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # 10. 清理多余空白（保留换行）
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符合并为一个空格
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多个换行合并为两个

    return text.strip()


# ============ 启动 ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
