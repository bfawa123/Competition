#!/bin/bash
echo "============================================================"
echo "  测试 start.bat 路径计算"
echo "============================================================"
echo ""

# 模拟 %~dp0 的行为（脚本所在目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "脚本目录: $SCRIPT_DIR"
echo ""

echo "检查路径:"
echo "  setup.py:       $(dirname "$SCRIPT_DIR")/setup.py"
echo "  frontend:       $(dirname "$SCRIPT_DIR")/frontend"
echo "  backend:        $(dirname "$SCRIPT_DIR")/backend"
echo "  venv:           $(dirname "$SCRIPT_DIR")/backend/.venv/Scripts/python.exe"
echo "  backend/app:    $(dirname "$SCRIPT_DIR")/backend/app/main.py"
echo ""

echo "实际检查:"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_ROOT/setup.py" ]; then
    echo "  [OK] setup.py 存在"
else
    echo "  [MISS] setup.py 不存在"
fi

if [ -d "$PROJECT_ROOT/frontend" ]; then
    echo "  [OK] frontend/ 存在"
else
    echo "  [MISS] frontend/ 不存在"
fi

if [ -d "$PROJECT_ROOT/frontend/node_modules" ]; then
    echo "  [OK] frontend/node_modules 存在"
else
    echo "  [WARN] frontend/node_modules 不存在"
fi

if [ -d "$PROJECT_ROOT/backend" ]; then
    echo "  [OK] backend/ 存在"
else
    echo "  [MISS] backend/ 不存在"
fi

if [ -d "$PROJECT_ROOT/backend/.venv" ]; then
    echo "  [OK] backend/.venv 存在"
else
    echo "  [WARN] backend/.venv 不存在"
fi

if [ -f "$PROJECT_ROOT/backend/app/main.py" ]; then
    echo "  [OK] backend/app/main.py 存在"
else
    echo "  [MISS] backend/app/main.py 不存在"
fi

echo ""
