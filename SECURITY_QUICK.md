# API 密钥安全配置 - 快速开始

## ⚡ 3 秒配置（Windows）

### 方法1：PowerShell（推荐）
```powershell
$env:OPENAI_API_KEY="sk-你的密钥"
```

### 方法2：CMD（永久）
```cmd
setx OPENAI_API_KEY "sk-你的密钥"
```

---

## 🔐 推荐方案

### 比赛期间：环境变量
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-你的密钥"

# 验证
python -c "import os; print('✓ 密钥已加载' if os.getenv('OPENAI_API_KEY') else '✗ 未配置')"
```

### 日常开发：密钥管理器
```bash
# 保存到密钥文件
python -m utils.secure_config

# 以后自动加载
python main.py
```

---

## ⚠️ 重要提醒

1. **不要**把密钥写到 `.env` 文件中
2. **不要**提交 `.env` 到 Git
3. **不要**在屏幕共享时显示密钥
4. **比赛结束后**撤销密钥

---

## 📚 详细文档

完整配置指南：详见 `SECURITY.md`
