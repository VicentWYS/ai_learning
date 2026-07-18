"""
模块 22：LangSmith 集成
学习如何追踪、监控和调试 LLM 应用
"""

import os
import time
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig


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


def setup_langsmith(project_name: str = "langchain_study"):
    """
    配置 LangSmith 追踪
    """

    # 检查是否有 API Key
    api_key = os.environ.get("LANGSMITH_API_KEY")

    if api_key:
        os.environ["LANGSMITH_TRACING_V2"] = "true"
        os.environ["LANGSMITH_PROJECT"] = project_name

        print(f"LangSmith 已启用（项目：{project_name}）")
        return True
    else:
        print("未配置 LANGSMITH_API_KEY，追踪功能未启用")
        print("请在 .env 文件中添加：LANGSMITH_API_KEY=your_key")
        return False


# 尝试设置 LangSmith
LANGSMITH_ENABLED = setup_langsmith()


# =================================================================
# 性能监控
# =================================================================
def performance_monitoring():
    """
    监控 LLM 调用的性能指标
    """
    questions = [
        "1+1等于几？",
        "解释什么是机器学习，用100字以内。",
        "写一个简短的 Python 函数来计算斐波那契数列。",
    ]

    results = []

    for i, question in enumerate(questions, 1):
        print(f"\n测试 {i}: {question[:30]}...")

        start_time = time.time()

        # 带性能元数据的调用
        config = RunnableConfig(
            metadata={
                "test_id": f"perf_test_{i}",
                "complexity": "low" if i == 1 else ("medium" if i == 2 else "high"),
            },
            tags=["performance_test"],
        )

        response = model.invoke(question, config=config)

        elapsed_time = time.time() - start_time

        # 提取 token 使用情况（如果有）
        token_usage = getattr(response, "usage_metadata", None)

        result = {
            "question": question[:30],
            "response_length": len(response.content),
            "elapsed_time": elapsed_time,
            "token_usage": token_usage,
        }

        results.append(result)

        print(f"响应长度：{result["response_length"]} 个字符")
        print(f"耗时：{result["elapsed_time"]:.2f} 秒")
        if token_usage:
            print(f"Token 使用：{token_usage}")

    # 汇总
    print("\n性能汇总：")
    total_time = sum(r["elapsed_time"] for r in results)
    avg_time = total_time / len(results)

    print(f"总耗时：{total_time:.2f} 秒")
    print(f"平均耗时：{avg_time:.2f} 秒")

    return results


# =================================================================
# 主程序
# =================================================================
if __name__ == "__main__":
    if not LANGSMITH_ENABLED:
        print("\n提示：配置 LANGSMITH_API_KEY 以启用完整的追踪功能")
        print("本地演示仍可运行，但数据不会发送到 LangSmith\n")

    # 运行示例
    performance_monitoring()
