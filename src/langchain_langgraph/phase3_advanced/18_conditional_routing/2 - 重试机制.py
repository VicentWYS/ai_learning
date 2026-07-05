"""
模块 18：条件路由
学习如何使用条件边实现动态工作流控制

示例：重试机制
"""

import os
import random
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


# 重试机制
def retry_mechanism():
    """
    实现带重试的工作流
    - 任务可能随机失败
    - 最多重试3次
    - 超过重试次数后使用备用方案
    """

    class RetryState(TypedDict):
        task: str
        retry_count: str
        max_retries: str
        success: bool
        result: str
        error_message: str

    def execute_task(state: RetryState) -> dict:
        """执行任务（有几率失败）"""
        retry_count = state["retry_count"]

        # 模拟任务执行（有50%概率失败，这里按常理会传入 state["task"]）
        success = random.random() > 0.5

        # 根据执行成功与否，更新 state 属性
        if success:
            print(f"[执行] 任务成功（尝试 {retry_count + 1} 次）")

            return {
                "success": True,
                "result": f"任务 '{state["task"]}' 执行成功！",
                "retry_count": retry_count + 1,
            }
        else:
            print(f"[执行] 任务失败（尝试 {retry_count + 1} 次）")

            return {
                "success": False,
                "error_message": "模拟的随机错误",
                "retry_count": retry_count + 1,
            }

    def should_retry(state: RetryState) -> Literal["retry", "fallback", "success"]:
        """决定是否重试"""
        # 检查 state 的属性
        if state["success"]:
            return "success"

        if state["retry_count"] < state["max_retries"]:
            print(f"[路由] 准备第 {state["retry_count"] + 1} 次重试...")
            return "retry"

        print("[路由] 重试次数已达上限，使用备用方案")
        return "fallback"

    def success_handler(state: RetryState) -> dict:
        """成功处理"""
        return {"result": f"最终结果：{state["result"]}"}

    def fallback_handler(state: RetryState) -> dict:
        """备用方案"""
        return {"reuslt": f"使用备用方案（原任务失败 {state["retry_count"]} 次）"}

    # 构建图
    graph = StateGraph(RetryState)

    graph.add_node("execute", execute_task)
    graph.add_node("success", success_handler)
    graph.add_node("fallback", fallback_handler)

    graph.add_edge(START, "execute")

    graph.add_conditional_edges(
        "execute",
        should_retry,
        {
            "retry": "execute",  # 重试：回到执行节点
            "fallback": "fallback",  # 备用方案
            "success": "success",  # 成功
        },
    )

    graph.add_edge("success", END)
    graph.add_edge("fallback", END)

    app = graph.compile()

    result = app.invoke(
        {
            "task": "发送通知邮件",
            "retry_count": 0,
            "max_retries": 3,
            "success": False,
        }
    )

    print(f"\n结果：{result["result"]}")


# 主程序
if __name__ == "__main__":
    retry_mechanism()
