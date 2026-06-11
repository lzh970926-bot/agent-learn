"""
工具实现
"""
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """搜索互联网获取最新信息"""
    # TODO(作者)：接入 Tavily API
    # from tavily import TavilyClient
    # client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    # return client.search(query)["results"]
    raise NotImplementedError("接入 Tavily")


@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    # TODO(作者)：用 numexpr 替代 eval，更安全
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"计算错误: {e}"


@tool
def file_reader(path: str) -> str:
    """读取本地文件内容"""
    # TODO(作者)：增加路径白名单（防止读取敏感文件）
    try:
        with open(path) as f:
            return f.read()[:5000]
    except Exception as e:
        return f"读取失败: {e}"


TOOLS = [web_search, calculator, file_reader]
