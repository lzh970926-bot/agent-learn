"""
Ch4.2｜Function Calling 进阶：并行、依赖、错误处理
"""
import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field
import time

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === 5 个工具 ===
def get_weather(city: str) -> str:
    return f"{city} 25°C 晴"


def calculator(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"错误: {e}"


def search_web(query: str) -> str:
    # 模拟搜索
    return f"关于 '{query}' 的 3 条结果..."


def read_file(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()[:2000]
    except Exception as e:
        return f"读取失败: {e}"


def send_email(to: str, subject: str, body: str) -> str:
    # 真实环境接 SMTP / SendGrid
    return f"邮件已发送到 {to}"


TOOLS_MAP = {
    "get_weather": get_weather,
    "calculator": calculator,
    "search_web": search_web,
    "read_file": read_file,
    "send_email": send_email,
}


# === OpenAI 工具定义 ===
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气。返回温度、湿度、天气状况。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "计算数学表达式，支持加减乘除和括号。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"},
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索互联网获取最新信息。适用于训练数据外的问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容。仅限文本文件，不超过 2000 字符。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件绝对路径"},
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "发送邮件给指定收件人。⚠️ 高风险操作，需要用户确认。",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "收件人邮箱"},
                    "subject": {"type": "string", "description": "邮件主题"},
                    "body": {"type": "string", "description": "邮件正文"},
                },
                "required": ["to", "subject", "body"],
            },
        },
    },
]


def execute_tool_call(tool_call) -> str:
    """执行单个工具调用，带重试"""
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if name not in TOOLS_MAP:
        return f"错误：未知工具 {name}"

    # 重试机制
    for attempt in range(3):
        try:
            return TOOLS_MAP[name](**args)
        except Exception as e:
            if attempt == 2:
                return f"工具 {name} 调用失败（重试 3 次）: {e}"
            time.sleep(0.5 * (attempt + 1))


def run_agent(user_input: str, max_steps: int = 5) -> str:
    """支持多步调用的 Agent"""
    messages = [{"role": "user", "content": user_input}]

    for step in range(max_steps):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        messages.append(msg)

        # 没有 tool_call，结束
        if not msg.tool_calls:
            return msg.content

        # 并行执行所有 tool_calls
        print(f"\n--- Step {step + 1} ---")
        print(f"🤖 LLM 调用 {len(msg.tool_calls)} 个工具:")
        for tc in msg.tool_calls:
            print(f"   - {tc.function.name}({tc.function.arguments})")

        for tool_call in msg.tool_calls:
            result = execute_tool_call(tool_call)
            print(f"   ✓ 结果: {result[:100]}")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    return "[达到最大步数]"


if __name__ == "__main__":
    # 演示 1：单工具调用
    print("=== 示例 1：单工具 ===")
    print(run_agent("上海天气怎么样？"))

    # 演示 2：依赖调用（先算再总结）
    print("\n=== 示例 2：依赖调用 ===")
    print(run_agent("23 * 47 + 156 等于多少？把答案乘以 2"))

    # 演示 3：并行调用（理论上可）
    print("\n=== 示例 3：需要调工具的问题 ===")
    print(run_agent("查一下上海和北京今天的天气"))


# TODO(作者)：实现"依赖调用"模式（第一次结果决定第二次调用）
# TODO(作者)：加入高风险操作的二次确认（send_email）
# TODO(作者)：添加 token 计数和成本监控
