# -*- coding: utf-8 -*-
"""
从 书库（换封面版）.xlsx 提取内嵌封面图，按行号对位写入 backend/covers/{book_id}.jpg，
并更新 books.json 的 cover 字段为 /covers/{book_id}.jpg

对应关系：
- drawing1.xml 中锚点 <row>N</row>（0基）→ 表格第 N+1 行 → 数据第 N 行 → books.json[N-1]（id=N）
"""
import json
import os
import re
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
_xlsx_candidates = ["书库1.xlsx", "书库（换封面版）.xlsx"]
XLSX = next((os.path.join(os.path.dirname(BASE), n) for n in _xlsx_candidates if os.path.exists(os.path.join(os.path.dirname(BASE), n))), None)
if XLSX is None:
    raise FileNotFoundError(f"未找到书库文件，尝试过: {_xlsx_candidates}")
BOOKS_JSON = os.path.join(BASE, "data", "books.json")
COVERS_DIR = os.path.join(BASE, "covers")


def main():
    z = zipfile.ZipFile(XLSX)

    # 1. 解析 rels: rId -> media 文件名
    rels_xml = z.read("xl/drawings/_rels/drawing1.xml.rels").decode("utf-8")
    rid_to_media = {}
    for rel in re.finditer(r"<Relationship\b[^>]*/>", rels_xml):
        tag = rel.group(0)
        rid_m = re.search(r'Id="([^"]+)"', tag)
        target_m = re.search(r'Target="([^"]+)"', tag)
        if rid_m and target_m:
            rid_to_media[rid_m.group(1)] = os.path.basename(target_m.group(1))

    # 2. 解析 drawing: 行号 -> rId
    draw_xml = z.read("xl/drawings/drawing1.xml").decode("utf-8")
    row_to_media = {}
    for anchor in re.finditer(r"<oneCellAnchor>(.*?)</oneCellAnchor>", draw_xml, re.S):
        body = anchor.group(1)
        row_m = re.search(r"<row>(\d+)</row>", body)
        embed_m = re.search(r'r:embed="([^"]+)"', body)
        if row_m and embed_m:
            row_to_media[int(row_m.group(1))] = rid_to_media.get(embed_m.group(1))

    print(f"锚点图片数: {len(row_to_media)}")

    # 3. 准备输出目录（直接覆盖写入，不做目录删除）
    os.makedirs(COVERS_DIR, exist_ok=True)

    # 4. 按行号对位导出图片并更新 books.json
    with open(BOOKS_JSON, encoding="utf-8") as f:
        books = json.load(f)

    exported = 0
    for row, media in row_to_media.items():
        book_idx = row - 1  # drawing row N -> books[N-1]
        if 0 <= book_idx < len(books):
            book = books[book_idx]
            ext = os.path.splitext(media)[1].lower() or ".jpg"
            filename = f"{book['id']}{ext}"
            with z.open(f"xl/media/{media}") as src, \
                 open(os.path.join(COVERS_DIR, filename), "wb") as dst:
                dst.write(src.read())
            book["cover"] = f"/covers/{filename}"
            exported += 1

    with open(BOOKS_JSON, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"导出封面: {exported} 张 -> {COVERS_DIR}")
    print(f"books.json 更新完成，含 cover 字段的书: {sum(1 for b in books if b.get('cover'))}/{len(books)}")


if __name__ == "__main__":
    main()
