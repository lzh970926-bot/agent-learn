"""
可观测性：OpenTelemetry + 自定义指标
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram


# Prometheus 指标
REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total requests",
    ["tenant", "model", "status"],
)

TOKEN_USAGE = Counter(
    "gateway_tokens_total",
    "Token usage",
    ["tenant", "model", "type"],  # type: input/output
)

LATENCY = Histogram(
    "gateway_latency_seconds",
    "Request latency",
    ["tenant", "model", "stage"],  # stage: cache/router/provider
)

CACHE_HIT = Counter(
    "gateway_cache_hits_total",
    "Cache hits",
    ["tenant", "type"],  # type: exact/semantic
)


def setup_tracing():
    """初始化 OpenTelemetry"""
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer("llm-gateway")


tracer = setup_tracing()

# TODO(作者）：集成 Langfuse（自动捕获 LLM 调用）
# TODO(作者）：添加慢查询日志（P99 告警）
# TODO(作者）：OpenTelemetry Auto-instrumentation（FastAPI / httpx / redis）
