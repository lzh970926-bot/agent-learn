"""
Ch3.3｜结构化输出：JSON Mode + Pydantic

3 种方式实现结构化输出，从易到难：
1. response_format={"type": "json_object"}（OpenAI 原生）
2. Pydantic + 手动解析
3. instructor 库（自动校验 + 重试）
"""
from openai import OpenAI
from pydantic import BaseModel, Field
import os
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# === 方式 1：JSON Mode（最简单，但不保证 schema）===
def json_mode_demo():
    """OpenAI JSON Mode：保证合法 JSON，但不保证字段"""
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "从用户输入中提取人名和公司，以 JSON 输出。",
            },
            {"role": "user", "content": "张伟在 ABC 公司担任 CTO"},
        ],
    )
    print("JSON Mode 输出:")
    print(resp.choices[0].message.content)


# === 方式 2：Pydantic Schema（推荐）===
class PersonInfo(BaseModel):
    """个人信息结构"""
    name: str = Field(..., description="中文姓名")
    company: str = Field(..., description="所在公司")
    title: str | None = Field(None, description="职位")
    confidence: float = Field(..., ge=0, le=1, description="置信度 0-1")


def pydantic_extraction(text: str) -> PersonInfo:
    """Pydantic + Prompt 描述 schema"""
    schema = PersonInfo.model_json_schema()
    prompt = f"""
    从以下文本提取信息，严格按 JSON Schema 输出。
    Schema: {json.dumps(schema, ensure_ascii=False)}

    文本：{text}
    """
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    # Pydantic 自动校验
    return PersonInfo.model_validate_json(resp.choices[0].message.content)


# === 方式 3：instructor 库（生产推荐）===
def instructor_extraction(text: str) -> PersonInfo:
    """instructor：自动校验 + 自动重试（需 pip install instructor）"""
    try:
        import instructor
        from openai import OpenAI as OAI
        patched_client = instructor.from_openai(OAI(api_key=os.getenv("OPENAI_API_KEY")))

        return patched_client.chat.completions.create(
            model="gpt-4o-mini",
            response_model=PersonInfo,
            messages=[{"role": "user", "content": f"提取信息：{text}"}],
            max_retries=2,  # 失败自动重试
        )
    except ImportError:
        print("请安装 instructor: uv add instructor")
        return pydantic_extraction(text)


if __name__ == "__main__":
    print("=" * 50)
    json_mode_demo()

    print("\n" + "=" * 50)
    text = "李雷在字节跳动做高级工程师，主要做推荐系统。"
    person = pydantic_extraction(text)
    print(f"Pydantic 解析: {person}")
    print(f"  name: {person.name}")
    print(f"  company: {person.company}")
    print(f"  校验通过 ✓")

    print("\n" + "=" * 50)
    person2 = instructor_extraction("韩梅梅是美团的产品经理，专注于本地生活业务。")
    print(f"instructor 解析: {person2}")


# TODO(作者)：添加嵌套结构（List[Project>）
# TODO(作者)：添加 Union 类型（"工作 OR 教育"）
# TODO(作者)：演示如何处理"模型不返回"或"返回非法 JSON"的情况
