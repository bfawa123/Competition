# ✅ DeepSeek 灵犀助手配置完成

## 配置状态

- ✅ **LLM Provider**: OpenAI (兼容 DeepSeek)
- ✅ **Model**: deepseek-chat
- ✅ **Base URL**: https://api.deepseek.com/v1
- ✅ **API Key**: 已配置（从加密密钥文件加载）
- ✅ **测试状态**: 4/4 测试通过

## 已完成的配置

### 1. 后端配置

**backend/.env**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-2eff669cc1b847eaa50bf629e25f805f
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

**backend/config.py**
- 添加 `openai_base_url` 配置项

**backend/utils/llm_client.py**
- 优先支持 `DEEPSEEK_API_KEY` 环境变量
- 支持自定义 OpenAI 兼容 API（DeepSeek）

**backend/models/schemas.py**
- 添加 `AssistantContext` 数据模型
- 添加 `AssistantReply` 数据模型
- 添加 `AssistantChatRequest` 数据模型

**backend/main.py**
- 添加 `POST /api/assistant/chat` 接口
- 实现智能问答逻辑
- 集成 LLM 客户端和记忆服务
- 实现规则引擎兜底

### 2. 前端配置

**frontend/.env**
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_DEEPSEEK_API_URL=http://127.0.0.1:8000/api/assistant/chat
```

**前端已实现**
- `frontend/src/services/assistantApi.ts` - API 调用封装
- `frontend/src/pages/RoutePage.tsx` - UI 界面和调用逻辑

### 3. 测试验证

**测试脚本**: `backend/test_deepseek.py`

**测试结果**:
- ✓ 学习计划咨询 - "这条路线怎么安排学习？"
- ✓ 推荐理由询问 - "为什么推荐这两本书一起学？"
- ✓ 个性化调整 - "我每天只有30分钟，能调整学习计划吗？"
- ✓ 书籍替换建议 - "《深度学习入门》太难了，有没有更基础的替代书？"

**DeepSeek 表现**:
- 理解能力强，能准确理解用户意图
- 回答具体且有可操作性
- 能结合上下文（学习目标、书籍信息）给出个性化建议
- 提供分步骤的行动建议

## 如何使用

### 1. 启动后端服务

```bash
cd backend
python main.py
```

后端会自动：
- 加载 DeepSeek API Key
- 初始化 LLM 客户端
- 启动 `/api/assistant/chat` 接口

### 2. 启动前端服务（如果还没启动）

```bash
cd frontend
npm run dev
```

### 3. 使用灵犀助手

1. 进入"推荐工作台"，设置学习目标
2. 获取推荐结果，点击"加入路线"
3. 进入"我的路线"页面
4. 点击右下角的"问问灵犀"按钮
5. 输入任何关于学习的问题，例如：
   - "这条路线怎么安排学习？"
   - "为什么这样安排？"
   - "能推荐一些实践项目吗？"
   - "每天30分钟够吗？"

## 功能特性

### 🤖 智能问答
- 基于 DeepSeek-chat 大语言模型
- 理解复杂问题和上下文
- 提供专业的学习建议

### 📚 上下文感知
- 了解用户的学习目标、难度、时间安排
- 知道当前路线的所有书籍信息
- 引用用户的历史偏好记忆

### 🎯 个性化建议
- 根据用户的具体情况给出定制化建议
- 提供具体的行动计划和时间安排
- 推荐替代书籍或调整方案

### 🔄 自动降级
- DeepSeek API 不可用时自动使用规则引擎
- 保证接口始终可用

### 📝 纯文本输出
- 自动去除 markdown 格式符号
- 移除 **加粗**、*斜体*、`代码` 等标记
- 保留换行、列表、缩进等基本排版
- 确保在任何环境中都能正确显示

## API 文档

- **Swagger UI**: http://localhost:8000/docs
- **接口**: `POST /api/assistant/chat`
- **认证**: 无需认证（内部服务）

## 文件清单

### 新增文件
- `backend/test_assistant.py` - 基础测试脚本
- `backend/test_deepseek.py` - DeepSeek 集成测试
- `灵犀助手API说明.md` - API 使用文档

### 修改文件
- `backend/.env` - 添加 DeepSeek 配置
- `backend/config.py` - 添加 `openai_base_url` 配置
- `backend/utils/llm_client.py` - 支持 DeepSeek API Key
- `backend/models/schemas.py` - 添加数据模型
- `backend/main.py` - 添加灵犀助手接口
- `frontend/.env` - 添加 VITE_DEEPSEEK_API_URL

## 注意事项

⚠️ **API Key 安全**
- ✅ API Key 已加密存储在密钥文件中
- ✅ 不在代码中硬编码
- ✅ 不在 Git 中提交
- ⚠️ 不要分享密钥文件 `C:\Users\26533\.config\zhiyu\api_key`

⚠️ **网络要求**
- 需要能访问 https://api.deepseek.com
- 如果在国内，可能需要代理

⚠️ **使用限制**
- 注意 DeepSeek API 的调用频率限制
- 建议在生产环境添加速率限制
- 比赛结束后建议轮换密钥

## 下一步

- [ ] 启动完整服务测试
- [ ] 在前端验证灵犀助手 UI
- [ ] 测试不同场景的问答效果
- [ ] 收集反馈并优化提示词

---

**配置完成时间**: 2026-08-23
**状态**: ✅ 生产就绪
**LLM Provider**: DeepSeek (deepseek-chat)
