"""
LangGraph 基础

学习如何使用 LangGraph 创建状态图工作流
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

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


# ======================================== 带内存的对话工作流 ========================================
def conversation_workflow():
    class ConversationState(TypedDict):
        messages: Annotated[
            list, add_messages
        ]  # 使用 add_messages 注解，消息会自动追加
        turn_count: int

    def chat_node(state: ConversationState) -> dict:
        # 添加系统提示（如果是第一轮）
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [
                SystemMessage(content="你是一名智能助手，请记住用户告诉你的信息。")
            ] + messages

        response = model.invoke(messages)
        turn_count = state.get("turn_count", 0) + 1
        print(f"\n对话轮次：{turn_count} AI: {response.content[:80]}...")

        return {
            "messages": [response],  # add_messages 会自动追加
            "turn_count": turn_count,
        }

    def should_continue(state: ConversationState) -> Literal["continue", "end"]:
        # 这里简化为总是返回 end, 实际应用中可以检查用户意图
        return "end"

    graph = StateGraph(ConversationState)

    graph.add_node("chat", chat_node)

    graph.add_edge(START, "chat")
    graph.add_edge("chat", END)  # 简化：每次调用处理一轮

    # 使用内存保存器
    memory = MemorySaver()
    app = graph.compile(checkpointer=memory)

    # 模拟多轮对话（使用相同的 thread_id）
    config = {"configurable": {"thread_id": "user_1001"}}

    conversations = [
        "你好！我叫小明。",
        "我最喜欢的编程语言是 Python。",
        "你还记得我的名字吗？",
        "我喜欢什么编程语言？",
    ]

    for user_input in conversations:
        result = app.invoke(
            {"messages": [HumanMessage(content=user_input)]}, config=config
        )

        print(f"AI: {result["messages"][-1].content}")

    state = app.get_state(config)
    for msg in state.values["messages"]:
        role = "用户" if isinstance(msg, HumanMessage) else "AI"
        print(f"{role} {msg.content[:50]}...")

    return result


# 主程序
if __name__ == "__main__":
    conversation_workflow()
