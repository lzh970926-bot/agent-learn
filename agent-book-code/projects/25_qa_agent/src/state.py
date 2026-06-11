"""
LangGraph State 定义
"""
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """Agent 状态机"""
    messages: Annotated[list, add_messages]  # 自动合并消息
    iterations: int  # 已执行步数
    final_answer: str | None  # 最终答案
    # TODO(作者)：添加自定义字段（如工具调用历史、token 累计、错误计数）
