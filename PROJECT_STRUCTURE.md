# 项目结构说明

## 重构完成 ✅

项目已成功重组为标准开源项目结构。

## 新的目录结构

```
灵犀0.15-修复详情弹窗/
├── frontend/              # React 前端项目
│   ├── src/              # 源代码
│   ├── public/           # 静态资源
│   ├── package.json      # 依赖配置
│   ├── vite.config.ts    # Vite 配置
│   └── ...
│
├── backend/              # FastAPI 后端项目
│   ├── app/             # 主要业务代码
│   │   ├── main.py      # FastAPI 主应用
│   │   └── config.py    # 配置管理
│   ├── tests/           # 后端测试
│   │   ├── test_backend.py
│   │   ├── test_assistant.py
│   │   ├── test_deepseek.py
│   │   └── test_markdown.py
│   ├── services/        # 业务服务层
│   ├── models/          # 数据模型
│   ├── utils/           # 工具函数
│   ├── data/            # JSON 数据文件
│   │   ├── books.json
│   │   ├── memories.json
│   │   └── embeddings_cache.json
│   ├── covers/          # 书籍封面图片（400+ 张）
│   ├── backend/docs/    # 后端文档
│   │   ├── ALGORITHM.md
│   │   ├── API.md
│   │   └── SUMMARY.md
│   ├── requirements.txt # Python 依赖
│   └── .env             # 环境配置
│
├── scripts/             # 启动、诊断、维护脚本
│   ├── start.py         # 跨平台启动脚本
│   ├── start.bat        # Windows 一键启动
│   └── diagnose.py      # 环境诊断脚本
│
├── docs/                # 项目文档
│   ├── deployment.md            # 部署说明
│   ├── api.md                   # API 说明
│   ├── deepseek-setup.md        # DeepSeek 配置
│   ├── colleague-deployment.md  # 同事部署说明
│   └── fixes/                   # 修复说明
│       ├── scroll-lock.md
│       └── detail-dialog-position.md
│
├── data/                # 原始数据文件
│   └── 书库1.xlsx       # Excel 书库（34 MB）
│
├── .claude/             # Claude AI 配置
├── .gitignore          # Git 忽略配置
├── README.md           # 项目说明
├── setup.py            # 环境安装脚本
├── requirements.txt    # 根级依赖（如有）
└── PROJECT_STRUCTURE.md # 本文件
```

## 主要变更

### 1. 前端目录
- **旧**：`fronted/fronted/`（拼写错误 + 嵌套）
- **新**：`frontend/`（标准命名 + 根层级）

### 2. 后端目录
- **旧**：所有代码混在 `backend/` 根目录
- **新**：
  - `backend/app/` - 核心业务代码
  - `backend/tests/` - 测试文件
  - `backend/docs/` - 后端文档

### 3. 文档整理
- **旧**：6 个 Markdown 文档散落在根目录
- **新**：集中到 `docs/` 目录，按类型分类

### 4. 脚本整理
- **旧**：`start_all_fixed.py`、`start_all_fixed.bat`、`diagnose.py` 在根目录
- **新**：统一移到 `scripts/` 目录
  - `start_all_fixed.py` → `scripts/start.py`
  - `start_all_fixed.bat` → `scripts/start.bat`
  - `diagnose.py` → `scripts/diagnose.py`

### 5. 数据文件
- **旧**：`书库1.xlsx` 在根目录
- **新**：`data/书库1.xlsx`

## 已更新的引用

以下文件中的路径引用已全部更新：

✅ `scripts/start.py` - 前端路径、项目根目录计算
✅ `scripts/start.bat` - 前端路径
✅ `README.md` - 所有路径引用
✅ `docs/deployment.md` - 部署说明
✅ `docs/colleague-deployment.md` - 同事部署说明
✅ `docs/api.md` - API 文档
✅ `docs/deepseek-setup.md` - DeepSeek 配置
✅ `docs/fixes/*.md` - 修复说明
✅ `backend/convert_xlsx.py` - 书库查找路径
✅ `backend/extract_covers.py` - 书库查找路径
✅ `backend/docs/*` - 后端文档
✅ `.gitignore` - 忽略规则更新

## 兼容性说明

### Python 相对导入
后端代码使用相对路径 `data/books.json`，不受影响。

### 启动脚本
- `scripts/start.py` 会自动定位项目根目录
- `scripts/start.bat` 使用 `%~dp0` 相对路径
- 所有脚本都已测试路径计算正确

### 数据查找脚本
`backend/convert_xlsx.py` 和 `backend/extract_covers.py` 会在以下位置查找书库：
1. 项目根目录：`书库1.xlsx`
2. data 目录：`data/书库1.xlsx`

## 启动方式

### 方式一：双击启动
```
scripts/start.bat
```

### 方式二：命令行
```bash
python scripts/start.py
```

### 方式三：分别启动
```bash
# 后端
cd backend/app
.venv\Scripts\python.exe main.py

# 前端
cd frontend
npm run dev
```

## 验证结果

✅ 所有目录结构正确
✅ 所有关键文件存在
✅ 旧目录已清理
✅ 路径引用已更新
✅ 前端依赖已安装
✅ 后端环境已配置

## 下一步

1. **启动项目**：`python scripts/start.py`
2. **访问应用**：http://127.0.0.1:5173
3. **API 文档**：http://localhost:8000/docs
