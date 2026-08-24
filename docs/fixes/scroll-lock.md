# 书库滚动穿透修复

## 问题

书库页面点击书籍弹出详情浮层后，在浮层内上下滑动浏览内容时，底层的书架列表不受控制地同步滚动（滚动穿透）。

## 根因

1. 原来的锁逻辑只设置了 `document.body.style.overflow = "hidden"`，但这个项目布局里真正承担视口滚动的是 `document.documentElement`（`<html>`），所以底层根本没被真正锁住。
2. 原来的 `onWheel` / `onTouchMove` 里用的 `stopPropagation()` 只能阻止事件冒泡，挡不住浏览器默认的滚动行为；而且 React 19 会把这两类监听器注册为被动（passive）监听器，`preventDefault` 也会失效。
3. 同页面的移动端筛选浮层（`mobile-filter-sheet`）完全没有锁底层，同样会穿透。

## 改了什么

### 1. `src/components.tsx`

- 新增 `useScrollLock(active)` hook：通过引用计数在 `documentElement` + `body` 上设 `overflow: hidden`，直接锁住根滚动器；同时补偿消失的滚动条宽度（`padding-right`），避免背景内容横向抖动。引用计数保证多个浮层叠加 / React StrictMode 双执行 effect 时不会把页面"卡死"。
- `BookDetail` 组件改用 `useScrollLock(true)`，删掉无效的 `onWheel` / `onTouchMove` 处理。
- `.detail-drawer` 原有的 `overflow-y: auto; overscroll-behavior: contain` 保留不动 —— 所以弹窗内部照常滚动，到边界也不会连锁。

### 2. `src/pages/BooksPage.tsx`

- 引入 `useScrollLock`，给移动端筛选浮层加上锁：`useScrollLock(mobileFilters || !!selected)`。

## 如何同步回你的项目

改动只在以下两个文件，直接覆盖到你们项目对应位置即可：

```
frontend/src/components.tsx
frontend/src/pages/BooksPage.tsx
```

> 如果你们项目里 `components.tsx` / `BooksPage.tsx` 在此基础上还有其它本地改动，请手动合并——核心改动点是：
> 1. 复制整个 `useScrollLock` hook；
> 2. `BookDetail` 里调用 `useScrollLock(true)`，删掉原来的 `useEffect` 锁 body 的逻辑和 `onWheel` / `onTouchMove` 相关代码；
> 3. `BooksPage` 里 import `useScrollLock` 并调用。

## 已验证

- `npx tsc -b` 类型检查通过（exit 0）
- `npx vite build` 生产构建通过（exit 0）

## 顺带说明

`MemoriesPage` 里的删除确认弹层（`confirm-dialog`）也存在同样"没锁底层"的隐患，本次未在需求范围内所以没改。如果需要，同样调用 `useScrollLock(true)` 即可修复。
