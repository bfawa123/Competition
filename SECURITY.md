# 🔐 API 密钥安全配置指南

## ⚠️ 重要安全提醒

**永远不要**：
- ❌ 在代码中硬编码 API 密钥
- ❌ 提交 `.env` 文件到 Git 仓库
- ❌ 在聊天/邮件中分享真实密钥
- ❌ 将密钥写入 README 或文档
- ❌ 在公共场合（比赛现场）显示密钥

**必须做到**：
- ✅ 使用环境变量或密钥管理器
- ✅ 定期轮换密钥
- ✅ 比赛结束后立即撤销密钥
- ✅ 开启 API 使用量告警

---

## 🎯 推荐配置方案

### 方案1：系统环境变量（最简单，推荐）⭐⭐⭐

#### Windows PowerShell（当前终端）
```powershell
$env:OPENAI_API_KEY="sk-你的密钥"
```

#### Windows CMD（永久设置）
```cmd
setx OPENAI_API_KEY "sk-你的密钥"
```

#### Windows PowerShell（永久设置）
```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-你的密钥", "User")
```

#### Linux/Mac（永久设置）
```bash
echo 'export OPENAI_API_KEY="sk-你的密钥"' >> ~/.bashrc
source ~/.bashrc
```

**优点**：
- 不存储在任何文件中
- 最简单
- 跨平台支持

**缺点**：
- 需要手动设置
- 重启终端后需要重新设置（如果不使用永久设置）

---

### 方案2：1Password / Bitwarden 密钥管理器（最安全）⭐⭐⭐⭐⭐

#### 1Password
```bash
# 1. 安装 1Password CLI
# 2. 登录
op signin

# 3. 存储密钥（一次）
op item create --category="API Credential" --title="OpenAI" --vault="Development" credential=sk-你的密钥

# 4. 使用密钥（自动加载）
op item get openai-api-key --fields credential
```

#### Bitwarden
```bash
# 1. 安装 Bitwarden CLI
# 2. 登录并解锁
bw login
bw unlock

# 3. 存储密钥
bw create item --name openai-api-key --login.password sk-你的密钥

# 4. 使用密钥
bw get item openai-api-key --nointeraction
```

**优点**：
- 最安全
- 支持团队共享
- 自动填充
- 加密存储

**缺点**：
- 需要安装额外软件
- 需要学习成本

---

### 方案3：本地密钥文件（开发环境）⭐⭐⭐

```bash
# 1. 保存密钥到文件
python -m utils.secure_config

# 2. 选择 "2. 密钥文件（仅限开发）"
# 3. 输入密钥

# 密钥会保存到：
# Windows: C:\Users\你的用户名\.config\zhiyu\api_key
# Linux/Mac: ~/.config/zhiyu/api_key
# 文件权限自动设置为仅当前用户可读写
```

**优点**：
- 简单易用
- 文件权限保护
- 跨项目通用

**缺点**：
- 文件仍然在本地
- 需要手动备份

---

## 🔧 快速配置命令

### Windows 用户

#### PowerShell（推荐）
```powershell
# 设置密钥（当前终端）
$env:OPENAI_API_KEY="sk-2eff669cc1b847eaa50bf629e25f805f"

# 永久设置（无需重新打开终端）
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-2eff669cc1b847eaa50bf629e25f805f", "User")
```

#### CMD
```cmd
:: 设置密钥（永久）
setx OPENAI_API_KEY "sk-2eff669cc1b847eaa50bf629e25f805f"

:: 设置密钥（当前终端）
set OPENAI_API_KEY=sk-2eff669cc1b847eaa50bf629e25f805f
```

### Linux/Mac 用户
```bash
# 设置密钥（永久）
export OPENAI_API_KEY="sk-2eff669cc1b847eaa50bf629e25f805f"
echo 'export OPENAI_API_KEY="sk-2eff669cc1b847eaa50bf629e25f805f"' >> ~/.bashrc
source ~/.bashrc
```

---

## ✅ 验证配置

配置完成后，验证密钥是否生效：

```bash
# 测试1：检查环境变量
# Windows PowerShell
echo $env:OPENAI_API_KEY

# Windows CMD
echo %OPENAI_API_KEY%

# Linux/Mac
echo $OPENAI_API_KEY

# 测试2：运行服务
python main.py
# 应该看到 ✓ 从环境变量加载 OPENAI_API_KEY

# 测试3：测试 API
curl http://localhost:8000/
```

