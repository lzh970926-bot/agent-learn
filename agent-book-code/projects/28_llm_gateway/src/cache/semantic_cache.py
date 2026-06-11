"""
语义缓存：基于 Embedding 相似度判断是否命中
"""
import hashlib
import numpy as np
from redis import Redis
from openai import OpenAI
import os
import json


class SemanticCache:
    """语义缓存"""

    def __init__(self, redis: Redis, threshold: float = 0.95):
        self.redis = redis
        self.threshold = threshold
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _embed(self, text: str) -> list[float]:
        resp = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
        )
        return resp.data[0].embedding

    def _key(self, text: str) -> str:
        return "cache:" + hashlib.sha256(text.encode()).hexdigest()[:16]

    def get(self, query: str) -> dict | None:
        """精确 + 语义查找"""
        # 1. 精确命中
        exact = self.redis.get(self._key(query))
        if exact:
            return json.loads(exact)

        # 2. 语义命中
        # TODO(作者）：用 Qdrant / Redis Vector 存储 embedding
        # 当前为简化版：仅精确命中
        return None

    def set(self, query: str, response: dict, ttl: int = 3600):
        """写入缓存"""
        self.redis.setex(
            self._key(query),
            ttl,
            json.dumps(response, ensure_ascii=False),
        )

    # TODO(作者）：集成 Qdrant 做语义搜索
    # TODO(作者）：支持"按 tenant 隔离"（key 加 tenant 前缀）
    # TODO(作者）：命中率统计 + 自动调优 threshold
