"""Ch1 单元测试：工具函数和解析逻辑"""
import pytest
from ch01.02_levels import level0_pure_llm, get_weather
from ch01.03_capstone import calculator, parse_action


def test_get_weather_returns_string():
    result = get_weather("北京")
    assert isinstance(result, str)
    assert "北京" in result


def test_calculator_basic():
    assert calculator("2 + 2") == "4"
    assert calculator("10 * 5") == "50"


def test_calculator_handles_invalid():
    result = calculator("invalid expression")
    assert "错误" in result


def test_parse_action_format():
    # TODO(作者)：补充完整 Action 解析测试
    assert parse_action("Action: calculator(2+2)") == ("calculator", "2+2")
    assert parse_action("Action: None") is None
