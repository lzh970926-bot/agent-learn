"""
混合检索：BM25 + 向量 + RRF 融合
"""
from rank_bm25 import BM25Okapi
# from qdrant_client import QdrantClient  # TODO：集成向量召回


class HybridRetriever:
    """混合检索器"""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.bm25: BM25Okapi | None = None
        self.documents: list[str] = []
        # TODO(作者）：初始化向量检索客户端

    def index(self, documents: list[str]):
        """构建 BM25 索引"""
        tokenized = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
        self.documents = documents

    def search(self, query: str, top_k: int = 10) -> list[dict]:
        """检索 + RRF 融合"""
        # TODO(作者）：实现 RRF (Reciprocal Rank Fusion)
        # 1. BM25 召回 top_k
        # 2. 向量召回 top_k
        # 3. RRF 融合排序
        bm25_scores = self.bm25.get_scores(query.split()) if self.bm25 else []
        return [{"text": self.documents[i], "score": s}
                for i, s in sorted(enumerate(bm25_scores), key=lambda x: -x[1])[:top_k]]
