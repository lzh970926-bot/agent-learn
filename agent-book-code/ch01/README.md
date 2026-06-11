# Ch1｜大模型 Agent 时代的软件工程

> 本章目标：建立 Agent 系统的"共同语言"——自主性等级、核心组件、典型形态。

## 章节结构

| 节 | 内容 | 字数目标 |
|---|---|---|
| 1.1 | LLM 能力边界与软件工程新挑战 | 1000 |
| 1.2 | Agent 自主性等级（Level 0–5） | 1500 |
| 1.3 | Agent 系统的 4 种典型形态 | 1500 |
| 1.4 | 为什么需要新架构 | 1500 |
| 1.5 | 5 行代码实现第一个 Agent | 1500 |
| 1.6 | 进阶：从 L0 到 L3 的演进 | 1500 |
| 1.7 | 小结与思考 | 500 |

## 文件说明

- `01_basic.py`：5 行代码的最小 Agent 循环
- `02_levels.py`：演示 L0–L3 的不同自主性
- `03_capstone.py`：构建一个简单的工作流 Agent（含 Tool 调用）

## 运行

```bash
export OPENAI_API_KEY=sk-...
uv run python ch01/01_basic.py
```

## 思考题

- ★ L0 和 L3 的本质区别是什么？
- ★★ 如果把 LLM 换成规则引擎，"Agent" 还有意义吗？
- ★★★ 阅读 OpenAI 的 [A Practical Guide to Building Agents](https://cdn.openai.com/business-guides-and-tools/a-practical-guide-to-building-agents.pdf)，对比书中的分级是否一致。
