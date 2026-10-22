"""
配置管理
"""
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

# backend 根目录（app/config.py 的上一级）。用它来固定数据文件位置，
# 避免从不同工作目录启动时把数据路径解析到别处、误生成 3 本样例书。
BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # LLM 配置
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"  # openai | anthropic
    llm_model: str = "gpt-3.5-turbo"
    openai_base_url: Optional[str] = None  # 自定义 OpenAI 兼容 API 地址（如 DeepSeek）

    # 代理配置
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None

    # 服务配置
    port: int = 8000
    debug: bool = True

    # 记忆检索配置
    memory_top_k: int = 5
    # 字符 n-gram TF-IDF 的余弦相似度通常很低，阈值要小而合理（原 0.7 是为稠密向量设的，会把所有记忆过滤光）
    memory_similarity_threshold: float = 0.15
    semantic_model: str = "BAAI/bge-m3"
    semantic_similarity_threshold: float = 0.35

    # 推荐评分权重
    weight_topic: int = 30
    weight_difficulty: int = 25
    weight_time: int = 20
    weight_preference: int = 20
    rejection_penalty: int = 100

    # 数据路径（默认绝对路径，指向 backend/data，不依赖启动时的工作目录）
    books_data_path: str = str(BACKEND_DIR / "data" / "books.json")
    memories_data_path: str = str(BACKEND_DIR / "data" / "memories.json")
    embeddings_cache_path: str = str(BACKEND_DIR / "data" / "embeddings_cache.json")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
