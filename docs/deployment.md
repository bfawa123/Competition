# 灵犀 AI 馆员 - 部署说明

本文档说明如何部署和运行灵犀 AI 馆员项目。

## 环境要求

- Python 3.10+（建议 3.11/3.12）
- Node.js 18+（建议 20 LTS）
- Windows 10/11

## 快速开始

### 方式一：使用启动脚本（推荐）

双击运行 `scripts/start.bat`，脚本会自动：

1. 检测并创建 Python 虚拟环境
2. 安装后端依赖
3. 安装前端依赖
4. 启动后端（端口 8000）和前端（端口 5173）

访问 http://127.0.0.1:5173 使用应用。

### 方式二：命令行启动

**同时启动前后端：**

```bash
python scripts/start.py
```

**分别启动：**

```bash
# 终端 1：后端
cd backend/app
.venv\Scripts\python.exe main.py

# 终端 2：前端
cd frontend
npm run dev
```

## 项目结构

```
灵犀0.15-修复详情弹窗/
├── frontend/          # React 前端
├── backend/           # FastAPI 后端
│   ├── app/          # 核心业务代码（main.py, config.py）
│   ├── tests/        # 测试文件
│   ├── services/     # 业务服务层
│   ├── models/       # 数据模型
│   ├── utils/        # 工具函数
│   ├── data/         # JSON 数据文件
│   └── covers/       # 书籍封面图片
├── scripts/          # 启动脚本（start.py, start.bat, diagnose.py）
├── docs/             # 项目文档
├── data/             # 原始数据文件（书库1.xlsx）
└── setup.py          # 环境安装脚本
```

## 测试

```bash
# 后端测试
cd backend
.venv\Scripts\python.exe -m pytest tests/

# 前端测试
cd frontend
npm test
```

## 常见问题

### 1. start.bat 提示找不到 setup.py

**原因：** `scripts/start.bat` 使用相对路径 `%~dp0..\setup.py` 查找项目根目录的 `setup.py`。

**解决：** 确保 `start.bat` 位于 `scripts/` 目录，且 `setup.py` 在项目根目录。

### 2. 提示找不到 Python / npm

- 检查安装时是否勾选了 "添加到 PATH"。
- 打开新的终端窗口再试。

### 3. `npm install` 很慢或失败

```bash
npm config set registry https://registry.npmmirror.com
npm install
```

### 4. pip 安装失败

```bash
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 端口被占用

修改 `backend/config.py` 里的端口设置。
