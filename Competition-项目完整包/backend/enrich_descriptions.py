"""
为 books.json 生成更真实的简介
原 xlsx 简介列是模板占位文本（如 "Python基础入门读物..."），
本脚本基于标题、主题、作者、关键词、页数合成 2~3 句有意义的中文描述。

相比早期版本，本脚本使用多套句式模板，根据书籍元数据稳定选择变体，
让不同书的简介在信息一致的前提下保持自然差异。
"""
import json
import os
import random

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE, "data", "books.json")


def is_chinese_author(author: str) -> bool:
    if not author:
        return False
    return any("\u4e00" <= ch <= "\u9fff" for ch in author)


def is_english_author(author: str) -> bool:
    if not author:
        return False
    return any(ch.isascii() and ch.isalpha() for ch in author) and not is_chinese_author(author)


def case_phrase(case_ratio: float, theory_ratio: float) -> str:
    case_pct = round(case_ratio * 100)
    theory_pct = round(theory_ratio * 100)
    if case_pct >= 70:
        return random.choice([
            "案例驱动、注重实操演练",
            "以大量实例贯穿始终，强调动手能力",
            "注重项目实践，案例密度很高",
        ])
    if case_pct <= 30:
        return random.choice([
            "理论推导扎实、注重原理溯源",
            "偏理论阐释，强调概念与推导",
            "以原理和体系化论述为主",
        ])
    if case_pct >= theory_pct + 15:
        return random.choice([
            "案例与理论并重、偏向应用实践",
            "在讲清原理的同时安排了丰富案例",
            "理论与实践结合，更侧重实际应用",
        ])
    if theory_pct >= case_pct + 15:
        return random.choice([
            "理论与案例兼顾、偏向原理梳理",
            "以理论框架为主，辅以典型案例",
            "重在建立系统认知，案例服务于原理",
        ])
    return random.choice([
        "理论与实践并重",
        "理论讲解与实战案例均衡安排",
        "兼顾概念梳理与动手练习",
    ])


def difficulty_tail(diff: str) -> str:
    return {
        "beginner": random.choice([
            "适合零基础读者循序渐进地入门",
            "可帮助初学者建立扎实基础",
            "对刚接触该领域的读者非常友好",
        ]),
        "intermediate": random.choice([
            "适合希望系统提升的读者研读",
            "适合有一定基础后用来进阶提高",
            "适合作为从中级迈向高级的参考书",
        ]),
        "advanced": random.choice([
            "适合具备相当基础的读者深入钻研",
            "面向已有积累、希望挑战高阶内容的读者",
            "适合用于深化理解和专题研究",
        ]),
    }.get(diff, "适合相关方向读者参考")


def author_verb(author: str) -> str:
    if not author:
        return ""
    if is_english_author(author):
        return random.choice(["撰写", "编著", "著"])
    return random.choice(["编著", "撰写", "著"])


def author_phrase(title: str, author: str) -> str:
    if not author:
        return f"《{title}》"
    verb = author_verb(author)
    return random.choice([
        f"《{title}》由{author}{verb}",
        f"{author}所{verb}的《{title}》",
        f"《{title}》出自{author}之手",
    ])


def topic_keyword_phrase(topic: str, keywords: list) -> str:
    # 过滤掉与主题重复或过于宽泛的通用标签，避免“覆盖计算机、专业教材等议题”这种不自然表达
    generic = {"计算机", "专业教材", "教材", "入门", "进阶", "实战", "科研", "理论"}
    kw = [k for k in keywords if k and k != topic and k not in generic][:3]
    kw_str = "、".join(kw) if kw else ""
    if kw_str:
        return random.choice([
            f"围绕{topic}方向展开，覆盖{kw_str}等核心议题",
            f"聚焦{topic}领域，系统讲解{kw_str}等主题",
            f"以{topic}为主线，深入{kw_str}等关键内容",
            f"面向{topic}方向，对{kw_str}等议题进行了完整梳理",
        ])
    return random.choice([
        f"围绕{topic}方向系统梳理",
        f"聚焦{topic}领域的核心内容",
        f"以{topic}为主线组织全书",
    ])


def volume_phrase(pages: int) -> str:
    if pages <= 250:
        return random.choice([
            f"全书约{pages}页，篇幅精炼",
            f"内容精炼，全书仅约{pages}页",
        ])
    if pages <= 500:
        return random.choice([
            f"全书约{pages}页，体量适中",
            f"全书约{pages}页，内容翔实而不冗长",
        ])
    if pages <= 750:
        return random.choice([
            f"全书约{pages}页，内容系统而全面",
            f"全书约{pages}页，是一本较为厚重的参考书",
        ])
    return random.choice([
        f"全书约{pages}页，体系完整、内容广博",
        f"全书约{pages}页，属于该领域的大部头参考书",
    ])


def synthesize(book: dict) -> str:
    title = book.get("title") or ""
    author = book.get("author") or ""
    topic = book.get("topic") or ""
    keywords = book.get("keywords") or []
    case = case_phrase(book.get("case_ratio", 0.5), book.get("theory_ratio", 0.5))
    diff_tail = difficulty_tail(book.get("difficulty", ""))
    pages = book.get("pages") or 0

    # 用 book id 做稳定随机种子，保证同一本书每次生成一致
    book_id = book.get("id", 0)
    state = random.getstate()
    random.seed(book_id)

    opener = author_phrase(title, author)
    middle = topic_keyword_phrase(topic, keywords)
    volume = volume_phrase(pages)

    # 优先把 opener（作者+书名）放在前面，更自然
    patterns = [
        f"{opener}，{middle}。{volume}，整体风格{case}，{diff_tail}。",
        f"{opener}。{middle}，{volume}；整体风格{case}，{diff_tail}。",
        f"{opener}，{middle}，{volume}。该书整体风格{case}，{diff_tail}。",
        f"{opener}，{volume}，{middle}。整体风格{case}，{diff_tail}。",
    ]
    result = random.choice(patterns)

    random.setstate(state)
    return result


def main(force=False):
    with open(DATA_PATH, encoding="utf-8") as f:
        books = json.load(f)

    rewritten = 0
    skipped = 0
    for b in books:
        old = b.get("description", "")
        # 跳过人工写过的（非模板文本）：识别旧占位语句
        template_markers = [
            "入门读物，讲解基础概念与核心方法，适合初学者系统学习",
            "进阶教材，系统讲解理论体系与实践应用，适合有一定基础的读者",
            "高阶著作，深入探讨理论原理与前沿进展，适合专业研究者阅读",
            "案例教程，通过真实项目案例讲解核心方法，适合动手实践",
            "基础概念与核心方法",
            "理论体系与实践应用",
            "理论原理与前沿进展",
        ]
        if not force and old and not any(m in old for m in template_markers):
            skipped += 1
            continue
        b["description"] = synthesize(b)
        rewritten += 1

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print(f"已重新生成 {rewritten} 本简介；跳过 {skipped} 本（非模板）")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="为 books.json 生成书籍简介")
    parser.add_argument("--force", action="store_true", help="强制重新生成所有简介")
    args = parser.parse_args()
    main(force=args.force)
