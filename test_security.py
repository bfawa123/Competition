"""
安全配置快速测试
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("知遇 AI 馆员 - 安全配置测试")
print("=" * 70)
print()

# 检查当前配置
print("1. 检查当前环境变量")
print("-" * 70)

openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")

if openai_key:
    masked = f"{openai_key[:10]}...{openai_key[-4:]}" if len(openai_key) > 14 else "***"
    print(f"✓ OPENAI_API_KEY: {masked}")
else:
    print("✗ OPENAI_API_KEY 未设置")

if anthropic_key:
    masked = f"{anthropic_key[:10]}...{anthropic_key[-4:]}" if len(anthropic_key) > 14 else "***"
    print(f"✓ ANTHROPIC_API_KEY: {masked}")
else:
    print("✗ ANTHROPIC_API_KEY 未设置")

print()

# 检查 .env 文件
print("2. 检查 .env 文件")
print("-" * 70)

env_file = Path(".env")
if env_file.exists():
    content = env_file.read_text(encoding="utf-8")
    lines = content.split("\n")

    openai_line = [l for l in lines if l.startswith("OPENAI_API_KEY=")]
    anthropic_line = [l for l in lines if l.startswith("ANTHROPIC_API_KEY=")]

    if openai_line:
        value = openai_line[0].split("=", 1)[1]
        if value.startswith("CHANGE_ME"):
            print("✓ OPENAI_API_KEY 使用占位符（安全）")
        else:
            print(f"⚠ OPENAI_API_KEY 包含真实值（建议使用环境变量）")

    if anthropic_line:
        value = anthropic_line[0].split("=", 1)[1]
        if value.startswith("CHANGE_ME"):
            print("✓ ANTHROPIC_API_KEY 使用占位符（安全）")
        else:
            print(f"⚠ ANTHROPIC_API_KEY 包含真实值（建议使用环境变量）")
else:
    print("✗ .env 文件不存在")

print()

# 检查密钥管理器
print("3. 检查密钥管理器（可选）")
print("-" * 70)

try:
    import subprocess
    result = subprocess.run(["op", "--version"], capture_output=True, text=True, timeout=2)
    if result.returncode == 0:
        print(f"✓ 1Password CLI: {result.stdout.strip()}")
    else:
        print("  ⚠ 1Password CLI 未安装")
except FileNotFoundError:
    print("  ⚠ 1Password CLI 未安装（可选）")

print()

# 配置建议
print("=" * 70)
print("配置建议")
print("=" * 70)
print()

if not openai_key and not anthropic_key:
    print("❌ 未找到任何 API 密钥")
    print()
    print("请使用以下方式之一配置密钥：")
    print()
    print("方式1：系统环境变量（推荐）")
    print("  Windows PowerShell:")
    print('    $env:OPENAI_API_KEY="sk-你的密钥"')
    print()
    print("方式2：密钥文件（开发环境）")
    print("  python -m utils.secure_config")
    print()
else:
    print("✓ 已找到 API 密钥配置")
    print()
    print("下一步：")
    print("  1. 运行服务: python main.py")
    print("  2. 测试推荐: curl http://localhost:8000/")
    print("  3. 访问文档: http://localhost:8000/docs")

print()
print("详细文档: SECURITY.md")
print("=" * 70)
