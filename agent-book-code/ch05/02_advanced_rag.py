"""
Ch5.2｜Advanced RAG：Pre-Retrieval + Post-Retrieval 优化

Pre-Retrieval：
- Query Rewriting：让 LLM 改写 query
- HyDE：让 LLM 生成"假设答案"再检索

Post-Retrieval：
- Re-ranking：用更强的模型重排
- Compression：压缩 context
"""
import os
from openai import OpenAI
import numpy as np
from typing import List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === Pre-Retrieval 1: Query Rewriting ===
def rewrite_query(query: str) -> str:
    """Query Rewriting：让 LLM 改写 query"""
    prompt = f"""请改写以下用户问题，使其更适合检索。保留核心意图，但用更标准化的表述。

原问题：{query}

改写后（只输出改写后的问题，不要其他内容）："""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


# === Pre-Retrieval 2: HyDE ===
def hyde_query(query: str) -> str:
    """
    HyDE (Hypothetical Document Embeddings)：
    让 LLM 生成"假设答案"，用假设答案的 embedding 做检索
    """
    prompt = f"""请基于以下问题，写一段可能的答案（150 字内）。即使不确定，也要写一个看起来合理的答案。

问题：{query}

假设答案："""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


# === Pre-Retrieval 3: Step-back ===
def step_back_query(query: str) -> str:
    """Step-back：先抽象，再检索"""
    prompt = f"""请把以下具体问题抽象为一个更通用的问题，以便检索背景知识。

具体问题：{query}

通用问题："""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


# === Post-Retrieval: Re-ranking ===
def rerank_documents(query: str, documents: List[str], top_k: int = 3) -> List[int]:
    """
    Re-ranking：用 LLM 对检索结果重排
    简化版：让 LLM 打分
    """
    # 实际项目用 Cohere Rerank / bge-reranker
    scored = []
    for i, doc in enumerate(documents):
        score_prompt = f"""给定问题，对以下文档的相关性打分（0-10）。

问题：{query}
文档：{doc[:500]}

分数（0-10，只输出数字）："""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": score_prompt}],
            temperature=0,
        )
        try:
            score = float(resp.choices[0].message.content.strip())
        except ValueError:
            score = 0
        scored.append((score, i))

    scored.sort(reverse=True)
    return [i for _, i in scored[:top_k]]


# === 综合：Advanced RAG Pipeline ===
class AdvancedRAG:
    """Advanced RAG"""

    def __init__(self, naive_rag):
        self.rag = naive_rag

    def query_with_rewrite(self, question: str, top_k: int = 3) -> str:
        """Query Rewriting + Re-ranking"""
        # 1. 改写 query
        rewritten = rewrite_query(question)
        print(f"  改写后: {rewritten}")

        # 2. 检索
        docs = self.rag.retrieve(rewritten, top_k=top_k * 2)  # 多取一些

        # 3. Re-rank
        contents = [d.content for d in docs]
        top_indices = rerank_documents(question, contents, top_k=top_k)
        reranked = [docs[i] for i in top_indices]

        # 4. 生成
        return self._generate(question, reranked)

    def query_with_hyde(self, question: str, top_k: int = 3) -> str:
        """HyDE + Re-ranking"""
        # 1. 生成假设答案
        hypothetical = hyde_query(question)
        print(f"  假设答案: {hypothetical[:100]}...")

        # 2. 用假设答案的 embedding 检索
        docs = self.rag.retrieve(hypothetical, top_k=top_k * 2)

        # 3. Re-rank
        contents = [d.content for d in docs]
        top_indices = rerank_documents(question, contents, top_k=top_k)
        reranked = [docs[i] for i in top_indices]

        # 4. 生成
        return self._generate(question, reranked)

    def _generate(self, question: str, docs) -> str:
        """最终生成"""
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
        return resp.choices[0].message.content


if __name__ == "__main__":
    from ch05.01_naive_rag import NaiveRAG

    # 准备文档
    documents = [
        "Python 是一种解释型、面向对象、动态数据类型的高级程序设计语言。"
        "由 Guido van Rossum 于 1989 年发明。",
        "机器学习是人工智能的一个分支，核心是从数据中学习模式。",
        "深度学习使用多层神经网络，在图像识别、NLP 取得突破。",
    ]

    print("=== 准备索引 ===")
    base_rag = NaiveRAG(chunk_size=200, chunk_overlap=20)
    base_rag.add_documents(documents)
    adv_rag = AdvancedRAG(base_rag)

    question = "深度学习是啥？"
    print(f"\n=== Question: {question} ===\n")

    print("--- Naive RAG ---")
    answer, _ = base_rag.query(question)
    print(answer)

    print("\n--- Advanced RAG (Query Rewrite + Re-rank) ---")
    answer = adv_rag.query_with_rewrite(question)
    print(answer)

    print("\n--- Advanced RAG (HyDE + Re-rank) ---")
    answer = adv_rag.query_with_hyde(question)
    print(answer)


# TODO(作者)：用 Cohere Rerank 替换 LLM 打分
# TODO(作者)：对比 Query Rewrite vs HyDE 的效果
