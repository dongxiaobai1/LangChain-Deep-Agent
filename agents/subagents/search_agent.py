# agents/subagents/search_agent.py
from agents.tools.search_tool import internet_search
from agents.tools.helper_tools import llm
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

class SearchAgent:
    def __init__(self):
        self.name = "联网搜索专家"
        # 绑定原生工具
        self.tools = {internet_search.name: internet_search}
        self.model_with_tools = llm.bind_tools([internet_search])

    def run(self, user_input: str):
        print(f"[{self.name}] 正在调用官网 SDK 搜索: {user_input}")
        
        messages = [
            SystemMessage(content=
        "你是一个联网搜索专家。请通过工具获取实时信息。"
        "重要：请直接给出搜索到的事实性数据和简短结论，不要包含冗余的网页描述。"
        "如果后续需要进行计算，请确保保留原始数值（如金额、气温）。"),
            HumanMessage(content=user_input)
        ]
        
        ai_msg = self.model_with_tools.invoke(messages)
        
        if ai_msg.tool_calls:
            messages.append(ai_msg)
            for tool_call in ai_msg.tool_calls:
                # 执行我们刚刚写好的原生工具函数
                tool_output = internet_search.invoke(tool_call["args"])
                
                messages.append(ToolMessage(
                    content=str(tool_output), 
                    tool_call_id=tool_call["id"]
                ))
            
            final_response = llm.invoke(messages)
            return final_response.content
            
        return ai_msg.content