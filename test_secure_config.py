"""
安全配置测试脚本 - 验证密钥加载机制
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 path
sys.path.insert(0, str(Path(__file__).parent))


def test_secure_config():
    """测试安全配置"""
    print("=" * 70)
    print("安全配置测试")
    print("=" * 70)
    print()

    # 测试1：环境变量
    print("1. 测试环境变量加载")
    print("-" * 70)

    # 临时设置环境变量（模拟配置）
    os.environ["OPENAI_API_KEY"] = "sk-test-key-from-env"

    from utils.secure_config import load_api_key

    api_key = load_api_key("OPENAI_API_KEY")
    if api_key:
        print(f"✓ 成功加载密钥: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("✗ 未找到密钥")

    # 清理
    del os.environ["OPENAI_API_KEY"]
    print()

    # 测试2：检查密钥管理器
    print("2. 测试密钥管理器")
    print("-" * 70)

    try:
        import subprocess
        # 测试 1Password
        result = subprocess.run(
            ["op", "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            print(f"✓ 1Password CLI 已安装 (版本: {result.stdout.strip()})")
        else:
            print("  ⚠ 1Password CLI 未安装或未登录")
    except FileNotFoundError:
        print("  ⚠ 1Password CLI 未安装（可选）")

    try:
        # 测试 Bitwarden
        result = subprocess.run(
            ["bw", "--version"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            print(f"✓ Bitwarden CLI 已安装 (版本: {result.stdout.strip()})")
        else:
            print("  ⚠ Bitwarden CLI 未安装或未登录")
    except FileNotFoundError:
        print("  ⚠ Bitwarden CLI 未安装（可选）")

    print()

    # 测试3：检查密钥文件
    print("3. 测试密钥文件")
    print("-" * 70)

    key_file = Path.home() / ".config" / "zhiyu" / "api_key"
    if key_file.exists():
        api_key = key_file.read_text().strip()
        if api_key:
            print(f"✓ 找到密钥文件: {key_file}")
            print(f"  密钥: {api_key[:10]}...{api_key[-4:]}")
        else:
            print(f"⚠ 密钥文件存在但为空: {key_file}")
    else:
        print(f"  ℹ 密钥文件不存在（可选）")
        print(f"  路径: {key_file}")

    print()

    # 测试4：检查环境变量（当前）
    print("4. 检查当前环境变量")
    print("-" * 70)

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key and not openai_key.startswith("CHANGE_ME"):
        print(f"✓ OPENAI_API_KEY 已设置: {openai_key[:10]}...{openai_key[-4:]}")
    else:
        print("✗ OPENAI_API_KEY 未设置")

    if anthropic_key and not anthropic_key.startswith("CHANGE_ME"):
        print(f"✓ ANTHROPIC_API_KEY 已设置: {anthropic_key[:10]}...{anthropic_key[-4:]}")
    else:
        print("✗ ANTHROPIC_API_KEY 未设置")

    print()

    # 测试5：检查 .env 文件
    print("5. 检查 .env 文件")
    print("-" * 70)

    env_file = Path(".env")
    if env_file.exists():
        content = env_file.read_text(encoding="utf-8")

        # 检查是否包含真实密钥（非占位符）
        has_real_key = False
        for line in content.split("\n"):
            if line.startswith("OPENAI_API_KEY=") or line.startswith("ANTHROPIC_API_KEY="):
                value = line.split("=", 1)[1]
                if value and not value.startswith("CHANGE_ME"):
                    has_real_key = True
                    print(f"⚠ 警告：.env 文件中包含真实密钥")
                    break

        if not has_real_key:
            print("✓ .env 文件中没有真实密钥（使用占位符）")
    else:
        print("✗ .env 文件不存在")

    print()

    # 总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print()
    print("推荐配置方式：")
    print("1. Windows PowerShell:")
    print('   $env:OPENAI_API_KEY="sk-你的密钥"')
    print()
    print("2. Windows CMD (永久):")
    print('   setx OPENAI_API_KEY "sk-你的密钥"')
    print()
    print("3. 密钥文件 (开发):")
    print("   python -m utils.secure_config")
    print()
    print("配置后运行: python main.py")
    print("=" * 70)


if __name__ == "__main__":
    test_secure_config()
