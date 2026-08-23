"""
安全配置管理 - API 密钥加载

支持的密钥加载方式（按优先级）：
1. 系统环境变量（最安全）
2. 1Password CLI
3. Bitwarden CLI
4. 密钥文件（仅限开发环境）

使用方法：
    # 在代码中加载密钥
    from utils.secure_config import load_api_key
    api_key = load_api_key("OPENAI_API_KEY")

    # 配置密钥
    from utils.secure_config import save_key_to_file
    save_key_to_file("sk-你的密钥", "OPENAI_API_KEY")
"""
import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
from config import settings


def load_api_key(key_name: str = "OPENAI_API_KEY") -> Optional[str]:
    """
    安全加载 API 密钥

    加载优先级：
    1. 系统环境变量（最安全）
    2. 1Password CLI
    3. Bitwarden CLI
    4. 密钥文件（仅限开发环境）

    Args:
        key_name: 环境变量名（如 "OPENAI_API_KEY"）

    Returns:
        API 密钥或 None

    示例：
        api_key = load_api_key("OPENAI_API_KEY")
        if not api_key:
            print("请先配置 API 密钥")
    """
    # 1. 从系统环境变量加载（最安全）
    env_key = os.getenv(key_name)
    if env_key and not env_key.startswith("CHANGE_ME"):
        print(f"[OK] 从环境变量加载 {key_name}")
        return env_key

    # 2. 从 1Password 加载
    try:
        result = subprocess.run(
            ["op", "item", "get", "openai-api-key", "--fields", "credential"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            api_key = result.stdout.strip()
            if api_key:
                print(f"[OK] 从 1Password 加载 {key_name}")
                return api_key
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 3. 从 Bitwarden 加载
    try:
        import json  # 移到 try 块外或确保导入
        result = subprocess.run(
            ["bw", "get", "item", "openai-api-key", "--nointeraction"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            api_key = data.get("login", {}).get("password")
            if api_key:
                print(f"[OK] 从 Bitwarden 加载 {key_name}")
                return api_key
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        pass

    # 4. 从密钥文件加载
    key_file = Path.home() / ".config" / "zhiyu" / "api_key"
    if key_file.exists():
        api_key = key_file.read_text().strip()
        if api_key:
            print(f"[OK] 从密钥文件加载 {key_name}")
            return api_key

    print(f"[FAIL] {key_name} not found")
    return None


def save_key_to_file(api_key: str, key_name: str = "OPENAI_API_KEY") -> bool:
    """
    安全保存密钥到本地文件（仅限开发环境）

    文件权限设置为仅当前用户可读写

    Args:
        api_key: API 密钥
        key_name: 密钥名称（用于显示）

    Returns:
        是否保存成功
    """
    try:
        import stat

        # 创建密钥目录
        key_dir = Path.home() / ".config" / "zhiyu"
        key_dir.mkdir(parents=True, exist_ok=True)

        # 保存密钥
        key_file = key_dir / "api_key"
        key_file.write_text(api_key)

        # Unix-like 系统设置文件权限为仅用户可读写
        if hasattr(os, 'chmod') and sys.platform != 'win32':
            key_file.chmod(stat.S_IRUSR | stat.S_IWUSR)

        print(f"[OK] 密钥已保存到 {key_file}")
        print(f"  （文件权限已设置为仅当前用户可访问）")
        return True

    except Exception as e:
        print(f"[FAIL] 保存密钥失败: {e}")
        return False


def setup_guide():
    """打印密钥配置指南"""
    print("=" * 70)
    print("API 密钥配置指南 - 知遇 AI 馆员")
    print("=" * 70)
    print()
    print("请选择一种方式配置 API 密钥（按安全性排序）：")
    print()
    print("方案1：系统环境变量（推荐）⭐")
    print("  Windows PowerShell（当前终端有效）：")
    print('    $env:OPENAI_API_KEY="sk-你的密钥"')
    print()
    print("  Windows CMD（永久有效）：")
    print('    setx OPENAI_API_KEY "sk-你的密钥"')
    print()
    print("  Linux/Mac（永久有效）：")
    print('    echo \'export OPENAI_API_KEY="sk-你的密钥"\' >> ~/.bashrc')
    print('    source ~/.bashrc')
    print()
    print("方案2：密钥管理器（最安全）🔒")
    print("  - 1Password CLI: op item get openai-api-key")
    print("  - Bitwarden CLI: bw get item openai-api-key")
    print()
    print("方案3：密钥文件（仅限开发）")
    print('  python -m utils.secure_config')
    print()
    print("=" * 70)
    print()
    print("⚠️  安全提醒：")
    print("  - 不要将密钥硬编码在代码中")
    print("  - 不要将 .env 文件提交到 Git")
    print("  - 定期轮换 API 密钥")
    print("  - 比赛结束后撤销密钥")
    print("=" * 70)


def interactive_setup():
    """交互式配置密钥"""
    print("知遇 AI 馆员 - API 密钥配置")
    print()

    print("选择配置方式：")
    print("  1. 系统环境变量（推荐）")
    print("  2. 密钥文件（仅限开发）")
    print()

    choice = input("请输入选择 (1-2): ").strip()

    if choice == "1":
        print("\n请输入 API 密钥（不会显示）")
        api_key = input(": ").strip()
        if not api_key:
            print("[FAIL] 密钥不能为空")
            return

        # 验证格式
        if not api_key.startswith("sk-"):
            print("⚠️  警告：密钥格式可能不正确（通常以 sk- 开头）")
            confirm = input("是否继续？(y/N): ").strip().lower()
            if confirm != 'y':
                return

        print("\n选择环境变量名：")
        print("  1. OPENAI_API_KEY")
        print("  2. ANTHROPIC_API_KEY")
        var_choice = input("请输入选择 (1-2): ").strip()

        if var_choice == "1":
            var_name = "OPENAI_API_KEY"
        elif var_choice == "2":
            var_name = "ANTHROPIC_API_KEY"
        else:
            print("[FAIL] 无效选择")
            return

        print(f"\n请在终端运行以下命令：")
        if sys.platform == "win32":
            print(f'  set {var_name}="{api_key}"')
            print(f'  # 或永久设置（需要管理员权限）')
            print(f'  setx {var_name} "{api_key}"')
        else:
            print(f'  export {var_name}="{api_key}"')
            print(f'  # 或永久设置')
            print(f'  echo \'export {var_name}="{api_key}"\' >> ~/.bashrc')

    elif choice == "2":
        api_key = input("请输入 API 密钥: ").strip()
        if api_key:
            save_key_to_file(api_key)
    else:
        print("[FAIL] 无效选择")


if __name__ == "__main__":
    # 作为模块运行时提供帮助信息
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        interactive_setup()
    else:
        # 测试密钥加载
        print("知遇 AI 馆员 - 密钥加载测试")
        print()

        api_key = load_api_key("OPENAI_API_KEY")
        if api_key:
            print(f"\n[OK] 成功加载密钥: {api_key[:10]}...{api_key[-4:]}")
            print(f"  长度: {len(api_key)} 字符")
        else:
            print("\n[FAIL] 未找到密钥")
            setup_guide()

        # 测试 Anthropic 密钥
        print()
        anthropic_key = load_api_key("ANTHROPIC_API_KEY")
        if anthropic_key:
            print(f"[OK] 找到 Anthropic 密钥: {anthropic_key[:10]}...{anthropic_key[-4:]}")
