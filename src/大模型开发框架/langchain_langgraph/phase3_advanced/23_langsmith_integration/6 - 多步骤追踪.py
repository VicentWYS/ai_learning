"""
模块 22：LangSmith 集成
学习如何追踪、监控和调试 LLM 应用

这个方法可以免去在控制台打印内容的繁琐，直接到 langsmith 仪表板观察每次大模型调用情况即可
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
# 多步骤追踪
# =================================================================
def multi_step_tracing():
    """
    追踪多步骤工作流
    """
    # 模拟一个多步骤的 AI 工作流
    parent_config = RunnableConfig(
        metadata={"workflow": "content_creation"}, tags=["multi_step", "workflow"]
    )

    # 步骤一：生成大纲
    print("\n一、生成大纲")
    step1_config = RunnableConfig(
        metadata={**parent_config.get("metadata", {}), "step": "outline"},
        tags=["step1"],
    )
    outline = model.invoke(
        "为一篇关于'AI 的未来'的文章生成3点大纲。", config=step1_config
    )
    print(f"AI 回复：{outline.content[:150]}...")

    # 步骤二、扩展第一点
    print("\n二、扩展内容")
    step2_config = RunnableConfig(
        metadata={**parent_config.get("metadata", {}), "step": "expand"}, tags=["step2"]
    )
    expaned = model.invoke(
        f"基于以下大纲，扩展第一点（50字以内）：\n{outline.content}",
        config=step2_config,
    )
    print(f"扩展后的大纲：{expaned.content[:150]}...")

    # 步骤三、润色
    print("\n三、润色文字")
    step3_config = RunnableConfig(
        metadata={**parent_config.get("metadata", {}), "step": "polish"}, tags=["step3"]
    )
    polished = model.invoke(
        f"请润色以下文字，使其更专业：\n{expaned.content}", config=step3_config
    )

    print(f"\n最终内容：{polished.content}")
    print("\n工作流完成。所有步骤已追踪记录。")

    return polished.content


# =================================================================
# 主程序
# =================================================================
if __name__ == "__main__":
    if not LANGSMITH_ENABLED:
        print("\n提示：配置 LANGSMITH_API_KEY 以启用完整的追踪功能")
        print("本地演示仍可运行，但数据不会发送到 LangSmith\n")

    # 运行示例
    multi_step_tracing()
