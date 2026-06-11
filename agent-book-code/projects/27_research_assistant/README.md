# 项目 27｜多 Agent 研究助手

> Ch27 综合项目：自动完成「选题 → 调研 → 写作 → 审核」的研究助手

## 目标

构建一个由 4 个 Agent 协作的研究助手：
- **Researcher**：搜索资料、整理文献
- **Writer**：基于资料撰写文章
- **Editor**：审核、修改、润色
- **Coordinator**：协调 3 者，分配任务

## 技术栈

- CrewAI（多 Agent 协作）
- LangGraph（状态持久化）
- Langfuse（观测 + 调试）
- PostgreSQL（Checkpointer）
- Tavily（搜索）

## 目录结构

```
27_research_assistant/
├── src/
│   ├── agents/         # Agent 定义
│   ├── workflows/      # 协作流程
│   ├── tools/          # 工具
│   └── api/            # FastAPI
├── tests/
└── pyproject.toml
```

## 协作流程

```
用户请求 → Coordinator 分发
            ├── Researcher (并行)
            ├── Writer (依赖 Researcher)
            └── Editor (依赖 Writer)
         → 最终输出
```

## 核心模块

- [ ] `agents/researcher.py`：研究 Agent
- [ ] `agents/writer.py`：写作 Agent
- [ ] `agents/editor.py`：编辑 Agent
- [ ] `workflows/crew.py`：CrewAI Crew 定义
- [ ] `workflows/state.py`：任务状态管理
- [ ] `api/main.py`：异步任务 API

## 验收指标

- 研究深度评分 > 4/5（LLM-as-Judge）
- 人机协作延迟 < 2s
- 任务可中断恢复（Postgres checkpointer）
