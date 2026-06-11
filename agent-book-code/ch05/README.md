# Ch5｜RAG 原理：检索、增强、生成

> 本章目标：理解 RAG 的核心思想、Advanced RAG 优化技巧、评估方法，并能实现生产级 RAG 系统。

## 章节结构

| 节 | 内容 | 字数目标 |
|---|---|---|
| 5.1 | 为什么需要 RAG | 1500 |
| 5.2 | 朴素 RAG：Embed → Retrieve → Stuff | 2000 |
| 5.3 | Advanced RAG：Pre/Post Retrieval | 2500 |
| 5.4 | Modular RAG：可插拔的检索-生成管线 | 1500 |
| 5.5 | RAG 评估：怎么知道 RAG 好不好 | 2000 |
| 5.6 | 实战：从 0 到 1 实现朴素 RAG | 1500 |
| 5.7 | 小结与思考 | 500 |

## 文件说明

- `01_naive_rag.py`：朴素 RAG 实现（200 行）
- `02_advanced_rag.py`：Query Rewrite + ReRank
- `03_evaluation.py`：RAGAS 评估
- `tests/test_rag.py`：RAG 单元测试

## 运行

```bash
export OPENAI_API_KEY=sk-...
uv run python ch05/01_naive_rag.py
```

## 关键 takeaway

1. **RAG 解决 LLM 的 3 大知识困境**：时效 / 私有 / 幻觉
2. **Advanced RAG = Pre + Post Retrieval 优化**——查询改写 + 重排是核心
3. **没有评估 = 盲调**——RAGAS 是行业标准
