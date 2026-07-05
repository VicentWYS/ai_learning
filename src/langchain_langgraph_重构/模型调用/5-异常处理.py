"""
针对运行过程中可能出现的报错信息，添加针对性的异常处理机制。
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# 校验 key 和 url
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_api_key_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_API_KEY\n")

if not DEEPSEEK_BASE_URL or DEEPSEEK_BASE_URL == "your_base_url_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_BASE_URL\n")

# 初始化模型
model = init_chat_model(
    model="deepseek-v4-flash",
    model_provider="openai",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    temperature=0.8,
)


# 错误处理
def example_error_handling():

    try:
        response = model.invoke("请用一句话介绍什么是智能体")
        print(f"\nAI回复：\n{response.content}")

    except ValueError as e:
        print(f"配置错误：{e}")

    except ConnectionError as e:
        print(f"网络错误：{e}")

    except Exception as e:
        print(f"未知错误：{type(e).__name__}: {e}")


# 主程序
def main():
    try:
        example_error_handling()
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
