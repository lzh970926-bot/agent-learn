"""
Researcher Agent：负责搜索、整理资料
"""
from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults


def build_researcher() -> Agent:
    """构建研究 Agent"""
    return Agent(
        role="高级研究员",
        goal="基于用户的研究问题，全面、准确地收集相关资料",
        backstory="""
        你是一位资深研究员，擅长从海量信息中提炼核心观点。
        你的研究方法严谨，引用规范。
        """,
        tools=[TavilySearchResults(max_results=5)],
        llm=ChatOpenAI(model="gpt-4o"),
        verbose=True,
        allow_delegation=False,
    )

    # TODO(作者）：添加 PDF / 网页内容读取工具
    # TODO(作者）：添加引用追踪（每条资料带 URL）
