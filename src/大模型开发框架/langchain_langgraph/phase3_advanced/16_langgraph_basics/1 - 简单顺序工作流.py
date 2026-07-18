"""
LangGraph 基础

学习如何使用 LangGraph 创建状态图工作流
"""

import os
import stat
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict
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


# ======================================== 简单顺序工作流 ========================================
def simple_workflow():
    print(f"\n" + "=" * 40 + "简单顺序工作流" + "=" * 40)

    # 定义工作流的状态结构类型
    class SimpleState(TypedDict):
        """
        描述 LangGraph 中状态字典里会有哪些键，以及它们的类型。

        - 流程：
            1. 清理用户输入的文本 (START -> pre_process)
            2. 调用 LLM 模型 (-> call_llm)
            3. 清理模型输出的文本 (-> post_process)
            4. 返回最终输出 (-> END)

        - START -> pre_process -> call_llm -> post_process -> END
        """

        input_text: str
        processed_text: str
        llm_response: str
        final_output: str

    # 初始化模型
    # 定义节点函数
    def pre_process(state: SimpleState) -> dict:
        """预处理节点：清理和格式化输入"""
        text = state["input_text"].strip().lower()
        return {"processed_text": text}

    def call_llm(state: SimpleState) -> dict:
        """LLM 节点：调用语言模型"""
        messages = [
            SystemMessage(content="你是一个友好的助手，请简洁回答问题。"),
            HumanMessage(content=state["processed_text"]),  # 将处理后的文本作为用户输入
        ]

        response = model.invoke(messages)
        return {"llm_response": response.content}

    def post_process(state: SimpleState) -> dict:
        """后处理节点：格式化输出"""
        final = f"AI 回复：{state["llm_response"]}"
        return {"final_output": final}

    # 构建图
    graph = StateGraph(SimpleState)

    # 添加节点
    graph.add_node("pre_process", pre_process)
    graph.add_node("call_llm", call_llm)
    graph.add_node("post_process", post_process)

    # 添加边（定义执行顺序）
    graph.add_edge(START, "pre_process")
    graph.add_edge("pre_process", "call_llm")
    graph.add_edge("call_llm", "post_process")
    graph.add_edge("post_process", END)

    # 编译图
    app = graph.compile()

    # 运行
    result = app.invoke({"input_text": "用100字左右的篇幅介绍，什么是人工智能？"})

    print(f"\n最终输出：\n{result["final_output"]}")

    return result


# ======================================== 主程序 ========================================
if __name__ == "__main__":
    simple_workflow()
