"""
Ch2.4｜综合：Token 成本计算器

功能：
- 输入文本/Token 数
- 选择模型
- 估算单次/日均/月均成本
- 支持缓存命中场景
"""
from dataclasses import dataclass
import tiktoken


@dataclass
class ModelPricing:
    name: str
    input_per_1m: float   # 美元 / 1M tokens
    output_per_1m: float
    cache_discount: float  # 缓存命中折扣 (0~1)


MODELS = {
    "gpt-4o":          ModelPricing("gpt-4o", 2.5, 10.0, 0.5),
    "gpt-4o-mini":     ModelPricing("gpt-4o-mini", 0.15, 0.6, 0.5),
    "gpt-4-turbo":     ModelPricing("gpt-4-turbo", 10.0, 30.0, 0.5),
    "claude-3.5-sonnet": ModelPricing("claude-3.5-sonnet", 3.0, 15.0, 0.1),
}


def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """使用 tiktoken 估算（Claude 用近似公式）"""
    if model.startswith("claude"):
        # Claude 近似：1 token ≈ 3.5 字符
        return len(text) // 3
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


@dataclass
class CostEstimate:
    single_call: float
    daily: float
    monthly: float
    with_cache: float


def estimate(
    input_text: str,
    expected_output_tokens: int,
    model: str,
    daily_calls: int,
    cache_hit_rate: float = 0.0,
) -> CostEstimate:
    """成本估算器"""
    pricing = MODELS.get(model)
    if not pricing:
        raise ValueError(f"未知模型: {model}")

    input_tokens = count_tokens(input_text, model)
    cache_discount = pricing.cache_discount * cache_hit_rate

    # 单次成本（输入 + 输出 - 缓存折扣）
    input_cost = input_tokens * pricing.input_per_1m / 1_000_000
    output_cost = expected_output_tokens * pricing.output_per_1m / 1_000_000
    single = (input_cost + output_cost) * (1 - cache_discount)

    daily = single * daily_calls
    monthly = daily * 30

    return CostEstimate(
        single_call=single,
        daily=daily,
        monthly=monthly,
        with_cache=single * daily_calls * (1 - cache_hit_rate * 0.5),
    )


def format_estimate(est: CostEstimate) -> str:
    return f"""
    📊 成本估算
    ────────────────────────────────
    单次调用:       ${est.single_call:.6f}
    日均 ({est.daily:.0f} 次):  ${est.daily:.4f}
    月均:           ${est.monthly:.2f}
    缓存优化后:     ${est.with_cache:.4f}/日
    """


if __name__ == "__main__":
    sample_text = "请基于以下财报数据，分析公司 Q3 的财务健康状况..." * 50

    est = estimate(
        input_text=sample_text,
        expected_output_tokens=1000,
        model="gpt-4o",
        daily_calls=10_000,
        cache_hit_rate=0.3,
    )
    print(format_estimate(est))

    # 选型对比
    print("\n📈 模型选型对比 (相同输入):")
    for model in MODELS:
        e = estimate(sample_text, 1000, model, 10_000, 0.3)
        print(f"  {model:20s}  ${e.monthly:8.2f}/月")


# TODO(作者)：接入实时 OpenAI Pricing API（如果有）
# TODO(作者)：添加"按角色计费"（系统提示 vs 用户消息 vs 助手响应）
