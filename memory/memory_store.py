import os
from langchain_community.chat_message_histories import FileChatMessageHistory

def get_history_adapter(memory_dir: str, session_id: str):
    """
    根据 session_id 获取对应的本地文件记忆适配器。
    """
    # 确保存储文件夹存在
    if not os.path.exists(memory_dir):
        os.makedirs(memory_dir)
        # 创建一个空的 __init__.py 让 Python 识别该目录
        with open(os.path.join(memory_dir, "__init__.py"), "w") as f:
            pass
            
    file_path = os.path.join(memory_dir, f"{session_id}.json")
    
    # 使用 LangChain 原生的文件记录器
    return FileChatMessageHistory(file_path)