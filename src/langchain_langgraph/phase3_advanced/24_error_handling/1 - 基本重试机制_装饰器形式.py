"""
模块 23：错误处理
学习如何实现健壮的错误处理和恢复机制
"""

import os
import time
import random
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
# 基本重试机制
# ==================================================================================
def retry_with_backoff(
    max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0
):
    """
    带指数退避的重试装饰器（支持 @retry_with_backoff(...) 形式）
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt < max_retries - 1:
                        # 计算等待时间（指数退避 + 随机抖动）
                        delay = min(base_delay * (2**attempt), max_delay)
                        jitter = random.uniform(0, delay * 0.1)
                        wait_time = delay + jitter

                        print(f"  ⚠️ 尝试 {attempt + 1} 失败: {e}")
                        print(f"     等待 {wait_time:.1f} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        print(f"  ❌ 所有 {max_retries} 次尝试均失败")

            raise last_exception

        return wrapper

    return decorator


def basic_retry():
    """
    实现基本的重试机制
    """
    # 模拟不稳定的函数
    call_count = [0]

    @retry_with_backoff(max_retries=3, base_delay=0.5)
    def unstable_function(query: str):
        """模拟一个可能失败的函数"""
        call_count[0] += 1

        # 前两次调用失败
        if call_count[0] <= 2:
            raise ConnectionError(f"模拟网络错误 (尝试 {call_count[0]})")

        return model.invoke(query)

    print("调用不稳定函数（前2次会失败）...")
    try:
        result = unstable_function("简单回答：1+1等于几？")
        print(f"最终成功: {result.content}")
    except Exception as e:
        print(f"最终失败: {e}")


# ==================================================================================
# 主程序
# ==================================================================================
if __name__ == "__main__":
    basic_retry()
