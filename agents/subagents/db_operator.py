# agents/subagents/db_operator.py

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from agents.tools import run_sqlite_query
from agents.tools.helper_tools import llm

class DBAgent:
    def __init__(self):
        self.name = "数据库专家"
        # 现代写法：将工具直接“绑定”给模型
        self.tools = {"run_sqlite_query": run_sqlite_query}
        self.model_with_tools = llm.bind_tools([run_sqlite_query])
        
    def run(self, user_input: str):
        print(f"[{self.name}] 接收到指令: {user_input}")
        
        # 1. 初始化对话上下文
        messages = [
            SystemMessage(content=(
                "你是一个数据库专家，请使用工具解决用户问题。"
                "特别注意：用户可能会指定不同的数据库文件名（如 test.db）。"
                "如果用户要求的数据库或表不存在，请先执行 CREATE TABLE 语句创建它们。 你有权管理本地 SQLite 文件，请确保 SQL 语法符合 SQLite 标准。"
                "请从用户问题中提取文件名并传给工具的 db_name 参数。"
            )),
            HumanMessage(content=user_input)
        ]
        
        # 第一步：让模型思考
        ai_msg = self.model_with_tools.invoke(messages)
        
        # 2. 检查模型是否想调用工具
        if ai_msg.tool_calls:
            print(f"[{self.name}] 正在调用工具...")
            # 【重要修正 1】：先将 AI 的 tool_calls 消息存入历史
            # 必须先有 Assistant 消息，后面才能跟 Tool 消息
            messages.append(ai_msg)
            
            # 遍历所有的工具调用（有时候 AI 会一次性要求执行多条 SQL）
            for tool_call in ai_msg.tool_calls:
                # 获取工具并运行
                tool_name = tool_call["name"].lower()
                selected_tool = self.tools[tool_name]
                
                # 执行工具获取结果
                tool_output = selected_tool.invoke(tool_call["args"])
                
                # 【重要修正 2】：将每个工具的结果封装为 ToolMessage
                # 必须传入正确的 tool_call_id，否则 OpenAI 会报 400
                messages.append(ToolMessage(
                    content=str(tool_output), 
                    tool_call_id=tool_call["id"]
                ))
            messages.append(SystemMessage(content="请根据工具返回的数据，给出一个简短明了的总结。如果涉及到数值，请确保数值清晰可见，以便后续计算。"))
            # 【重要修正 3】：循环结束后，一次性将完整的上下文发回给模型
            # 此时的 messages 结构：[System, Human, AI(tool_calls), Tool(result1), Tool(result2)...]
            final_response = llm.invoke(messages)
            return final_response.content
        
        # 如果不需要调用工具，直接返回 AI 的回复
        return ai_msg.content