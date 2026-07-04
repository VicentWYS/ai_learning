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
    model="qwen-turbo",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# 备用模型
# 这里这种写法不好，代码有冗余，如果备用模型有多个，那么代码会变得很复杂，后续需优化
model_backup = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ==================================================================================
# 示例2 - 使用 with_fallbacks() 降级方案
# ==================================================================================
def example_2_with_fallbacks():
    """
    示例2 - 使用 with_fallbacks() 降级方案

    - 主模型失败时，自动切换到备用模型

    - 配置：
        - 主模型：qwen-turbo
        - 备用模型：qwen-plus

    - 流程：
        - 主模型成功 → 使用主模型响应
        - 主模型失败 → 自动切换到备用模型
        - 适用于高可用性场景
    """
    print("\n" + "-" * 40)
    print("示例2 - with_fallbacks() 降级方案")

    # 主模型（假设可能失败）
    primary_model = model

    # 备用模型（更可靠或更便宜）
    fallback_model = model_backup

    # 配置降级
    llm_with_fallbacks = primary_model.with_fallbacks([fallback_model])

    try:
        response = llm_with_fallbacks.invoke("用一句话简单介绍一下小说《三国演义》")
        print(f"\nAI 回复：{response.content[:50]}...")
    except Exception as e:
        print(f"\n所有模型都调用失败：{e}")


# ==================================================================================
# 主程序
# ==================================================================================
def main():
    try:
        example_2_with_fallbacks()
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()
    except KeyboardInterrupt:
        print("\n\n程序中断")


if __name__ == "__main__":
    main()
