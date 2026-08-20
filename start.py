#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
知遇 AI 馆员 - 快速启动脚本
简化版：直接启动服务（依赖需提前安装）
"""

import sys


def main():
    """启动服务"""
    print("[LAUNCH] 启动知遇 AI 馆员...")

    # 检查依赖
    try:
        import uvicorn
        from config import settings
    except ImportError as e:
        print(f"[FAIL] 缺少依赖: {e}")
        print("\n请先安装依赖:")
        print("  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-build-isolation")
        sys.exit(1)

    # 检查 API 密钥
    try:
        from utils.secure_config import load_api_key
        api_key = load_api_key("OPENAI_API_KEY")
        if not api_key:
            print("[WARN] 未找到 API 密钥")
            print("请配置: python -m utils.secure_config")
            sys.exit(1)
        print(f"[OK] API 密钥已加载: {api_key[:15]}...")
    except Exception as e:
        print(f"[WARN] 密钥检查失败: {e}")

    # 启动服务
    print()
    print("=" * 60)
    print(f"[LAUNCH] 知遇 AI 馆员 - 后端服务")
    print("=" * 60)
    print()
    print(f"[ADDR] 服务地址: http://localhost:{settings.port}")
    print(f"[DOC] API文档: http://localhost:{settings.port}/docs")
    print(f"[HEALTH] 健康检查: http://localhost:{settings.port}/health")
    print()
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    print()

    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)


if __name__ == "__main__":
    main()
