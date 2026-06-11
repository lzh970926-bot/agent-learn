# 项目 25｜工具增强问答 Agent

> Ch25 综合项目：从 0 构建一个生产级 QA Agent

## 目标

构建一个支持 Web 搜索、计算器、文件读取 3 个工具的问答 Agent，覆盖：
- LangGraph 状态机
- 工具选择准确性
- 错误恢复
- 流式输出

## 技术栈

- LangChain + LangGraph
- OpenAI gpt-4o-mini
- Tavily（Web 搜索）
- Streamlit（前端）

## 目录结构

```
25_qa_agent/
├── src/
│   ├── agent.py        # Agent 主逻辑
│   ├── tools.py        # 工具实现
│   ├── state.py        # LangGraph State
│   └── ui.py           # Streamlit 界面
├── tests/
│   └── test_agent.py
├── pyproject.toml
└── README.md
```

## 核心代码占位

- [ ] `src/agent.py`：LangGraph StateGraph
- [ ] `src/tools.py`：search / calculator / file_reader
- [ ] `src/state.py`：MessagesState + 自定义字段
- [ ] `src/ui.py`：流式聊天界面

## 验收指标

- 工具选择准确率 > 90%（基于 100 题测试集）
- 端到端成功率 > 85%
- P99 响应延迟 < 5s