---

## 🚨 紧急情况：密钥已泄露

### 立即执行

1. **撤销密钥**
   - OpenAI: https://platform.openai.com/api-keys → 删除旧密钥 → 创建新密钥
   - Anthropic: https://console.anthropic.com/settings/keys → 删除旧密钥 → 创建新密钥

2. **更新配置**
   ```bash
   # 更新系统环境变量
   setx OPENAI_API_KEY "sk-新的密钥"
   ```

3. **检查使用记录**
   - OpenAI: https://platform.openai.com/usage
   - Anthropic: https://console.anthropic.com/usage

4. **通知团队成员**
   - 如果有团队成员使用了泄露的密钥

---

## 🔍 检查密钥是否泄露

### 检查 Git 历史
```bash
# 搜索 Git 历史中的密钥
git log -p | grep -i "sk-" | grep -v "^+.*CHANGE_ME"
```

### 检查 GitHub
```bash
# 使用 GitHub 的 secret scanning
# 访问：https://github.com/你的用户名/你的仓库/security/secret-scanning
```

### 撤销并重新生成
如果发现密钥已提交到公开仓库：
1. **立即撤销旧密钥**
2. **生成新密钥**
3. **更新所有使用旧密钥的地方**
4. **审查 Git 历史**（如果需要保密）

---

## 💡 比赛期间安全建议

### 最低要求（必须）
- ✅ 不要将 `.env` 文件提交到 Git
- ✅ 不要在屏幕共享时显示密钥
- ✅ 比赛结束后撤销密钥

### 推荐方案（更好）
- ✅ 使用系统环境变量
- ✅ 开启 API 使用量限制
- ✅ 设置使用告警

### 最佳实践（最安全）
- ✅ 使用密钥管理器（1Password/Bitwarden）
- ✅ 定期轮换密钥
- ✅ 最小权限原则（如果可能）

---

## 📊 成本控制

### 设置使用限额
1. **OpenAI**
   - 访问：https://platform.openai.com/usage
   - 设置月度预算限额

2. **Anthropic**
   - 访问：https://console.anthropic.com/settings/usage
   - 设置使用告警

### 监控使用量
```bash
# OpenAI 使用情况
curl https://api.openai.com/dashboard/billing/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## 🆘 常见问题

### Q1: 如何查看当前环境变量？
**Windows PowerShell**:
```powershell
[System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
```

**Windows CMD**:
```cmd
echo %OPENAI_API_KEY%
```

**Linux/Mac**:
```bash
echo $OPENAI_API_KEY
```

### Q2: 密钥设置后重启终端就没了？
**原因**：可能设置了用户级变量但 PowerShell 没有正确加载

**解决**：
```powershell
# 检查用户级变量
[System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")

# 如果存在，强制加载到当前会话
$env:OPENAI_API_KEY = [System.Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
```

### Q3: 如何确认密钥没有提交到 Git？
```bash
# 检查 .gitignore
cat .gitignore | grep "\.env"

# 检查 Git 状态
git status
# .env 应该显示为 "untracked" 或 "ignored"

# 检查最近提交
git log --oneline -10
# 不应该有任何包含密钥的提交
```

### Q4: 可以临时在 .env 文件中使用密钥吗？
**可以**，但仅限于：
- 本地开发环境
- 确保 `.env` 在 `.gitignore` 中
- **不要**提交到 Git
- **不要**分享文件
- 比赛结束后删除密钥

---

## 📚 参考资源

- [OpenAI API 密钥管理](https://platform.openai.com/docs/guides/api-key-rotation)
- [1Password CLI 文档](https://developer.1password.com/docs/cli/)
- [Bitwarden CLI 文档](https://bitwarden.com/help/article/cli/)
- [OWASP 密钥管理指南](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)

---

## ✅ 配置检查清单

配置完成后，请确认：
- [ ] 密钥已设置（不在 `.env` 文件中）
- [ ] 可以通过环境变量访问密钥
- [ ] 服务可以正常启动
- [ ] API 调用成功
- [ ] `.env` 文件未提交到 Git
- [ ] 已开启 API 使用量告警
- [ ] 比赛结束后计划撤销密钥

---

**记住**：安全配置不仅是技术问题，更是习惯问题。从小事做起！🔒
