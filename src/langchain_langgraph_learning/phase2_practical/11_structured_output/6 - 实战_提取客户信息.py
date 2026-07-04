from enum import Enum
from optparse import Option
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


def safe_structured_output(prompt: str, output_class: Type[T]) -> T:
    """
    安全的结构化输出函数

    用  实现结构化输出
    """
    try:
        structured_llm = create_safe_structured_llm(output_class)
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"结构化输出失败: {e}")


def create_safe_structured_llm(output_class):
    """
    创建带 fallback 的结构化输出 LLM
    """
    base_llm = model.with_structured_output(output_class, method="function_calling")

    class SafeStructuredLLM:
        def invoke(self, prompt):
            try:
                return base_llm.invoke(prompt)
            except Exception as e:
                print(f"结构化输出失败: {e}")

    return SafeStructuredLLM()


# ===================================================================================
# 示例6 - 实际应用：客户信息提取
# ===================================================================================


# (str, Enum) 用于创建一个“枚举类型”类，可以限制某个字段只能取特定的几个字符串值。
# 例如下面的 Priority 类，表明优先级字段只能是 "低"、"中"、"高" 这三种类型之一，避免出错。
class Priority(str, Enum):
    """优先级"""

    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


class CustomerInfo(BaseModel):
    """客户信息"""

    name: str = Field(description="客户姓名")
    phone: str = Field(description="客户电话")
    email: Optional[str] = Field(None, description="客户邮箱(可选)")
    issue: str = Field(description="问题描述")
    urgency: Priority = Field(description="问题紧急程度: low/mid/high")


def example_6_customer_info_extraction():
    """
    示例6 - 实际应用：客户信息提取

    - 从客服对话中提取结构化信息
    - 应用场景：
        - 自动填充 CRM 系统
        - 工单自动分类
        - 紧急问题优先处理
    """
    print("\n" + "-" * 40)
    print("示例6 - 实际应用：客户信息提取")

    structured_llm = create_safe_structured_llm(CustomerInfo)

    conversation = """
    客服: 您好，请问有什么可以帮助您？
    客户: 我是李明，电话 138-1234-5678，我的订单一直没发货，很着急！
    客服: 好的，我帮您查一下
    """

    print(f"\n对话记录：{conversation}\n")
    result = structured_llm.invoke(f"从以下客服对话中提取客户信息：\n{conversation}")

    print(f"\n提取结果：{result}\n")
    print(f"客户姓名：{result.name}")  # 李明
    print(f"客户电话：{result.phone}")  # 138-1234-5678
    print(f"客户邮箱：{result.email}")  # None
    print(f"问题描述：{result.issue}")  # 订单一直没发货
    print(f"问题紧急程度：{result.urgency.value}")  # 高


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    try:
        example_6_customer_info_extraction()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
