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

    # 这里使用 with_structured_output 方法，将普通的 LLM（大模型）包装成能够直接输出结构化数据（如 Pydantic 模型对象）的版本。
    # 这样，后续调用 .invoke(prompt) 时，返回的不再是纯文本，而会自动解析为我们想要的数据模型类型（output_class）。
    # 与一般的 init_chat_model() 不同，with_structured_output 会返回一个「结构化输出」版本的 LLM。
    # 普通 init_chat_model() 得到的 LLM 调用 .invoke(prompt) 时返回原始文本；
    # 而 with_structured_output 后的 LLM，则能直接解析 LLM 输出并转为 Pydantic 的输出模型（output_class 实例），
    #   它会在内部自动做解析、校验等，失败会抛出异常。
    # 适用于需要直接拿结构化数据（如 dict、Pydantic 实例）的场景，而不是只收字符串！
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
# 示例 3 - 提取嵌套的结构化对象
# ===================================================================================
class Address(BaseModel):
    """地址信息"""

    city: str = Field(description="城市")
    district: str = Field(description="区县")


class Company(BaseModel):
    """公司信息"""

    name: str = Field(description="公司名称")
    employee_count: int = Field(description="员工数量")
    address: Address = Field(description="公司地址")


def example_3_nested_structured_output():
    """
    示例 3 - 提取嵌套的结构化对象

    - 该示例演示了如何使用安全的结构化输出函数 safe_structured_output() 来提取嵌套的结构化数据。
    """
    print("\n" + "-" * 40)
    print("示例 3：提取嵌套的结构化对象")

    text = """
    阿里巴巴公司在杭州滨江区，有约 10 万名员工
    """
    response = safe_structured_output(f"从以下文本中提取公司信息：{text}", Company)

    print(f"\n返回类型：{response.__class__.__name__}")
    print(f"返回结果：{response}")
    print(f"公司名称：{response.name}")
    print(f"员工数量：{response.employee_count}")
    print(f"公司地址：{response.address}")
    print(f"城市：{response.address.city}")
    print(f"区县：{response.address.district}")


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    try:
        example_3_nested_structured_output()

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
