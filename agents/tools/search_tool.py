# agents/tools/search_tool.py
import os
import datetime
from tavily import TavilyClient
from langchain.tools import tool

# 初始化原生客户端
tavily_client = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

@tool
def internet_search(query: str):
    """
    当需要查询实时信息、新闻、天气或当前日期时，调用此工具。
    参数 query 是具体的搜索查询词。
    """
    # 1. 自动获取当前日期，帮助搜索算法定位“最新”
    today = datetime.date.today().strftime("%Y-%m-%d")
    refined_query = f"{query} (today is {today})"

    print(f"🌐 [Tavily] 正在搜索: {refined_query}")

    # 2. 优化参数：
    # search_depth="basic" 速度比 "advanced" 快一倍，且足够应付大多数事实查询
    # topic="news" 强制搜索新闻源，彻底解决“远古信息”问题
    response = tavily_client.search(
        query=refined_query, 
        search_depth="basic",  # ⚡ 提速：basic 响应更快
        topic="news",         # 🕒 时效：强制新闻模式
        max_results=5         # ⚡ 提速：减少结果数量，降低后续 LLM 处理压力
    )
    
    results = response.get("results", [])
    if not results:
        # 如果新闻模式没搜到，自动退回到通用模式（兜底逻辑）
        response = tavily_client.search(query=query, max_results=3)
        results = response.get("results", [])
        if not results:
            return "未搜索到相关实时结果。"
    
    formatted_results = []
    for res in results:
        # 3. 增加标题，帮助汇总官更好地识别信息点
        title = res.get('title', '无标题')
        formatted_results.append(f"【{title}】\n来源: {res['url']}\n内容: {res['content']}\n")
    
    return "\n".join(formatted_results)