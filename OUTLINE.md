# 详细大纲

> 写作约定：每章约 8000–12000 字，源码解读 1–2 处，代码示例 3–5 个，思考题 3–5 道。
> 章节内部统一采用「概念 → 原理 → 源码 → 实践 → 小结」五段式结构。

---

## Part 1：基础篇

建立 LLM 与 Agent 的共同语言。

### Ch1｜大模型 Agent 时代的软件工程
- LLM 能力边界：能做什么、不能做什么
- 从 Copilot 到 Agent：自主性等级光谱（Level 0–5）
- Agent 系统的典型形态：聊天机器人、RAG、Workflow、Autonomous Agent
- 为什么需要新架构：Context Window、Tool Use、Stateful Execution
- **实战**：5 行代码实现第一个 Agent（ReAct 循环）

### Ch2｜核心概念：Token、Context、Embedding
- Tokenization：GPT 系 BPE、Claude 系 SentencePiece
- Context Window：长上下文误区、信息位置偏差（Lost in the Middle）
- Embedding：Cosine Similarity、MTEB 基准、模型选型矩阵
- Temperature、Top-p、Top-k：解码策略对 Agent 行为的影响
- **源码解读**：`tiktoken` 的 BPE 编码流程
- **实战**：可视化 Token、Embedding 相似度热力图

### Ch3｜Prompt Engineering 进阶
- 结构化 Prompt：Role / Task / Context / Format / Constraint
- 推理增强：Chain-of-Thought、Self-Consistency、Tree of Thoughts
- 防御性 Prompt：Delimiter、XML Tag、JSON Mode
- Prompt 版本管理：代码化、灰度、A/B
- **实战**：用 Prompt 模板构建可复用的「金融分析助手」

---

## Part 2：核心能力篇

Agent 三大核心能力：**工具使用、知识增强、记忆**。

### Ch4｜Function Calling 与 Tool Use
- 协议演进：ReAct 文本格式 → OpenAI JSON Schema → Anthropic Tool Use → MCP
- 工具描述工程：name、description、parameters 三要素
- 并行调用、依赖调用、错误处理
- **源码解读**：`langchain_core.tools.BaseTool` 的定义与执行流
- **实战**：实现一个支持 5 个工具的「个人助理 Agent」

### Ch5｜RAG 原理：检索、增强、生成
- 朴素 RAG：Embed → Retrieve → Stuff
- Advanced RAG：Pre-Retrieval（Query Rewrite / HyDE）、Post-Retrieval（Rerank / Compression）
- Modular RAG：可插拔的检索-生成管线
- 评估：检索 Recall@k、生成 Faithfulness、Answer Relevancy（RAGAS）
- **实战**：从 0 到 1 实现一个朴素 RAG，并对比 Advanced RAG 效果

### Ch6｜向量数据库与混合检索
- 向量索引：HNSW、IVF、PQ
- 主流系统对比：Chroma、Milvus、Qdrant、Weaviate、Pinecone
- 混合检索：BM25 + Dense、Reciprocal Rank Fusion（RRF）
- 元数据过滤、多租户隔离
- **源码解读**：`langchain_community.vectorstores` 的接口设计
- **实战**：用 Qdrant 搭建支持混合检索的知识库

### Ch7｜Memory 机制与状态管理
- Memory 分类：Short-term（Buffer / Window / Summary）、Long-term（Vector / Entity）、Episodic
- LangChain Memory 抽象的演进（已废弃到 LCEL 重写）
- **源码解读**：`ConversationBufferWindowMemory` 实现
- 状态持久化：Redis、PostgreSQL、Checkpointer
- **实战**：为对话 Agent 实现「短期摘要 + 长期实体」混合记忆

---

## Part 3：框架原理篇

深入 LangChain、LangGraph、LlamaIndex、AutoGen 的核心抽象与源码。

### Ch8｜LangChain 核心抽象：Runnable 与 LCEL
- 为什么需要 `Runnable`：函数式 + 流式 + 可组合
- LCEL 表达式：`prompt | model | parser`
- `RunnableParallel`、`RunnablePassthrough`、`RunnableLambda`
- **源码解读**：`langchain_core.runnables.base.RunnableSequence` 的 `invoke` / `stream` / `batch`
- **实战**：用 LCEL 重构「翻译 + 摘要 + 改写」管线

