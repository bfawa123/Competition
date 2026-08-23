"""
测试灵犀助手 API
"""
import asyncio
import sys
from pathlib import Path
import os

# 设置环境变量确保 UTF-8 编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent))

from main import app
from fastapi.testclient import TestClient
from models.schemas import (
    AssistantChatRequest,
    AssistantContext,
    UserInput,
    DifficultyLevel,
    Language,
    BookScore,
    Book
)
from config import settings

# 初始化数据库
from models.database import init_db
init_db(settings.books_data_path, settings.memories_data_path)

def test_assistant_chat():
    """测试灵犀助手聊天接口"""
    client = TestClient(app)

    # 构建测试数据
    test_book = Book(
        id=1,
        title="机器学习实战",
        topic="machine_learning",
        difficulty=DifficultyLevel.BEGINNER,
        pages=350,
        language=Language.ZH,
        case_ratio=0.7,
        theory_ratio=0.3,
        prerequisites=["Python基础"],
        goals=["入门机器学习"],
        keywords=["Scikit-learn", "监督学习"],
        availability=True
    )

    test_book_score = BookScore(
        book=test_book,
        total_score=85.5,
        topic_score=1.0,
        difficulty_score=1.0,
        time_score=0.7,
        preference_score=0.8,
        explanation="测试说明"
    )

    test_context = AssistantContext(
        userName="测试用户",
        input=UserInput(
            goal="machine_learning",
            difficulty=DifficultyLevel.BEGINNER,
            time_per_day=30,
            language=Language.ZH
        ),
        books=[test_book_score],
        currentPage="route"
    )

    # 测试请求
    request_data = AssistantChatRequest(
        question="这条路线怎么安排学习？",
        context=test_context
    )

    print("=" * 60)
    print("灵犀助手 API 测试")
    print("=" * 60)

    # 测试 1: 无 LLM 配置的兜底回复
    print("\n[测试 1] 测试兜底回复（无 LLM 配置）")
    response = client.post(
        "/api/assistant/chat",
        json=request_data.model_dump(mode="json")
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("OK - 接口响应成功")
        print(f"回答: {data['answer'][:100]}...")
    else:
        print(f"FAIL - 接口调用失败: {response.text}")

    # 测试 2: 空书籍列表
    print("\n[测试 2] 空书籍列表")
    empty_context = AssistantContext(
        userName="测试用户",
        input=UserInput(
            goal="python",
            difficulty=DifficultyLevel.BEGINNER,
            time_per_day=30,
            language=Language.ZH
        ),
        books=[],
        currentPage="route"
    )

    empty_request = AssistantChatRequest(
        question="我该怎么学习？",
        context=empty_context
    )

    response = client.post(
        "/api/assistant/chat",
        json=empty_request.model_dump(mode="json")
    )

    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("OK - 接口响应成功")
        print(f"回答: {data['answer'][:100]}...")
    else:
        print(f"FAIL - 接口调用失败: {response.text}")

    # 测试 3: 不同问题类型
    print("\n[测试 3] 不同问题类型测试")
    test_questions = [
        "为什么这样安排？",
        "路线太难了，能调整吗？",
        "应该按什么顺序学习？"
    ]

    for question in test_questions:
        test_req = AssistantChatRequest(
            question=question,
            context=test_context
        )
        response = client.post(
            "/api/assistant/chat",
            json=test_req.model_dump(mode="json")
        )
        if response.status_code == 200:
            data = response.json()
            print(f"\n问题: {question}")
            print(f"回答: {data['answer'][:150]}...")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_assistant_chat()
