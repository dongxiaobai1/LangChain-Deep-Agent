import os
def format_chat_history(messages, k=5):
    """
    将消息列表格式化为文本，以便注入给 LLM。
    k: 取最近的 k 条记录。
    """
    if not messages:
        return "无历史对话记录。"
        
    recent_messages = messages[-k:]
    formatted_history = []
    
    for msg in recent_messages:
        role = "用户" if msg.type == "human" else "助理"
        formatted_history.append(f"{role}: {msg.content}")
        
    return "\n".join(formatted_history)

def get_session_list(memory_dir: str):
    """
    供前端 app.py 使用，获取所有已保存的会话列表。
    """
    if not os.path.exists(memory_dir):
        return []
    files = [f.replace(".json", "") for f in os.listdir(memory_dir) if f.endswith(".json")]
    return sorted(files, reverse=True)