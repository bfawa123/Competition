"""
Embedding 管理 - 本地向量检索（支持离线备选）
"""
import numpy as np
import os
from typing import List, Optional
from config import settings

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity


class EmbeddingManager:
    """Embedding 管理器（支持离线和在线模式）"""

    def __init__(self, model_name: Optional[str] = None, force_tfidf: bool = False):
        """
        初始化 embedding 模型

        Args:
            model_name: SentenceTransformer 模型名称
            force_tfidf: 是否强制使用 TF-IDF 模式
        """
        model_name = model_name or getattr(settings, "semantic_model", None) or os.getenv("SEMANTIC_MODEL", "BAAI/bge-m3")
        self.model_name = model_name
        self.use_tfidf = False
        self.model = None
        self.dim = 0

        # 检查是否强制使用 TF-IDF
        if force_tfidf:
            print("Force using TF-IDF embedding (offline mode)")
            self.use_tfidf = True
            self._init_tfidf()
        elif HAS_SENTENCE_TRANSFORMERS:
            try:
                print(f"Loading embedding model: {model_name}")
                self.model = SentenceTransformer(model_name, device="cpu")
                self.dim = self.model.get_sentence_embedding_dimension()
                print(f"Model loaded, dimension: {self.dim}")
            except Exception as e:
                print(f"Warning: Failed to load SentenceTransformer: {e}")
                print("Falling back to TF-IDF embedding (offline mode)")
                self.use_tfidf = True
                self._init_tfidf()
        else:
            print("Warning: sentence-transformers not available")
            print("Using TF-IDF embedding (offline mode)")
            self.use_tfidf = True
            self._init_tfidf()

    def _init_tfidf(self):
        """初始化 TF-IDF 向量器（离线备选）"""
        self.vectorizer = TfidfVectorizer(
            max_features=512,
            stop_words=None,  # 中文需要自定义停用词
            analyzer='word',
            ngram_range=(1, 2)
        )
        # 预拟合一个初始文档以初始化
        initial_docs = ["初始文档", "初始化", "测试", "example", "test"]
        self.vectorizer.fit(initial_docs)
        self.dim = 512  # TF-IDF 默认维度

    def get_embedding(self, text: str) -> List[float]:
        """
        生成文本 embedding

        Args:
            text: 输入文本

        Returns:
            embedding 向量（List[float]）
        """
        if self.use_tfidf:
            # TF-IDF 模式
            vector = self.vectorizer.transform([text]).toarray()[0]
            return vector.tolist()
        else:
            # SentenceTransformer 模式
            embedding = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return embedding.tolist()

    def batch_embed(self, texts: List[str]) -> List[List[float]]:
        """批量生成 embedding"""
        if self.use_tfidf:
            vectors = self.vectorizer.transform(texts).toarray()
            return vectors.tolist()
        else:
            embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False)
            return embeddings.tolist()

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))


# 全局实例
embedding_mgr: Optional[EmbeddingManager] = None


def get_embedding_mgr(force_tfidf: bool = True) -> EmbeddingManager:
    """
    获取 embedding 管理器（单例）

    Args:
        force_tfidf: 是否强制使用 TF-IDF 模式（默认 True，避免 Hugging Face 网络问题）
    """
    global embedding_mgr
    if embedding_mgr is None:
        embedding_mgr = EmbeddingManager(force_tfidf=force_tfidf)
    return embedding_mgr
