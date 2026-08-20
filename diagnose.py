#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""诊断脚本 - 逐步检查模块导入"""

import sys
import traceback

print("=" * 60)
print("Step 1: Importing config...")
try:
    from config import settings
    print("[OK] config imported")
except Exception as e:
    print(f"[FAIL] config failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 2: Importing database...")
try:
    from models.database import init_db, get_db
    print("[OK] database module imported")

    print("\nInitializing database...")
    init_db(settings.books_data_path, settings.memories_data_path)
    print("[OK] database initialized")
except Exception as e:
    print(f"[FAIL] database failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 3: Importing schemas...")
try:
    from models.schemas import Book, UserInput, Memory
    print("[OK] schemas imported")
except Exception as e:
    print(f"[FAIL] schemas failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 4: Importing embedding...")
try:
    from utils.embedding import get_embedding_mgr
    print("[OK] embedding module imported")

    print("\nInitializing embedding manager...")
    mgr = get_embedding_mgr()
    print(f"[OK] embedding manager ready (dim={mgr.dim})")
except Exception as e:
    print(f"[FAIL] embedding failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 5: Importing book_service...")
try:
    from services.book_service import book_service
    print("[OK] book_service imported")
except Exception as e:
    print(f"[FAIL] book_service failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 6: Importing memory_service...")
try:
    from services.memory_service import memory_service
    print("[OK] memory_service imported")
except Exception as e:
    print(f"[FAIL] memory_service failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 7: Importing recommender...")
try:
    from services.recommender import recommender
    print("[OK] recommender imported")
except Exception as e:
    print(f"[FAIL] recommender failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Step 8: Importing llm_client...")
try:
    from utils.llm_client import get_llm_client
    print("[OK] llm_client imported")
except Exception as e:
    print(f"[FAIL] llm_client failed: {e}")
    print("(Skipping - requires API key configuration)")

print("\n" + "=" * 60)
print("Step 9: Importing agent...")
try:
    from services.agent import agent
    print("[OK] agent imported")
except Exception as e:
    print(f"[FAIL] agent failed: {e}")
    print("(Skipping - requires LLM and API key)")

print("\n" + "=" * 60)
print("[OK][OK][OK] Core modules imported successfully!")
print("(LLM and Agent skipped - need API key)")
print("=" * 60)
