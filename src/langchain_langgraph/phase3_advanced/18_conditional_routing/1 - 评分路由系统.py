"""
模块 18：条件路由
学习如何使用条件边实现动态工作流控制

示例：路由评分系统
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict, Literal
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


# 评分路由系统
def score_based_routing():
    """
    根据评分决定处理流程
    - 优秀(>= 90): 发送表扬信
    - 良好(>= 70): 正常通过
    - 需改进(>= 50): 提供建议
    - 不及格(<50): 需要重新提交
    """

    class ScoreState(TypedDict):
        content: str
        score: str
        feedback: str
        result: str

    def evaluate(state: ScoreState) -> dict:
        """评估内容并打分"""
        print("[评估&打分] 评估内容并打分...")
        messages = [
            SystemMessage(
                content="""你是一个内容评估专家。请评估以下内容并给出1-100的分数。
只返回一个数字分数，不要其他内容。评估标准：
- 90-100：优秀，内容完整、准确、有创意
- 70-89：良好，内容基本完整，表达清晰
- 50-69：需改进，内容有所欠缺
- 0-49：不合格，需要重新撰写"""
            ),
            HumanMessage(content=state["content"]),
        ]
        response = model.invoke(messages)

        try:
            score = int(response.content.strip())
            score = max(0, min(100, score))  # 确保在 0~100范围内
        except:
            score = 70  # 默认分数

        print(f"[评估&打分]: {score}")
        return {"score": score}

    def route_by_score(
        state: ScoreState,
    ) -> Literal["excellent", "good", "improve", "reject"]:
        """根据分数路由"""
        score = state["score"]
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "improve"
        else:
            return "reject"

    def handel_excellent(state: ScoreState) -> dict:
        """处理优秀评分"""
        return {
            "feedback": "恭喜！您的内容非常出色！",
            "result": "APPROVED_WITH_HONORS",
        }

    def handel_good(state: ScoreState) -> dict:
        """处理良好评分"""
        return {"feedback": "内容合格，已通过审核", "result": "APPROVED"}

    def handel_improve(state: ScoreState) -> dict:
        """处理需改进评分"""
        print("需改进：生成改进建议...")

        messages = [
            SystemMessage(
                content="请为以下内容提供简洁的改进建议（50字以内）。用中文回复。"
            ),
            HumanMessage(content=state["content"]),
        ]

        response = model.invoke(messages)

        return {
            "feedback": f"改进建议：{response.content}",
            "result": "NEEDS_IMPROVEMENT",
        }

    def handel_reject(state: ScoreState) -> dict:
        """处理不合格评分"""
        return {"feedback": "内容不符合要求，请重新撰写并提交。", "result": "REJECTED"}

    # 构建图
    graph = StateGraph(ScoreState)

    graph.add_node("evaluate", evaluate)
    graph.add_node("excellent", handel_excellent)
    graph.add_node("good", handel_good)
    graph.add_node("improve", handel_improve)
    graph.add_node("reject", handel_reject)

    graph.add_edge(START, "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        route_by_score,
        {
            "excellent": "excellent",
            "good": "good",
            "improve": "improve",
            "reject": "reject",
        },
    )

    for node in ["excellent", "good", "improve", "reject"]:
        graph.add_edge(node, END)

    app = graph.compile()

    # 测试不同质量内容
    test_contents = [
        "Python 是一种广泛使用的高级编程语言，以其清晰的语法和强大的功能著称。它支持多种编程范式，包括面向对象、函数式和过程式编程。Python 拥有丰富的标准库和第三方库，广泛应用于 Web 开发、数据科学、人工智能等领域。",
        "Python 是编程语言，很好用。",
        "编程",
    ]

    for content in test_contents:
        print(f"\n提交内容：{content[:100]}...")

        result = app.invoke({"content": content})

        print(f"结果：{result["result"]}")
        print(f"反馈：{result["feedback"]}")


# 主程序
if __name__ == "__main__":
    score_based_routing()
