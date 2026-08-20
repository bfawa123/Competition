# --no-build-isolation 选项说明

## 背景

在安装某些 Python 包时，可能会遇到构建隔离导致的依赖问题。

## 什么是构建隔离？

默认情况下，当 `pip` 尝试安装包含 `pyproject.toml` 文件的包时，它会创建一个**隔离的环境**来构建这个包。这个隔离环境确保了构建过程中使用的依赖与项目其他部分的依赖隔离开来，从而减少版本冲突的可能性。

## 为什么会出现问题？

**问题的根源**：构建过程中需要的某些依赖（如 `packaging` 模块）在隔离的构建环境中不可用。

当 `pip` 尝试在隔离环境中构建包时，如果构建系统（如 `setuptools`、`wheel`、`packaging` 等）本身不在隔离环境中，就会导致构建失败。

## --no-build-isolation 的作用

使用 `--no-build-isolation` 时，`pip` 将不会创建隔离环境，而是**直接在当前环境中构建包**。这意味着构建过程可以访问当前环境中已安装的所有依赖，包括 `packaging` 等构建工具。

## 何时使用 --no-build-isolation？

✅ **建议使用**：
- 遇到构建隔离错误时（如 `subprocess-exited-with-error`）
- 构建工具（`setuptools`、`wheel`、`packaging`）相关的依赖问题
- 网络环境较好的情况下（避免额外的下载时间）

❌ **不建议使用**：
- 生产环境（可能导致版本冲突）
- 依赖关系复杂的项目

## 安装优先级

现在 `start.py` 的安装策略是：

1. **清华镜像 - 常规安装**（默认隔离）
2. **清华镜像 - --no-build-isolation**（失败时自动尝试）
3. **阿里云镜像 - 常规安装**
4. **阿里云镜像 - --no-build-isolation**（最后的尝试）

## 手动使用示例

如果需要单独使用此选项：

```bash
# 基础用法
pip install -r requirements.txt --no-build-isolation

# 配合镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --no-build-isolation

# 针对单个包
pip install sentence-transformers==2.2.2 --no-build-isolation
```

## 注意事项

⚠️ **潜在风险**：
- 可能导致包版本冲突
- 可能安装不同版本的依赖
- 可能影响项目的可重现性

💡 **最佳实践**：
- 仅在构建隔离错误时使用
- 记录所使用的特定版本
- 定期测试项目功能
