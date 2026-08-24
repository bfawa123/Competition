#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知遇 AI 馆员 - 一键启动前后端（同事/新电脑专用）
不依赖任何写死路径，自动使用 backend/.venv 虚拟环境或系统 Python。
"""
import os
import sys
import subprocess
import time
import threading
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  # scripts/ 的父目录是项目根目录
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
VENV_DIR = BACKEND_DIR / ".venv"


def find_python():
    """优先使用 backend/.venv 里的 Python；venv 损坏时提示重建"""
    if sys.platform == "win32":
        venv_py = VENV_DIR / "Scripts" / "python.exe"
    else:
        venv_py = VENV_DIR / "bin" / "python"
    if venv_py.exists():
        try:
            result = subprocess.run(
                [str(venv_py), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                return str(venv_py)
        except Exception:
            pass
        raise RuntimeError(
            "backend/.venv 已损坏（通常是从其他电脑直接拷贝文件夹导致）。\n"
            "请先运行一次：python setup.py\n"
            "脚本会自动删除损坏的 venv 并重建。"
        )
    if sys.executable:
        return sys.executable
    return "python"


def find_npm():
    """在 PATH 里找 npm"""
    import shutil
    npm = shutil.which("npm")
    if npm:
        return npm
    raise RuntimeError("未检测到 npm。请先运行 setup.py 安装环境，或安装 Node.js。")


def find_node_modules():
    """检查前端依赖是否已安装"""
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        raise RuntimeError(
            "前端依赖未安装。请先运行一次：python setup.py\n"
            "或进入 frontend 执行：npm install"
        )


def stream_output(proc, prefix):
    """实时打印子进程输出"""
    try:
        for line in iter(proc.stdout.readline, ""):
            line = line.rstrip()
            if line:
                print(f"[{prefix}] {line}")
    except Exception:
        pass


def start_backend():
    """启动后端"""
    python = find_python()
    print(f"[BACKEND] 使用 Python: {python}")
    print("[BACKEND] 启动 FastAPI 后端 (端口 8000)...")
    proc = subprocess.Popen(
        [python, "main.py"],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stream_output(proc, "BACKEND")


def start_frontend():
    """启动前端"""
    find_node_modules()
    npm = find_npm()
    time.sleep(3)  # 等后端先起来
    print(f"[FRONTEND] 使用 npm: {npm}")
    print("[FRONTEND] 启动 Vite 前端 (端口 5173)...")
    proc = subprocess.Popen(
        [npm, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stream_output(proc, "FRONTEND")


def main():
    print("=" * 60)
    print("  知遇 AI 馆员 - 一键启动")
    print("=" * 60)
    print()

    if not VENV_DIR.exists():
        print("⚠️  未检测到 backend/.venv 虚拟环境。")
        print("   如果是第一次运行，请先执行：python setup.py")
        print()

    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    backend_thread.start()
    frontend_thread.start()

    print("  前端页面: http://127.0.0.1:5173")
    print("  后端文档: http://localhost:8000/docs")
    print()
    print("  按 Ctrl+C 停止所有服务")
    print("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] 正在停止所有服务...")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)
