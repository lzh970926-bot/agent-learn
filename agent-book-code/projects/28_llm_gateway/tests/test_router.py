"""路由测试"""
import pytest
from projects.twenty_eight_llm_gateway.src.routing.router import ModelRouter, ModelConfig


def test_router_weighted_select():
    router = ModelRouter()
    router.add_route("tenant_a", [
        ModelConfig(name="fast", provider="openai", model_id="gpt-4o-mini", weight=0.8),
        ModelConfig(name="smart", provider="openai", model_id="gpt-4o", weight=0.2),
    ])

    # 1000 次采样，验证权重分布
    counts = {"fast": 0, "smart": 0}
    for _ in range(1000):
        m = router.select("tenant_a")
        counts[m.name] += 1

    assert 0.7 < counts["fast"] / 1000 < 0.9
    assert 0.1 < counts["smart"] / 1000 < 0.3


def test_router_unknown_tenant_raises():
    router = ModelRouter()
    with pytest.raises(ValueError):
        router.select("unknown_tenant")
