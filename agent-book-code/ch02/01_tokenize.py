"""
Ch2.1｜Token 切分可视化

直观看 BPE 在中英文上的差异。
"""
import tiktoken
from typing import List


def tokenize(text: str, model: str = "gpt-4o") -> List[str]:
    """使用 tiktoken 切分 Token 并返回原文片段"""
    enc = tiktoken.encoding_for_model(model)
    token_ids = enc.encode(text)
    return [enc.decode([t]) for t in token_ids]


def visualize_tokens(text: str) -> None:
    tokens = tokenize(text)
    print(f"原文: {text}")
    print(f"Token 数: {len(tokens)}")
    print("切分结果:")
    for i, t in enumerate(tokens, 1):
        print(f"  [{i:2d}] {repr(t)}")


def compare_chinese_english():
    """对比中英文 Token 效率"""
    examples = [
        ("EN: hello world", "hello world"),
        ("ZH: 你好世界", "你好世界"),
        ("EN: I love programming", "I love programming"),
        ("ZH: 我爱编程", "我爱编程"),
        ("Code: def foo(x): return x*2", "def foo(x): return x*2"),
    ]
    print(f"{'文本':40s} {'字符数':>6s} {'Token数':>8s} {'效率':>8s}")
    print("-" * 70)
    for label, text in examples:
        tokens = tokenize(text)
        ratio = len(text) / len(tokens) if tokens else 0
        print(f"{label:40s} {len(text):6d} {len(tokens):8d} {ratio:8.2f}")


def cost_calculator(input_tokens: int, output_tokens: int, model: str = "gpt-4o") -> float:
    """根据 OpenAI 公开定价计算成本（美元）"""
    pricing = {
        "gpt-4o": (2.5 / 1_000_000, 10.0 / 1_000_000),      # input, output per token
        "gpt-4o-mini": (0.15 / 1_000_000, 0.6 / 1_000_000),
        "gpt-4-turbo": (10.0 / 1_000_000, 30.0 / 1_000_000),
    }
    in_price, out_price = pricing.get(model, pricing["gpt-4o"])
    return input_tokens * in_price + output_tokens * out_price


if __name__ == "__main__":
    visualize_tokens("""
    春风又绿江南岸，明月何时照我还。
    """)
    print()
    compare_chinese_english()
    print()
    print(f"成本示例 (10k 输入 + 2k 输出, gpt-4o):")
    print(f"  ${cost_calculator(10_000, 2_000):.4f}")
    print(f"  vs gpt-4o-mini: ${cost_calculator(10_000, 2_000, 'gpt-4o-mini'):.4f}")


# TODO(作者)：在 2.2 节扩展为可视化（中英文颜色区分）
# TODO(作者)：添加 token 数量超限时的截断策略（保留头部/尾部/中间）
