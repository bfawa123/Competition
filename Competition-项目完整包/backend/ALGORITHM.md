# 算法与实现详解

## 1. 记忆压缩算法

### 核心流程
```
用户反馈 → LLM压缩 → 结构化记忆 → Embedding → 向量存储
```

### LLM Prompt 设计
**位置**: `services/memory_service.py::_compress_feedback()`

**关键设计要点**：
1. **Type 分类**：
   - `fixed_profile`: 硬约束（如"我每天只有30分钟"）
   - `preference`: 软偏好（如"我喜欢中文"）
   - `task_feedback`: 特定任务反馈（如"这本书太难"）

2. **Field 映射**：
   - `time` → 时间约束
   - `difficulty` → 难度偏好
   - `language` → 语言偏好
   - `pages` → 页数偏好
   - `format` → 书籍格式偏好

3. **Confidence 置信度**：
   - 根据反馈明确程度给出 0.5-1.0
   - 明确反馈（如"我每天只有30分钟"）→ 0.9+
   - 模糊反馈（如"这本书还行"）→ 0.5-0.7

### 降级策略
如果 LLM 解析失败，会降级为简单规则：
```python
return {
    "type": "preference",
    "field": "general",
    "value": feedback[:50],
    "confidence": 0.5
}
```

---

## 2. 向量检索算法

### 核心流程
```
查询文本 → Embedding → 余弦相似度 → Top-K 记忆
```

### Embedding 模型
**位置**: `utils/embedding.py`

**推荐模型**：
- `paraphrase-multilingual-MiniLM-L12-v2`（多语言，推荐）
- `all-MiniLM-L6-v2`（英文，更快）

**原因**：
- 轻量（~100MB），适合24小时开发
- 多语言支持，中英文均可
- 速度快，单条 < 50ms

### 相似度计算
```python
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)
```

### 加权机制
```python
weighted_score = similarity * memory.confidence
```

**为什么加权**：
- 高置信度记忆（明确反馈）获得更高优先级
- 避免模糊记忆干扰推荐

---

## 3. 推荐评分算法

### 评分公式
```
book_score = Σ(score_i * weight_i) - rejection_penalty

其中：
- topic_match * 30
- difficulty_match * 25
- time_match * 20
- preference_match * 20
- rejection_penalty * 100（如果被拒绝）
```

### 各维度评分逻辑

#### 3.1 主题匹配 (30分)
```python
# 精确匹配
if book.topic == user_goal: return 1.0

# 关键词匹配
keywords = goal_keywords.get(user_goal, [])
matches = 关键词命中数 / 总关键词数
return 0.7 + 0.3 * matches
```

**示例**：
- 用户目标："machine_learning"
- 书目关键词："Scikit-learn", "监督学习"
- 命中2个关键词 → score = 0.7 + 0.3 * 1.0 = 1.0

#### 3.2 难度匹配 (25分)
```python
difficulty_levels = {"beginner": 1, "intermediate": 2, "advanced": 3}

if 完全相同: return 1.0
elif 差一级: return 0.6
else: return 0.2
```

**设计理由**：
- 完全匹配得分最高
- 差一级（如 beginner → intermediate）仍有价值
- 差两级（beginner → advanced）风险较大

#### 3.3 时间匹配 (20分)
```python
daily_pages = time_per_day / 3  # 30分钟读10页
ideal_pages = book.pages / 14   # 14天读完

if daily_pages <= ideal_pages <= daily_pages * 1.5:
    return 1.0
elif 0.5 * daily_pages <= ideal_pages <= 1.5 * daily_pages:
    return 0.7
else:
    return 0.4
```

**设计理由**：
- 假设用户每天30分钟能读10页
- 推荐在14天内读完
- 给予0.5倍容错空间

#### 3.4 偏好匹配 (20分)
```python
score = 0.5  # 基础分

# 语言偏好
if book.language == user_language: score += 0.2

# 案例驱动偏好
if 有记忆偏好案例 and book.case_ratio >= 0.6: score += 0.15

# 理论偏好
if 有记忆偏好理论 and book.theory_ratio >= 0.6: score += 0.15

return clamp(score, 0, 1)
```

**设计理由**：
- 基础分 0.5 保证中立
- 语言偏好权重最高（0.2）
- 偏好只能加分，不能超过1.0

#### 3.5 拒绝惩罚 (-100分)
```python
def check_rejection(book, memories):
    for mem in memories:
        if mem.field in ["rejected_book", "too_thick", "too_difficult"]:
            if book.id in mem.value: return 1.0
            if book.title in mem.value: return 1.0
            if 关键词匹配: return 0.8
    return 0.0
```

**设计理由**：
- 直接惩罚（-100分）确保被拒绝的书不会出现在结果中
- 关键词匹配提供模糊惩罚（-80分）

---

## 4. Agent 决策流程

### 工具调用链
```
1. retrieve_memory(query, user_id)
   ↓
2. search_books(filters)
   ↓
3. recommend_books(candidates, memories)
   ↓
4. generate_explanation()  # LLM
```

### 轨迹记录
**位置**: `services/agent.py::_log_trace()`

每个步骤都会记录：
```python
{
    "action": "search_books",
    "details": {"topic": "machine_learning"},
    "timestamp": "2025-08-20T10:30:00Z"
}
```

**用途**：
- 调试推荐逻辑
- 向评委展示决策过程
- 问题排查

---

## 5. 数据模型设计

