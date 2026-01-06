from config.settings import settings

# 全局共享一个 llm 实例，节省内存
llm = settings.get_llm()

def quick_llm_query(prompt: str) -> str:
    """
    快速调用 LLM 的辅助函数
    """
    response = llm.invoke(prompt)
    return response.content

# 你也可以在这里定义一些通用的 LangChain Tool
# 比如：打印日志、文本格式化等