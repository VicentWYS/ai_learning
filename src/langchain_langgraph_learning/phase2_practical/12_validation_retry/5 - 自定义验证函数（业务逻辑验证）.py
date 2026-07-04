"""
LangChain 1.0 - 自定义验证函数
用于验证 Pydantic 验证之外的业务逻辑

方法：通过构建验证函数（返回bool类型），验证失败后返回 False
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
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
    model="qwen-turbo",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ===================================================================================
# 示例5 - 自定义验证函数
# ===================================================================================
class Article(BaseModel):
    """
    文章信息类
    """

    title: str = Field(description="标题")
    content: str = Field(description="内容")
    word_count: int = Field(description="字数")


def validate_article(article: Article) -> bool:
    """
    自定义验证逻辑

    - 检查 word_count 是否与 content 实际字数接近
    """

    actual_count = len(article.content)  # 实际字数
    claimed_count = article.word_count  # 声称字数

    # 允许10%误差
    tolerance = 0.1
    lower_bound = actual_count * (1 - tolerance)
    upper_bound = actual_count * (1 + tolerance)

    if not (lower_bound <= claimed_count <= upper_bound):
        return False

    return True


def example_5_custom_validation():
    """
    示例5 - 自定义验证函数

    - Pydantic 验证之外的业务逻辑验证

    - 关键点:
        - Pydantic 验证类型和格式
        - 自定义函数验证业务逻辑
        - 可以结合使用实现完整验证
    """
    print("\n" + "-" * 40)
    print("示例5 - 自定义验证函数")

    # -------------------------------------------------------------------
    print("\n测试1：字数匹配（误差在运行范围内）")
    article1 = Article(
        title="测试文章", content="这是一篇测试文章的内容", word_count=12
    )
    if validate_article(article1):
        print(
            f"验证通过，实际字数：{len(article1.content)}，声称字数：{article1.word_count}"
        )
    else:
        print(f"验证失败，字数不匹配")

    # -------------------------------------------------------------------
    print("\n测试2：字数不匹配（相差太大）")
    article2 = Article(
        title="测试文章", content="这是一篇测试文章的内容", word_count=1000
    )  # 字数明显相差太大
    if validate_article(article2):
        print(f"验证通过")
    else:
        print(
            f"验证失败，字数不匹配。实际字数：{len(article2.content)}，声称字数：{article2.word_count}"
        )


# ===================================================================================
# 主函数
# ===================================================================================
def main():
    try:
        example_5_custom_validation()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
