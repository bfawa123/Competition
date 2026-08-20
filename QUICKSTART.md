# 知遇AI馆员 - 快速开始指南

## 5分钟启动

### 1. 安装依赖

```bash
# 方法1: 使用 start.py（推荐）
python start.py

# 方法2: 手动安装
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env，填入你的 API 密钥
```

**必需配置**（至少一个）：
```env
# OpenAI（推荐，速度最快）
OPENAI_API_KEY=sk-...

# 或 Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
```

**可选配置**：
```env
LLM_PROVIDER=openai  # openai 或 anthropic
LLM_MODEL=gpt-3.5-turbo  # 或 claude-3-sonnet-20240229
```

### 3. 启动服务

```bash
python main.py
# 或
uvicorn main:app --reload --port 8000
```

### 4. 测试

打开浏览器访问：
- **Swagger UI**: http://localhost:8000/docs
- **测试页面**: 直接在 Swagger UI 中测试所有接口

或在终端测试：
```bash
# 健康检查
curl http://localhost:8000/

# 搜索书目
curl http://localhost:8000/api/books/search?topic=machine_learning

# 获取推荐（需要配置LLM）
curl -X POST http://localhost:8000/api/agent/recommend \
  -H "Content-Type: application/json" \
  -d '{"user_input":{"goal":"machine_learning","difficulty":"beginner","time_per_day":30,"language":"zh"},"user_id":"test"}'
```

---

## 测试脚本

```bash
# 运行基础测试（不依赖LLM）
python test_backend.py
```

测试覆盖：
- ✓ 模块导入
- ✓ 数据库读写
- ✓ 书目检索
- ✓ 推荐引擎
- ✓ API端点

---

## 核心接口速查

### 1. 推荐接口（最重要）
```http
POST /api/agent/recommend
{
  "user_input": {"goal": "xxx", "difficulty": "xxx", "time_per_day": 30, "language": "zh"},
  "user_id": "xxx"
}
```

### 2. 写入记忆
```http
POST /api/memory/write
{
  "user_id": "xxx",
  "feedback": "用户反馈文本"
}
```

### 3. 检索记忆
```http
GET /api/memory/retrieve?query=xxx&user_id=xxx
```

### 4. 搜索书目
```http
GET /api/books/search?topic=xxx&difficulty=xxx
```

### 5. 前后对比（评委演示）
```http
GET /api/demo/compare/user_xxx
```

---

## 数据文件

### 书目数据
- **位置**: `data/books.json`
- **数量**: 初始10本，可扩展到60-80本
- **格式**: 见 `data/books.json`

### 记忆数据
- **位置**: `data/memories.json`
- **格式**: 按 user_id 组织
- **自动创建**: 首次写入时

### Embedding 缓存
- **位置**: `data/embeddings_cache.json`
- **作用**: 缓存向量检索结果，加速查询
- **自动创建**: 首次检索时

---

## 开发调试

### 查看日志
```bash
uvicorn main:app --reload --log-level debug
```

### 修改配置
编辑 `config.py` 或 `.env`

### 添加书目
直接编辑 `data/books.json`，或调用接口扩展

---

## 常见问题

### Q1: 提示 "OpenAI API key not configured"
**解决**: 在 `.env` 文件中配置 `OPENAI_API_KEY`

### Q2: 提示 "Failed to parse LLM output"
**解决**: 这是记忆压缩时的降级处理，不影响功能，但会降低记忆质量

### Q3: Embedding 模型下载慢
**解决**: 首次运行会自动下载，约100MB。可配置镜像或手动下载

### Q4: 推荐结果重复
**解决**: 检查记忆系统中是否有 `rejection_penalty` 生效

### Q5: 内存占用高
**解决**: `sentence-transformers` 模型约500MB，是正常的

---

## 部署检查清单

- [ ] `.env` 文件已配置 API 密钥
- [ ] `data/books.json` 已填充60-80本书
- [ ] `test_backend.py` 测试通过
- [ ] Swagger UI 可以访问
- [ ] 推荐接口返回结果
- [ ] 记忆可以写入和读取
- [ ] 前后对比接口正常

---

## 下一步

1. **填充书目数据**: 扩展到60-80本，覆盖多个主题
2. **准备演示场景**: 5-10个模拟用户的完整流程
3. **优化记忆压缩**: 调整 Prompt 提升记忆质量
4. **完善前端**: 实现推荐展示、记忆管理等页面

---

## 项目结构

```
backend/
├── main.py                    # FastAPI 入口（最重要的文件）
├── config.py                  # 配置管理
├── start.py                   # 快速启动脚本
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量示例
├── test_backend.py           # 测试脚本
├── README.md                 # 项目说明
├── API.md                    # API文档
│
├── models/                   # 数据模型
│   ├── schemas.py           # Pydantic 模型
│   └── database.py          # JSON数据库
│
├── services/                 # 业务逻辑
│   ├── book_service.py      # 书目检索
│   ├── memory_service.py    # 记忆管理（核心）
│   ├── agent.py             # Agent决策（核心）
│   └── recommender.py       # 推荐引擎
│
├── data/                     # 数据文件
│   ├── books.json           # 书目数据
│   └── memories.json        # 记忆存储（自动生成）
│
└── utils/                    # 工具函数
    ├── llm_client.py        # LLM封装
    ├── embedding.py         # 向量检索
    └── scorer.py            # 评分计算
```

---

## 技术支持

遇到问题？检查：
1. API密钥是否正确
2. 依赖版本是否兼容
3. 数据文件是否存在
4. 查看 `API.md` 接口文档

祝开发顺利！🎉
