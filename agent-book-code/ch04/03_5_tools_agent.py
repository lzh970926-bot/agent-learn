"""
Ch4.3｜综合实战：5 工具个人助理 Agent

支持：
- get_weather：天气查询
- calculator：数学计算
- search_web：网络搜索
- read_file：文件读取
- send_email：发送邮件（需确认）

特性：
- 并行调用
- 错误恢复
- 高风险操作确认
"""
import json
import os
from openai import OpenAI
from typing import Literal
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === 工具实现（同 02_advanced.py）===
def get_weather(city: str) -> str:
    return f"{city} 25°C 晴，湿度 45%"

def calculator(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"错误: {e}"

def search_web(query: str) -> str:
    return f"关于 '{query}' 的 3 条最新结果..."

def read_file(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()[:2000]
    except Exception as e:
        return f"读取失败: {e}"

# ⚠️ 高风险操作：实际发送需要用户确认
def send_email(to: str, subject: str, body: str, confirmed: bool = False) -> str:
    if not confirmed:
        return f"⚠️ 邮件待发送（需要用户确认）:\n  收件人: {to}\n  主题: {subject}\n  正文: {body[:100]}..."
    return f"✓ 邮件已发送到 {to}"


TOOLS_MAP = {
    "get_weather": get_weather,
    "calculator": calculator,
    "search_web": search_web,
    "read_file": read_file,
    "send_email": send_email,
}

# 高风险工具列表
HIGH_RISK_TOOLS = {"send_email", "delete_account", "transfer_money"}


# === 工具 schema ===
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气。",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式。",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索互联网。",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件。",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "发送邮件（高风险，需要用户确认）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]


def run_personal_assistant(user_input: str, user_confirm: bool = False) -> str:
    """
    5 工具个人助理 Agent
    user_confirm: 是否允许执行高风险操作
    """
    messages = [{"role": "user", "content": user_input}]

    for step in range(8):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        print(f"\n--- Step {step + 1} ---")
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            name = tc.function.name

            # 高风险工具拦截
            if name in HIGH_RISK_TOOLS and not user_confirm:
                # 给 LLM 一个"需要确认"的响应
                result = (
                    f"⚠️ 工具 {name} 是高风险操作。请先询问用户确认。"
                    f"参数: {args}"
                )
                print(f"   ⚠️ 拦截高风险操作: {name}")
            else:
                # 正常执行
                print(f"   ✓ {name}({args})")
                try:
                    result = TOOLS_MAP[name](**args, **(dict(confirmed=user_confirm) if name == "send_email" else {}))
                except Exception as e:
                    result = f"执行错误: {e}"

            print(f"     → {result[:100]}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return "[达到最大步数]"


if __name__ == "__main__":
    # 示例 1：低风险组合
    print("=== 示例 1：低风险（天气+计算）===")
    print(run_personal_assistant("查上海天气，然后把温度乘以 2"))

    # 示例 2：高风险（邮件）
    print("\n=== 示例 2：高风险（邮件）— 未确认 ===")
    print(run_personal_assistant("给 boss@example.com 发邮件，主题'周报'，内容'本周完成 X'", user_confirm=False))

    print("\n=== 示例 3：高风险（邮件）— 已确认 ===")
    print(run_personal_assistant("给 boss@example.com 发邮件，主题'周报'，内容'本周完成 X'", user_confirm=True))


# TODO(作者)：实现"工具调用历史"的可视化
# TODO(作者)：添加成本监控（每步 Token 累计）
# TODO(作者)：用 LangGraph 重构（带 Checkpointer）
