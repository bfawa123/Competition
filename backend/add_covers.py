# -*- coding: utf-8 -*-
"""
把 data/书库1.xlsx 的「封面」列链接合并进 backend/data/books.json 的 cover 字段。

books.json 与书库1.xlsx 逐行一一对应（第 1 本对第 1 行），按行序对齐，
并对每一行校验书名一致（不一致只告警、仍按行序写入，避免错位）。
重复执行安全：只新增/更新 cover 字段，不改动其它字段。
"""
import json
import os
import sys

import openpyxl

# 控制台打印可能遇到 GBK 无法编码的字符，兜底避免崩溃
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
BOOKS_JSON = os.path.join(BASE, "data", "books.json")
XLSX_CANDIDATES = ["书库1.xlsx", "书库2.xlsx", "书库（换封面版）.xlsx"]


def find_xlsx():
    # 在项目根目录和 data/ 目录下查找书库文件
    project_root = os.path.dirname(BASE)
    search_paths = [project_root, os.path.join(project_root, "data")]
    for name in XLSX_CANDIDATES:
        for search_path in search_paths:
            p = os.path.join(search_path, name)
            if os.path.exists(p):
                return p
    raise FileNotFoundError(f"未找到书库文件，尝试过: {XLSX_CANDIDATES}")


def main():
    xlsx_path = find_xlsx()

    with open(BOOKS_JSON, "r", encoding="utf-8") as f:
        books = json.load(f)

    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip() if h is not None else "" for h in next(rows)]
    col = {name: i for i, name in enumerate(header)}
    if "封面" not in col or "书名" not in col:
        raise RuntimeError(f"书库文件缺少「封面」或「书名」列: {header}")

    covers = []
    for row in rows:
        if len(row) < len(header):
            continue
        title = str(row[col["书名"]]).strip() if row[col["书名"]] is not None else ""
        cover = str(row[col["封面"]]).strip() if row[col["封面"]] is not None else ""
        if not title:
            continue
        covers.append((title, cover or None))

    if len(covers) != len(books):
        raise RuntimeError(f"行数不一致: books.json {len(books)} 本 vs 书库 {len(covers)} 行，中止")

    added = 0
    mismatches = 0
    for book, (title, cover) in zip(books, covers):
        if book.get("title", "").strip() != title:
            mismatches += 1
        book["cover"] = cover
        if cover:
            added += 1

    with open(BOOKS_JSON, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"读取书库: {xlsx_path}")
    print(f"完成: {len(books)} 本书已写回")
    print(f"  有封面链接: {added}")
    print(f"  书名不一致(仍按行序写入): {mismatches}")
    print(f"  输出: {BOOKS_JSON}")


if __name__ == "__main__":
    main()
