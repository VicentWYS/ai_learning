"""
模块 22：LangSmith 集成
学习如何追踪、监控和调试 LLM 应用
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
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
# 带元数据的追踪
# =================================================================
def tracing_with_metadata():
    """
    添加自定义元数据到追踪
    """
    # 创建带元数据的配置
    config = RunnableConfig(
        metadata={
            "user_id": "user_1234",
            "session_id": "session_1122",
            "request_type": "question",
            "app_version": "1.0.0",
        },
        tags=["langchain", "phase3", "module22"],
    )

    messages = [
        SystemMessage(content="你是一名友好的智能助手，用中文简洁回答。"),
        HumanMessage(content="在具体的工程实践中，LangSmith 是如何被使用的？"),
    ]

    response = model.invoke(messages, config=config)

    print(f"AI 回复：{response.content}")

    return response


# =================================================================
# 主程序
# =================================================================
if __name__ == "__main__":
    if not LANGSMITH_ENABLED:
        print("\n提示：配置 LANGSMITH_API_KEY 以启用完整的追踪功能")
        print("本地演示仍可运行，但数据不会发送到 LangSmith\n")

    # 运行示例
    tracing_with_metadata()
