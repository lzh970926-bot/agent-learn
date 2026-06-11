"""
FastAPI 问答接口
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    tenant_id: str
    query: str
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """问答接口"""
    # TODO(作者）：组合 retrieval + generation
    # 1. 检索
    # 2. 构建 prompt（带 source 引用）
    # 3. 调用 LLM
    # 4. 返回答案 + 来源
    raise NotImplementedError


# TODO(作者）：添加流式响应（SSE）
# TODO(作者）：添加权限校验（验证 tenant_id 合法性）
