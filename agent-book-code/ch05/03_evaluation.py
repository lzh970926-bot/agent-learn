"""
Ch5.3｜RAG 评估：RAGAS 框架

核心指标：
- Context Recall：检索召回率
- Context Precision：检索准确率
- Faithfulness：生成答案是否忠于 context
- Answer Relevancy：答案与问题的相关度
"""
import os
from openai import OpenAI
from typing import List, Dict

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def evaluate_retrieval(retrieved_docs: List[str], relevant_docs: List[str], k: int = 5) -> Dict[str, float]:
    """检索评估：Recall@k, Precision@k, MRR"""
    retrieved_set = set(retrieved_docs[:k])
    relevant_set = set(relevant_docs)

    if not relevant_set:
        return {"recall@k": 0, "precision@k": 0, "mrr": 0}

    # Recall@k
    recall = len(retrieved_set & relevant_set) / len(relevant_set)

    # Precision@k
    precision = len(retrieved_set & relevant_set) / min(k, len(retrieved_set))

    # MRR (Mean Reciprocal Rank)
    for i, doc in enumerate(retrieved_docs, 1):
        if doc in relevant_set:
            mrr = 1.0 / i
            break
    else:
        mrr = 0.0

    return {"recall@k": recall, "precision@k": precision, "mrr": mrr}


def evaluate_faithfulness(answer: str, context: str) -> float:
    """Faithfulness：答案是否忠于 context"""
    prompt = f"""判断以下答案是否完全基于提供的 context。如果答案中的事实都能在 context 中找到，打 1；否则打 0。

Context: {context[:1000]}

Answer: {answer}

分数（0 或 1）："""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    try:
        return float(resp.choices[0].message.content.strip())
    except ValueError:
        return 0.0


def evaluate_answer_relevancy(question: str, answer: str) -> float:
    """Answer Relevancy：答案与问题的相关度"""
    prompt = f"""判断以下答案是否回答了用户问题。回答切题且完整得 1；答非所问或信息缺失得 0。

Question: {question}

Answer: {answer}

分数（0 或 1）："""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    try:
        return float(resp.choices[0].message.content.strip())
    except ValueError:
        return 0.0


# === 完整评估流程 ===
def evaluate_rag_system(rag, test_questions: List[Dict]) -> Dict[str, float]:
    """
    test_questions 格式：
    [
        {"question": "...", "relevant_docs": ["doc1", "doc2"], "ground_truth": "..."},
        ...
    ]
    """
    metrics = {
        "recall@5": [],
        "precision@5": [],
        "mrr": [],
        "faithfulness": [],
        "answer_relevancy": [],
    }

    for item in test_questions:
        question = item["question"]
        relevant = item["relevant_docs"]

        # 检索评估
        retrieved = rag.retrieve(question, top_k=5)
        retrieved_contents = [d.content for d in retrieved]
        ret_metrics = evaluate_retrieval(retrieved_contents, relevant, k=5)
        metrics["recall@5"].append(ret_metrics["recall@k"])
        metrics["precision@5"].append(ret_metrics["precision@k"])
        metrics["mrr"].append(ret_metrics["mrr"])

        # 生成评估
        answer, _ = rag.query(question, top_k=3)
        context = "\n".join(retrieved_contents)

        metrics["faithfulness"].append(evaluate_faithfulness(answer, context))
        metrics["answer_relevancy"].append(evaluate_answer_relevancy(question, answer))

    # 求平均
    return {k: sum(v) / len(v) if v else 0 for k, v in metrics.items()}


if __name__ == "__main__":
    # 示例：评估 5 个问题
    from ch05.01_naive_rag import NaiveRAG

    documents = [
        "Python 由 Guido van Rossum 于 1989 年发明。",
        "机器学习是 AI 的分支，从数据中学习模式。",
        "深度学习使用神经网络。",
        "比特币由中本聪 2008 年提出。",
    ]

    rag = NaiveRAG(chunk_size=200, chunk_overlap=20)
    rag.add_documents(documents)

    test_questions = [
        {
            "question": "Python 是谁发明的？",
            "relevant_docs": ["Python 由 Guido van Rossum 于 1989 年发明。"],
            "ground_truth": "Guido van Rossum",
        },
        {
            "question": "什么是深度学习？",
            "relevant_docs": ["深度学习使用神经网络。"],
            "ground_truth": "使用神经网络",
        },
    ]

    metrics = evaluate_rag_system(rag, test_questions)
    print("\n=== 评估结果 ===")
    for k, v in metrics.items():
        print(f"  {k}: {v:.3f}")


# TODO(作者)：用 RAGAS 库替代自实现
# TODO(作者)：扩展评估集到 100+ 问题
# TODO(作者)：加 Human Eval 对比
