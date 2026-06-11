"""
Ch4.1｜第一次 Function Calling

从 0 演示 LLM 如何调用一个简单的 get_weather 工具
"""
import json
import os
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === 1. 用 Pydantic 定义工具参数 ===
class GetWeatherParams(BaseModel):
    """get_weather 工具的参数"""
    city: str = Field(..., description="城市名，如 '上海'、'Beijing'")


# === 2. 实现工具函数 ===
def get_weather(city: str) -> str:
    """查询天气（真实实现可接 wttr.in / OpenWeatherMap）"""
    # TODO(作者)：接入真实 API
    return f"{city} 今日晴，25°C，湿度 45%"


# === 3. 定义 OpenAI 格式的 tool schema ===
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气。返回温度、湿度、天气状况。",
            "parameters": GetWeatherParams.model_json_schema(),
        },
    }
]


# === 4. 调用 LLM（让它决定是否调工具）===
def chat(user_input: str) -> str:
    messages = [{"role": "user", "content": user_input}]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # 让 LLM 自己决定
    )

    msg = resp.choices[0].message

    # 情况 1：LLM 决定不调工具，直接答
    if not msg.tool_calls:
        return msg.content

    # 情况 2：LLM 决定调工具
    print(f"🤖 LLM 决定调工具: {msg.tool_calls[0].function.name}")
    messages.append(msg)  # 把 LLM 的 tool_call 消息加进去

    # 执行工具
    for tool_call in msg.tool_calls:
        args = json.loads(tool_call.function.arguments)
        result = get_weather(**args)
        print(f"   工具返回: {result}")

        # 把工具结果喂回给 LLM
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        })

    # 再次调用 LLM，让它基于工具结果给出最终答案
    final = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return final.choices[0].message.content


if __name__ == "__main__":
    print("=== 示例 1：需要调工具 ===")
    print(chat("上海今天天气怎么样？"))

    print("\n=== 示例 2：不需要调工具 ===")
    print(chat("用一句话解释 Agent"))


# TODO(作者)：在 4.2 节扩展为支持多轮对话
# TODO(作者)：添加 tool_choice="required" 强制调工具
