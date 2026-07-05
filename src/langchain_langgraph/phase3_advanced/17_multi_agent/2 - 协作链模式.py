"""
多智能体 - 协作链模式
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


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
# 多智能体 - 协作链模式
# ====================================================================
def collaborative_chain():
    """
    协作链模式：Agent 按顺序接力处理
    """

    class ReviewState(TypedDict):
        code: str
        messages: Annotated[list, add_messages]
        security_review: str
        performance_review: str
        style_review: str
        final_report: str

    def security_reviewer(state: ReviewState) -> dict:
        """安全审查员"""
        print("[安全审查] 检查代码安全性...")

        messages = [
            SystemMessage(
                content="你是一个安全专家，请审查代码的安全性问题。用中文简洁回复。"
            ),
            HumanMessage(content=f"代码：\n{state["code"]}"),
        ]

        response = model.invoke(messages)

        # return 中的这个 AIMessage 在代码中主要是“记录过程”，不是“驱动主逻辑”；删掉通常不影响当前主流程输出，但会损失链路可追踪性和可扩展性
        return {
            "security_review": response.content,
            "messages": [AIMessage(content=f"[安全审查] {response.content}")],
        }

    def performance_reviewer(state: ReviewState) -> dict:
        """性能审查员"""
        print("[性能审查] 分析代码性能...")

        messages = [
            SystemMessage(
                content="你是一个性能优化专家，请分析代码的性能问题和优化建议。用中文简洁回复。"
            ),
            HumanMessage(content=f"代码：\n{state["code"]}"),
        ]

        response = model.invoke(messages)

        return {
            "performance_review": response.content,
            "messages": [AIMessage(content=f"[性能审查] {response.content}")],
        }

    def style_reviewer(state: ReviewState) -> dict:
        """代码风格审查员"""
        print("[风格审查] 检查代码风格...")

        messages = [
            SystemMessage(
                content="你是一个代码风格专家，请检查代码是否符合最佳实践。用中文简洁回复。"
            ),
            HumanMessage(content=f"代码：\n{state["code"]}"),
        ]

        response = model.invoke(messages)

        return {
            "style_review": response.content,
            "messages": [AIMessage(content=f"[风格审查] {response.content}")],
        }

    def report_generator(state: ReviewState) -> dict:
        """报告生成器"""
        print("[报告生成] 汇总所有审查结果...")

        messages = [
            SystemMessage(
                content="你是一个技术报告撰写者，请汇总以下审查结果，生成一份简洁的审查报告。用中文回复。"
            ),
            HumanMessage(
                content=f"""
安全审查结果：
{state["security_review"]}

性能审查结果：
{state["performance_review"]}

风格审查结果：
{state["style_review"]}
"""
            ),
        ]

        response = model.invoke(messages)

        return {"final_report": response.content}

    # 构建顺序执行的图
    graph = StateGraph(ReviewState)

    graph.add_node("security", security_reviewer)
    graph.add_node("performance", performance_reviewer)
    graph.add_node("style", style_reviewer)
    graph.add_node("report", report_generator)

    graph.add_edge(START, "security")
    graph.add_edge("security", "performance")
    graph.add_edge("performance", "style")
    graph.add_edge("style", "report")
    graph.add_edge("report", END)

    app = graph.compile()

    # 测试代码
    test_code = """
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    data = []
    for row in result:
        data.append(row)
    return data
    """

    result = app.invoke({"code": test_code, "messages": []})

    print("\n代码审查报告：")
    print(result["final_report"])

    return result


# 主程序
if __name__ == "__main__":
    collaborative_chain()
