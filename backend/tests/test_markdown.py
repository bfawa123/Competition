"""
测试 markdown 去除功能
"""
import re


def _remove_markdown(text: str) -> str:
    """
    去除 markdown 格式符号，返回纯文本
    """
    if not text:
        return text

    # 1. 移除加粗 **text** 或 __text__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'__(.*?)__', r'\1', text)

    # 2. 移除斜体 *text* 或 _text_
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)\*(?!\*)', r'\1', text)
    text = re.sub(r'(?<!_)_(?!_)(.*?)_(?!_)', r'\1', text)

    # 3. 移除行内代码 `code`
    text = re.sub(r'`(.*?)`', r'\1', text)

    # 4. 移除代码块 ```code```
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # 5. 移除链接 [text](url)
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)

    # 6. 移除图片 ![alt](url)
    text = re.sub(r'!\[(.*?)\]\(.*?\)', r'\1', text)

    # 7. 移除标题标记 # ## ### 等
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # 8. 移除引用标记 >
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # 9. 移除水平线 --- 或 ***
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # 10. 清理多余空白
    text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符合并
    text = re.sub(r'\n{3,}', '\n\n', text)  # 多个换行合并

    return text.strip()


# 测试用例
test_cases = [
    # 测试 1: 加粗和列表
    {
        "name": "加粗和列表",
        "input": """你好！我看到你的目标是学Python。

1. **换一本Python入门书**（如《Python编程：从入门到实践》）
2. **每天只学一个小节**，30分钟足够
3. **用在线练习平台**巩固

**理由**：Python语法简洁，适合新手。""",
    },
    # 测试 2: 斜体和代码
    {
        "name": "斜体和代码",
        "input": """建议使用 `print()` 函数，这是 *最常用* 的输出方式。

你可以这样写：
```python
print("Hello World")
```

参考 [Python官方文档](https://docs.python.org) 了解更多。""",
    },
    # 测试 3: 标题和引用
    {
        "name": "标题和引用",
        "input": """### 学习建议

> 每天进步一点点

---

#### 进阶技巧

- 多做练习
- 阅读源码""",
    },
]

print("Markdown 去除功能测试")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {test['name']}")
    print("-" * 70)
    print("【原始文本】")
    print(test['input'])
    print("\n【处理后】")
    print(_remove_markdown(test['input']))
    print("-" * 70)

print("\n" + "=" * 70)
print("测试完成！")
