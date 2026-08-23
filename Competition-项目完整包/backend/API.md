# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 文档**: http://localhost:8000/docs
- **格式**: JSON

## 接口列表

### 1. 健康检查

```http
GET /
```

**响应**：
```json
{
  "service": "知遇 AI 馆员",
  "version": "1.0.0",
  "status": "running"
}
```

---

### 2. 获取推荐（核心接口）

```http
POST /api/agent/recommend
```

**请求体**：
```json
{
  "user_input": {
    "goal": "machine_learning",
    "difficulty": "beginner",
    "time_per_day": 30,
    "language": "zh",
    "additional_constraints": "偏好中文案例"
  },
  "user_id": "user_123"
}
```

**响应**：
```json
{
  "books": [
    {
      "book": {
        "id": 1,
        "title": "机器学习实战",
        "topic": "machine_learning",
        "difficulty": "beginner",
        "pages": 350,
        "language": "zh",
        "case_ratio": 0.7,
        "theory_ratio": 0.3,
        "prerequisites": ["Python基础"],
        "goals": ["入门机器学习", "实战项目"],
        "keywords": ["Scikit-learn", "监督学习", "Kaggle"],
        "availability": true
      },
      "total_score": 85.5,
      "topic_score": 1.0,
      "difficulty_score": 1.0,
      "time_score": 0.7,
      "preference_score": 0.8,
      "explanation": "✓ 主题匹配：machine_learning；✓ 难度合适：beginner；✓ 符合偏好"
    }
  ],
  "memories_used": [
    {
      "id": "mem_abc123",
      "type": "preference",
      "field": "language",
      "value": "prefer_chinese",
      "confidence": 0.9,
      "source": "用户反馈: 偏好中文"
    }
  ],
  "explanation": "根据您的偏好，推荐以下书籍...",
  "agent_trace": [
    {"action": "retrieve_memory", "details": {"query": "machine_learning", "user_id": "user_123"}},
    {"action": "search_books", "details": {"topic": "machine_learning"}},
    {"action": "recommend", "details": {"candidates": 5}}
  ]
}
```

---

### 3. 写入记忆

```http
POST /api/memory/write
```

**请求体**：
```json
{
  "user_id": "user_123",
  "feedback": "这本书太厚了，我每天只有30分钟",
  "context": {
    "current_book_id": 1,
    "current_book_title": "机器学习实战"
  }
}
```

**响应**：
```json
{
  "success": true,
  "memory": {
    "id": "mem_xyz789",
    "user_id": "user_123",
    "type": "preference",
    "field": "pages",
    "value": "prefer_short",
    "confidence": 0.9,
    "source": "这本书太厚了，我每天只有30分钟",
    "created_at": "2025-08-20T10:30:00"
  },
  "message": "记忆已保存：pages = prefer_short"
}
```

---

### 4. 检索记忆

```http
GET /api/memory/retrieve?query=机器学习入门&user_id=user_123&top_k=5
```

**响应**：
```json
{
  "query": "机器学习入门",
  "user_id": "user_123",
  "memories": [
    {
      "id": "mem_abc123",
      "user_id": "user_123",
      "type": "preference",
      "field": "language",
      "value": "prefer_chinese",
      "confidence": 0.9,
      "source": "用户反馈: 偏好中文",
      "created_at": "2025-08-20T10:30:00",
      "last_used": "2025-08-20T11:00:00",
      "usage_count": 3
    }
  ]
}
```

---

### 5. 获取所有记忆

```http
GET /api/memory/list/user_123
```

**响应**：
```json
{
  "user_id": "user_123",
  "memories": [...]
}
```

---

### 6. 删除记忆

```http
DELETE /api/memory/user_123/mem_abc123
```

**响应**：
```json
{
  "success": true,
  "message": "记忆已删除"
}
```

---

### 7. 检索书目

```http
GET /api/books/search?topic=machine_learning&difficulty=beginner&language=zh&max_pages=300
```

**参数**：
- `topic`（可选）：主题筛选
- `difficulty`（可选）：难度筛选（beginner/intermediate/advanced）
- `language`（可选）：语言筛选（zh/en）
- `max_pages`（可选）：最大页数
- `min_case_ratio`（可选）：最小案例占比（0-1）
- `availability`（可选）：馆藏状态（默认 true）

