"""
DeepSeek 灵犀助手集成测试
"""
import sys
import os
from pathlib import Path

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


def test_deepseek_assistant():
    """测试 DeepSeek 灵犀助手"""
    client = TestClient(app)

    # 构建测试数据 - 机器学习路线
    books = [
        Book(
            id=1,
            title="机器学习实战",
            topic="machine_learning",
            difficulty=DifficultyLevel.BEGINNER,
            pages=350,
            language=Language.ZH,
            case_ratio=0.7,
            theory_ratio=0.3,
            prerequisites=["Python基础"],
            goals=["入门机器学习", "实战项目"],
            keywords=["Scikit-learn", "监督学习", "Kaggle"],
            availability=True
        ),
        Book(
            id=2,
            title="深度学习入门",
            topic="deep_learning",
            difficulty=DifficultyLevel.INTERMEDIATE,
            pages=400,
            language=Language.ZH,
            case_ratio=0.6,
            theory_ratio=0.4,
            prerequisites=["机器学习基础"],
            goals=["深度学习入门", "神经网络"],
            keywords=["神经网络", "TensorFlow", "PyTorch"],
            availability=True
        )
    ]

    book_scores = [
        BookScore(
            book=book,
            total_score=85.0 + i * 5,
            topic_score=1.0,
            difficulty_score=0.9,
            time_score=0.8,
            preference_score=0.85,
            explanation=f"匹配度很高"
        )
        for i, book in enumerate(books)
    ]

    context = AssistantContext(
        userName="张三",
        input=UserInput(
            goal="machine_learning",
            difficulty=DifficultyLevel.BEGINNER,
            time_per_day=30,
            language=Language.ZH
        ),
        books=book_scores,
        currentPage="route"
    )

    print("=" * 70)
    print("DeepSeek 灵犀助手集成测试")
    print("=" * 70)
    print(f"\n配置信息：")
    print(f"  LLM Provider: {settings.llm_provider}")
    print(f"  Model: {settings.llm_model}")
    print(f"  Base URL: {settings.openai_base_url}")
    print(f"  API Key: {'已配置' if settings.openai_api_key else '未配置'}")

    # 测试用例
    test_cases = [
        {
            "question": "这条路线怎么安排学习？",
            "description": "学习计划咨询"
        },
        {
            "question": "为什么推荐这两本书一起学？",
            "description": "推荐理由询问"
        },
        {
            "question": "我每天只有30分钟，能调整学习计划吗？",
            "description": "个性化调整"
        },
        {
            "question": "《深度学习入门》太难了，有没有更基础的替代书？",
            "description": "书籍替换建议"
        }
    ]

    print(f"\n开始测试 {len(test_cases)} 个场景...")
    print("=" * 70)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] {test_case['description']}")
        print(f"问题: {test_case['question']}")
        print("-" * 70)

        request = AssistantChatRequest(
            question=test_case['question'],
            context=context
        )

        response = client.post(
            "/api/assistant/chat",
            json=request.model_dump(mode="json")
        )

        if response.status_code == 200:
            data = response.json()
            print(f"状态: [成功]")
            print(f"回答:\n{data['answer']}")
        else:
            print(f"状态: [失败] ({response.status_code})")
            print(f"错误: {response.text}")

        print("-" * 70)

    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    test_deepseek_assistant()
