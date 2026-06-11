"""
Qdrant 客户端封装
支持多租户（每个 tenant 独立 collection）
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from ..config import settings


def get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url)


def ensure_collection(tenant_id: str, vector_size: int = 1536):
    """为租户创建 collection（如不存在）"""
    client = get_client()
    name = f"kb_{tenant_id}"
    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    return name


# TODO(作者)：添加 collection 删除、列出、状态查询
# TODO(作者)：支持 metadata 索引（payload 字段）
