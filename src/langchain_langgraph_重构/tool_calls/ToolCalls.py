"""
1. 定义工具 — 声明一个 get_horoscope 函数及其参数 schema（星座名称）。
2. 首次请求 — 把用户消息和工具定义一起发给模型，模型判断需要调用工具，返回 tool_calls（含函数名和参数）。
3. 本地执行 — 解析模型的工具调用参数，本地运行 get_horoscope("水瓶座")，得到结果。
4. 回传结果 — 将工具执行结果以 role: "tool" 的消息追加到对话中。
5. 二次请求 — 把完整对话历史（用户消息 → 助手 tool_calls → 工具结果）再次发给模型，模型据此生成最终的自然语言回复。

简言之：模型说"我需要调这个函数" → 代码执行函数 → 把结果告诉模型 → 模型给出最终回答。


注意：
1. 大模型本身不会执行函数，是客户端自身执行的函数，大模型只是接受函数结果。
2. 只需要理解这个流程，后续会用langchain框架提供的方法
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")

if not api_key or api_key == "your_api_key_here":
    raise ValueError("\n请先在.env文件中设置有效的DEEPSEEK_API_KEY\n")

if not base_url or base_url == "your_base_url_here":
    raise ValueError("\n请先在.env文件中设置有效的DEEPSEEK_API_KEY\n")


# 初始化OpenAI客户端
client = OpenAI(base_url=base_url, api_key=api_key)

# 1. 为模型定义可调用工具列表
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_horoscope",
            "description": "获取指定星座的今日运势",
            "parameters": {
                "type": "object",
                "properties": {
                    "sign": {
                        "type": "string",
                        "description": "星座名称，如金牛座或水瓶座",
                    },
                },
                "required": ["sign"],
            },
        },
    },
]

# 创建一个消息列表，随着时间推移会不断添加内容
messages = [{"role": "user", "content": "我的运势如何？我是水瓶座。"}]

# 2. 使用定义的工具提示模型
response = client.chat.completions.create(
    model="deepseek-v4-flash",
    tools=tools,
    messages=messages,
)

print("模型初始输出:")
print(json.dumps(response.model_dump(), indent=2, ensure_ascii=False)) # str 一个json字符串


# 保存函数调用输出以供后续请求使用
function_call = None  # 所调用的函数
function_call_arguments = None  # 所调用的函数的参数
messages.append(response.choices[0].message)


# 检查模型是否想要调用函数
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_call = tool_call
    function_call_arguments = json.loads(tool_call.function.arguments)


def get_horoscope(sign):
    return f"{sign}: 下周二你将结识一只小水獭。"


# 3. 执行 get_horoscope 函数逻辑
result = {"horoscope": get_horoscope(function_call_arguments["sign"])}

# 4. 向模型提供函数调用结果
messages.append(
    {
        "tool_call_id": function_call.id,
        "role": "tool",
        "name": "get_horoscope",
        "content": json.dumps(result),
    }
)
# print("消息流程:")
# for i, message in enumerate(messages):
#     if isinstance(message, dict):
#         role = message.get("role", "unknown")
#         if role == "user":
#             print(f"{i+1}. 用户输入: {message.get('content', '')}")
#         elif role == "tool":
#             content = json.loads(message.get("content", "{}"))
#             print(f"{i+1}. 工具返回: {content}")
#     else:
#         print(
#             f"{i+1}. 助手: 调用工具 {message.tool_calls[0].function.name if message.tool_calls else '无工具调用'}"
#         )


response = client.chat.completions.create(
    model="deepseek-v4-flash",
    tools=tools,
    messages=messages,
)

# 5. 模型应该能够给出响应！
print("最终输出:")
# print(json.dumps(response.model_dump(), indent=2))
print("\n" + response.choices[0].message.content)
