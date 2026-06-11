"""
Ch5.1｜朴素 RAG 实现

4 步流程：
1. 文档切分（Chunking）
2. Embedding
3. 检索（Top-K）
4. Stuff 拼接 + LLM 生成
"""
import os
import numpy as np
from openai import OpenAI
from dataclasses import dataclass
from typing import List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class Document:
    """文档块"""
    content: str
    metadata: dict = None


def simple_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    朴素切分：按固定大小切分，带 overlap
    """
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def embed_texts(texts: List[str], model: str = "text-embedding-3-small") -> np.ndarray:
    """Embedding 批量接口"""
    resp = client.embeddings.create(model=model, input=texts)
    return np.array([d.embedding for d in resp.data])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """余弦相似度"""
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return a_norm @ b_norm.T


class NaiveRAG:
    """朴素 RAG"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: List[Document] = []
        self.vectors: np.ndarray | None = None

    def add_documents(self, texts: List[str]):
        """添加文档并构建索引"""
        # 1. 切分
        for text in texts:
            chunks = simple_chunk(text, self.chunk_size, self.chunk_overlap)
            for chunk in chunks:
                self.documents.append(Document(content=chunk))

        # 2. Embedding
        contents = [d.content for d in self.documents]
        self.vectors = embed_texts(contents)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """检索 Top-K 相关文档"""
        query_vec = embed_texts([query])[0]
        similarities = cosine_similarity(self.vectors, query_vec.reshape(1, -1)).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.documents[i] for i in top_indices]

    def query(self, question: str, top_k: int = 3) -> str:
        """完整 RAG 流程"""
        # 3. 检索
        docs = self.retrieve(question, top_k)

        # 4. Stuff 拼接 + LLM 生成
        context = "\n\n---\n\n".join([d.content for d in docs])
        prompt = f"""基于以下参考资料回答问题。如果资料中没有答案，回答"不知道"。

参考资料：
{context}

问题：{question}
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content, docs


if __name__ == "__main__":
    # 示例文档
    documents = [
        "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。"
        "由 Guido van Rossum 于 1989 年发明，第一个公开发行版发行于 1991 年。",
        "机器学习是人工智能的一个分支。它的核心是让计算机从数据中学习模式，"
        "而不是通过明确的编程指令。常见算法包括线性回归、决策树、神经网络。",
        "深度学习是机器学习的一个子集，使用多层神经网络进行特征学习。"
        "它在图像识别、自然语言处理等领域取得突破性进展。",
        "今天的天气晴朗，气温 25°C，适合户外运动。但明天可能有雨。",
        "比特币是一种加密货币，由中本聪在 2008 年提出，2009 年正式上线。",
    ]

    rag = NaiveRAG(chunk_size=200, chunk_overlap=20)
    rag.add_documents(documents)

    # 测试
    questions = [
        "Python 是谁发明的？",
        "深度学习是什么？",
        "今天适合户外运动吗？",
        "比特币是谁提出的？",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        answer, sources = rag.query(q)
        print(f"A: {answer}")
        print(f"来源 ({len(sources)} 个文档块):")
        for i, d in enumerate(sources, 1):
            print(f"  [{i}] {d.content[:80]}...")


# TODO(作者)：5.2 节扩展为支持 metadata 过滤
# TODO(作者)：添加 chunk 切分策略对比（固定 / 句子 / 段落 / 语义）
