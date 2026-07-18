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
# 错误追踪
# =================================================================
def error_tracing():
    """
    追踪和记录错误
    """

    def risky_operation(query: str, should_fail: bool = False):
        """模拟可能失败的操作"""
        config = RunnableConfig(
            metadata={"operation_type": "risky", "should_fail": should_fail},
            tags=["error_test"],
        )

        if should_fail:
            # 注意，这里的错误信息属于业务错误，因为是发生在 model.invoke之前，
            # 故错误信息无法记录到 langsmith 中
            raise ValueError("模拟的错误：请求参数无效")

        return model.invoke(query, config=config)

    # 成功的调用
    print("\n测试1：正常调用")
    try:
        response = risky_operation(query="你好！")
        print(f"成功：{response.content}")
    except Exception as e:
        print(f"失败：{e}")

    # 失败的调用
    print(f"\n测试2：会失败的调用")
    try:
        response = risky_operation(query="介绍成语“刻舟求剑”", should_fail=True)
        print(f"成功：{response.content}")
    except Exception as e:
        print(f"捕获错误：{e}")


# =================================================================
# 主程序
# =================================================================
if __name__ == "__main__":
    if not LANGSMITH_ENABLED:
        print("\n提示：配置 LANGSMITH_API_KEY 以启用完整的追踪功能")
        print("本地演示仍可运行，但数据不会发送到 LangSmith\n")

    # 运行示例
    error_tracing()
