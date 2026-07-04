import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import TypeVar, Type


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


# =================================== 辅助函数 ===================================
T = TypeVar("T", bound=BaseModel)


def safe_structured_output(prompt: str, output_class: Type[T]) -> T:
    """
    安全的结构化输出函数
    """
    try:
        structured_llm = create_safe_structured_llm(output_class)
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"结构化输出失败: {e}")


def create_safe_structured_llm(output_class):
    """
    指定输出结果类型：创建结构化输出 LLM
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


# ===================================================================================
# 示例4 - LLM 输出验证+retry
# ===================================================================================
class Product(BaseModel):
    """
    产品信息（严格验证）

    - 用于验证 LLM 输出结果是否符合要求
    """

    name: str = Field(description="产品名称", min_length=2)  # 最小长度2
    price: float = Field(description="产品价格", gt=0)  # 大于 0
    stock: int = Field(description="库存数量", ge=0)  # 大于等于 0

    # 定义了一个 Pydantic 的自定义字段验证器，用来验证 name 字段
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if v.lower() == "unknow":
            raise ValueError("产品名称不能是 unknow")
        return v


def example_4_llm_validation_retry():
    """
    示例4 - LLM 输出验证 + retry 重试循环

    - 如果 LLM 输出不符合验证规则，则重新提示并重试

    - 关键点:
        - ValidationError 捕获 Pydantic 验证失败
        - Exception 捕获 API 端验证失败
        - 在提示中强调类型要求
        - 限制最大重试次数防止无限循环

    - 可优化：
        - 将多次验证逻辑封装成一个函数，避免重复代码（见示例6）
    """
    print("\n" + "-" * 40)
    print("示例4 - LLM 输出验证 + retry 重试循环")

    structured_llm = create_safe_structured_llm(Product)

    # 最大重试次数
    max_retries = 3

    # 使用一个简单的测试案例（改为正常价格，避免触发验证错误）
    # text = "iPhone 15 售价 5999 元，库存 50 件，产品名称为 unknown"
    text = "iPhone 15 售价 -2222 元，库存 50 件"

    print(f"输入文本: {text}")
    print(f"验证规则：name 最小长度2且不能为unknow，price 大于 0，stock 大于等于 0")

    for attempt in range(1, max_retries + 1):
        print(f"\n第 {attempt}/{max_retries} 次尝试...")

        try:
            # 调用 LLM
            prompt = f"""从以下文本提取产品信息。
重要：price 必须是数字类型（不是字符串），stock 必须是整数类型。

文本: {text}
            """
            result = structured_llm.invoke(prompt)

            # 如果到这里，说明验证通过
            print("提取成功！")
            print(
                f"产品名称：{result.name}, 产品价格：{result.price}, 产品库存：{result.stock}"
            )
            break

        # 捕获 Pydantic 验证失败
        except ValidationError as e:
            print(f"Pydantic 验证失败：{e.errors()[0]['msg']}")

            # 若还有重试次数
            if attempt < max_retries:
                # 提取报错信息
                error_msg = e.errors()[0]["msg"]
                # 根据报错信息完善提示词
                text = f"{text}\n注意：{error_msg}，按照提示将输入内容进行修改完善以适配要求。"
                print(f"修正后的提示词: {text}")
            else:
                print("已达到最大重试次数")
                return None

        except Exception as e:
            # 捕获到其他错误（如 BadRequestError）
            error_str = str(e)
            if "expected number, but got string" in error_str:
                print("API 验证失败: LLM 返回了字符串而不是数字")
            elif "expected integer, but got string" in error_str:
                print("API 验证失败: LLM 返回了字符串而不是整数")
            else:
                print(f"其他错误: {e}")

            # 若还有重试次数
            if attempt < max_retries:
                print("重试...")
            else:
                print("已达到最大重试次数，说明 LLM 无法满足要求，任务失败")


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    try:
        example_4_llm_validation_retry()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
