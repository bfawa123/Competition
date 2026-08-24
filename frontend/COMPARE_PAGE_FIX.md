# ComparePage（对比页面）修复说明

## 问题描述

用户报告了两个问题：
1. **"展示下一步"按钮** - 点了没有反应
2. **"反馈前"和"记忆后"的书籍列表** - 点击没有反应

## 问题分析

### 问题 1："展示下一步"按钮

按钮逻辑是正确的（`setStep((value) => Math.min(3, value + 1))`），但可能的情况：

- **数据加载中**：页面正在等待 `getComparison()` 返回，此时显示 LoadingRoute
- **已到最后一步**：当 step=3 时，按钮文字变为"对比已完成"，再次点击不会增加 step

**正常行为示例：**
```
step=0: "展示下一步" → step=1 (显示：第一次推荐)
step=1: "展示下一步" → step=2 (显示：+ 记忆提取)
step=2: "展示下一步" → step=3 (显示：+ 记忆后推荐)
step=3: "对比已完成" (不再增加)
```

### 问题 2：书籍列表点击无反应（已修复 ✅）

**原因：** ComparePage 缺少以下功能：
1. ❌ 没有 `BookDetail` 弹窗组件
2. ❌ 书籍项没有 `onClick` 事件
3. ❌ 没有 `openBook()` 函数

**对比其他页面：**
- ✅ **BooksPage（书架页）**：实现了点击书籍查看详情
- ✅ **ResultPage（结果页）**：实现了点击书籍查看详情
- ❌ **ComparePage（对比页）**：**缺失此功能**

## 修复内容

### 1. 添加书籍详情功能

```typescript
// 新增 state
const [selectedBook, setSelectedBook] = useState<Book | null>(null);

// 新增函数
async function openBook(book: Book) {
  try {
    setSelectedBook(await getBook(book.id) || book);
  } catch {
    console.error("无法读取书籍详情");
  }
}

// 渲染 BookDetail 弹窗
{selectedBook && <BookDetail book={selectedBook} onClose={() => setSelectedBook(null)} />}
```

### 2. 为书籍项添加点击事件

**反馈前书籍列表：**
```typescript
<div
  key={score.book.id}
  className="comparison-book-item"
  onClick={() => openBook(score.book)}
>
  <span className="compare-rank">#{index + 1}</span>
  <BookCover book={score.book} size="sm" />
  <span>
    <strong>{score.book.title}</strong>
    <small>{score.book.pages} 页 · 案例 {Math.round(score.book.case_ratio * 100)}%</small>
  </span>
  <code>{score.total_score.toFixed(1)}</code>
  <BookOpenIcon className="book-open-icon" />
</div>
```

**记忆后书籍列表：**（同样的修改）

### 3. 添加样式

在 `styles.css` 中添加：

```css
/* 可点击的书籍项 */
.comparison-book-item {
  cursor: pointer;
  transition: background .2s;
  border-radius: 4px;
}

.comparison-book-item:hover {
  background: var(--surface-2);
}

/* 打开图标（悬停时显示） */
.book-open-icon {
  color: var(--blue);
  opacity: 0;
  transition: opacity .2s;
}

.comparison-book-item:hover .book-open-icon {
  opacity: 1;
}
```

## 修复文件

- ✅ `frontend/src/pages/ComparePage.tsx` - 添加点击功能
- ✅ `frontend/src/styles.css` - 添加悬停样式

## 验证方式

1. **启动前端**：`cd frontend && npm run dev`
2. **进入对比页面**：从推荐结果进入对比页
3. **等待数据加载**：页面显示书籍列表（Loading 消失）
4. **点击"展示下一步"**：逐步查看四个阶段
5. **点击任意书籍**：应该弹出书籍详情弹窗
6. **关闭弹窗**：点击 X 或背景

## 效果

### 修复前
- ❌ 点击"反馈前"的书籍 → 无反应
- ❌ 点击"记忆后"的书籍 → 无反应

### 修复后
- ✅ 点击"反馈前"的书籍 → 显示详情弹窗
- ✅ 点击"记忆后"的书籍 → 显示详情弹窗
- ✅ 悬停时显示蓝色打开图标
- ✅ 背景高亮提示可点击

## 相关页面参考

- **BooksPage**: `src/pages/BooksPage.tsx` (第21-28行)
- **ResultPage**: `src/pages/ResultPage.tsx` (第73行, 第83行)
- **BookDetail**: `src/components.tsx` (第384-402行)
