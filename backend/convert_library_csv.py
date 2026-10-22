# -*- coding: utf-8 -*-
"""
将 backend/书库/dlut_campus_books_8000.csv 转换为 backend/data/books.json

字段映射规则：
- 难度:   入门 -> beginner, 进阶 -> intermediate, 深入 -> advanced
- 语言:   英语 -> en, 其余（中文/日语/双语等）-> zh
- 案例/理论程度: 低 -> 0.2, 中 -> 0.5, 高 -> 0.8
- 馆藏状态: 含「可借」-> True，否则 False
- 主题/前置知识/适用目标/关键词/学习空间: 分号分隔，主题取首段
- 封面:   保留 CSV 中的第三方图片 URL（可能未来失效）
"""
import csv
import json
import os
import re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "书库", "dlut_campus_books_8000.csv")
OUTPUT = os.path.join(BASE, "data", "books.json")

DIFFICULTY_MAP = {"入门": "beginner", "进阶": "intermediate", "深入": "advanced"}
LEVEL_MAP = {"低": 0.2, "中": 0.5, "高": 0.8}
EMPTY_MARKERS = {"无", "无。", "无严格前置要求", "无特别前置要求", ""}


def split_list(val, sep="[;；,，、]"):
    """把分隔符连接的字符串拆成列表，处理空值"""
    if val is None:
        return []
    s = str(val).strip()
    if s in EMPTY_MARKERS:
        return []
    return [p.strip() for p in re.split(sep, s) if p.strip()]


def main():
    books = []
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        col = {name: i for i, name in enumerate(header)}

        for row in reader:
            if len(row) < len(header):
                continue  # 跳过不完整的行

            def cell(name):
                i = col.get(name)
                if i is None or i >= len(row) or row[i] is None:
                    return ""
                return str(row[i]).strip()

            title = cell("书名")
            if not title:
                continue

            lang = cell("语言")
            language = "en" if lang == "英语" else "zh"

            try:
                pages = int(float(cell("页数") or "0"))
            except ValueError:
                pages = 0

            # 主题取首段（分号多主题）
            topic = split_list(cell("主题"))[0] if cell("主题") else ""

            keywords = split_list(cell("关键词"), "[;；]")
            if not keywords:
                keywords = [topic, title.split(":")[0].split("：")[0].strip()]

            space = split_list(cell("适配学习空间"), "[;；/]")
            space = space[0] if space else ""

            status = cell("馆藏状态")

            books.append({
                "id": len(books) + 1,
                "title": title,
                "author": cell("作者") or None,
                "topic": topic,
                "difficulty": DIFFICULTY_MAP.get(cell("难度"), "beginner"),
                "pages": pages,
                "language": language,
                "case_ratio": LEVEL_MAP.get(cell("案例程度"), 0.5),
                "theory_ratio": LEVEL_MAP.get(cell("理论程度"), 0.5),
                "prerequisites": split_list(cell("前置知识")),
                "goals": split_list(cell("适用目标")),
                "keywords": keywords,
                "availability": "可借" in status,
                "description": cell("简介") or None,
                "location": cell("馆藏位置") or None,
                "space": space or None,
                "cover": cell("封面") or None,
            })

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"转换完成: {len(books)} 本书 -> {OUTPUT}")
    print("难度分布:", dict(Counter(b["difficulty"] for b in books)))
    print("语言分布:", dict(Counter(b["language"] for b in books)))
    print("可借:", sum(1 for b in books if b["availability"]), "/", len(books))
    print("主题种类:", len(set(b["topic"] for b in books)))
    print("有封面:", sum(1 for b in books if b["cover"]), "/", len(books))


if __name__ == "__main__":
    main()
