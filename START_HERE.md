# 🚀 启动服务 - 3 种方式

## ✅ 当前状态

- 📍 **位置**：`c:\Users\26533\Desktop\Competition`
- ✅ **配置文件**：已就绪
- ✅ **安全配置**：已完成
- ⏳ **下一步**：配置密钥并启动

---

## ⚡ 快速启动（推荐流程）

### 第1步：配置密钥（只需一次）

在 **PowerShell** 中运行：
```powershell
$env:OPENAI_API_KEY="sk-2eff669cc1b847eaa50bf629e25f805f"
```

**注意**：
- 复制粘贴你的真实密钥
- 这个命令只在当前终端窗口有效
- 关闭终端后需要重新设置

---

### 第2步：启动服务

在 **PowerShell** 中运行：
```powershell
python start.py
```

或直接运行：
```powershell
python main.py
```

---

### 第3步：验证服务

打开浏览器访问：
- **API 文档**：http://localhost:8000/docs
- **健康检查**：httplocalhost:8000/

应该看到：
```json
{
  "service": "知遇 AI 馆员",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 📋 启动方式对比

| 方式 | 命令 | 适用场景 |
|------|------|---------|
| **start.py（推荐）** | `python start.py` | 首次启动，自动检查环境 |
| **main.py** | `python main.py` | 快速启动，跳过检查 |
| **uvicorn** | `uvicorn main:app --reload` | 开发模式，自动重载 |

---

## 🔄 日常启动流程

### 每次打开电脑/终端

```powershell
# 1. 进入项目目录
cd c:\Users\26533\Desktop\Competition

# 2. 设置密钥
$env:OPENAI_API_KEY="sk-2eff669cc1b847eaa50bf629e25f805f"

# 3. 启动服务
python start.py
```

就这么简单！3 条命令搞定 ✅

---

## ⚙️ 配置永久密钥（可选）

如果不想每次重启终端都设置密钥，可以永久设置：

### Windows CMD
```cmd
setx OPENAI_API_KEY "sk-2eff669cc1b847eaa50bf629e25f805f"
```

### Windows PowerShell
```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-2eff669cc1b847eaa50bf629e25f805f", "User")
```

设置后，重启终端即可生效，无需再运行 `$env:...`

---

## 🧪 测试服务

### 测试1：健康检查
```powershell
curl http://localhost:8000/
```

### 测试2：搜索书目
```powershell
curl http://localhost:8000/api/books/search?topic=machine_learning
```

### 测试3：完整推荐
```powershell
curl -X POST http://localhost:8000/api/agent/recommend `
  -H "Content-Type: application/json" `
  -d '{\"user_input\":{\"goal\":\"machine_learning\",\"difficulty\":\"beginner\",\"time_per_day\":30,\"language\":\"zh\"},\"user_id\":\"test\"}'
```

### 测试4：前后对比（评委演示）
```powershell
curl http://localhost:8000/api/demo/compare/test_user
```

---

## ❓ 常见问题

### Q: 提示 "No module named 'xxx'"
**解决**：安装依赖
```powershell
pip install -r requirements.txt
```

### Q: 提示 "OpenAI API key not configured"
**解决**：
1. 检查是否设置了环境变量
2. 运行 `python test_security.py` 查看配置状态

### Q: 服务启动很慢
**原因**：首次运行会下载 embedding 模型（~100MB）
**解决**：耐心等待，只需一次

### Q: 端口 8000 被占用
**解决**：修改 `.env` 中的端口
```env
PORT=8001
```

### Q: 推荐接口超时
**解决**：检查网络连接，或在 `.env` 中增加超时时间
```env
LLM_TIMEOUT=60
```

---

## 📊 启动后查看日志

服务启动后会看到：
```
🚀 知遇 AI 馆员 - 后端服务
======================================================================
📍 服务地址：http://localhost:8000
📖 API文档：http://localhost:8000/docs
❤️  健康检查：http://localhost:8000/health

按 Ctrl+C 停止服务
======================================================================

INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Waiting for application startup.
🚀 启动知遇AI馆员服务...
✓ 从环境变量加载 OPENAI_API_KEY
✅ 数据库初始化完成
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

看到 `✓ 从环境变量加载 OPENAI_API_KEY` 就说明密钥加载成功！

---

## 🎯 下一步

启动成功后：
1. ✅ 访问 http://localhost:8000/docs
2. ✅ 测试推荐接口
3. ✅ 准备演示数据

---

**现在就在 PowerShell 中运行**：
```powershell
cd c:\Users\26533\Desktop\Competition
$env:OPENAI_API_KEY="sk-2eff669cc1b847eaa50bf629e25f805f"
python start.py
```
