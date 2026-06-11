"""
Ch2.2｜Embedding 相似度

演示：
- 文本转向量
- Cosine Similarity 计算
- 可视化热力图
"""
import numpy as np
from openai import OpenAI
import os
import matplotlib.pyplot as plt
from typing import List
import seaborn as sns

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def embed(texts: List[str], model: str = "text-embedding-3-small") -> np.ndarray:
    """调用 OpenAI Embedding API"""
    resp = client.embeddings.create(model=model, input=texts)
    return np.array([d.embedding for d in resp.data])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """计算两组向量的两两余弦相似度"""
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return a_norm @ b_norm.T


SAMPLE_TEXTS = [
    "猫在沙发上睡觉",
    "小狗在客厅打盹",          # 语义相似
    "今天股票涨了",            # 无关
    "Python 是一门编程语言",   # 无关
    "宠物在休息",              # 语义相似（更抽象）
]


def demo_similarity():
    """对比语义相似度"""
    vectors = embed(SAMPLE_TEXTS)
    sim = cosine_similarity(vectors, vectors)

    # 打印表格
    print("相似度矩阵:")
    header = " " * 12 + "".join(f"{i:10d}" for i in range(len(SAMPLE_TEXTS)))
    print(header)
    for i, row in enumerate(sim):
        text_preview = SAMPLE_TEXTS[i][:10]
        print(f"[{i}]{text_preview:10s}" + "".join(f"{v:10.3f}" for v in row))

    # 画热力图
    plt.figure(figsize=(8, 6))
    sns.heatmap(
        sim,
        annot=True,
        fmt=".3f",
        xticklabels=[t[:8] for t in SAMPLE_TEXTS],
        yticklabels=[t[:8] for t in SAMPLE_TEXTS],
        cmap="YlOrRd",
    )
    plt.title("Cosine Similarity Heatmap")
    plt.tight_layout()
    plt.savefig("ch02/embedding_heatmap.png", dpi=100)
    print("\n✓ 热力图已保存到 ch02/embedding_heatmap.png")


if __name__ == "__main__":
    demo_similarity()


# TODO(作者)：扩展为支持多模型对比（text-embedding-3-small vs text-embedding-3-large vs bge-m3）
# TODO(作者)：添加"语义搜索"功能：输入查询，返回 Top-K 最相似的
