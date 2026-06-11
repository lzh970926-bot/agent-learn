"""Ch5 单元测试"""
import pytest
from ch05.01_naive_rag import simple_chunk, NaiveRAG


def test_simple_chunk():
    text = "a" * 1000
    chunks = simple_chunk(text, chunk_size=300, overlap=50)
    assert len(chunks) == 4  # 300 + 250 + 250 + 200
    assert chunks[0] == "a" * 300
    assert "a" * 50 in chunks[1]  # overlap 验证


def test_chunk_with_overlap():
    text = "0123456789" * 100
    chunks = simple_chunk(text, chunk_size=50, overlap=10)
    # 相邻 chunk 应该有 10 字符重叠
    assert chunks[0][40:] == chunks[1][:10]


# TODO(作者)：test_rag_retrieve（需要 mock embedding）
# TODO(作者)：test_rag_query（需要 mock LLM）
