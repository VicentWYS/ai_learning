"""
多智能体 - 动态分发模式
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated, Literal
from langchain_core import messages
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
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


# ====================================================================
# 多智能体 - 动态分发模式
# ====================================================================
def dynamic_dispatch():
    """
    动态分发模式：根据任务类型动态选择 Agent
    """

    class SupportState(TypedDict):
        query: str
        category: str
        messages: Annotated[list, add_messages]
        response: str

    def classifier(state: SupportState) -> dict:
        """分类器：识别问题类型"""
        print("[分类器] 分析问题类型...")

        messages = [
            SystemMessage(
                content="""
分析用户问题，返回分类：
- billing：账单、付款、退款相关
- technical：技术问题、Bug、使用方法
- general：其他一般性问题
只返回分类名称，不要其他内容。"""
            ),
            HumanMessage(content=state["query"]),
        ]

        response = model.invoke(messages)

        category = response.content.strip().lower()

        # 确保返回有效分类
        if category not in ["billing", "technical", "general"]:
            category = "general"

        print(f"[分类器] 问题分类为：{category}")
        return {"category": category}

    def billing_agent(state: SupportState) -> dict:
        """账单客服"""

        messages = [
            SystemMessage(
                content="你是专业的账单客服，擅长处理付款、退款、账单查询等问题。请友好地回复用户。用中文回复。"
            ),
            HumanMessage(content=state["query"]),
        ]

        response = model.invoke(messages)

        return {
            "response": f"[账单客服] {response.content}",
            "messages": [AIMessage(content=f"[账单客服] {response.content}")],
        }

    def technical_agent(state: SupportState) -> dict:
        """技术支持"""
        print("[技术支持] 处理技术问题...")

        messages = [
            SystemMessage(
                content="你是专业的技术支持工程师，擅长解决技术问题、Bug和使用指导。请专业地回复用户。用中文回复。"
            ),
            HumanMessage(content=state["query"]),
        ]

        response = model.invoke(messages)

        return {
            "response": f"[技术支持] {response.content}",
            "messages": [AIMessage(content=f"[技术支持] {response.content}")],
        }

    def general_agent(state: SupportState) -> dict:
        """通用客服"""
        print("[通用客服] 处理一般问题...")

        messages = [
            SystemMessage(
                content="你是友好的客服代表，请热情地回复用户的问题。用中文回复。"
            ),
            HumanMessage(content=state["query"]),
        ]

        response = model.invoke(messages)

        return {
            "response": f"[通用客服] {response.content}",
            "messages": [AIMessage(content=f"[通用客服] {response.content}")],
        }

    def route_to_specialist(
        state: SupportState,
    ) -> Literal["billing", "technical", "general"]:
        return state["category"]

    # 构件图
    graph = StateGraph(SupportState)

    graph.add_node("classifier", classifier)
    graph.add_node("billing", billing_agent)
    graph.add_node("technical", technical_agent)
    graph.add_node("general", general_agent)

    graph.add_edge(START, "classifier")

    graph.add_conditional_edges(
        "classifier",
        route_to_specialist,
        {"billing": "billing", "technical": "technical", "general": "general"},
    )

    graph.add_edge("billing", END)
    graph.add_edge("technical", END)
    graph.add_edge("general", END)

    app = graph.compile()

    # 测试不同类型的问题
    test_queries = [
        "我想申请退款，上个月的订阅费用扣错了",
        "软件打开后一直显示加载中，怎么解决？",
        "你们公司在哪里？营业时间是什么？",
    ]

    for query in test_queries:
        print(f"\n用户提问：{query}")
        result = app.invoke({"query": query, "messages": []})
        print(f"回复：{result["response"]}")

    return result


# 主程序
if __name__ == "__main__":
    dynamic_dispatch()
