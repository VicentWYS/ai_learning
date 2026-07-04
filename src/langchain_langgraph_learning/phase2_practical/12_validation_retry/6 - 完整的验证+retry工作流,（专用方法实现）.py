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


# ============================= 辅助函数 =============================
T = TypeVar("T", bound=BaseModel)


def safe_structured_output(prompt: str, output_class: Type[T]) -> T:
    """
    安全的结构化输出函数

    用 实现结构化输出
    """
    try:
        structured_llm = create_safe_structured_llm(output_class)
        result = structured_llm.invoke(prompt)
        return result
    except Exception as e:
        print(f"结构化输出失败: {e}")


def create_safe_structured_llm(output_class):
    """
    返回一个能够安全地进行结构化输出的 LLM 对象

    - 返回值是一个 SafeStructuredLLM 对象，该对象有一个 invoke 方法，可以接受一个 prompt 参数，并返回一个 T 类型的对象
    """
    base_llm = model.with_structured_output(output_class, method="function_calling")

    class SafeStructuredLLM:
        def invoke(self, prompt):
            try:
                return base_llm.invoke(prompt)
            except Exception as e:
                print(f"结构化输出失败: {e}")
                # 将异常原封不动重新抛出去，让上层知道这次重试彻底失败了
                raise

    return SafeStructuredLLM()


# ===================================================
# 示例6 - 完整的验证+retry工作流
# ===================================================
class ExtractedData(BaseModel):
    """
    待提取的数据类
    """

    name: str = Field(description="名称", min_length=1)  # 最小长度为1
    value: float = Field(description="值", gt=0)  # 大于0

    # 定义了一个 Pydantic 的自定义字段验证器，用来验证 name 字段
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("名称不能为空")
        return v.strip()


def extract_with_validation(text: str, max_retries: int = 3) -> Optional[ExtractedData]:
    """
    带验证的提取函数

    - 参数：
        - text: 待提取的文本
        - max_retries: 最大重试次数

    - 返回值：
        - 提取成功时返回 ExtractedData 对象
        - 提取失败时返回 None
    """
    structured_llm = create_safe_structured_llm(ExtractedData)

    current_text = text

    for attempt in range(1, max_retries + 1):
        try:
            prompt = f"""从以下文本中提取数据信息。
注意：value 必须是数字类型（float），不能是字符串。
文本如下：
{current_text}"""
            result = structured_llm.invoke(prompt)
            return result

        except ValidationError as e:
            error_msg = e.errors()[0]["msg"]

            # 若还有重试次数
            if attempt < max_retries:
                current_text = f"{current_text}\n注意：{error_msg}，按照提示将输入内容进行修改完善以适配要求。"
            else:
                print("已达到最大重试次数")
                return None  # 如果所有重试都失败，返回 None

        except Exception as e:
            # 捕获到其他错误（如 BadRequestError）
            if attempt < max_retries:
                print("重试...")
            else:
                print("已达到最大重试次数")
                return None  # 如果所有重试都失败，返回 None

    # 如果所有重试都失败，返回 None，对应类声明中的 Optional[ExtractedData]
    return None


def example_6_complete_validation_retry():
    """
    示例6 - 完整的验证+retry工作流

    - 展示生产环境中的最佳实践
    """
    print("\n" + "-" * 40)
    print("示例6 - 完整的验证+retry工作流")

    test_cases = [
        "产品 A 的价值是 999.99 元",
        "产品 B 的价值是 1299 元",
    ]

    for i, test_case in enumerate[str](test_cases, 1):
        print(f"\n测试 {i}: {test_case}")

        result = extract_with_validation(test_case)

        if result:
            print(f"提取成功：{result.model_dump()}")
        else:
            print("提取失败（重试 2 次后仍无法通过验证）")


# ===================================================
# 主函数
# ===================================================
def main():
    try:
        example_6_complete_validation_retry()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
