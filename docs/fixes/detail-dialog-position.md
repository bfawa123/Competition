# 修复说明 — 书籍详情弹窗定位失效 + 无法内部滚动（灵犀 0.15）

## 问题现象

1. 书架页滚动到下方后点击书籍，侧边详情弹窗一打开就停在内容中部/底部，标题看不到，需手动往上滑；
2. 弹窗内部内容无法上下滚动浏览。

## 根因

CSS 中 `.page-enter`（每个页面根容器的入场动画类）写的是：

```css
.page-enter { animation: premium-page-in .85s var(--motion) both; }
```

`animation-fill-mode: both` 使动画播完后元素仍保持 `transform: matrix(1,0,0,1,0,0)`（恒等矩阵，而非 `none`）。
**只要元素的 computed transform 不是 `none`，它就会成为内部所有 `position: fixed` 后代的"包含块"**。

而 `BookDetail` 详情弹窗的 `.detail-drawer` 是 `position: fixed; inset: 0 0 0 auto`，且渲染在 `.books-page.page-enter` 内部——于是 fixed 不再相对视口定位，而是相对整个（高达数万像素的）长页面定位：

- `top:0 / bottom:0` 对齐到整页文档的顶和底 → 视口里露出的正好是弹窗中部/底部 → 现象 1；
- 弹窗高度被拉伸成整个文档高度，内容"装得下" → 自身不再产生滚动 → 现象 2。

## 修复内容（双保险）

1. **Portal 结构性修复**：`BookDetail`、`Toast`、移动端筛选浮层（BooksPage）、反馈弹窗（MemoriesPage / ResultPage）、删除确认弹窗（MemoriesPage）全部改用 `createPortal(..., document.body)` 渲染，彻底脱离带动画的页面容器，fixed 恢复相对视口定位。
   - 涉及文件：`src/components.tsx`、`src/pages/BooksPage.tsx`、`src/pages/MemoriesPage.tsx`、`src/pages/ResultPage.tsx`
2. **CSS 根因修复**：`.page-enter` 动画去掉 `both` 填充模式（改回默认 `none`），动画结束后 transform 回到 `none`，该元素不再成为后代的包含块（视觉无差异）。
   - 涉及文件：`src/styles.css`

## 验证方式

前后端真实启动 + 浏览器实测：滚动到页面 80000px 深处点书 → 弹窗 `top=0`、`scrollTop=0`（从标题开始显示）、`scrollHeight > clientHeight`（内部可滚动）、背景锁定不动；关闭重开状态同样干净。`tsc -b` 与 `vite build` 均通过。

## 同事合并指引

若本地已有其它改动，可只做两件事：

1. 把所有 fixed 定位的浮层（`modal-backdrop` 系列）用 `createPortal` 包一层渲染到 `document.body`；
2. `styles.css` 中 `.page-enter` 的 `both` 填充模式删掉（保持 `animation: premium-page-in .85s var(--motion);` 即可）。
