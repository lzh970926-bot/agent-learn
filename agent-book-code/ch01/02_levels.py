"""
Ch1.2｜Agent 自主性等级演示（L0 → L3）

本文件用同一个"问今天天气"任务，演示 4 个等级的差异。
"""
from openai import OpenAI
import os
from typing import Callable

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === Level 0：纯 LLM，无外部能力 ===
def level0_pure_llm(question: str) -> str:
    """L0：只能回答训练数据中的问题。问今天天气 = 编造。"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}],
    )
    return resp.choices[0].message.content


# === Level 1：单工具调用 ===
def get_weather(city: str) -> str:
    """模拟天气工具（实际可接入 wttr.in / OpenWeatherMap）"""
    # TODO(作者)：替换为真实 API
    return f"{city} 今日晴，25°C"


def level1_single_tool(question: str) -> str:
    """L1：人工决定何时调工具，无循环。"""
    if "天气" in question:
        city = question.split("天气")[0].strip() or "北京"
        weather = get_weather(city)
        prompt = f"用户问题：{question}\n实时数据：{weather}\n请回答。"
        return level0_pure_llm(prompt)
    return level0_pure_llm(question)


# === Level 2：多工具 + ReAct 循环 ===
TOOLS: dict[str, Callable] = {
    "get_weather": get_weather,
    # TODO(作者)：添加 calculator、web_search 等
}

REACT_PROMPT = """你是一个 Agent，可以通过工具行动。
可用工具：
- get_weather(city: str): 查询天气

格式要求：
Thought: 你的思考
Action: 工具名(参数)
Observation: 工具返回结果
... 重复直到能给出 Final Answer
Final Answer: 最终答案

问题：{question}
"""


def level2_react(question: str, max_steps: int = 5) -> str:
    """L2：让 LLM 自己决定调什么工具，循环直到 Final Answer。"""
    history = REACT_PROMPT.format(question=question)
    for step in range(max_steps):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": history}],
        ).choices[0].message.content

        history += f"\n{resp}"

        if "Final Answer:" in resp:
            return resp.split("Final Answer:")[-1].strip()

        # 解析 Action（生产环境用 OutputParser 更稳健）
        if "Action:" in resp:
            action_line = [l for l in resp.split("\n") if l.startswith("Action:")][0]
            action = action_line.replace("Action:", "").strip()
            tool_name, arg = action.split("(", 1)
            arg = arg.rstrip(")").strip().strip('"')
            observation = TOOLS[tool_name](arg)
            history += f"\nObservation: {observation}\n"

    return history  # 超过最大步数


# === Level 3：规划 + 执行 + 反思 ===
def level3_plan_execute(goal: str) -> str:
    """L3：先规划，再逐步执行，每步可反思。
    完整实现见 ch15_plan_execute.py
    """
    # TODO(作者)：实现 Planner → Executor → Reflector 三段
    raise NotImplementedError("见 ch15")


if __name__ == "__main__":
    q = "上海天气怎么样？"

    print("=" * 50)
    print("L0（无工具）:")
    print(level0_pure_llm(q))

    print("\n" + "=" * 50)
    print("L1（人工触发工具）:")
    print(level1_single_tool(q))

    print("\n" + "=" * 50)
    print("L2（ReAct 自主循环）:")
    print(level2_react(q))
