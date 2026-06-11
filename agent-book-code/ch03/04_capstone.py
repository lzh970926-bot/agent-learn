"""
Ch3.4｜综合：金融分析助手 Prompt 模板库

特性：
- 模块化：Role/Task/Context/Format/Constraint 分文件管理
- 可版本化：每个模板带版本号
- 可灰度：同一任务多个 Prompt 变体，A/B 测试
"""
from openai import OpenClient
from dataclasses import dataclass, field
from typing import Dict
import os

# 注意：实际项目用 OpenAI()，这里改名为演示 import
from openai import OpenAI as OpenClient

client = OpenClient(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class PromptVersion:
    """Prompt 版本管理"""
    version: str
    template: str
    description: str
    metrics: Dict[str, float] = field(default_factory=dict)
    # 例如: {"accuracy": 0.85, "avg_tokens": 320, "user_satisfaction": 4.2}


# === Prompt 模板库 ===
FINANCIAL_ANALYSIS_PROMPTS = {
    "v1.0_basic": PromptVersion(
        version="1.0",
        template="""
        分析 {company} 的财报，给出投资建议。
        """,
        description="最简版",
    ),
    "v2.0_structured": PromptVersion(
        version="2.0",
        template="""
        # Role
        你是一名 CFA 持证分析师，专注 {industry} 行业 10 年。

        # Task
        基于 {company} 提供的财报数据，进行财务健康度分析。

        # Context
        行业：{industry}
        财报期间：{period}
        核心数据：{financial_data}

        # Output Format
        输出 JSON：
        {{
          "health_score": <0-100>,
          "key_findings": [<不超过 3 条>],
          "risks": [<不超过 2 条>],
          "investment_advice": "<买/观望/卖>"
        }}

        # Constraint
        - 引用数据必须来自提供的财报
        - 不确定时明确说"数据不足"
        - 避免情绪化措辞
        """,
        description="结构化 + JSON 输出",
        metrics={"accuracy": 0.87, "avg_tokens": 280},
    ),
    "v3.0_cot": PromptVersion(
        version="3.0",
        template="""
        # Role
        你是一名 CFA 持证分析师...

        # Task
        基于以下财报，先做推理链分析，再给出结论。

        # Reasoning Steps
        1. 计算 3 大比率（毛利率、ROE、负债率）
        2. 与行业平均对比
        3. 识别异常项
        4. 综合判断

        # Context
        {financial_data}

        # Output Format
        先输出推理过程，再输出 JSON 结论。
        """,
        description="加入 CoT 推理",
        metrics={"accuracy": 0.92, "avg_tokens": 450},  # 准确率↑ 但 token 也↑
    ),
}


class PromptRegistry:
    """Prompt 注册中心，支持灰度和 A/B"""

    def __init__(self):
        self.prompts: Dict[str, PromptVersion] = {}
        self.traffic_split: Dict[str, float] = {}

    def register(self, task: str, version_name: str, prompt: PromptVersion):
        self.prompts[f"{task}::{version_name}"] = prompt

    def set_traffic(self, task: str, splits: Dict[str, float]):
        """设置流量分配，如 {"v2.0": 0.7, "v3.0": 0.3}"""
        assert abs(sum(splits.values()) - 1.0) < 0.01, "流量和必须为 1"
        self.traffic_split[task] = splits

    def pick(self, task: str) -> PromptVersion:
        """根据流量分配选择版本"""
        import random
        splits = self.traffic_split.get(task, {})
        versions = list(splits.keys())
        weights = list(splits.values())
        chosen = random.choices(versions, weights=weights, k=1)[0]
        return self.prompts[f"{task}::{chosen}"]


def demo_financial_analysis():
    """演示金融分析助手的两种 Prompt 效果对比"""
    registry = PromptRegistry()

    for v_name, prompt in FINANCIAL_ANALYSIS_PROMPTS.items():
        registry.register("financial_analysis", v_name, prompt)

    registry.set_traffic("financial_analysis", {"v2.0_structured": 0.5, "v3.0_cot": 0.5})

    # 模拟数据
    context = {
        "company": "阿里巴巴",
        "industry": "电商",
        "period": "2024 Q3",
        "financial_data": "营收 2365 亿，YoY +5%；净利润 439 亿，YoY -9%...",
    }

    # 灰度调用
    for i in range(3):
        chosen = registry.pick("financial_analysis")
        print(f"\n--- 调用 #{i+1}: 使用 {chosen.version} ---")
        prompt = chosen.template.format(**context)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        print(resp.choices[0].message.content[:200] + "...")


if __name__ == "__main__":
    demo_financial_analysis()


# TODO(作者)：接入 Langfuse 记录每次调用的 Prompt/Response/Metrics
# TODO(作者)：实现自动 Prompt 优化（DSPy 风格）
