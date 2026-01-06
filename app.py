import streamlit as st
import os
import uuid
from datetime import datetime
from agents.main_agent import MainAgent
from memory import get_session_list

# --- 1. 基础配置 ---
st.set_page_config(page_title="Multi-Agent System", layout="wide", page_icon="🤖")
MEMORY_DIR = os.path.join(os.path.dirname(__file__), "memory")

# --- 2. 侧边栏：会话管理 ---
with st.sidebar:
    st.title("💬 会话管理")
    
    if st.button("➕ 新建对话", use_container_width=True):
        new_id = f"chat_{datetime.now().strftime('%m%d_%H%M')}"
        st.session_state.current_session = new_id
        if "agent" in st.session_state:
            del st.session_state.agent
        st.rerun()
    
    st.divider()
    st.subheader("历史记录")
    
    sessions = get_session_list(MEMORY_DIR)
    
    if "current_session" not in st.session_state:
        st.session_state.current_session = sessions[0] if sessions else "default_user"
    
    display_sessions = sessions.copy()
    if st.session_state.current_session not in display_sessions:
        display_sessions.insert(0, st.session_state.current_session)

    selected_session = st.radio(
        "选择会话", 
        display_sessions, 
        index=display_sessions.index(st.session_state.current_session),
        label_visibility="collapsed"
    )
    
    if selected_session != st.session_state.current_session:
        st.session_state.current_session = selected_session
        if "agent" in st.session_state:
            del st.session_state.agent
        st.rerun()

# --- 3. 智能 Agent 实例维护 ---
if "agent" not in st.session_state or st.session_state.agent.session_id != st.session_state.current_session:
    st.session_state.agent = MainAgent(session_id=st.session_state.current_session)

# --- 4. 主界面：命名与标题渲染 ---
# 使用 st.columns 让标题和重命名按钮并排
col1, col2 = st.columns([0.8, 0.2])
with col1:
    st.title("🤖 专家协作系统")
with col2:
    # --- 💥 新增：重命名功能 ---
    if st.button("📝 重命名"):
        st.session_state.renaming = True

# 如果处于重命名状态，显示输入框
if st.session_state.get("renaming", False):
    with st.container():
        new_name = st.text_input("请输入新的会话名称：", value=st.session_state.current_session)
        c1, c2 = st.columns(2)
        if c1.button("确认修改"):
            if new_name and new_name != st.session_state.current_session:
                old_path = os.path.join(MEMORY_DIR, f"{st.session_state.current_session}.json")
                new_path = os.path.join(MEMORY_DIR, f"{new_name}.json")
                
                # 如果旧文件存在，直接重命名文件
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                
                # 更新状态并重新加载
                st.session_state.current_session = new_name
                st.session_state.renaming = False
                if "agent" in st.session_state:
                    del st.session_state.agent # 强制 Agent 重新绑定新文件
                st.rerun()
        if c2.button("取消"):
            st.session_state.renaming = False
            st.rerun()

st.caption(f"🚀 当前会话: **{st.session_state.current_session}**")

# --- 5. 渲染聊天记录 ---
for msg in st.session_state.agent.history.messages:
    role = "user" if msg.type == "human" else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- 6. 用户输入处理 ---
if prompt := st.chat_input("有什么我可以帮您的？"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response_placeholder = st.empty() 
        with st.status("🧠 专家团队正在研讨...", expanded=True) as status:
            try:
                response = st.session_state.agent.run(prompt)
                status.update(label="✅ 任务处理完成", state="complete", expanded=False)
                response_placeholder.markdown(response)
            except Exception as e:
                status.update(label="❌ 调度失败", state="error")
                st.error(f"错误详情: {str(e)}")