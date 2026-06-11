"""Ch4 单元测试"""
import pytest
from ch04.02_advanced import calculator, get_weather, execute_tool_call


def test_calculator_basic():
    assert calculator("2 + 2") == "4"
    assert calculator("10 * 5") == "50"


def test_calculator_invalid():
    result = calculator("invalid expression")
    assert "错误" in result


def test_get_weather():
    result = get_weather("上海")
    assert "上海" in result
    assert "°C" in result or "温度" in result


# TODO(作者)：测试 tool_call 解析（mock 整个 LLM 响应）
# TODO(作者)：测试高风险工具的拦截逻辑
# TODO(作者)：测试并行调用
