"""
诊断脚本 - 检查后端启动问题
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("知遇 AI 馆员 - 诊断工具")
print("=" * 60)
print()

# 1. 检查依赖
print("1. 检查依赖...")
try:
    import fastapi
    print(f"  ✓ fastapi {fastapi.__version__}")
except ImportError:
    print("  ❌ fastapi 未安装")

try:
    import uvicorn
    print(f"  ✓ uvicorn {uvicorn.__version__}")
except ImportError:
    print("  ❌ uvicorn 未安装")

try:
    import pydantic
    print(f"  ✓ pydantic {pydantic.__version__}")
except ImportError:
    print("  ❌ pydantic 未安装")

print()

# 2. 检查配置
print("2. 检查配置...")
try:
    from config import settings
    print(f"  ✓ 端口: {settings.port}")
    print(f"  ✓ LLM提供商: {settings.llm_provider}")
    print(f"  ✓ 模型: {settings.llm_model}")
except Exception as e:
    print(f"  ❌ 配置加载失败: {e}")

print()

# 3. 检查数据文件
print("3. 检查数据文件...")
data_dir = Path("data")
if data_dir.exists():
    books_file = data_dir / "books.json"
    memories_file = data_dir / "memories.json"

    if books_file.exists():
        import json
        with open(books_file, 'r', encoding='utf-8') as f:
            books = json.load(f)
        print(f"  ✓ books.json: {len(books)} 条记录")
    else:
        print(f"  ❌ 找不到 books.json")

    if memories_file.exists():
        print(f"  ✓ memories.json 存在")
    else:
        print(f"  ⚠ memories.json 不存在（首次运行会创建）")
else:
    print(f"  ❌ data 目录不存在")

print()

# 4. 尝试导入主模块
print("4. 尝试导入主模块...")
try:
    from main import app
    print("  ✓ main.py 导入成功")
    print(f"  ✓ FastAPI 应用: {app.title}")
except Exception as e:
    print(f"  ❌ main.py 导入失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 5. 尝试启动服务（1秒后自动停止）
print("5. 尝试启动服务（测试模式）...")
try:
    import uvicorn
    from config import settings

    print("  启动中...（按 Ctrl+C 停止）")
    print()

    # 启动服务（这会阻塞）
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # 只监听本地，方便测试
        port=settings.port,
        reload=False,  # 关闭热重载
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n  服务已停止")
except Exception as e:
    print(f"  ❌ 启动失败: {e}")
    import traceback
    traceback.print_exc()
