# 灵犀学习助手 API 使用说明

## 概述

灵犀学习助手（`/api/assistant/chat`）是知遇 AI 馆员的智能问答接口，用于在"我的路线"页面为用户提供个性化的学习建议。

## 接口信息

- **Endpoint**: `POST /api/assistant/chat`
- **功能**: 结合用户上下文回答学习相关问题
- **文档**: http://localhost:8000/docs （Swagger UI 自动生成）

## 请求格式

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
        "book": {
          "id": 1,
          "title": "机器学习实战",
          "topic": "machine_learning",
          "difficulty": "beginner",
          "pages": 350,
          "language": "zh",
          "keywords": ["Scikit-learn", "监督学习"]
        },
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

## 响应格式

```json
{
  "answer": "根据你的学习目标，建议...（灵犀助手的回答）"
}
```

## 核心功能

### 1. 上下文感知
灵犀助手会结合以下信息生成回答：
- 用户的学习目标和偏好
- 当前路线中的书籍信息
- 用户的历史偏好记忆

### 2. LLM 智能回答
如果配置了 OpenAI 或 Anthropic API Key，灵犀助手会调用 LLM 生成专业、个性化的回答。

### 3. 自动降级
如果 LLM 不可用，灵犀助手会自动切换到规则引擎，根据关键词匹配返回预设的兜底回复。

## 配置 LLM

### OpenAI 配置
在 `backend/.env` 文件中添加：
```env
OPENAI_API_KEY=sk-your-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

### Anthropic 配置
在 `backend/.env` 文件中添加：
```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-haiku-20240307
```

## 使用示例

### cURL 测试

```bash
curl -X POST http://localhost:8000/api/assistant/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "这条路线怎么安排学习？",
    "context": {
      "userName": "测试用户",
      "input": {
        "goal": "machine_learning",
        "difficulty": "beginner",
        "time_per_day": 30,
        "language": "zh"
      },
      "books": [],
      "currentPage": "route"
    }
  }'
```

### Python 调用

```python
import requests

response = requests.post(
    "http://localhost:8000/api/assistant/chat",
    json={
        "question": "为什么这样安排？",
        "context": {
            "userName": "张三",
            "input": {...},
            "books": [...],
            "currentPage": "route"
        }
    }
)

answer = response.json()["answer"]
print(answer)
```

### JavaScript 调用

```javascript
const response = await fetch('http://localhost:8000/api/assistant/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "路线太难了，能调整吗？",
    context: { ... }
  })
});

const { answer } = await response.json();
```

## 兜底回复逻辑

当 LLM 不可用时，灵犀助手会根据问题关键词自动匹配不同的兜底回复：

### 1. 学习顺序问题
触发关键词：`顺序`、`怎么学`、`计划`
返回：建议的学习顺序和预计时间

### 2. 调整难度问题
触发关键词：`太难`、`调整`、`修改`
返回：调整难度的具体建议

### 3. 原因解释问题
触发关键词：`为什么`
返回：路线设计的理由和逻辑

### 4. 通用问题
其他所有问题
返回：路线概览和调整建议

## 测试

运行自动化测试：
```bash
cd backend
python test_assistant.py
```

测试覆盖：
- ✓ 接口基本功能（兜底回复）
- ✓ 空书籍列表场景
- ✓ 不同问题类型的响应

## 前端配置

在前端的 `fronted/fronted/.env` 文件中添加：
```env
VITE_DEEPSEEK_API_URL=http://127.0.0.1:8000/api/assistant/chat
```

前端已经在 `src/services/assistantApi.ts` 中实现了调用逻辑。

## API 文档

FastAPI 会自动生成交互式 API 文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

启动后端服务后，可以直接在浏览器中测试接口。

## 注意事项

1. **API Key 安全**: API Key 必须放在后端 `.env` 文件，不能写入前端环境变量
2. **数据库初始化**: 调用此接口前需要先初始化数据库（`init_db()`）
3. **记忆检索**: 接口会自动调用记忆服务检索相关记忆，需要确保记忆服务正常运行
4. **降级策略**: 无 LLM 时自动使用规则引擎，保证接口始终可用

## 技术实现

- **后端框架**: FastAPI
- **数据验证**: Pydantic 模型（`AssistantChatRequest`、`AssistantReply`）
- **LLM 调用**: 复用现有 `LLMClient`（支持 OpenAI 和 Anthropic）
- **记忆集成**: 通过 `memory_service.retrieve_memory()` 获取用户历史偏好
- **降级策略**: 捕获 LLM 异常，调用 `_generate_fallback_answer()` 生成规则回复

## 文件清单

### 新增/修改文件
- ✓ `backend/models/schemas.py` - 添加 `AssistantContext`、`AssistantReply`、`AssistantChatRequest` 数据模型
- ✓ `backend/main.py` - 添加 `/api/assistant/chat` 路由和 `_generate_fallback_answer()` 兜底逻辑
- ✓ `backend/API.md` - 更新接口文档，添加灵犀助手 API 说明
- ✓ `backend/test_assistant.py` - 添加自动化测试脚本
- ✓ `灵犀助手API说明.md` - 本使用说明文档

### 未修改文件（已实现功能）
- ✓ `fronted/fronted/src/services/assistantApi.ts` - 前端 API 调用封装（已存在）
- ✓ `fronted/fronted/src/pages/RoutePage.tsx` - 前端 UI 和调用逻辑（已存在）

## 开发记录

- 2026-08-23: 实现灵犀助手 API 接口
  - 添加数据模型定义
  - 实现 POST /api/assistant/chat 路由
  - 集成 LLM 客户端和记忆服务
  - 实现规则引擎兜底回复
  - 添加自动化测试
  - 更新 API 文档
