#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知遇 AI 馆员 - 一键环境安装脚本（同事/新电脑专用）
功能：检测 Python/Node，创建后端虚拟环境并安装依赖，检查前端 node_modules。
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "fronted" / "fronted"
VENV_DIR = BACKEND_DIR / ".venv"

PY_MIN = (3, 10)
NODE_MIN = 18


def run(cmd, cwd=None, check=True):
    """运行命令并打印输出"""
    print(f"\n> {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"命令失败，退出码 {result.returncode}")
    return result


def check_python():
    """检查 Python 版本"""
    print("=== 检查 Python 环境 ===")
    version = sys.version_info[:2]
    if version < PY_MIN:
        raise RuntimeError(f"需要 Python >= {PY_MIN[0]}.{PY_MIN[1]}，当前 {version[0]}.{version[1]}")
    print(f"✓ Python {version[0]}.{version[1]} 满足要求")
    return sys.executable


def get_venv_python():
    """获取虚拟环境 Python 路径"""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def is_venv_valid():
    """检查已有 .venv 是否可用（解决跨电脑拷贝后 pyvenv.cfg 指向不存在的 Python）"""
    if not VENV_DIR.exists():
        return False
    venv_python = get_venv_python()
    if not venv_python.exists():
        return False
    try:
        result = subprocess.run(
            [str(venv_python), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.returncode == 0
    except Exception:
        return False


def create_venv(python):
    """创建后端虚拟环境"""
    print("\n=== 创建后端虚拟环境 ===")
    if VENV_DIR.exists():
        if is_venv_valid():
            print(f"✓ 已存在可用虚拟环境 {VENV_DIR}，跳过创建")
            return
        print(f"⚠️  检测到 {VENV_DIR} 已损坏（可能是从其他电脑拷贝而来），正在删除重建...")
        shutil.rmtree(VENV_DIR)
    run([python, "-m", "venv", str(VENV_DIR)], cwd=BASE_DIR)
    print("✓ 虚拟环境创建完成")


def install_backend_deps(python):
    """安装后端依赖"""
    print("\n=== 安装后端依赖 ===")
    req_file = BACKEND_DIR / "requirements.txt"
    if not req_file.exists():
        raise RuntimeError(f"找不到 {req_file}")

    # 优先用清华镜像，失败则回退默认源
    for idx, mirror in enumerate([
        ["-i", "https://pypi.tuna.tsinghua.edu.cn/simple"],
        [],
    ]):
        try:
            cmd = [python, "-m", "pip", "install", "--upgrade", "pip"]
            if mirror:
                cmd.extend(mirror)
            run(cmd, cwd=BASE_DIR, check=True)

            cmd = [python, "-m", "pip", "install", "-r", str(req_file)]
            if mirror:
                cmd.extend(mirror)
            run(cmd, cwd=BASE_DIR, check=True)
            print("✓ 后端依赖安装完成")
            return
        except RuntimeError as e:
            if idx == 0:
                print("清华镜像失败，尝试默认 PyPI 源...")
            else:
                raise


def check_node():
    """检查 Node.js 版本和 npm"""
    print("\n=== 检查 Node.js 环境 ===")
    node = shutil.which("node")
    npm = shutil.which("npm")
    if not node:
        raise RuntimeError("未检测到 Node.js。请先从 https://nodejs.org 安装 LTS 版本（建议 20+）。")
    if not npm:
        raise RuntimeError("未检测到 npm，请检查 Node.js 安装。")

    version_out = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    major = int(version_out.lstrip("v").split(".")[0])
    if major < NODE_MIN:
        raise RuntimeError(f"Node.js 版本需 >= {NODE_MIN}，当前 {version_out}")
    print(f"✓ Node.js {version_out} 满足要求，npm: {npm}")
    return node, npm


def install_frontend_deps(npm):
    """安装前端依赖"""
    print("\n=== 检查前端依赖 ===")
    node_modules = FRONTEND_DIR / "node_modules"
    if node_modules.exists() and any((node_modules / d).exists() for d in ["vite", "react", "@phosphor-icons"]):
        print("✓ node_modules 已存在且看起来完整，跳过 npm install")
        return

    print("node_modules 缺失或不完整，执行 npm install...")
    # 优先用淘宝镜像，失败回退
    for idx, registry in enumerate([
        ["--registry", "https://registry.npmmirror.com"],
        [],
    ]):
        try:
            cmd = [npm, "install"] + registry
            run(cmd, cwd=FRONTEND_DIR, check=True)
            print("✓ 前端依赖安装完成")
            return
        except RuntimeError:
            if idx == 0:
                print("淘宝镜像失败，尝试默认 npm 源...")
            else:
                raise


def write_env_hint():
    """如果还没有 .env，写一个提示文件"""
    env_file = BACKEND_DIR / ".env"
    if not env_file.exists():
        env_file.write_text(
            "# 如需开启 LLM 智能解释，取消下一行注释并填入你的 API Key\n"
            "# OPENAI_API_KEY=sk-你的key\n"
            "# ANTHROPIC_API_KEY=你的key\n",
            encoding="utf-8",
        )
        print(f"\n✓ 已在 {env_file} 写入 LLM 配置提示（未配置时推荐功能用规则兜底）")


def main():
    print("=" * 60)
    print("  知遇 AI 馆员 - 环境安装")
    print("=" * 60)

    try:
        python = check_python()
        create_venv(python)
        venv_python = get_venv_python()
        install_backend_deps(str(venv_python))
        write_env_hint()
        node, npm = check_node()
        install_frontend_deps(npm)

        print("\n" + "=" * 60)
        print("  环境安装完成！")
        print("=" * 60)
        print("\n接下来运行以下命令启动项目：")
        print("  方式1（推荐）：双击 start_all_fixed.bat")
        print("  方式2：python start_all_fixed.py")
        print("\n启动后访问：")
        print("  前端页面：http://127.0.0.1:5173")
        print("  后端文档：http://localhost:8000/docs")
    except RuntimeError as e:
        print(f"\n❌ 安装失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
