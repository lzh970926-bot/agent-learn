# agent-book-code

《大模型 Agent 系统开发：从原理到架构》配套代码仓库。

## 目录结构

```
agent-book-code/
├── ch01/ ~ ch30/         # 30 章示例代码
│   ├── 01_basic.py       # 基础示例
│   ├── 02_advanced.py    # 进阶示例
│   ├── 03_capstone.py    # 综合示例
│   ├── tests/
│   ├── README.md         # 章节说明 + 运行指引
│   └── requirements.txt
├── projects/             # 4 个综合项目
│   ├── 25_qa_agent/
│   ├── 26_rag_kb/
│   ├── 27_research_assistant/
│   └── 28_llm_gateway/
├── docker-compose.yml    # 依赖服务（Qdrant / Redis / Postgres）
├── pyproject.toml        # 统一依赖（uv workspace）
├── .python-version
└── .env.example
```

## 快速开始

```bash
# 1. 安装 uv（如果还没装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安装依赖
cd agent-book-code
uv sync

# 3. 启动依赖服务
docker compose up -d

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY 等

# 5. 运行某一章示例
uv run python ch01/01_basic.py
```

## 章节与代码对照表

| 章节 | 主题 | 关键文件 |
|---|---|---|
| Ch1 | Agent 时代软件工程 | `01_basic.py`（5 行 Agent）、`02_levels.py` |
| Ch2 | Token/Context/Embedding | `01_tokenize.py`、`02_embedding.py` |
| Ch3 | Prompt Engineering | `01_structured.py`、`02_cot.py`、`03_capstone.py` |
| ... | ... | ... |
| Ch25 | QA Agent | `projects/25_qa_agent/` |

## 状态

- [x] Part 1（Ch1–Ch3）骨架
- [ ] Part 2（Ch4–Ch7）待创建
- [ ] Part 3（Ch8–Ch13）待创建
- [ ] Part 4（Ch14–Ch18）待创建
- [ ] Part 5（Ch19–Ch24）待创建
- [ ] Part 6（Ch25–Ch28）项目骨架已建立
