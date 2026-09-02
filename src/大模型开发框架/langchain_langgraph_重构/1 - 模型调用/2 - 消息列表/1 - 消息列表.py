"""
消息列表支持构建多轮对话历史
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


# 使用消息列表进行对话
def example_2_messages():
    """
    三种消息形式：
    - SystemMessage: 系统消息，用于设定 AI 的角色和行为
    - HumanMessage: 用户消息
    - AIMessage: AI 的回复消息

    消息列表支持构建多轮对话历史
    """
    # 第一轮对话
    messages = [
        SystemMessage(
            content="你是一个友好的 Python 编程助手，擅长用简单易懂的方式解释编程概念。 回答字数不超过100字。"
        ),
        HumanMessage(content="什么是 Python 装饰器？"),
    ]

    response = model.invoke(messages)  # type: AIMessage
    print(f"AI回复：\n{response.content}")

    # 第二轮对话：将AI回复添加到对话历史
    messages.append(response)  # 这里追加的是 AIMessage/HumanMessage
    messages.append(HumanMessage(content="请给出一个具体示例"))

    response2 = model.invoke(messages)
    print(f"\nAI回复：\n{response2.content}")


# 主程序
def main():
    try:
        example_2_messages()
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()


"""
AI回复：
Python 装饰器是一种“函数加工厂”：在不改原函数代码的前提下，给它增加额外功能（如计时、权限检查）。用 `@decorator_name` 语法写在函数定义前即可。

AI回复：
```python
import time

def timer(func):
    def wrapper():
        start = time.time()
        func()
        print(f"耗时: {time.time()-start:.2f}秒")
    return wrapper

@timer
def hello():
    time.sleep(1)
    print("Hello")

hello()  # 输出 Hello 和耗时
```
"""
