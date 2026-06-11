# 项目 28｜生产级 LLM 网关

> Ch28 综合项目：支持 10+ 模型、多租户配额、语义缓存、全链路可观测的 LLM 网关

## 目标

构建一个 OpenAI 兼容的 LLM API Gateway，作为企业内部 LLM 流量的统一入口。

## 核心能力

- **统一接口**：兼容 OpenAI Chat Completions API
- **多模型路由**：OpenAI、Anthropic、本地模型（vLLM）
- **多租户**：按 tenant 配额、限流
- **语义缓存**：精确缓存 + 语义缓存
- **灰度发布**：按比例切流量
- **可观测**：OpenTelemetry 集成，Langfuse 追踪
- **降级熔断**：失败自动 fallback

## 技术栈

- FastAPI（HTTP 服务）
- Redis（缓存 + 限流 + 配额）
- PostgreSQL（租户、审计日志）
- OpenTelemetry（链路追踪）
- Prometheus（指标）

## 目录结构

```
28_llm_gateway/
├── src/
│   ├── routing/        # 模型路由
│   ├── cache/          # 缓存（精确 + 语义）
│   ├── observability/  # 追踪 + 指标
│   └── api/            # FastAPI
├── tests/
└── pyproject.toml
```

## 架构图

```
Client → Gateway
            │
            ├── Auth (API Key → Tenant)
            ├── Rate Limit (Redis Token Bucket)
            ├── Cache Lookup (Redis + Qdrant)
            ├── Model Router (按 tenant 配置)
            ├── Provider Adapter (OpenAI/Anthropic/...)
            ├── Fallback (失败重试 / 降级)
            └── Observability (OTel + Langfuse)
```

## 验收指标

- P99 延迟 < 500ms（缓存命中 < 50ms）
- QPS 200+
- 可用性 99.9%
- 缓存命中率 > 30%
- Token 成本节省 > 40%（vs 直连）
