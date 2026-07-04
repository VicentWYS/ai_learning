"""
LangChain 1.0 - Validation Retry Fallbacks

流程：
1. 主模型成功 → 使用主模型响应
2. 主模型失败 → 自动切换到备用模型
3. 备用模型失败 → 自动重试
4. 重试失败 → 返回 None
5. 验证失败 → 返回 None
6. 验证成功 → 返回数据

不建议在备用模型上也添加重试机制，以避免重试次数过多，以及日志打印过于复杂。

在很多业务里，“较快失败 + 可观测”比“又慢又不稳定地偶尔成功”更好。
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, TypeVar, Type


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


# ===================================================
# 示例7 - 组合使用 retry + fallbacks + validation
# ===================================================
class ExtractedData(BaseModel):
    """
    待提取的数据类
    """

    name: str = Field(description="名称", min_length=1)  # 最小长度为1
    value: float = Field(description="值", gt=0)  # 大于0

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("名称不能为空")
        return v.strip()


def example_7_combined():
    """
    示例7 - 组合使用 retry + fallbacks + validation

    - 重试 + 模型降级 + 验证
    - 流程：
        - 主模型成功 → 使用主模型响应
        - 主模型失败 → 自动切换到备用模型
        - 备用模型失败 → 自动重试
        - 重试失败 → 返回 None
        - 验证失败 → 返回 None
        - 验证成功 → 返回数据

    - 配置：
        - 主模型：qwen-turbo
        - 备用模型：qwen-plus
    """
    print("\n" + "-" * 40)
    print("示例7 - 组合使用 retry + fallbacks + validation")

    # 创建结构化输出 llm
    structured_primary = model.with_structured_output(
        ExtractedData, method="function_calling"
    )

    # 创建备用模型（也要进行结构化输出）
    fallback_model = init_chat_model(
        model="qwen-plus",  # 备用模型改为 qwen-plus
        model_provider="openai",
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0.8,
    )
    structured_fallback = fallback_model.with_structured_output(
        ExtractedData, method="function_calling"
    )

    # （嵌入）主模型添加重试机制
    primary_with_retry = structured_primary.with_retry(
        retry_if_exception_type=(ConnectionError, TimeoutError),  # 重试的异常类型
        wait_exponential_jitter=True,  # 退避策略：指数退避+随机抖动
        stop_after_attempt=3,  # 最多重试3次
    )

    # 添加降级
    robust_llm = primary_with_retry.with_fallbacks([structured_fallback])

    try:
        prompt = """从以下文本中提取数据信息。
注意：value 必须是数字类型（float），不能是字符串。
文本如下：
产品 C 的价值是 1299 元"""
        result = robust_llm.invoke(prompt)
        print(f"提取成功：{result.model_dump()}")
    except Exception as e:
        print(f"所有策略都失败：{e}")


# ===================================================
# 主函数
# ===================================================
def main():
    try:
        example_7_combined()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
