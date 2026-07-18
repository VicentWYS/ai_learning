"""
LangChain 1.0 - outputparser 结构化输出
=======================================================

这里使用一个手工设计的方法 safe_structured_output() 来实现结构化输出
核心是：model.with_structured_output(output_class)
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing import TypeVar, Type, List, Optional
from pydantic import BaseModel, Field

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


# 这句代码的含义：
# T 是一个类型变量（TypeVar），限定只能是 BaseModel 或其子类。
# 这样 T 可以在泛型函数/类中代表任意一个 Pydantic 数据模型类型。
#
# BaseModel 是 Pydantic 框架的基础类，用来定义数据模型，具有数据校验、类型提示、序列化/反序列化等特性。
# 与普通 Python 类相比，BaseModel 子类会自动检查字段类型、提供默认的 .dict()/.json() 方法等，更适合做结构化数据输入输出。
T = TypeVar("T", bound=BaseModel)


def create_safe_structured_llm(output_class):
    """
    创建结构化输出的 LLM
    """

    # 这里将普通的 LLM（大模型）包装成能够直接输出结构化数据（如 Pydantic 模型对象）的版本。
    # 这样，后续调用 .invoke(prompt) 时，返回的不再是纯文本，而会自动解析为我们想要的数据模型类型（output_class）。
    # 从而可以进入代码的运行流程中
    base_llm = model.with_structured_output(output_class)

    class SafeStructuredLLM:
        def invoke(self, prompt):
            try:
                return base_llm.invoke(prompt)
            except Exception as e:
                print(f"结构化输出失败: {e}")

    return SafeStructuredLLM()


def safe_structured_output(prompt: str, output_class: Type[T]) -> T:
    """
    安全的结构化输出函数
    """
    try:
        result = create_safe_structured_llm(output_class).invoke(prompt)
        return result
    except Exception as e:
        print(f"结构化输出失败: {e}")


# ===================================================================================
# 示例 4 - 可选字段和默认值
# ===================================================================================
class Project(BaseModel):
    """产品信息"""

    name: str = Field(description="产品名称")
    price: float = Field(description="产品价格")
    description: Optional[str] = Field(default="暂无描述", description="对该产品的描述（可选）")
    stock: int = Field(default=50, description="库存数量（默认50")


def example_4_optional_and_default_value():
    """
    示例 4 - 可选字段和默认值

    - 该示例演示了如何使用安全的结构化输出函数 safe_structured_output() 来提取可选字段和默认值。
    - 可选字段和默认值的组合，可以处理不完整的信息，并提供默认值，避免缺失字段导致错误
    """
    print("\n" + "-" * 40)
    print("示例 4：可选字段和默认值")

    # 缺少描述和库存
    text = """
    iPhone 15 售价 5999 元。
    """

    response = safe_structured_output(f"{text}", Project)

    print(f"\n返回类型：{response.__class__.__name__}")
    print(f"返回结果：{response}")
    print(f"用户提示词：{text}")
    print(f"产品名称：{response.name}")
    print(f"产品价格：{response.price}")
    print(f"产品描述：{response.description}")
    print(f"库存数量：{response.stock}")


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    try:
        example_4_optional_and_default_value()

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
