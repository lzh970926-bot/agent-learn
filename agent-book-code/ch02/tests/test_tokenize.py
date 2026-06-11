"""Ch2 单元测试"""
import pytest
from ch02.01_tokenize import tokenize, cost_calculator
from ch02.03_capstone import count_tokens, estimate


def test_tokenize_chinese():
    tokens = tokenize("你好")
    assert len(tokens) >= 1
    assert all(isinstance(t, str) for t in tokens)


def test_cost_calculator_positive():
    cost = cost_calculator(1000, 500, "gpt-4o-mini")
    assert cost > 0


def test_count_tokens_basic():
    n = count_tokens("hello world", "gpt-4o")
    assert n == 2


def test_estimate_returns_dataclass():
    est = estimate("test", 100, "gpt-4o-mini", 100)
    assert est.single_call > 0
    assert est.monthly > est.daily