### 书目数据结构
```python
{
    "id": int,              # 唯一标识
    "title": str,           # 书名
    "topic": str,           # 主题（machine_learning, python, etc.）
    "difficulty": enum,     # 难度（beginner/intermediate/advanced）
    "pages": int,           # 页数
    "language": enum,       # 语言（zh/en）
    "case_ratio": float,    # 案例占比（0-1）
    "theory_ratio": float,  # 理论占比（0-1）
    "prerequisites": list,  # 前置知识
    "goals": list,          # 适用目标
    "keywords": list,       # 关键词
    "availability": bool,   # 馆藏状态
    "description": str      # 简介
}
```

### 记忆数据结构
```python
{
    "id": str,              # 唯一标识
    "user_id": str,         # 用户ID
    "type": enum,           # 类型（fixed_profile/preference/task_feedback）
    "field": str,           # 维度（difficulty/time/language/pages/...）
    "value": any,           # 值
    "confidence": float,    # 置信度（0-1）
    "source": str,          # 来源（原始反馈文本）
    "created_at": datetime, # 创建时间
    "last_used": datetime,  # 最后使用时间
    "usage_count": int      # 使用次数
}
```

---

## 6. 扩展与优化

### 6.1 增加新书目
编辑 `data/books.json`，按格式添加即可：
```json
{
  "id": 11,
  "title": "新书名",
  "topic": "python",
  ...
}
```

### 6.2 调整评分权重
编辑 `config.py`：
```python
weight_topic = 30      # 主题匹配权重
weight_difficulty = 25 # 难度匹配权重
weight_time = 20       # 时间匹配权重
weight_preference = 20 # 偏好匹配权重
rejection_penalty = 100  # 拒绝惩罚
```

### 6.3 添加新记忆维度
1. 在 `services/memory_service.py::_compress_feedback()` 的 Prompt 中添加新 field
2. 在 `services/recommender.py::_score_preference()` 中添加对应评分逻辑

### 6.4 优化向量检索
**当前方案**：本地 embedding + 余弦相似度
**升级方案**：
- 使用向量数据库（Chroma、Pinecone）
- 支持大规模记忆 (>1000条)
- 更高效的索引（HNSW）

### 6.5 缓存策略
```python
# 已实现：Embedding 缓存
self.embeddings_cache = {}  # 内存缓存

# 可扩展：推荐结果缓存
# 对相同 user_id + user_input 的推荐结果缓存5分钟
```

---

## 7. 性能指标

### 预期响应时间（单次推荐）
- 记忆检索：< 100ms
- 书目检索：< 50ms
- 评分计算：< 10ms
- LLM 调用：500-2000ms
- **总响应时间**：1-3秒

### 内存占用
- Embedding 模型：~500MB
- 60本书数据：< 1MB
- 1000条记忆：~10MB
- **总计**：< 1GB

### API 成本（每1000次推荐）
- OpenAI GPT-3.5：~0.5-1元
- Embedding：0元（本地）
- **总计**：0.5-1元/1000次

---

## 8. 安全注意事项

### 8.1 API 密钥管理
- ❌ 不要硬编码在代码中
- ✅ 使用 `.env` 文件
- ✅ 提交前加入 `.gitignore`

### 8.2 输入验证
- ✅ Pydantic 模型验证
- ✅ FastAPI 自动验证
- ⚠️ 可增加频率限制

### 8.3 数据隔离
- ✅ 按 user_id 隔离记忆
- ✅ 用户只能访问自己的记忆

---

## 9. 测试策略

### 单元测试
```python
# 测试评分算法
def test_difficulty_score():
    assert calculate_difficulty_score("beginner", "beginner") == 1.0
    assert calculate_difficulty_score("beginner", "intermediate") == 0.6

# 测试记忆写入
def test_memory_write():
    memory = memory_service.write_memory("test_user", "测试反馈")
    assert memory.field == "general"
```

### 集成测试
```python
# 测试完整推荐流程
def test_full_recommendation():
    result = agent.run(user_input, "test_user")
    assert len(result.books) > 0
    assert len(result.agent_trace) > 0
```

### 性能测试
```python
# 测试响应时间
import time
start = time.time()
result = agent.run(user_input, "test_user")
elapsed = time.time() - start
assert elapsed < 5.0  # 5秒内完成
```

---

## 10. 常见问题排查

### Q: 推荐结果不理想
**排查步骤**：
1. 检查 `memories_used` 是否为空
2. 查看 Agent 轨迹中的 `retrieve_memory` 步骤
3. 手动测试评分公式
4. 检查记忆置信度是否过低

### Q: 记忆检索无结果
**排查步骤**：
1. 检查 embedding 是否生成成功
2. 降低 `memory_similarity_threshold`
3. 检查记忆字段是否匹配

### Q: LLM 调用超时
**排查步骤**：
1. 检查网络连接
2. 增加超时时间
3. 使用降级方案

---

## 附录：关键代码位置

| 功能 | 文件 | 关键函数 |
|------|------|---------|
| 记忆压缩 | `services/memory_service.py` | `_compress_feedback()` |
| 向量检索 | `services/memory_service.py` | `retrieve_memory()` |
| 评分算法 | `services/recommender.py` | `recommend()`, `_calculate_scores()` |
| Agent决策 | `services/agent.py` | `run()`, `process_feedback()` |
| LLM封装 | `utils/llm_client.py` | `chat()` |
| Embedding | `utils/embedding.py` | `get_embedding()`, `cosine_similarity()` |

---

最后更新：2025-08-20
