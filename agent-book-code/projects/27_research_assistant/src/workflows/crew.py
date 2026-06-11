"""
CrewAI Crew：组装 3 个 Agent
"""
from crewai import Crew, Process, Task

from ..agents.researcher import build_researcher
from ..agents.writer import build_writer
from ..agents.editor import build_editor


def build_crew(topic: str) -> Crew:
    """组装 Crew"""
    researcher = build_researcher()
    writer = build_writer()
    editor = build_editor()

    research_task = Task(
        description=f"研究主题：{topic}\n收集至少 10 条高质量资料，整理关键观点和数据。",
        expected_output="结构化资料清单（含来源 URL、核心观点、关键数据）",
        agent=researcher,
    )

    writing_task = Task(
        description="基于研究资料，撰写 2000 字左右的深度文章。",
        expected_output="结构完整的文章 markdown 文本",
        agent=writer,
        context=[research_task],
    )

    editing_task = Task(
        description="审核文章，给出修改建议或最终版本。",
        expected_output="审核报告（问题清单 + 修订后文章）",
        agent=editor,
        context=[writing_task],
    )

    return Crew(
        agents=[researcher, writer, editor],
        tasks=[research_task, writing_task, editing_task],
        process=Process.sequential,  # 也可试 hierarchical
        verbose=2,
    )

    # TODO(作者）：支持 hierarchical 模式（自动选举 manager）
    # TODO(作者）：加入人机协作（编辑环节插入人工审核）


# TODO(作者）：用 LangGraph 重构，支持 checkpoint + interrupt
