# Ch2｜核心概念：Token、Context、Embedding

> 本章目标：理解 LLM 的"度量单位"，避免常见的认知误区。

## 章节结构

| 节 | 内容 | 字数目标 |
|---|---|---|
| 2.1 | Token 是什么：BPE 与 SentencePiece | 1500 |
| 2.2 | 中英文 Token 差异与成本计算 | 1000 |
| 2.3 | Context Window 与"长上下文误区" | 2000 |
| 2.4 | Lost in the Middle 实验 | 1500 |
| 2.5 | Embedding 与相似度 | 2000 |
| 2.6 | 主流 Embedding 模型选型 | 1500 |
| 2.7 | 小结与思考 | 500 |

## 文件说明

- `01_tokenize.py`：可视化 Token 切分
- `02_embedding.py`：Embedding 相似度热力图
- `03_lost_in_middle.py`：复现"中间遗忘"现象
- `03_capstone.py`：构建一个 Token 成本计算器

## 运行

```bash
uv run python ch02/01_tokenize.py
uv run python ch02/02_embedding.py
uv run python ch02/03_lost_in_middle.py
```

## 关键 takeaway

1. **1 个汉字 ≠ 1 个 Token**：中文通常 1.5–2 Token/字
2. **Context 不是越大越好**：128K 也有 Lost in the Middle
3. **Embedding 模型选型 > 向量数据库选型**：换模型可能涨 10% 检索率
