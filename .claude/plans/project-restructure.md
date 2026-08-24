# 项目结构重构计划

## 目标

将当前松散的项目结构整理成标准开源项目结构，提升可维护性和专业性。

## 当前问题

1. **前端目录问题**：`fronted/fronted` 拼写错误 + 嵌套目录
2. **后端结构松散**：所有代码混在 backend/ 根目录，缺少 app/、tests/ 等标准目录
3. **文档分散**：6 个 Markdown 文档散落在项目根目录
4. **脚本位置混乱**：启动脚本在根目录而非 scripts/
5. **数据文件位置不当**：`书库1.xlsx` 应在 data/ 目录

## 重构方案

### 1. 前端目录重命名与移动

**操作：**
```bash
mv fronted/fronted frontend
```

**影响范围：**
- 启动脚本：`start_all_fixed.py`、`start_all_fixed.bat`
- 文档中的路径引用：`README.md`、所有 `*.md` 文档

### 2. 后端目录重组

**目标结构：**
```
backend/
├── app/                    # 主要业务代码
│   ├── __init__.py
│   ├── main.py            # FastAPI 主应用
│   ├── config.py          # 配置管理
│   └── ... (其他核心代码)
├── tests/                  # 后端测试
│   ├── __init__.py
│   ├── test_backend.py
│   ├── test_assistant.py
│   ├── test_deepseek.py
│   └── test_markdown.py
├── data/                   # JSON 数据（保持不变）
├── covers/                 # 封面图片（保持不变）
├── requirements.txt        # 依赖（保持在根目录）
└── 可选：docs/            # 后端文档
    ├── ALGORITHM.md
    ├── API.md
    └── SUMMARY.md
```

**影响范围：**
- Python 模块导入路径（内部相对导入不受影响）
- 启动脚本中的 cwd 设置
- 数据文件相对路径（使用 `data/books.json`，不受影响）

### 3. 文档整理到 docs/

**移动文件：**
```bash
mkdir -p docs/fixes
mv README.md docs/ (或保留在根目录)
mv DEEPSEEK配置完成.md docs/
mv 部署说明.md docs/deployment.md
mv 同事部署说明.md docs/
mv 灵犀助手API说明.md docs/api.md
mv 修复说明-滚动穿透.md docs/fixes/scroll-lock.md
mv 修复说明-详情弹窗定位.md docs/fixes/detail-dialog-position.md
```

**注意：** `README.md` 可以保留在根目录（标准做法），其他文档移到 `docs/`

### 4. 脚本整理到 scripts/

**移动文件：**
```bash
mkdir -p scripts
mv start_all_fixed.py scripts/start.py
mv start_all_fixed.bat scripts/start.bat
mv diagnose.py scripts/diagnose.py
```

### 5. 数据文件整理

**移动文件：**
```bash
mkdir -p data
mv 书库1.xlsx data/
```

### 6. 更新所有路径引用

**需要更新的文件：**

1. **启动脚本：**
   - `scripts/start.py`：更新 `FRONTEND_DIR` 路径
   - `scripts/start.bat`：更新前端路径

2. **文档文件（所有包含路径引用的）：**
   - `README.md`（根目录）
   - `docs/deployment.md`
   - `docs/colleague-deployment.md`
   - `docs/api.md`
   - `docs/DEEPSEEK配置完成.md`
   - `修复说明-*.md` → `docs/fixes/`

3. **后端脚本（引用书库路径）：**
   - `backend/convert_xlsx.py`：更新 `书库1.xlsx` 路径
   - `backend/extract_covers.py`：更新路径引用

4. **.gitignore：**
   - 更新忽略规则以适应新结构

## 实施步骤

### 阶段 1：创建新目录结构
1. 创建 `frontend/`（从 fronted/fronted 移动）
2. 创建 `backend/app/`、`backend/tests/`
3. 创建 `docs/`、`docs/fixes/`
4. 创建 `scripts/`、`data/`

### 阶段 2：移动文件
按上述方案移动所有文件

### 阶段 3：更新路径引用
批量更新所有包含旧路径的文件

### 阶段 4：测试验证
1. 运行 `scripts/diagnose.py` 验证环境
2. 运行 `scripts/start.py` 验证启动
3. 运行后端测试：`cd backend && python -m pytest tests/`
4. 前端构建测试：`cd frontend && npm run build`

## 注意事项

1. **相对路径**：后端代码使用 `data/books.json` 相对路径，不受影响
2. **绝对路径**：启动脚本使用绝对路径计算，只需更新常量
3. **Git 历史**：移动文件会保留 Git 历史（git mv）
4. **备份建议**：建议先提交当前状态，再执行重构

## 预期收益

✅ 标准开源项目结构
✅ 清晰的代码组织
✅ 文档集中管理
✅ 易于团队协作
✅ 便于 CI/CD 配置
