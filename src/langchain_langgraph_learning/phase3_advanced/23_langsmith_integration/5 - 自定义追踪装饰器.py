"""
模块 22：LangSmith 集成
学习如何追踪、监控和调试 LLM 应用
"""

from functools import wraps
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
# 自定义追踪装饰器
# =================================================================
def custom_traceable(name: str = None, tags: list = None):
    """
    自定义追踪装饰器
    在没有 LangSmith 的情况下也提供本地追踪
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            func_tags = tags or []

            start_time = time.time()
            print(f"  🔍 开始追踪: {func_name}")

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                print(f"  ✅ 完成: {func_name} ({elapsed:.2f}s)")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                print(f"  ❌ 失败: {func_name} ({elapsed:.2f}s) - {e}")
                raise

        return wrapper

    return decorator


@custom_traceable(name="summarize_text", tags=["demo", "summarization"])
def summarize_text(text: str) -> str:
    """带追踪的文本摘要函数"""
    response = model.invoke(f"请用一句话总结：{text}")
    return response.content


def custom_decorator_demo():
    """
    演示自定义追踪装饰器
    """
    print("\n" + "=" * 60)
    print("示例 5：自定义追踪装饰器")
    print("=" * 60)

    text = "Python 是一种广泛使用的高级编程语言，以其简洁的语法和强大的功能著称。"

    summary = summarize_text(text)
    print(f"\n原文: {text}")
    print(f"摘要: {summary}")


# =================================================================
# 主程序
# =================================================================
if __name__ == "__main__":
    if not LANGSMITH_ENABLED:
        print("\n提示：配置 LANGSMITH_API_KEY 以启用完整的追踪功能")
        print("本地演示仍可运行，但数据不会发送到 LangSmith\n")

    # 运行示例
    custom_decorator_demo()
