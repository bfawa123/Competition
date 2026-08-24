# 灵犀 AI 馆员前端

这是一个 React + TypeScript + Vite 前端，提供学习目标采集、个性化书目推荐、记忆管理、书目浏览、记忆影响对比和 Agent 执行轨迹。

## 给拿到项目的人

### 环境要求

- Node.js 18 或更高版本
- pnpm 8 或更高版本（推荐使用 `corepack enable pnpm` 启用）
- Windows 用户可以直接使用根目录的 `run.bat`

### Windows 一键运行

1. 解压项目并进入 `fronted` 根目录。
2. 双击 `run.bat`。
3. 脚本会安装依赖、启动 Vite，并自动打开 `http://127.0.0.1:5173/recommend`。
4. 使用过程中不要关闭标题为 `Lingxi Dev Server` 的终端窗口。

### 命令行运行

在 `fronted` 根目录打开 PowerShell、Windows Terminal、macOS Terminal 或 Linux Shell：

```bash
corepack enable pnpm       # 只需首次执行
pnpm install               # 首次运行或依赖变化后执行
pnpm dev                   # 启动开发服务器
```

然后打开 `http://127.0.0.1:5173/recommend`。停止服务时，在终端按 `Ctrl + C`。

### 连接后端

默认不配置后端时，前端使用 `src/mockData.ts` 的本地数据，方便检查界面和交互。连接队友的 FastAPI 后端时：

```powershell
Copy-Item .env.example .env.local
```

macOS/Linux 使用 `cp .env.example .env.local`。然后在 `.env.local` 中确认：

```env
VITE_API_BASE_URL=http://localhost:8000
```

保存后重启 `pnpm dev`。后端接口不可用时，前端会显示连接错误，不会把后端错误静默伪装成本地成功结果。

## 常用命令

```bash
pnpm dev         # 开发模式，支持热更新
pnpm run build   # 类型检查并生成 dist/
pnpm run preview # 预览最近一次生产构建
pnpm test        # 运行自动测试
pnpm run typecheck
```

## 目录结构

```text
fronted/
├─ public/             # 封面和页面插图等静态资源
├─ src/
│  ├─ pages/           # 推荐、书库、记忆、对比、轨迹、用户页面
│  ├─ api.ts           # 后端接口与本地演示数据切换
│  ├─ components.tsx   # 共用 UI 组件
│  ├─ state.tsx        # 用户、主题、推荐结果等全局状态
│  ├─ types.ts         # 前后端数据类型
│  ├─ mockData.ts      # 未连接后端时的演示数据
│  └─ styles.css       # 全局视觉样式
├─ .env.example        # 后端地址配置模板
├─ index.html          # Vite 的 HTML 挂载外壳，不要直接双击
├─ package.json        # 依赖和脚本命令
├─ pnpm-lock.yaml      # 精确锁定依赖版本
├─ pnpm-workspace.yaml # esbuild 构建许可配置
├─ vite.config.ts      # Vite 开发服务器配置
└─ run.bat             # Windows 双击启动入口
```

`node_modules/`、`dist/`、`.pnpm-store/` 和 `.playwright-cli/` 都是本机生成目录，不需要复制给其他人；删除后可通过 `pnpm install` 或 `pnpm run build` 重新生成。

## 后端接口

前端通过 `src/api.ts` 调用：`POST /api/agent/recommend`、记忆列表/写入/删除、书目搜索/详情、`GET /api/demo/compare/{user_id}` 和 `GET /api/agent/trace/{user_id}`。

## 常见问题

- **直接双击 `index.html` 不能访问**：这是 Vite 单页应用，必须通过 `pnpm dev` 或 `run.bat` 走 HTTP 服务。
- **找不到 pnpm**：安装 Node.js 后执行 `corepack enable pnpm`，再重新打开终端。
- **`ERR_PNPM_IGNORED_BUILDS: esbuild`**：确认 `pnpm-workspace.yaml` 中为 `esbuild: true`，再执行 `pnpm install`。
- **5173 端口被占用**：关闭旧的 Vite 终端，或执行 `pnpm dev --port 5174`，然后访问对应端口。
- **后端连接失败**：确认 FastAPI 正在 `http://localhost:8000` 运行，检查 `.env.local`，修改后重启前端。
