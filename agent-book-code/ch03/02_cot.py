"""
Ch3.2｜推理增强：CoT、ToT、Self-Consistency
"""
from openai import OpenAI
import os
from collections import Counter

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === CoT: Chain of Thought ===
COT_PROMPT = """
问题：小明有 5 个苹果，他给了小红 2 个，又买了 3 个，现在有几个？

让我们一步步思考：
"""


def cot_solve(problem: str) -> str:
    """基础 CoT：让模型写出推理步骤"""
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"{problem}\n\n让我们一步步思考："}],
    ).choices[0].message.content


# === Zero-Shot CoT: "Let's think step by step" 魔法短语 ===
ZERO_SHOT_COT_SUFFIX = " Let's think step by step."


def zero_shot_cot(problem: str) -> str:
    """Zero-Shot CoT：仅靠"逐步思考"指令，无需示例"""
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": problem + ZERO_SHOT_COT_SUFFIX}],
    ).choices[0].message.content


# === Self-Consistency: 多次采样 + 投票 ===
def self_consistency(problem: str, n_samples: int = 5) -> tuple[str, list[str]]:
    """多次采样 + 多数投票，提升答案稳定性"""
    answers = []
    for _ in range(n_samples):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"{problem}\n\n让我们一步步思考："}],
            temperature=0.7,  # 高温度获得多样性
        ).choices[0].message.content
        # 提取最终答案（简化：取最后一个数字）
        import re
        nums = re.findall(r"\d+", resp.split("\n")[-1])
        answers.append(nums[-1] if nums else resp)

    most_common = Counter(answers).most_common(1)[0][0]
    return most_common, answers


# === ToT: Tree of Thoughts (BFS 框架) ===
def tree_of_thoughts(problem: str, branching: int = 3, depth: int = 2) -> str:
    """ToT：每步生成多个候选，评估后保留 Top-K

    完整实现见 ch18 高级 Agent 章节
    """
    # TODO(作者)：实现 BFS + LLM 评估
    # 当前为简化版
    raise NotImplementedError("见 ch18_agentic_rag.py")


if __name__ == "__main__":
    problem = """
    农场里有 15 只鸡和 8 只鸭。
    卖出 3 只鸡后，又买入 5 只鸭。
    现在鸡比鸭少多少只？
    """

    print("=== CoT ===")
    print(cot_solve(problem))

    print("\n=== Self-Consistency (5 次采样) ===")
    answer, samples = self_consistency(problem, n_samples=5)
    print(f"各次答案: {samples}")
    print(f"投票结果: {answer}")


# TODO(作者)：添加 ToT 的简化实现（BFS 框架）
# TODO(作者)：加入 GSM8K 数据集评测
