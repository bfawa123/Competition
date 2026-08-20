# 依赖安装失败问题说明

## 问题原因

当你运行 `python start.py` 时,脚本会自动安装所需的 Python 依赖包。但安装过程中出现网络超时,导致失败:

```
subprocess.CalledProcessError: Command returned non-zero exit status 1
```

**具体原因:**
- 从 PyPI 官方源下载包速度慢(仅 46.3 kB/s)
- 下载大型包(如 scikit-learn 9.2MB, torch 等)时频繁超时
- 网络连接不稳定

## 解决方案

### ✅ 已实施的方案

我已经修改了 `start.py` 脚本,现在会自动使用**国内镜像源**加速下载:

1. **优先使用清华镜像源** - 速度快且稳定
2. **备选阿里云镜像** - 如果清华镜像失败会自动切换

### 手动安装依赖(如果自动安装仍然失败)

如果自动安装还有问题,可以手动执行以下命令:

#### 方法1: 使用清华镜像
```bash
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

#### 方法2: 使用阿里云镜像
```bash
python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

#### 方法3: 使用豆瓣镜像
```bash
python -m pip install -r requirements.txt -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com
```

### 分步安装(针对网络特别慢的情况)

如果一次性安装仍然超时,可以分步安装核心依赖:

```bash
# 先安装基础依赖
python -m pip install fastapi uvicorn python-multipart python-dotenv pydantic pydantic-settings -i https://pypi.tuna.tsinghua.edu.cn/simple

# 再安装机器学习依赖
python -m pip install sentence-transformers scikit-learn numpy -i https://pypi.tuna.tsinghua.edu.cn/simple

# 最后安装 AI API 依赖
python -m pip install openai anthropic -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 已安装的依赖

requirements.txt 包含以下依赖:

- **fastapi==0.104.1** - Web 框架
- **uvicorn==0.24.0** - ASGI 服务器
- **python-multipart==0.0.6** - 表单数据解析
- **python-dotenv==1.0.0** - 环境变量管理
- **sentence-transformers==2.2.2** - 文本向量化(大型包)
- **scikit-learn==1.3.2** - 机器学习库(大型包)
- **numpy==1.24.3** - 数值计算
- **openai==1.3.7** - OpenAI API
- **anthropic==0.8.1** - Anthropic API
- **pydantic==2.5.2** - 数据验证
- **pydantic-settings==2.1.0** - 配置管理

## 验证安装

安装完成后,可以运行测试脚本验证:

```bash
python test_backend.py
```

## 下一步

依赖安装成功后,重新运行:

```bash
python start.py
```

---

**注意**: 如果网络环境持续不稳定,建议考虑:
1. 使用 VPN 或代理
2. 在更好的网络环境下安装
3. 联系网络管理员开放 PyPI 访问权限
