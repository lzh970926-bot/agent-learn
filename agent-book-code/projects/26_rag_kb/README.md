# 项目 26｜企业级 RAG 知识库

> Ch26 综合项目：支持多格式文档、多租户、增量更新的生产 RAG 系统

## 目标

构建支持 PDF/Word/Markdown 混合文档、多租户隔离、增量更新、可观测的 RAG 知识库。

## 技术栈

- LlamaIndex（IngestionPipeline + Workflows）
- Qdrant（向量数据库）
- FastAPI（后端）
- Next.js（前端，可选）
- Langfuse（观测）

## 目录结构

```
26_rag_kb/
├── src/
│   ├── api/            # FastAPI 路由
│   ├── ingestion/      # 文档摄入
│   ├── retrieval/      # 检索与重排
│   ├── storage/        # Qdrant 客户端封装
│   └── config.py       # 配置
├── tests/
└── pyproject.toml
```

## 核心模块

- [ ] `ingestion/parser.py`：多格式文档解析
- [ ] `ingestion/pipeline.py`：LlamaIndex IngestionPipeline
- [ ] `retrieval/hybrid.py`：BM25 + 向量混合检索
- [ ] `retrieval/rerank.py`：Cohere/BGE 重排
- [ ] `api/chat.py`：问答接口
- [ ] `api/manage.py`：文档管理接口（CRUD）

## 验收指标

- 检索 Recall@5 > 0.85
- 生成 Faithfulness > 0.90（RAGAS 评测）
- 1000 文档摄入 < 5 分钟
- 端到端 P99 < 3s
