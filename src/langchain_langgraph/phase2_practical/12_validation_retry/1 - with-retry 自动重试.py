"""
失败不是异常，而是设计的一部分
成熟系统必须：
    - 处理网络波动
    - 处理限流
    - 处理服务不稳定

而不是假设 API 永远成功。
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model


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


# ==================================================================================
# 示例1 - 使用 with-retry 自动重试
# ==================================================================================
def example_1_with_retry():
    """
    示例1 - 使用 with_try() 处理网络错误

    - 当遇到临时性错误（网络超时、API 限流等）时自动重试
    - 关键点：
        - with_retry() 是 Runnable 接口的方法
        - 适用于临时性错误（网络波动、API限流）
        - 不适用于逻辑错误（提示词错误、参数错误）
    """
    print("\n" + "-" * 40)
    print("示例1 - with_try() 自动重试机制")

    # 创建带重试的 LLM
    # 重试之间的等待时间采用「指数退避 + 随机抖动（jitter）」策略，而不是固定间隔。
    # 也就是：第 1 次、第 2 次、第 3 次重试之间的等待时间会越来越长（指数增长），同时每次会在这个基础上加一点随机波动，而不是完全等同的时间。
    #
    # 作用：
    # 避免频繁、密集地打API：如果接口暂时不稳定或限流，指数退避会让你「越来越慢地」重试，更容易等到服务恢复。
    # 减少拥塞/雪崩效应：加上随机抖动后，很多客户端同时失败并一起重试时，可以将重试时间分散，减轻目标服务的压力。
    # 提高成功率：这种退避策略通常比定时重试更稳定、更友好。
    #
    #
    # 为什么 model 会有 with_retry 方法？
    # 这是因为在 langchain 的设计中，所有的模型（model）对象其实都是 Runnable 的子类。
    # Runnable 是 langchain 的一个核心基类（见 langchain_core/runnables/base.py），
    # 它除了提供 invoke 方法（用于单次调用）之外，还提供了 with_retry、with_fallbacks、with_structured_output 等方法，
    # 用于给链/模型包装出更多能力（比如自动重试、降级等）。
    #
    # 你可以理解为：invoke 是 Runnable 基类的基础能力，with_retry 则是“装饰器”式的组合能力。
    #
    # 所以 model 既可以 .invoke(...)，也可以 .with_retry(...).invoke(...)
    #
    # 参考文档可见：wiki/langchain/Runnable 的核心能力总览.md
    llm_with_retry = model.with_retry(
        retry_if_exception_type=(ConnectionError, TimeoutError),  # 重试的异常类型
        wait_exponential_jitter=True,  # 退避策略：指数退避+随机抖动
        stop_after_attempt=3,  # 最多重试3次
    )

    try:
        print("\n调用 LLM...")
        response = llm_with_retry.invoke("你好，简单介绍一下乞力马扎罗山")
        print(f"\nAI 回复：{response.content[:50]}...")
        print("调用成功")
    except Exception as e:
        print(f"\n重试 3 次后仍然失败：{e}")


# ==================================================================================
# 主程序
# ==================================================================================
def main():
    try:
        example_1_with_retry()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
