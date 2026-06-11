# Ch4｜Function Calling 与 Tool Use

> 本章目标：让 LLM 能"动手"——理解协议演进、工具描述工程、并行依赖调用、源码解读。

## 章节结构

| 节 | 内容 | 字数目标 |
|---|---|---|
| 4.1 | 协议演进：从 ReAct 到 MCP | 1500 |
| 4.2 | Function Calling 基础 | 2000 |
| 4.3 | 工具描述工程 | 1500 |
| 4.4 | 并行与依赖调用 | 1500 |
| 4.5 | 源码解读：BaseTool | 2000 |
| 4.6 | 5 工具个人助理 Agent | 1500 |
| 4.7 | 小结与思考 | 500 |

## 文件说明

- `01_basic_call.py`：第一次 Function Calling
- `02_advanced.py`：并行/依赖/错误处理
- `03_5_tools_agent.py`：5 工具个人助理
- `tests/test_tools.py`：工具测试

## 运行

```bash
export OPENAI_API_KEY=sk-...
uv run python ch04/01_basic_call.py
uv run python ch04/03_5_tools_agent.py
```

## 关键 takeaway

1. **Function Calling 是 2023 年的"iPhone 时刻"**——LLM 第一次有了"标准化的手脚"
2. **工具描述 = 给 LLM 看的"接口文档"**——name / description / parameters 决定调用准确性
3. **并行调用 = 多 LLM 调用合并**——3 个独立工具合并成 1 次 LLM 调用
