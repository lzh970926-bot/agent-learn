"""
Editor Agent：负责审核、修改
"""
from crewai import Agent
from langchain_openai import ChatOpenAI


def build_editor() -> Agent:
    """构建编辑 Agent"""
    return Agent(
        role="资深编辑",
        goal="审核文章质量，发现问题并给出具体修改建议",
        backstory="""
        你是一位拥有 20 年经验的资深编辑，擅长发现：
        - 事实错误
        - 逻辑漏洞
        - 表达不清
        - 数据未引用
        """,
        llm=ChatOpenAI(model="gpt-4o"),
        verbose=True,
        allow_delegation=False,
    )

    # TODO(作者）：实现"多轮编辑"（Editor → Writer → Editor 循环）
    # TODO(作者）：支持质量评分（事实/逻辑/表达/引用四维度）
