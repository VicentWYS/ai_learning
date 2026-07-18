"""
LangChain 1.0 - outputparser 结构化输出
=======================================================

这里使用一个手工设计的方法 safe_structured_output() 来实现结构化输出
核心是：model.with_structured_output(output_class)
"""

from enum import Enum
import os
from turtle import title
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


T = TypeVar("T", bound=BaseModel)


def create_safe_structured_llm(output_class):
    """
    创建结构化输出的 LLM
    """

    base_llm = model.with_structured_output(output_class, method="function_calling")

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
# 示例 5 - 提取枚举类型
# ===================================================================================
class Priority(str, Enum):
    """优先级"""

    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


class Task(BaseModel):
    """任务"""

    title: str = Field(description="任务标题")
    priority: Priority = Field(description="优先级：低/中/高")
    completed: bool = Field(default=False, description="是否完成")


def example_5_enum_types():
    """
    示例5：提取枚举类型

    - 限制字段的可选值
        - Priority(str, Enum) 定义枚举
        - LLM 只能选择 LOW/MEDIUM/HIGH
        - 自动验证，无效值会报错
    """
    print("\n" + "-" * 40)
    print("示例 5：提取枚举")

    structured_llm = create_safe_structured_llm(Task)

    print("\n提示：完成季度报告，这是紧急任务")
    prompt = """
    从输入内容中提取关键信息。
    输入内容：完成季度报告，这是紧急任务，优先级为高
    """

    result = structured_llm.invoke(prompt)

    print(f"\n任务：{result.title}")  # 完成季度报告
    print(f"优先级：{result.priority.value}")  # 高
    print(f"完成状态：{result.completed}")  # False


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    try:
        example_5_enum_types()

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
