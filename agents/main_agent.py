import json
import os
from agents.subagents.db_operator import DBAgent
from agents.subagents.code_editor import CodeAgent
from agents.subagents.search_agent import SearchAgent
from agents.tools.helper_tools import llm
from langchain_core.messages import SystemMessage

# --- 从 memory 包导入接口 ---
from memory import get_history_adapter, format_chat_history

class MainAgent:
    def __init__(self, session_id="default_user"):
        self.name = "总调度官"
        self.session_id = session_id
        
        # --- 1. 记忆系统初始化 ---
        current_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(current_dir)
        self.memory_dir = os.path.join(root_dir, "memory")
        
        self.history = get_history_adapter(self.memory_dir, session_id)
        
        self.db_agent = DBAgent()
        self.code_agent = CodeAgent()
        self.search_agent = SearchAgent()
        
        self.agents = {
            "数据库专家": self.db_agent,
            "代码计算专家": self.code_agent,
            "联网搜索专家": self.search_agent
        }

    def run(self, user_query: str):
        context_record = {"original_query": user_query, "intermediate_steps": []}
        
        # --- 2. 优化：减少 Planner 看到的历史深度 (k=2 足够识别上下文，又不会干扰新话题) ---
        history_str = format_chat_history(self.history.messages, k=2)

        # 3. 增强型任务拆解 (Planner) - 加入意图分类逻辑
        planner_prompt = f"""
        你是一个最高级别的任务规划官。
        
        [对话历史]
        {history_str if history_str else "无"}
        
        [当前问题]
        {user_query}

        --- 规划指令 ---
        1. 判断当前问题是否需要【专家团队】协作（如查询、计算、搜索等）。
        2. 如果只是寒暄（如“你好”、“谢谢”）、闲聊，或者用户明确想开启一个与历史无关的新话题，请返回空列表 []。
        3. 如果是历史任务的明确延续或复杂需求，请按以下 JSON 格式拆解步骤。

        可用专家：[数据库专家], [代码计算专家], [联网搜索专家]。
        请严格按 JSON 格式回复，不要有任何开场白：
        [
            {{"step": 1, "agent": "...", "task": "..."}}
        ]
        """

        print(f"\n🧠 [{self.name}] 正在分析意图与任务...")
        res = llm.invoke([SystemMessage(content=planner_prompt)])
        
        # --- 清理与解析 ---
        raw_content = res.content.strip()
        clean_json = raw_content.replace("```json", "").replace("```", "").strip()
        
        try:
            plan = json.loads(clean_json)
            
            # 标准化 plan 格式
            if isinstance(plan, dict):
                plan = plan.get("steps", plan.get("plan", [plan]))
            
            # --- 💥 核心修改：如果是闲聊或空计划，直接进入对话模式 ---
            if not plan or len(plan) == 0:
                print(f"💬 [{self.name}] 识别为简单对话，直接生成回复...")
                chat_prompt = f"""
                参考对话历史，直接回答用户。不要提及专家或任务拆解。
                [对话历史]: {history_str}
                [用户]: {user_query}
                """
                final_answer = llm.invoke([SystemMessage(content=chat_prompt)]).content
                
                # 存入记忆并返回
                self.history.add_user_message(user_query)
                self.history.add_ai_message(final_answer)
                return final_answer

        except Exception as e:
            print(f"⚠️ 解析异常，切换搜索兜底: {e}")
            return self.search_agent.run(user_query)

        # 4. 迭代执行专家任务 (仅在 plan 不为空时执行)
        for step in plan:
            if not isinstance(step, dict): continue
                
            agent_key = step.get('agent')
            task_text = step.get('task')
            
            if agent_key in self.agents:
                print(f"🚀 调度中: {agent_key} -> 任务: {task_text}")
                
                steps_history = json.dumps(context_record["intermediate_steps"], ensure_ascii=False)
                task_with_context = f"背景历史: {steps_history}\n当前任务: {task_text}"
                
                try:
                    result = self.agents[agent_key].run(task_with_context)
                except Exception as e:
                    result = f"执行出错: {str(e)}"
                
                context_record["intermediate_steps"].append({
                    "step": step.get('step', 'unknown'), 
                    "agent": agent_key, 
                    "result": result
                })

            # 评估是否满足需求
            assessment_prompt = f"基于信息: {json.dumps(context_record['intermediate_steps'], ensure_ascii=False)}, 已足以回答 '{user_query}' 吗? 只回复 YES 或 NO"
            try:
                is_ready = llm.invoke([SystemMessage(content=assessment_prompt)]).content.strip()
                if "YES" in is_ready.upper():
                    break
            except:
                continue

        # 5. 整合最终答案
        print(f"🎨 [{self.name}] 正在汇总结果...")
        synthesis_prompt = f"""
        请整合以下执行过程，回答用户问题：{user_query}。
        过程：{json.dumps(context_record['intermediate_steps'], ensure_ascii=False)}
        """
        final_answer = llm.invoke([SystemMessage(content=synthesis_prompt)]).content

        # --- 6. 持久化保存 ---
        self.history.add_user_message(user_query)
        self.history.add_ai_message(final_answer)

        return final_answer