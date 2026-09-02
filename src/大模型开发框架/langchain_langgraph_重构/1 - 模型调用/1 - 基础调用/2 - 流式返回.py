"""
单次大模型调用
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

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


def example_1_streaming_output():
    print("AI回复内容：", end="", flush=True)
    for chunk in model.stream("介绍成语：望梅止渴"):
        content = chunk.content
        if content:
            print(content, end="", flush=True)
    print()


# 主程序
def main():
    try:
        example_1_streaming_output()
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
