"""
FastAPI 异步任务入口
"""
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(title="Research Assistant")


class ResearchRequest(BaseModel):
    topic: str
    user_id: str


class ResearchResponse(BaseModel):
    task_id: str
    status: str


@app.post("/research", response_model=ResearchResponse)
async def start_research(req: ResearchRequest):
    """启动研究任务（异步）"""
    # TODO(作者）：用 Celery / RQ / Arq 调度
    # 1. 创建 task_id
    # 2. 后台执行 crew.kickoff()
    # 3. 状态写入 DB
    raise NotImplementedError


@app.get("/research/{task_id}")
async def get_status(task_id: str):
    """查询任务状态"""
    # TODO(作者）：从 DB / Redis 读取状态
    raise NotImplementedError


# TODO(作者）：WebSocket 推送进度
# TODO(作者）：支持任务中断与恢复
