"""
Ch1.3｜综合：构建一个"研究助手"原型（L2 级别）

特性：
- 多工具：搜索 + 计算 + 文件读取
- 错误恢复：工具失败时自动重试
- 可观测：打印每一步 Thought/Action/Observation
"""
from openai import OpenAI
import os
import json
from typing import Callable

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === 工具实现 ===
def web_search(query: str) -> str:
    """真实实现可接 Tavily / SerpAPI"""
    # TODO(作者)：替换为真实 API 调用
    return f"[模拟搜索结果] 与 '{query}' 相关的 3 篇资料..."


def calculator(expression: str) -> str:
    """安全计算（生产环境建议用 numexpr）"""
    try:
        # ⚠️ 危险！真实环境必须做白名单校验
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误: {e}"


def read_file(path: str) -> str:
    """读取本地文件"""
    try:
        with open(path) as f:
            return f.read()[:2000]  # 截断避免超长
    except Exception as e:
        return f"读取失败: {e}"


TOOLS: dict[str, Callable] = {
    "web_search": web_search,
    "calculator": calculator,
    "read_file": read_file,
}


# === Agent 主体 ===
SYSTEM_PROMPT = """你是一个研究助手 Agent。

可用工具：
{tools}

工作流程：
1. 仔细分析用户问题
2. 必要时调用工具
3. 综合信息给出答案

每步输出格式：
Thought: <你的思考>
Action: <工具名(参数)> 或 None
"""


def run_agent(question: str, max_steps: int = 8) -> str:
    tools_desc = "\n".join(f"- {name}({fn.__doc__ or ''})" for name, fn in TOOLS.items())
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(tools=tools_desc)},
        {"role": "user", "content": question},
    ]

    for step in range(max_steps):
        print(f"\n─── Step {step + 1} ───")
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        ).choices[0].message.content

        print(resp)
        messages.append({"role": "assistant", "content": resp})

        # 解析 Action
        if "Action: None" in resp or "Action: None" not in resp and "Action:" not in resp:
            # 没有 Action，结束
            return resp

        try:
            action_line = [l for l in resp.split("\n") if l.strip().startswith("Action:")][0]
            action = action_line.split("Action:")[1].strip()
            if action == "None":
                return resp
            tool_name, arg = action.split("(", 1)
            arg = arg.rstrip(")").strip().strip('"').strip("'")
        except (IndexError, ValueError) as e:
            return f"[解析失败] {resp}\nError: {e}"

        # 执行工具
        if tool_name not in TOOLS:
            observation = f"未知工具: {tool_name}"
        else:
            observation = TOOLS[tool_name](arg)

        print(f"Observation: {observation}")
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    return "[达到最大步数] " + str(messages)


if __name__ == "__main__":
    # 示例 1：纯计算
    print("\n=== 示例 1：计算 23 * 47 + 156 ===")
    print(run_agent("请计算 23 * 47 + 156 的结果"))

    # 示例 2：多步推理
    print("\n=== 示例 2：复合问题 ===")
    print(run_agent("上海今天适合户外运动吗？需要先查天气再判断。"))
