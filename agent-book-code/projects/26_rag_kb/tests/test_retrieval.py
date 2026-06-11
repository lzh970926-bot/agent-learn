"""RAG 检索测试"""
import pytest
import sys
sys.path.insert(0, "../..")
from projects.twenty_six_rag_kb.src.retrieval.hybrid import HybridRetriever


def test_hybrid_index_and_search():
    retriever = HybridRetriever(tenant_id="test")
    docs = ["苹果是一种水果", "香蕉是黄色的", "汽车是交通工具"]
    retriever.index(docs)

    results = retriever.search("水果", top_k=2)
    assert len(results) <= 2
    assert "苹果" in results[0]["text"] or "香蕉" in results[0]["text"]
