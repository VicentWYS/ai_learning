"""
模块 23：错误处理
学习如何实现健壮的错误处理和恢复机制
"""

import os
import time
import random
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import Any


# 加载环境变量
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")

if not QWEN_API_KEY or QWEN_API_KEY == "your_qwen_api_key_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_API_KEY"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key 获取免费密钥"
    )

if not QWEN_BASE_URL or QWEN_BASE_URL == "your_qwen_base_url_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_BASE_URL"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/model-market/detail/qwen-plus 获取适配 OpenAI 的 url"
    )

# 初始化模型
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ==================================================================================
# 模型回退机制
# ==================================================================================
def model_fallback():
    """
    实现模型回退：主模型失败时使用备用模型
    """

    class FallbackChain:
        """带回退的模型链"""

        def __init__(self, models: list):
            self.models = models

        def invoke(self, query: str) -> Any:
            last_error = None

            for i, model in enumerate(self.models):
                model_name = f"模型 {i+1}"

                try:
                    print(f"尝试 {model_name}...")
                    result = model.invoke(query)
                    print(f"{model_name} 成功")
                    return result
                except Exception as e:
                    last_error = e
                    print(f"{model_name} 失败：{e}")

            raise Exception(f"所有模型都失败：{last_error}")

    # 创建模型列表（实际使用时可以用不同的模型）
    models = [model, model, model]  # 主模型  # 备用模型 1  # 备用模型 2

    fallback_chain = FallbackChain(models)

    print("\n使用回退链调用...")
    result = fallback_chain.invoke("用两句话简单介绍西红柿的历史")
    print(f"AI 回复：{result.content}")


# ==================================================================================
# 主程序
# ==================================================================================
if __name__ == "__main__":
    model_fallback()
