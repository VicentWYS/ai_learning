"""
模块 18：条件路由
学习如何使用条件边实现动态工作流控制

示例：复杂决策树
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypedDict, Literal
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


# 复杂决策树
def complex_decision_tree():
    """
    复杂决策树：多条件组合
    模拟贷款审批流程
    """

    class LoanState(TypedDict):
        applicant_name: str
        credit_score: int
        income: int
        loan_amount: int
        has_collateral: bool
        current_stage: str
        decision: str
        reason: str

    def initial_check(state: LoanState) -> dict:
        """初步检查"""
        print(f"[初步检查] 申请人：{state["applicant_name"]}")
        print(f"信用分：{state["credit_score"]}")
        print(f"月收入：{state["income"]}")
        print(f"贷款金额：{state["loan_amount"]}")
        print(f"有抵押物：{state["has_collateral"]}")

        return {
            "current_stage": "initial_check_done"
        }  # 这一节点的功能是更新 state 的属性

    def route_initial(
        state: LoanState,
    ) -> Literal["auto_reject", "credit_review", "income_review"]:
        """初步路由"""
        # 信用分太低直接拒绝
        if state["credit_score"] < 550:
            return "auto_reject"

        # 高信用分走快速通道
        if state["credit_score"] >= 750:
            return "income_review"

        # 中等信用分需要详细审查
        return "credit_review"

    def auto_reject(state: LoanState) -> dict:
        """自动拒绝"""
        print("[自动拒绝] 信用分过低")
        return {"decision": "REJECTED", "reason": "信用评分低于最低要求"}

    def credit_review(state: LoanState) -> dict:
        """信用审查"""
        print("[信用审查] 进行详细信用评估...")
        return {"current_stage": "credit_reviewed"}  # 这一节点的功能是更新 state 的属性

    def route_credit(state: LoanState) -> Literal["income_review", "manual_review"]:
        """信用检查后路由"""
        # 若有抵押物，可以继续
        if state["has_collateral"]:
            return "income_review"

        # 否则需人工审核
        return "manual_review"

    def income_review(state: LoanState) -> dict:
        """收入审查"""
        print("[收入审查] 评估还款能力...")
        return {"current_stage": "income_reviewed"}

    def route_income(
        state: LoanState,
    ) -> Literal["approve", "partial_approve", "manual_review"]:
        """收入审查后路由"""
        # 计算贷款收入比
        loan_to_income = state["loan_amount"] / (state["income"] * 12)

        if loan_to_income <= 3:
            return "approve"  # 贷款金额不超过年收入的 3 倍
        elif loan_to_income <= 5:
            return "partial_approve"  # 贷款金额不超过年收入的 5 倍
        else:
            return "manual_review"  # 贷款金额过大，走人工审查

    def approve(state: LoanState) -> dict:
        """批准贷款"""
        print("[批准] 贷款申请通过")
        return {"decision": "APPROVED", "reason": "符合所有审批条件"}

    def partial_approve(state: LoanState) -> dict:
        """批准部分金额"""
        approved_amount = state["income"] * 12 * 3  # 批准只贷出年收入的 3 倍

        print(f"[部分批准] 批准部分金额：{approved_amount} 元")
        return {
            "decision": "PARTIALLY_APPROVED",
            "reason": f"批准金额：{approved_amount}（原申请金额：{state["loan_amount"]}）",
        }

    def manual_review(state: LoanState) -> dict:
        """人工审核"""
        print(f"[人工审核] 已转人工审核")

        return {"decision": "PENDING_REVIEW", "reason": "需要信贷专员进一步审核"}

    # 构建图
    graph = StateGraph(LoanState)

    graph.add_node("initial_check", initial_check)
    graph.add_node("auto_reject", auto_reject)
    graph.add_node("credit_review", credit_review)
    graph.add_node("income_review", income_review)
    graph.add_node("approve", approve)
    graph.add_node("partial_approve", partial_approve)
    graph.add_node("manual_review", manual_review)

    graph.add_edge(START, "initial_check")

    graph.add_conditional_edges(
        "initial_check",
        route_initial,
        {
            "auto_reject": "auto_reject",
            "credit_review": "credit_review",
            "income_review": "income_review",
        },
    )

    graph.add_conditional_edges(
        "credit_review",
        route_credit,
        {"income_review": "income_review", "manual_review": "manual_review"},
    )

    graph.add_conditional_edges(
        "income_review",
        route_income,
        {
            "approve": "approve",
            "partial_approve": "partial_approve",
            "manual_review": "manual_review",
        },
    )

    graph.add_edge("auto_reject", END)
    graph.add_edge("approve", END)
    graph.add_edge("partial_approve", END)
    graph.add_edge("manual_review", END)

    app = graph.compile()

    # 测试不同的申请案例
    test_cases = [
        {
            "applicant_name": "张三",
            "credit_score": 800,
            "income": 20000,
            "loan_amount": 500000,
            "has_collateral": True,
        },
        {
            "applicant_name": "李四",
            "credit_score": 650,
            "income": 10000,
            "loan_amount": 200000,
            "has_collateral": True,
        },
        {
            "applicant_name": "王五",
            "credit_score": 500,
            "income": 8000,
            "loan_amount": 100000,
            "has_collateral": False,
        },
        {
            "applicant_name": "赵六",
            "credit_score": 720,
            "income": 15000,
            "loan_amount": 100000,
            "has_collateral": False,
        },
    ]

    for case in test_cases:
        result = app.invoke(case)
        print(f"\n决定：{result["decision"]}")
        print(f"理由：{result["reason"]}\n\n")


# 主程序
if __name__ == "__main__":
    complex_decision_tree()
