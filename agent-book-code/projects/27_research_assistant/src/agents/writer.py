"""
Writer Agent：负责撰写文章
"""
from crewai import Agent
from langchain_openai import ChatOpenAI


def build_writer() -> Agent:
    """构建写作 Agent"""
    return Agent(
        role="技术作家",
        goal="基于研究资料，撰写结构清晰、逻辑严谨的长文",
        backstory="""
        你是一位资深技术作家，擅长把复杂研究内容转化为易读文章。
        你的文风：清晰、有条理、举例丰富。
        """,
        llm=ChatOpenAI(model="gpt-4o"),
        verbose=True,
        allow_delegation=False,
    )

    # TODO(作者）：支持多种文体（学术 / 博客 / 报告）
    # TODO(作者）：加入"读者画像"参数（技术深度调整）
