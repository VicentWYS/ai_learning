"""
全局配置模块，从 .env 读取模型参数，提供 LLM 工厂函数

换模型只需改环境变量，代码不动
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# 获取模型参数
LLM_CONFIG = {
    "model": os.getenv("LLM_MODEL", "deepseek-v4-flash"),
    "base_url": os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1"),
    "api_key": os.getenv("LLM_API_KEY"),
    # 环境变量的值都是字符串, 故这里需转化
    "temperature": float(os.getenv("LLM_TEMPERATURE", "0.7")),
}


def get_llm() -> ChatOpenAI:
    """
    获取 LLM 实例（OpenAI 兼容协议，支持 DeepSeek / 千文 等）

    工厂函数，** 表示
    """
    return ChatOpenAI(**LLM_CONFIG)