### Ch9｜LangChain 核心模块源码导读
- `BaseChatModel`：`generate` vs `agenerate`、Callback 事件总线
- `BaseRetriever`：同步/异步、批量检索
- `OutputParser`：`PydanticOutputParser`、`JsonOutputParser`、`RetryOutputParser`
- Callback 系统：on_llm_start、on_chain_end、Tracing
- **源码解读**：`ChatOpenAI._stream` 的流式实现
- **实战**：自定义一个输出解析器，带自动重试

### Ch10｜LangGraph 状态图与有状态 Agent
- 为什么需要 LangGraph：循环、持久化、人机协作
- 核心概念：State、Node、Edge、Conditional Edge
- Checkpointer：MemorySaver、SqliteSaver、PostgresSaver
- 人机协作：`interrupt()`、`Command`
- **源码解读**：`langgraph.graph.StateGraph.compile` 与 Pregel 执行模型
- **实战**：构建一个带「计划 → 执行 → 审核 → 重试」状态机

### Ch11｜LlamaIndex 索引体系与 QueryEngine
- 索引类型：VectorIndex、SummaryIndex、TreeIndex、KeywordTableIndex、KnowledgeGraphIndex
- IngestionPipeline：Reader → Transform → Embed → Store
- QueryEngine vs ChatEngine vs SubQuestionQueryEngine
- **源码解读**：`BaseRetriever` 与 `ResponseSynthesizer` 的协作
- **实战**：用 LlamaIndex 构建多模态文档问答

### Ch12｜LlamaIndex Workflows：事件驱动编排
- Workflow 概念：Step、Event、Context
- `Workflow.run` / `Workflow.stream_events`
- 与 LangGraph 对比：事件驱动 vs 状态图
- **源码解读**：`@step` 装饰器与事件循环
- **实战**：实现一个支持「流式输出 + 中断恢复」的研究 Workflow

### Ch13｜多 Agent 框架对比：AutoGen / CrewAI / Swarm
- AutoGen：ConversableAgent、GroupChat、UserProxy
- CrewAI：Role / Task / Crew、Process（Sequential / Hierarchical）
- OpenAI Swarm：轻量级 Handoff
- 选型矩阵：复杂度、可控性、可观测性、生态
- **源码解读**：AutoGen 的 GroupChat 消息路由
- **实战**：用 CrewAI 实现「研究员 + 工程师 + 审核员」协作

---

## Part 4：Agent 设计模式篇

五大经典模式，每个模式给出**适用场景 + 代码骨架 + 实战变体**。

### Ch14｜ReAct：思考-行动循环
- 论文解读：ReAct（Yao et al. 2022）
- LangChain `create_react_agent` 实现
- 变体：ReAct + Memory、ReAct + Reflection
- **实战**：从 0 实现一个 ReAct Agent（不依赖框架）

### Ch15｜Plan-and-Execute：规划与执行分离
- 论文解读：Plan-and-Solve（Wang et al. 2023）
- Planner 拆解任务 → Executor 串行/并行执行 → Replanner 动态调整
- 与 LangGraph 结合：有状态的任务流
- **实战**：实现「多步研究任务」自动规划与执行

### Ch16｜Multi-Agent 协作模式
- 协作拓扑：Star、Ring、Hierarchical、Mesh
- 通信机制：共享消息总线、独立 Channel
- 冲突解决：投票、优先级、上级裁决
- **实战**：构建「产品 + 开发 + 测试」三角协作

### Ch17｜Reflection 与 Self-Critique
- 论文解读：Reflexion（Shinn et al. 2023）、CRITIC
- 实现路径：Self-Evaluation、External Critic、Tool-based Verification
- 与 Re-Rank 结合：生成多个候选 → 评分 → 选最优
- **实战**：为「代码生成 Agent」添加 Reflection 循环

### Ch18｜Agentic RAG 与自适应检索
- 从 RAG 到 Agentic RAG：何时检索、检索什么、如何处理「检索不到」
- Self-RAG、Adaptive-RAG、CRAG
- 工具化检索：Search、SQL、API、计算器
- **实战**：实现一个「判断 → 检索 → 评估 → 重试」的 Agentic RAG

---

## Part 5：工程架构篇

从 Demo 到生产的关键跨越。

### Ch19｜可观测性：链路追踪与调试
- 为什么传统 APM 不够：LLM 应用的非确定性
- OpenTelemetry + GenAI SemConv
- 工具对比：LangSmith、Langfuse、Phoenix、Helicone、Datadog LLM Observability
- 日志设计：Prompt、Response、Token、Latency、Cost
- **实战**：用 Langfuse 为 Agent 系统接入全链路追踪

