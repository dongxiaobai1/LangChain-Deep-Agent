import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载 .env 环境变量
load_dotenv()

class Settings:
    def __init__(self):
        self.api_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.base_url = os.getenv("OPENROUTER_BASE_URL")
        self.model_name = os.getenv("MODEL_NAME", "openai/gpt-4o")

    def get_llm(self, temperature=0):
        """
        初始化并返回 LangChain 的 ChatOpenAI 实例
        OpenRouter 兼容 OpenAI 接口，所以直接用 ChatOpenAI 即可
        """
        if not self.api_key:
            raise ValueError("未在 .env 中找到 OPENROUTER_API_KEY")

        return ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            max_tokens=2000,
            temperature=temperature,
            # OpenRouter 建议添加以下 header 以便在排行榜显示你的应用（可选）
            default_headers={
                "HTTP-Referer": "https://github.com/your-username/multi_agent_system", 
                "X-Title": "My Multi Agent System",
            }
        )

# 实例化配置对象，方便其他模块直接 import settings

settings = Settings()

