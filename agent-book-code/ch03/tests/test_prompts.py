"""Ch3 单元测试"""
import pytest
from pydantic import ValidationError
from ch03.03_json_output import PersonInfo


def test_person_info_valid():
    p = PersonInfo(name="张三", company="ABC", confidence=0.9)
    assert p.name == "张三"


def test_person_info_confidence_range():
    with pytest.raises(ValidationError):
        PersonInfo(name="李四", company="XYZ", confidence=1.5)


def test_person_info_optional_title():
    p = PersonInfo(name="王五", company="DEF", confidence=0.5)
    assert p.title is None


def test_prompt_template_render():
    from ch03.01_structured import PromptTemplate
    tpl = PromptTemplate(role="AI", task="test")
    rendered = tpl.render()
    assert "AI" in rendered
    assert "test" in rendered
