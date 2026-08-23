"""
LLM 客户端封装 - 支持安全密钥加载
"""
import os
from typing import Optional
<<<<<<< HEAD:backend/utils/llm_client.py
=======
from openai import OpenAI
import httpx
import anthropic
>>>>>>> 5a1079d06f156da6ff056ad2c63f5dba7585ccfd:utils/llm_client.py
from config import settings

# 可选导入：openai / anthropic 未安装时降级
try:
    from openai import OpenAI
    _HAS_OPENAI = True
except ImportError:
    OpenAI = None
    _HAS_OPENAI = False

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    anthropic = None
    _HAS_ANTHROPIC = False

# 可选：从安全配置加载密钥
try:
    from .secure_config import load_api_key as _secure_load_key
    _has_secure_config = True
except ImportError:
    _has_secure_config = False


def _load_api_key_safely(key_name: str, fallback: Optional[str]) -> Optional[str]:
    """
    安全加载 API 密钥

    加载优先级：
    1. 系统环境变量（最安全）
    2. secure_config 中的密钥管理器
    3. fallback（.env 中的值，仅作为最后 resort）

    Args:
        key_name: 环境变量名
        fallback: .env 中的值

    Returns:
        API 密钥或 None
    """
    # 1. 从系统环境变量加载（最安全）
    env_key = os.getenv(key_name)
    if env_key and not env_key.startswith("CHANGE_ME"):
        return env_key

    # 2. 从 secure_config 加载
    if _has_secure_config:
        secure_key = _secure_load_key(key_name)
        if secure_key:
            return secure_key

    # 3. 使用 fallback（.env 中的值）
    if fallback and not fallback.startswith("CHANGE_ME"):
        return fallback

    return None


class LLMClient:
    """统一 LLM 客户端"""

    def __init__(self):
        self.provider = settings.llm_provider
        self.model = settings.llm_model

        if self.provider == "openai":
            if not _HAS_OPENAI:
                raise ValueError("openai 包未安装，请运行 pip install openai")

            # [SEC] 安全加载 API 密钥
            api_key = _load_api_key_safely(
                "OPENAI_API_KEY",
                settings.openai_api_key
            )
            if not api_key:
                raise ValueError(
                    "OpenAI API key not configured\n"
                    "请使用以下方式之一配置密钥：\n"
                    "1. 设置环境变量: set OPENAI_API_KEY=sk-...\n"
                    "2. 使用密钥管理器: python -m utils.secure_config\n"
                    "3. 临时修改 .env 文件（不推荐用于生产环境）"
                )

            # 构建 OpenAI 客户端参数
            client_kwargs = {"api_key": api_key}

            # 如果配置了 base_url，添加进去（用于代理或自定义端点）
            if hasattr(settings, 'openai_base_url') and settings.openai_base_url:
                client_kwargs["base_url"] = settings.openai_base_url

            # 如果配置了代理，使用 httpx.HTTPTransport（新版本 httpx 语法）
<<<<<<< HEAD:backend/utils/llm_client.py
            if _HAS_HTTPX and (settings.http_proxy or settings.https_proxy):
=======
            if settings.http_proxy or settings.https_proxy:
>>>>>>> 5a1079d06f156da6ff056ad2c63f5dba7585ccfd:utils/llm_client.py
                proxy_url = settings.https_proxy or settings.http_proxy
                transport = httpx.HTTPTransport(proxy=proxy_url)
                http_client = httpx.Client(transport=transport)
                client_kwargs["http_client"] = http_client

            self.client = OpenAI(**client_kwargs)

        elif self.provider == "anthropic":
            if not _HAS_ANTHROPIC:
                raise ValueError("anthropic 包未安装，请运行 pip install anthropic")

            # [SEC] 安全加载 API 密钥
            api_key = _load_api_key_safely(
                "ANTHROPIC_API_KEY",
                settings.anthropic_api_key
            )
            if not api_key:
                raise ValueError(
                    "Anthropic API key not configured\n"
                    "请使用以下方式之一配置密钥：\n"
                    "1. 设置环境变量: set ANTHROPIC_API_KEY=sk-ant-...\n"
                    "2. 使用密钥管理器: python -m utils.secure_config\n"
                    "3. 临时修改 .env 文件（不推荐用于生产环境）"
                )
            self.client = anthropic.Anthropic(api_key=api_key)

        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """统一对话接口"""
        if self.provider == "openai":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            # Anthropic 格式转换
            system_msg = None
            user_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    user_messages.append(msg)

            response = self.client.messages.create(
                model=self.model,
                system=system_msg,
                messages=user_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.content[0].text

        raise NotImplementedError()


# 全局单例
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> Optional[LLMClient]:
    """获取 LLM 客户端（单例）。无 API Key 时返回 None，后端仍可正常运行。"""
    global _llm_client
    if _llm_client is None:
        try:
            _llm_client = LLMClient()
        except (ValueError, Exception) as e:
            print(f"[WARN] LLM 客户端未初始化（无 API Key），推荐说明将使用兜底文本: {e}")
            _llm_client = None
    return _llm_client