### Ch20｜高可用设计：限流、熔断、降级
- LLM API 的特殊性：Rate Limit、Quota、不可重试错误
- 多模型路由：主备、负载均衡、灰度
- 降级策略：缓存兜底、小模型兜底、静态响应
- 幂等性：请求 ID、状态机
- **实战**：用 Resilience4j 思想实现 LLM 调用的熔断器

### Ch21｜性能优化：成本与延迟
- 延迟优化：流式响应、并行工具调用、Prefetch
- 成本优化：模型分级、Prompt 压缩、Context 裁剪、Embedding 缓存
- 监控指标：TTFT、TPOT、TPS、$/1k 请求
- **实战**：通过 4 项优化把 P99 延迟从 8s 降到 2s

### Ch22｜安全：Prompt Injection 与防御
- 攻击分类：Direct Injection、Indirect Injection、Jailbreak
- 防御层次：输入侧（Delimiter / 隔离上下文）、系统侧（权限最小化）、输出侧（Schema 校验 / Guardrails）
- 工具调用安全：白名单、参数校验、副作用隔离
- **实战**：实现多层 Prompt Injection 防护体系

### Ch23｜测试与评估体系
- 单元测试：工具函数、解析器、Prompt 模板
- 集成测试：Agent 行为快照、Replaying
- 评估指标：Correctness、Hallucination、Toxicity、Helpfulness
- 评估框架：LangSmith Evaluator、DeepEval、RAGAS
- 数据集管理：Golden Set、合成数据、用户反馈回流
- **实战**：搭建 LLM-as-Judge 评估流水线

### Ch24｜LLM 网关设计
- 为什么需要 LLM Gateway：统一鉴权、模型路由、成本核算、可观测
- 架构：BFF → Gateway → Provider，插件化设计
- 核心能力：Routing、Cache（精确/语义）、Fallback、Quota、Budget
- 选型对比：Portkey、OpenRouter、Helicone、Cloudflare AI Gateway
- **实战**：基于 FastAPI + Redis 实现一个轻量级 LLM Gateway

---

## Part 6：实战项目篇

4 个递进式综合项目，覆盖个人工具到企业平台。

### Ch25｜项目一：工具增强问答 Agent
- 目标：构建支持 Web 搜索、计算器、文件读取的问答 Agent
- 技术栈：LangChain + LangGraph + Tavily + Streamlit
- 核心难点：工具选择准确性、错误恢复
- 验收指标：工具选择准确率 > 90%、端到端成功率 > 85%

### Ch26｜项目二：企业级 RAG 知识库
- 目标：支持 PDF/Word/Markdown 混合文档、多租户、增量更新
- 技术栈：LlamaIndex + Qdrant + FastAPI + Next.js
- 核心难点：混合检索、权限隔离、增量索引
- 验收指标：检索 Recall@5 > 0.85、Faithfulness > 0.9

### Ch27｜项目三：多 Agent 研究助手
- 目标：自动完成「选题 → 调研 → 写作 → 审核」全流程
- 技术栈：CrewAI + LangGraph + Langfuse + Postgres
- 核心难点：Agent 间消息路由、状态持久化、人类反馈接入
- 验收指标：研究深度评分 > 4/5、人机协作延迟 < 2s

### Ch28｜项目四：生产级 LLM 网关
- 目标：支持 10+ 模型、多租户配额、语义缓存、全链路可观测
- 技术栈：FastAPI + Redis + PostgreSQL + OpenTelemetry + Prometheus
- 核心难点：高并发、灰度发布、成本核算
- 验收指标：P99 < 500ms、QPS 200、可用性 99.9%

---

## Part 7：前沿与展望

### Ch29｜协议与生态：MCP、A2A、AG-UI
- MCP（Model Context Protocol）：工具调用的标准化
- A2A（Agent-to-Agent）：跨框架 Agent 通信
- AG-UI：Agent 与前端交互协议
- 生态影响：从框架之争走向协议之争

### Ch30｜未来趋势与思考
- 能力演进：更长 Context、Tool Use 能力、Reasoning 模型
- Agent 与工作流：边界与融合
- AGI 之路：弱 Agent → 强 Agent → 自主智能体
- 工程师的成长：保持「第一性原理 + 工程实践」双轮驱动

---

## 附录

- 附录 A：环境配置（Python 3.11、uv、Docker、常用 API Key）
- 附录 B：术语表
- 附录 C：推荐阅读（论文、博客、开源项目）
- 附录 D：示例代码仓库（GitHub 链接）
