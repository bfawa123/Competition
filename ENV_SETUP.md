# ============================================
# 知遇 AI 馆员 - .env 配置说明
# ============================================

## 快速配置指南

### 1. 选择你的 LLM 服务商

#### 选项 A：OpenAI（推荐）
**优点**：
- 速度快
- 稳定性高
- 中文支持好

**配置步骤**：
1. 访问 https://platform.openai.com/api-keys
2. 登录/注册 OpenAI 账号
3. 创建 API Key
4. 复制到下方配置

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

**国内用户**：建议配置代理（见下方）

---

#### 选项 B：Anthropic Claude
**优点**：
- 长上下文（200K）
- 推理能力强

**配置步骤**：
1. 访问 https://console.anthropic.com/settings/keys
2. 登录/注册 Anthropic 账号
3. 创建 API Key
4. 复制到下方配置

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
```

---

### 2. 国内用户：配置代理（重要！）

如果不配置代理，国内访问 OpenAI/Anthropic 可能会：
- 非常慢（>10秒）
- 连接超时
- IP 被封禁

#### OpenAI 代理推荐

**免费代理**：
```env
# ChatAnywhere（需要注册）
OPENAI_BASE_URL=https://api.chatanywhere.tech/v1
OPENAI_API_KEY=你的代理API密钥
```

**自建代理**：
```env
# 如果你有自己的代理服务器
OPENAI_BASE_URL=https://your-server.com/v1
OPENAI_API_KEY=你的密钥
```

#### Anthropic 代理

Anthropic 目前国内访问较难，建议使用中转服务：
```env
# 第三方中转服务
ANTHROPIC_BASE_URL=https://your-anthropic-proxy.com
ANTHROPIC_API_KEY=你的密钥
```

---

### 3. 验证配置

配置完成后，运行测试：

```bash
# 启动服务
python main.py

# 测试推荐接口
curl -X POST http://localhost:8000/api/agent/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": {
      "goal": "machine_learning",
      "difficulty": "beginner",
      "time_per_day": 30,
      "language": "zh"
    },
    "user_id": "test_user"
  }'
```

---

## 完整配置示例

### 示例 1：使用 OpenAI + 代理（国内推荐）
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.chatanywhere.tech/v1
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
PORT=8000
DEBUG=true
MEMORY_TOP_K=5
MEMORY_SIMILARITY_THRESHOLD=0.7
```

### 示例 2：使用 Anthropic（国外用户）
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-sonnet-20240229
PORT=8000
DEBUG=true
```

### 示例 3：混合配置（备选方案）
```env
# 主服务：OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
LLM_PROVIDER=openai

# 备选：Anthropic（当 OpenAI 不可用时）
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 常见问题

### Q1: 如何获取 OpenAI API 密钥？
**A**：访问 https://platform.openai.com/api-keys → 登录 → Create new secret key

### Q2: OpenAI API 收费吗？
**A**：收费，但很便宜：
- GPT-3.5-turbo: ~0.5元/1000次推荐
- GPT-4o-mini: ~1元/1000次推荐
- Embedding（本地运行，免费）

### Q3: 国内访问 OpenAI 很慢怎么办？
**A**：
1. 配置代理（见上方）
2. 或使用国内替代方案（如文心一言、通义千问）
3. 或联系我帮你配置国内模型

### Q4: 可以不用 LLM 吗？
**A**：理论上可以，但会失去记忆压缩和自然语言生成能力。对于比赛，建议至少配置一个。

### Q5: 配置后提示 "API key not configured"？
**A**：
1. 检查 .env 文件名是否正确（不是 .env.txt）
2. 检查 API 密钥是否完整复制
3. 检查是否有语法错误（如多余空格）

### Q6: 推荐接口一直超时？
**A**：
1. 检查网络连接
2. 增加 LLM_TIMEOUT 值（如 60）
3. 检查 LLM 服务商状态
4. 尝试切换服务商

---

## 成本估算

### 按推荐次数计算

| LLM 模型 | 单次推荐成本 | 1000次成本 |
|---------|------------|----------|
| GPT-3.5-turbo | ~0.001元 | ~1元 |
| GPT-4o-mini | ~0.002元 | ~2元 |
| Claude-3-Sonnet | ~0.003元 | ~3元 |

**Embedding**：本地运行，免费

**总计**：比赛期间（24小时）预计 < 10元

---

## 下一步

配置完成后：
1. ✅ 运行 `python start.py`
2. ✅ 测试 `python test_backend.py`
3. ✅ 访问 http://localhost:8000/docs
4. ✅ 测试推荐接口
5. ✅ 准备演示数据

需要帮助？随时问我！
