"""
Ch3.1｜5 要素 Prompt 模板

任何复杂 Prompt 都可以拆解为：
Role：你是什么
Task：做什么
Context：背景信息
Format：输出格式
Constraint：约束条件
"""
from openai import OpenAI
import os
from dataclasses import dataclass

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@dataclass
class PromptTemplate:
    """5 要素 Prompt 模板"""
    role: str
    task: str
    context: str = ""
    format: str = ""
    constraint: str = ""

    def render(self) -> str:
        parts = [
            f"# Role\n{self.role}",
            f"# Task\n{self.task}",
        ]
        if self.context:
            parts.append(f"# Context\n{self.context}")
        if self.format:
            parts.append(f"# Output Format\n{self.format}")
        if self.constraint:
            parts.append(f"# Constraint\n{self.constraint}")
        return "\n\n".join(parts)


# === 演示 1：反例（4 要素缺失）===
BAD_PROMPT = "帮我写个周报"  # 缺 Role/Context/Format/Constraint


# === 演示 2：正例（5 要素齐全）===
GOOD_PROMPT = PromptTemplate(
    role="你是一名资深产品经理，擅长用 OKR 框架总结工作",
    task="基于本周完成的工作，撰写一份周报",
    context="""
    本周完成：
    1. 完成用户调研 5 场
    2. 输出 v2.0 PRD 评审
    3. 与研发对齐 3 次技术方案
    """,
    format="""
    包含以下部分：
    - 本周 OKR 进度（百分比）
    - 关键产出（不超过 5 条 bullet）
    - 下周计划（不超过 3 条）
    - 风险与需要的支持
    """,
    constraint="""
    - 总字数不超过 500 字
    - 用 markdown 格式
    - 避免空话套话，必须有具体数据
    """,
).render()


def compare_bad_vs_good():
    """对比 4 要素缺失 vs 5 要素齐全的输出差异"""
    print("=" * 60)
    print("❌ 反例 Prompt:")
    print(BAD_PROMPT)
    print("\n✅ 正例 Prompt:")
    print(GOOD_PROMPT)
    print("=" * 60)

    # 实际调用
    bad_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": BAD_PROMPT}],
    ).choices[0].message.content

    good_resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": GOOD_PROMPT}],
    ).choices[0].message.content

    print("\n--- 反例输出 ---")
    print(bad_resp)
    print("\n--- 正例输出 ---")
    print(good_resp)


if __name__ == "__main__":
    compare_bad_vs_good()


# TODO(作者)：在 3.1 节末尾加入"自动 Prompt 优化器"（基于反馈迭代）
# TODO(作者)：演示 Few-shot 模板（正例/反例各 2 个）
