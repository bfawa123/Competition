# -*- coding: utf-8 -*-
"""
将 书库1.xlsx 转换为后端 books.json
按表头名定位列（列顺序变化自动适配），含作者字段
"""
import json
import os
import re

import openpyxl

BASE = os.path.dirname(os.path.abspath(__file__))
XLSX_CANDIDATES = ["书库1.xlsx", "书库（换封面版）.xlsx"]
OUTPUT_PATH = os.path.join(BASE, "data", "books.json")
# 难度映射: xlsx 5级 → 后端 3级
DIFFICULTY_MAP = {
    "1级-零基础入门": "beginner",
    "2级-有基础入门": "beginner",
    "3级-进阶": "intermediate",
    "4级-高阶": "advanced",
    "5级-专家级": "advanced",
}

# 语言映射
LANGUAGE_MAP = {
    "中文": "zh",
    "英文": "en",
    "中英双语": "zh",  # 双语归入中文，方便中文读者
}


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


def split_list(val):
    """将逗号分隔的字符串转为列表，处理'无'等空值"""
    if not val:
        return []
    s = str(val).strip()
    if s in ("无", "无。", "无。 ", ""):
        return []
    parts = re.split(r"[,，、;；]", s)
    return [p.strip() for p in parts if p.strip()]


def convert():
    xlsx_path = find_xlsx()
    print(f"读取书库: {xlsx_path}")
    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    ws = wb.active

    rows = ws.iter_rows(values_only=True)
    header = [str(h).strip() if h is not None else "" for h in next(rows)]
    col = {name: i for i, name in enumerate(header)}

    def cell(row, name, default=""):
        i = col.get(name)
        if i is None or i >= len(row) or row[i] is None:
            return default
        return str(row[i]).strip()

    books = []
    book_id = 0

    for row in rows:
        title = cell(row, "书名")
        if not title:
            continue

        book_id += 1
        topic = cell(row, "主题")
        difficulty_raw = cell(row, "难度", "1级-零基础入门")
        try:
            pages = int(float(cell(row, "页数", "0")))
        except ValueError:
            pages = 0
        language_raw = cell(row, "语言", "中文")
        try:
            case_level = int(float(cell(row, "案例程度", "3")))
        except ValueError:
            case_level = 3
        try:
            theory_level = int(float(cell(row, "理论程度", "3")))
        except ValueError:
            theory_level = 3
        author = cell(row, "作者")
        description = cell(row, "简介")
        location = cell(row, "馆藏位置")
        space = cell(row, "适配学习空间")

        difficulty = DIFFICULTY_MAP.get(difficulty_raw, "beginner")
        language = LANGUAGE_MAP.get(language_raw, "zh")
        case_ratio = round(case_level / 5.0, 2)
        theory_ratio = round(theory_level / 5.0, 2)
        prerequisites = split_list(cell(row, "前置知识"))
        goals = split_list(cell(row, "适用目标"))
        keywords = split_list(cell(row, "关键词"))

        # 如果关键词为空，从主题和标题生成
        if not keywords:
            keywords = [topic, title.split(":")[0].split("：")[0].strip()]

        # 如果目标为空，根据难度生成默认目标
        if not goals:
            if difficulty == "beginner":
                goals = ["入门"]
            elif difficulty == "intermediate":
                goals = ["进阶"]
            else:
                goals = ["高阶"]

        books.append({
            "id": book_id,
            "title": title,
            "author": author or None,
            "topic": topic,  # 保持中文主题，与前端 topicNames 一致
            "difficulty": difficulty,
            "pages": pages,
            "language": language,
            "case_ratio": case_ratio,
            "theory_ratio": theory_ratio,
            "prerequisites": prerequisites,
            "goals": goals,
            "keywords": keywords,
            "availability": True,
            "description": description,
            "location": location,
            "space": space,
        })

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"转换完成: {len(books)} 本书")
    print(f"输出: {OUTPUT_PATH}")

    topics = set(b["topic"] for b in books)
    diffs = {}
    langs = {}
    for b in books:
        diffs[b["difficulty"]] = diffs.get(b["difficulty"], 0) + 1
        langs[b["language"]] = langs.get(b["language"], 0) + 1

    print(f"含作者的书: {sum(1 for b in books if b['author'])}/{len(books)}")
    print(f"主题数: {len(topics)}")
    print(f"难度分布: {diffs}")
    print(f"语言分布: {langs}")

    print("\n前3本书:")
    for b in books[:3]:
        print(f"  [{b['id']}] {b['title']} | 作者={b['author']} | topic={b['topic']} | diff={b['difficulty']} | pages={b['pages']} | loc={b['location']}")


if __name__ == "__main__":
    convert()
