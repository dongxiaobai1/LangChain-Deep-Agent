# agents/subagents/code_editor.py

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from agents.tools.modify_code import python_repl_tool  # 从工具目录导入
from agents.tools.helper_tools import llm

class CodeAgent:
    def __init__(self):
        self.name = "编程专家"
        # 绑定工具
        self.tools = {"python_repl_tool": python_repl_tool}
        self.model_with_tools = llm.bind_tools([python_repl_tool])
        
    def run(self, user_input: str):
        print(f"[{self.name}] 接收到任务: {user_input}")
        
        messages = [
            SystemMessage(content=(
                "你是一个编程专家。"
                "1. 你可以将代码保存到文件中并运行。"
                "2. 请为你的代码起一个有意义的文件名（如 calculate_interest.py）。"
                "3. 务必在代码中使用 print() 输出结果，否则用户看不到反馈。"
            )),
            HumanMessage(content=user_input)
        ]
        
        # 1. 思考并决定调用工具
        ai_msg = self.model_with_tools.invoke(messages)
        
        if ai_msg.tool_calls:
            print(f"[{self.name}] 正在生成并运行 Python 代码...")
            messages.append(ai_msg)
            
            for tool_call in ai_msg.tool_calls:
                selected_tool = self.tools[tool_call["name"].lower()]
                tool_output = selected_tool.invoke(tool_call["args"])
                
                messages.append(ToolMessage(
                    content=str(tool_output), 
                    tool_call_id=tool_call["id"]
                ))
            
            # 2. 总结结果
            final_response = llm.invoke(messages)
            return final_response.content
            
        return ai_msg.content