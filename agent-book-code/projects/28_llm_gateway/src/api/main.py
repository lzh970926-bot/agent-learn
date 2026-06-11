"""
FastAPI 入口：OpenAI 兼容接口
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
from typing import Literal
import time

from ..routing.router import ModelRouter
from ..cache.semantic_cache import SemanticCache
from ..observability.tracing import REQUEST_COUNT, LATENCY, CACHE_HIT, TOKEN_USAGE

app = FastAPI(title="LLM Gateway", version="0.1.0")

# 全局实例（生产用 lifespan 管理）
router = ModelRouter()
cache: SemanticCache | None = None  # 在 startup 中初始化


class ChatRequest(BaseModel):
    model: str
    messages: list[dict]
    temperature: float = 1.0
    max_tokens: int | None = None
    stream: bool = False


class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    choices: list[dict]
    usage: dict


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(
    req: ChatRequest,
    authorization: str = Header(...),
):
    """OpenAI 兼容接口"""
    start = time.time()
    tenant_id = authorization  # 简化：实际应解析 JWT

    try:
        # 1. 缓存查找
        last_user = next((m for m in reversed(req.messages) if m["role"] == "user"), None)
        if last_user and not req.stream:
            cached = cache.get(last_user["content"]) if cache else None
            if cached:
                CACHE_HIT.labels(tenant=tenant_id, type="exact").inc()
                LATENCY.labels(tenant=tenant_id, model=req.model, stage="cache").observe(
                    time.time() - start
                )
                return cached

        # 2. 路由
        model_config = router.select(tenant_id)

        # 3. 调用 provider
        # TODO(作者）：根据 model_config.provider 调用 OpenAI / Anthropic / vLLM
        # response = await call_provider(model_config, req)

        # 4. 写缓存
        # if cache: cache.set(query, response_dict)

        # 5. 上报指标
        REQUEST_COUNT.labels(tenant=tenant_id, model=req.model, status="ok").inc()
        LATENCY.labels(tenant=tenant_id, model=req.model, stage="provider").observe(
            time.time() - start
        )

        # TODO(作者）：完整实现
        raise NotImplementedError

    except Exception as e:
        REQUEST_COUNT.labels(tenant=tenant_id, model=req.model, status="error").inc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


# TODO(作者）：/v1/models 列出可用模型
# TODO(作者）：管理 API：创建 tenant、设置配额、查看用量
# TODO(作者）：WebSocket 流式响应
# TODO(作者）：/metrics Prometheus 暴露
