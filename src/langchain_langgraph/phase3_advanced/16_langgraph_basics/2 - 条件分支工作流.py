"""
LangGraph 基础

学习如何使用 LangGraph 创建状态图工作流
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END


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


# ======================================== 条件分支工作流 ========================================
def conditional_workflow():
    class ConditionalState(TypedDict):
        query: str
        query_type: str
        response: str

    def classify_query(state: ConditionalState) -> dict:
        query = state["query"].lower()

        if any(word in query for word in ["天气", "温度", "下雨"]):
            query_type = "weather"
        elif any(word in query for word in ["计算", "加", "减", "乘", "除", "等于"]):
            query_type = "math"
        else:
            query_type = "general"

        return {"query_type": query_type}

    def handel_weather(state: ConditionalState) -> dict:
        response = "今天天气晴朗，温度25度，适合外出。"  # 模仿天气API返回结果
        return {"response": response}

    def handel_math(state: ConditionalState) -> dict:
        messages = [
            SystemMessage(
                content="你是一名数学助手，请计算用户输入的问题，并给出结果。"
            ),
            HumanMessage(content=state["query"]),
        ]

        result = model.invoke(messages)

        return {"response": result.content}

    def handel_general(state: ConditionalState) -> dict:
        messages = [
            SystemMessage(
                content="你是一名智能助手，请用简短的语言回答用户输入的问题。"
            ),
            HumanMessage(content=state["query"]),
        ]

        result = model.invoke(messages)

        return {"response": result.content}

    def route_query(state: ConditionalState) -> Literal["weather", "math", "general"]:
        return state["query_type"]

    graph = StateGraph(ConditionalState)

    # 添加节点
    graph.add_node("classify", classify_query)

    graph.add_node("weather", handel_weather)
    graph.add_node("math", handel_math)
    graph.add_node("general", handel_general)

    # 添加边
    graph.add_edge(START, "classify")

    # 添加条件边
    graph.add_conditional_edges(
        "classify",
        route_query,
        {"weather": "weather", "math": "math", "general": "general"},
    )

    graph.add_edge("weather", END)
    graph.add_edge("math", END)
    graph.add_edge("general", END)

    app = graph.compile()

    test_queries = [
        "今天北京的天气怎么样？",
        "计算 123 加 456 等于多少？",
        "Python 是什么编程语言？",
    ]

    for query in test_queries:
        result = app.invoke({"query": query})
        print(f"\nAI回复：{result["response"][:100]}...")

    return result


# 主程序
if __name__ == "__main__":
    conditional_workflow()
