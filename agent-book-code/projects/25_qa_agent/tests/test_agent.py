"""Agent 测试"""
import pytest
from projects.twenty_five_qa_agent.src.tools import calculator


def test_calculator():
    assert calculator.invoke("2 + 2") == "4"


def test_calculator_invalid():
    result = calculator.invoke("invalid")
    assert "错误" in result


# TODO(作者)：测试 Agent 端到端（需 mock LLM）
# TODO(作者)：工具选择准确性评测（基于标注数据集）
