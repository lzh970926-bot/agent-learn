"""
模型路由：按 tenant 配置选择模型
支持权重路由、灰度、fallback
"""
from dataclasses import dataclass


@dataclass
class ModelConfig:
    name: str
    provider: str       # openai / anthropic / vllm
    model_id: str
    weight: float = 1.0  # 权重
    fallback: str | None = None


class ModelRouter:
    """模型路由器"""

    def __init__(self):
        self.routes: dict[str, list[ModelConfig]] = {}  # tenant -> [models]

    def add_route(self, tenant_id: str, models: list[ModelConfig]):
        self.routes[tenant_id] = models

    def select(self, tenant_id: str) -> ModelConfig:
        """按权重选择模型"""
        import random
        models = self.routes.get(tenant_id, [])
        if not models:
            raise ValueError(f"No route for tenant: {tenant_id}")

        weights = [m.weight for m in models]
        return random.choices(models, weights=weights, k=1)[0]

    # TODO(作者）：实现"按请求类型路由"（简单问题用 mini，复杂用 opus）
    # TODO(作者）：实现"按用户级别路由"（VIP 走 premium）
    # TODO(作者）：A/B 测试路由（同一 tenant 内分流）
