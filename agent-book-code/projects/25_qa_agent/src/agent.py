"""
LangGraph Agent 主逻辑
"""
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .state import AgentState
from .tools import TOOLS


SYSTEM_PROMPT = """你是一个问答 Agent，可以调用以下工具：
- web_search: 搜索互联网
- calculator: 计算数学表达式
- file_reader: 读取本地文件

请按需调用工具，给出准确答案。
"""


def should_continue(state: AgentState) -> str:
    """判断是否需要继续调用工具"""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END


def call_model(state: AgentState) -> dict:
    """调用 LLM"""
    # TODO(作者)：加入 token 计数、回调、错误重试
    llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(TOOLS)
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


def build_graph():
    """构建状态图"""
    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


agent = build_graph()
