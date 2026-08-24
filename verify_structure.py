#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证项目结构是否正确重组"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """检查项目结构"""
    root = Path(".")
    errors = []
    warnings = []
    
    print("=" * 60)
    print("Lingxi AI Librarian - Project Structure Verification")
    print("=" * 60)
    print()
    
    # 检查关键目录
    print("[DIRS] Checking directory structure...")
    required_dirs = [
        "frontend",
        "backend",
        "backend/app",
        "backend/tests",
        "backend/data",
        "backend/covers",
        "scripts",
        "docs",
        "docs/fixes",
        "data",
    ]
    
    for dir_path in required_dirs:
        if (root / dir_path).is_dir():
            print(f"  [OK] {dir_path}/")
        else:
            errors.append(f"Missing directory: {dir_path}/")
            print(f"  [MISS] {dir_path}/")
    
    # 检查关键文件
    print("\n[FILES] Checking key files...")
    required_files = [
        ("frontend/package.json", "Frontend package config"),
        ("frontend/vite.config.ts", "Vite config"),
        ("backend/app/main.py", "Backend main app"),
        ("backend/app/config.py", "Backend config"),
        ("backend/requirements.txt", "Backend requirements"),
        ("scripts/start.py", "Start script"),
        ("scripts/start.bat", "Windows start script"),
        ("scripts/diagnose.py", "Diagnose script"),
        ("README.md", "Project README"),
        ("setup.py", "Setup script"),
    ]
    
    for file_path, desc in required_files:
        if (root / file_path).is_file():
            print(f"  [OK] {file_path} ({desc})")
        else:
            errors.append(f"Missing file: {file_path}")
            print(f"  [MISS] {file_path} ({desc})")
    
    # 检查不应存在的目录
    print("\n[CLEANUP] Checking old directories removed...")
    old_dirs = ["fronted"]
    for old_dir in old_dirs:
        if (root / old_dir).exists():
            warnings.append(f"Old directory still exists: {old_dir}/")
            print(f"  [WARN] {old_dir}/ (should be removed)")
        else:
            print(f"  [OK] {old_dir}/ (cleaned)")
    
    # 检查数据文件
    print("\n[DATA] Checking data files...")
    if (root / "data/书库1.xlsx").exists():
        size_mb = (root / "data/书库1.xlsx").stat().st_size / 1024 / 1024
        print(f"  [OK] data/书库1.xlsx ({size_mb:.1f} MB)")
    else:
        errors.append("Missing data file: data/书库1.xlsx")
        print(f"  [MISS] data/书库1.xlsx")
    
    # 检查前端依赖
    print("\n[DEPS] Checking frontend dependencies...")
    if (root / "frontend/node_modules").exists():
        print(f"  [OK] frontend/node_modules (installed)")
    else:
        warnings.append("Frontend dependencies not installed")
        print(f"  [WARN] frontend/node_modules (not installed, run: npm install)")
    
    # 检查后端虚拟环境
    print("\n[ENV] Checking backend environment...")
    if (root / "backend/.venv").exists():
        print(f"  [OK] backend/.venv (created)")
    else:
        warnings.append("Backend virtual environment not created")
        print(f"  [WARN] backend/.venv (not created, run: python setup.py)")
    
    # 汇总结果
    print("\n" + "=" * 60)
    if errors:
        print(f"[ERROR] Found {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"[WARN] Found {len(warnings)} warning(s):")
        for warning in warnings:
            print(f"  - {warning}")
    
    if not errors:
        print("[SUCCESS] Project structure verification passed!")
        print()
        print("Next steps:")
        print("  1. If dependencies not installed: python setup.py")
        print("  2. Start project: python scripts/start.py")
        print("  3. Or double-click: scripts/start.bat")
        return True
    else:
        print(f"\n[FAILED] Verification failed, please fix the errors above")
        return False
    
    print("=" * 60)

if __name__ == "__main__":
    success = check_project_structure()
    sys.exit(0 if success else 1)
