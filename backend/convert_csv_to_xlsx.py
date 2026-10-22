# -*- coding: utf-8 -*-
"""
将 data/书库/dlut_campus_books_8000.csv 改写成 data/书库2.xlsx，
列结构和取值格式对齐原 xlsx，供 convert_xlsx.py 直接读取。

取值转换：
- 难度: 入门 -> 1级-零基础入门, 进阶 -> 3级-进阶, 深入 -> 4级-高阶
- 案例/理论程度: 低/中/高 -> 1/3/5
- 语言: 英语 -> 英文, 中文+英语 -> 中英双语, 其余 -> 中文
- 主题/适配学习空间/跨界标签: 分号多值取首段
- 前置知识/适用目标/关键词: 分号 -> 逗号
- 关联延伸书目: 分号 -> 顿号
"""
import csv
import os
from openpyxl import Workbook

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
CSV_PATH = os.path.join(ROOT, "data", "书库", "dlut_campus_books_8000.csv")
XLSX_OUT = os.path.join(ROOT, "data", "书库2.xlsx")

DIFFICULTY_MAP = {"入门": "1级-零基础入门", "进阶": "3级-进阶", "深入": "4级-高阶"}
LEVEL_MAP = {"低": 1, "中": 3, "高": 5}
EMPTY_PREREQ = {"无", "无。", "无严格前置要求", "无特别前置要求", ""}

HEADER = ["封面", "书名", "作者", "主题", "难度", "页数", "语言", "案例程度", "理论程度",
          "前置知识", "适用目标", "简介", "关键词", "馆藏位置", "适配学习空间",
          "关联延伸书目", "跨界标签"]


def lang_map(s):
    if "英语" in s and "中文" in s:
        return "中英双语"
    if s == "英语":
        return "英文"
    return "中文"


def first_seg(s):
    if not s:
        return ""
    return s.replace("；", ";").split(";")[0].strip()


def join_sep(s, sep=","):
    if not s:
        return ""
    parts = [p.strip() for p in s.replace("；", ";").split(";") if p.strip()]
    return sep.join(parts)


def main():
    rows_out = [HEADER]
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        col = {name: i for i, name in enumerate(header)}

        for row in reader:
            def cell(name):
                i = col.get(name)
                if i is None or i >= len(row) or row[i] is None:
                    return ""
                return str(row[i]).strip()

            title = cell("书名")
            if not title:
                continue

            prereq = join_sep(cell("前置知识"))
            if prereq in EMPTY_PREREQ:
                prereq = ""

            try:
                pages = int(float(cell("页数") or "0"))
            except ValueError:
                pages = 0

            rows_out.append([
                cell("封面") or None,
                title,
                cell("作者") or None,
                first_seg(cell("主题")),
                DIFFICULTY_MAP.get(cell("难度"), "1级-零基础入门"),
                pages,
                lang_map(cell("语言")),
                LEVEL_MAP.get(cell("案例程度"), 3),
                LEVEL_MAP.get(cell("理论程度"), 3),
                prereq,
                join_sep(cell("适用目标")),
                cell("简介") or None,
                join_sep(cell("关键词")),
                cell("馆藏位置") or None,
                first_seg(cell("适配学习空间")),
                join_sep(cell("关联延伸书目"), "、"),
                first_seg(cell("跨界标签")),
            ])

    wb = Workbook()
    ws = wb.active
    for r in rows_out:
        ws.append(r)
    wb.save(XLSX_OUT)
    print(f"改写完成: {len(rows_out) - 1} 本书 -> {XLSX_OUT}")


if __name__ == "__main__":
    main()
