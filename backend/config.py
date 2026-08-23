"""
配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # LLM 配置
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    llm_provider: str = "openai"  # openai | anthropic
    llm_model: str = "gpt-3.5-turbo"

    # 代理配置
    http_proxy: Optional[str] = None
    https_proxy: Optional[str] = None

    # 服务配置
    port: int = 8000
    debug: bool = True

    # 记忆检索配置
    memory_top_k: int = 5
    memory_similarity_threshold: float = 0.7
    semantic_model: str = "BAAI/bge-m3"
    semantic_similarity_threshold: float = 0.35

    # 推荐评分权重
    weight_topic: int = 30
    weight_difficulty: int = 25
    weight_time: int = 20
    weight_preference: int = 20
    rejection_penalty: int = 100

    # 数据路径
    books_data_path: str = "data/books.json"
    memories_data_path: str = "data/memories.json"
    embeddings_cache_path: str = "data/embeddings_cache.json"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