**响应**：
```json
{
  "count": 3,
  "books": [...]
}
```

---

### 8. 获取单本书

```http
GET /api/books/1
```

**响应**：
```json
{
  "id": 1,
  "title": "机器学习实战",
  ...
}
```

---

### 9. 前后对比演示（评委用）

```http
GET /api/demo/compare/user_123
```

**响应**：
```json
{
  "user_id": "user_123",
  "feedback": "这本书太厚了，我每天只有30分钟",
  "memory_saved": {
    "id": "mem_xyz789",
    "type": "preference",
    "field": "pages",
    "value": "prefer_short",
    ...
  },
  "first_recommendation": {
    "books": [...],
    "explanation": "...",
    "memories_used": 0
  },
  "second_recommendation": {
    "books": [...],
    "explanation": "...",
    "memories_used": 1
  },
  "comparison": {
    "memory_added": "pages",
    "impact": "推荐结果已根据反馈调整"
  }
}
```

---

### 10. Agent 轨迹

```http
GET /api/agent/trace/user_123
```

**响应**：
```json
{
  "user_id": "user_123",
  "trace": [
    {
      "action": "retrieve_memory",
      "details": {"query": "machine_learning", "user_id": "user_123"},
      "timestamp": "now"
    },
    {
      "action": "search_books",
      "details": {"topic": "machine_learning"},
      "timestamp": "now"
    }
  ]
}
```

---

### 11. 灵犀学习助手（智能问答）

```http
POST /api/assistant/chat
```

**请求体**：
```json
{
  "question": "这条路线怎么安排学习？",
  "context": {
    "userName": "张三",
    "input": {
      "goal": "machine_learning",
      "difficulty": "beginner",
      "time_per_day": 30,
      "language": "zh"
    },
    "books": [
      {
        "book": { ... },
        "total_score": 85.5,
        "topic_score": 1.0,
        "difficulty_score": 1.0,
        "time_score": 0.7,
        "preference_score": 0.8,
        "explanation": "..."
      }
    ],
    "currentPage": "route"
  }
}
```

**参数说明**：
- `question`：用户的问题
- `context.userName`：当前用户名称
- `context.input`：用户的学习目标设置
- `context.books`：当前学习路线中的书籍列表
- `context.currentPage`：当前页面标识（route/recommend/compare）

**响应**：
```json
{
  "answer": "根据你的学习目标，建议...（纯文本，无markdown格式）"
}
```

**说明**：
- 返回的文本已自动去除 markdown 格式
- **加粗**、*斜体*、`代码`等符号会被移除
- 保留换行、列表、缩进等基本排版
- 确保在纯文本环境中也能正确显示

**功能特点**：
- 🤖 结合用户上下文智能回答
- 📚 了解当前学习路线的所有书籍
- 🧠 引用用户历史偏好记忆
- 💡 提供个性化的学习建议
- 🔄 LLM 不可用时自动降级到规则回复

**使用场景**：
- 在"我的路线"页面询问学习建议
- 询问为什么这样安排学习路线
- 询问如何调整学习计划
- 询问书籍的阅读顺序

---

## 使用示例

### 完整推荐流程

```bash
# 1. 健康检查
curl http://localhost:8000/

# 2. 获取推荐
curl -X POST http://localhost:8000/api/agent/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "goal": "machine_learning",
      "difficulty": "beginner",
      "time_per_day": 30,
      "language": "zh"
    },
    "user_id": "user_demo"
  }'

# 3. 用户反馈
curl -X POST http://localhost:8000/api/memory/write \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_demo",
    "feedback": "偏好中文书籍"
  }'

# 4. 再次推荐（会自动引用记忆）
curl -X POST http://localhost:8000/api/agent/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "goal": "machine_learning",
      "difficulty": "beginner",
      "time_per_day": 30,
      "language": "zh"
    },
    "user_id": "user_demo"
  }'

# 5. 查看记忆
curl http://localhost:8000/api/memory/list/user_demo
```

---

## 错误码

| 状态码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 注意事项

1. **LLM 配置**：推荐接口需要配置 OpenAI 或 Anthropic API 密钥
2. **Embedding 模型**：首次运行会自动下载 `sentence-transformers` 模型（~100MB）
3. **数据持久化**：记忆存储在 `data/memories.json`，书目在 `data/books.json`
