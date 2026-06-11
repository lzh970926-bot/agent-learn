"""
Ch1.1｜5 行代码的最小 Agent 循环

核心思想：Agent = LLM + 循环 + 工具
"""
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def minimal_agent(user_input: str) -> str:
    """最小可用 Agent：单轮 LLM 调用（Level 0）"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print(minimal_agent("用一句话解释什么是 LLM Agent"))
    # 预期输出：类似 "LLM Agent 是一个能感知环境、做出决策并执行动作的大模型应用..."


# TODO(作者)：在本节末尾扩展为 L1（多轮对话）和 L2（带工具调用）
