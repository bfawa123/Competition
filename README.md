# 灵犀 AI 馆员

灵犀是一个面向学习场景的可解释书目推荐应用。用户可以选择学习主题、当前水平、每日阅读时间和语言偏好；系统结合馆藏数据与用户反馈记忆，生成推荐书单、排序依据和执行轨迹。

## 主要功能

- 个性化推荐：按主题、水平、时间和语言生成最多 5 本候选书。
- 渐进式难度：入门只推荐入门书；进阶可推荐入门和进阶书；高阶可推荐入门、进阶和高阶书，避免小主题书目不足时结果为空。
- 长期记忆：将用户对篇幅、语言、案例比例等反馈保存为后续排序依据。
- 推荐对比：展示使用记忆前后的排序变化及变化结论。
- 书库检索：按主题、难度、语言、页数和关键词浏览馆藏。
- 用户隔离：不同本地用户使用独立的推荐记录和偏好记忆。
- Agent 轨迹：展示记忆检索、候选搜索和评分排序过程。

## 技术栈

- 前端：React 19、TypeScript、Vite
- 后端：FastAPI、Pydantic、Uvicorn
- 数据：`backend/data/books.json`、`backend/data/memories.json`
- 原始书库：`data/data/书库1.xlsx`

## 环境要求

- Windows 10/11
- Python 3.10 或更高版本，建议 3.11 或 3.12
- Node.js 18 或更高版本，建议当前 LTS
- Python 和 Node.js 安装目录已加入 `PATH`

## 一键安装与启动

在项目根目录双击 `scripts/start.bat`。脚本会在首次运行时：

1. 创建 `backend/.venv` Python 虚拟环境；
2. 安装 `backend/requirements.txt`；
3. 安装 `frontend` 的 npm 依赖；
4. 分别启动后端和前端。

启动后访问：

- 应用：<http://127.0.0.1:5173>
- API 文档：<http://localhost:8000/docs>

后续启动仍可直接双击 `scripts/start.bat`。关闭对应终端窗口即可停止服务。

## 命令行方式

首次安装：

```powershell
python setup.py
```

同时启动前后端：

```powershell
python scripts/start.py
```

分别启动：

```powershell
# 终端 1：后端
cd backend/app
.venv\Scripts\python.exe main.py

# 终端 2：前端
cd frontend
npm run dev
```

## 配置

后端配置位于 `backend/.env`。不配置大模型密钥时，推荐排序仍可工作，说明生成和反馈压缩会使用规则兜底。

```env
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

前端默认请求同源 `/api`，Vite 开发服务器会按 `frontend/vite.config.ts` 代理到后端。如需直连其他后端，在 `frontend/.env.local` 设置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

修改环境变量后需要重启服务。

## 测试与构建

```powershell
# 后端核心检查
cd backend
.venv\Scripts\python.exe test_backend.py

# 前端测试、类型检查和生产构建
cd frontend
npm test
npm run typecheck
npm run build
```

## 目录结构

```text
灵犀0.15-修复详情弹窗/
├─ frontend/             # React 前端
├─ backend/              # FastAPI 后端
│  ├─ app/              # 主要业务代码
│  ├─ tests/            # 后端测试
│  ├─ services/         # 业务服务层
│  ├─ models/           # 数据模型
│  ├─ utils/            # 工具函数
│  ├─ data/             # JSON 数据文件
│  └─ covers/           # 书籍封面图片
├─ scripts/             # 启动、诊断、维护脚本
│  ├─ start.py
│  ├─ start.bat
│  └─ diagnose.py
├─ docs/                # 项目文档
│  ├─ deployment.md
│  ├─ api.md
│  ├─ fixes/
│  │  ├─ scroll-lock.md
│  │  └─ detail-dialog-position.md
│  └─ ...
├─ data/                # 原始数据文件
│  └─ data/书库1.xlsx
├─ setup.py             # 环境安装脚本
└─ README.md            # 项目说明
```

## 推荐难度规则

“当前水平”表示用户可以阅读的最高难度，而不是必须精确匹配的唯一难度：

| 当前水平 | 候选书难度 |
| --- | --- |
| 入门 | 入门 |
| 进阶 | 入门、进阶 |
| 高阶 | 入门、进阶、高阶 |

候选集确定后，评分器仍会优先排序与当前水平精确匹配的书，因此放宽范围不会抹掉难度偏好。

## 常见问题

- 提示找不到 Python 或 npm：重新安装对应运行时并勾选“添加到 PATH”，然后打开新终端。
- `npm install` 失败：进入 `frontend` 后运行 `npm install`，检查网络和 npm registry 配置。
- Python 依赖安装失败：删除损坏的 `backend/.venv` 后重新运行 `python setup.py`。
- 端口 5173 或 8000 被占用：关闭旧的 Vite/Uvicorn 进程后重新启动。
- 页面能打开但接口报错：先访问 API 文档确认后端已启动，再检查浏览器网络请求和 `.env.local`。
- 推荐为空：确认主题在书库中存在、后端使用最新代码，并检查是否叠加了语言或篇幅偏好等严格条件。

## 数据维护

运行 `backend/convert_xlsx.py` 可将 Excel 书库转换为后端 JSON 数据。更新前请备份 `backend/data/books.json`，转换后运行后端检查和前端推荐流程，确认字段、封面及难度分布正常。
