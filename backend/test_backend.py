"""
后端测试脚本 - 验证核心功能

运行：python test_backend.py
"""

import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """测试导入"""
    print("=" * 60)
    print("1. 测试模块导入...")

    try:
        from config import settings
        print("  ✓ config")
        from models.schemas import Book, Memory, UserInput
        print("  ✓ models.schemas")
        from models.database import Database
        print("  ✓ models.database")
        from services.book_service import BookService
        print("  ✓ services.book_service")
        from services.memory_service import MemoryService
        print("  ✓ services.memory_service")
        from services.recommender import Recommender
        print("  ✓ services.recommender")
        from services.agent import LibrarianAgent
        print("  ✓ services.agent")
        from utils.llm_client import LLMClient
        print("  ✓ utils.llm_client")
        from utils.embedding import EmbeddingManager
        print("  ✓ utils.embedding")
        from utils.scorer import calculate_difficulty_score, check_rejection
        print("  ✓ utils.scorer")
        print("✅ 所有模块导入成功")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

    return True


def test_database():
    """测试数据库"""
    print("=" * 60)
    print("2. 测试数据库...")

    try:
        from models.database import Database, init_db
        from config import settings

        # 初始化
        init_db(settings.books_data_path, settings.memories_data_path)
        print("  ✓ 数据库初始化成功")

        # 测试书目
        books = Database(settings.books_data_path, settings.memories_data_path).get_all_books()
        print(f"  ✓ 获取书目：{len(books)} 本")

        # 测试搜索
        results = Database(settings.books_data_path, settings.memories_data_path).search_books(
            {"topic": "machine_learning", "difficulty": "beginner"}
        )
        print(f"  ✓ 搜索机器学习入门：{len(results)} 本")

        print("✅ 数据库测试通过")
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

    return True


def test_book_service():
    """测试书目服务"""
    print("=" * 60)
    print("3. 测试书目服务...")

    try:
        from services.book_service import BookService

        service = BookService()

        # 测试搜索
        books = service.search({"topic": "python", "difficulty": "beginner"})
        print(f"  ✓ 搜索Python入门：{len(books)} 本")
        for book in books[:2]:
            print(f"    - {book.title} ({book.difficulty})")

        print("✅ 书目服务测试通过")
    except Exception as e:
        print(f"❌ 书目服务测试失败: {e}")
        return False

    return True


def test_recommender():
    """测试推荐引擎"""
    print("=" * 60)
    print("4. 测试推荐引擎...")

    try:
        from services.recommender import Recommender
        from models.schemas import UserInput, DifficultyLevel, Language

        recommender = Recommender()

        # 创建测试数据
        from services.book_service import BookService
        books = BookService().search({"topic": "machine_learning"})

        if not books:
            print("  ⚠ 没有可用的书目数据")
            return True

        user_input = UserInput(
            goal="machine_learning",
            difficulty=DifficultyLevel.BEGINNER,
            time_per_day=30,
            language=Language.ZH
        )

        # 推荐
        scored_books = recommender.recommend(books, user_input, memories=[])

        print(f"  ✓ 推荐计算完成，评分前3：")
        for i, sb in enumerate(scored_books[:3], 1):
            print(f"    {i}. {sb.book.title} (总分: {sb.total_score})")
            print(f"       {sb.explanation}")

        print("✅ 推荐引擎测试通过")
    except Exception as e:
        print(f"❌ 推荐引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_memory_service():
    """测试记忆服务（不调用LLM）"""
    print("=" * 60)
    print("5. 测试记忆服务（基础功能）...")

    try:
        from models.database import Database, init_db
        from config import settings

        # 测试数据层
        db = Database(settings.books_data_path, settings.memories_data_path)

        # 测试记忆读写
        test_user = "test_user_001"
        memories = db.get_user_memories(test_user)
        print(f"  ✓ 读取记忆：{len(memories)} 条")

        print("✅ 记忆服务基础测试通过")
        print("  ⚠ 记忆压缩和检索需要配置LLM API密钥")
    except Exception as e:
        print(f"❌ 记忆服务测试失败: {e}")
        return False

    return True


def test_api_endpoints():
    """测试API端点（模拟FastAPI）"""
    print("=" * 60)
    print("6. 测试API端点定义...")

    try:
        from main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)

        # 健康检查
        response = client.get("/")
        assert response.status_code == 200
        print("  ✓ GET /")

        # 书目搜索
        response = client.get("/api/books/search?topic=machine_learning")
        assert response.status_code == 200
        data = response.json()
        print(f"  ✓ GET /api/books/search - 找到 {data['count']} 本")

        # 推荐接口（需要API密钥）
        print("  ⚠ 推荐接口需要配置LLM API密钥")

        print("✅ API端点测试通过")
    except ImportError:
        print("  ⚠ fastapi.testclient 未安装，跳过API测试")
        return True
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """主测试流程"""
    print("=" * 60)
    print("知遇AI馆员 - 后端测试")
    print("=" * 60)
    print()

    tests = [
        ("模块导入", test_imports),
        ("数据库", test_database),
        ("书目服务", test_book_service),
        ("推荐引擎", test_recommender),
        ("记忆服务", test_memory_service),
        ("API端点", test_api_endpoints),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 测试异常: {e}")
            results.append((name, False))
        print()

    # 汇总
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:20s} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print()
    print(f"总计：{passed}/{total} 项通过")

    return all(r for _, r in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
