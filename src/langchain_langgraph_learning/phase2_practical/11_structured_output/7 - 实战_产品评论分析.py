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


# =================================== 辅助函数 ===================================
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


# ==================================================================================
# 示例7 - 实际应用：产品评论分析
# ==================================================================================
class Sentiment(str, Enum):
    """情感"""

    POSITIVE = "正面"
    NEUTRAL = "中性"
    NEGATIVE = "负面"


class Review(BaseModel):
    """
    评论

    LLM 需要从用户评论的属性
    """

    product: str = Field(description="产品名称")
    rating: int = Field(description="评分(1-5)")
    sentiment: Sentiment = Field(description="情感: 正面/中性/负面")
    pros: List[str] = Field(description="优点列表")
    cons: List[str] = Field(description="缺点列表")


def example_7_review_analysis():
    """
    示例7 - 实际应用：产品评论分析

    - 从自然语言评论中提取结构化信息
    - 应用场景：
        - 批量处理用户评论
        - 自动生成分析报告
        - 发现产品改进点
    """
    print("\n" + "-" * 40)
    print("示例7 - 实际应用：产品评论分析")

    structured_llm = create_safe_structured_llm(Review)

    review_text = """
    这款 iPhone 15 Pro 真的很不错！摄像头非常强大，夜拍效果惊艳。
    钛金属边框手感也很好。但是价格有点贵，而且没有充电器。
    总体来说还是值得购买的，我给 4 分。
    """

    print(f"\n评论文本：{review_text}\n")

    result = structured_llm.invoke(f"从以下评论文本中提取结构化信息：\n{review_text}")

    print(f"\n提取结果：{result}\n")
    print(f"产品名称：{result.product}")  # iPhone 15 Pro
    print(f"评分：{result.rating} / 5")  # 4
    print(f"情感：{result.sentiment.value}")  # 正面
    print(
        f"优点列表：{result.pros}"
    )  # ['摄像头非常强大', '夜拍效果惊艳', '钛金属边框手感也很好']
    print(f"缺点列表：{result.cons}")  # ['价格有点贵', '没有充电器']


# ==================================================================================
# 主程序
# ==================================================================================
def main():
    try:
        example_7_review_analysis()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
