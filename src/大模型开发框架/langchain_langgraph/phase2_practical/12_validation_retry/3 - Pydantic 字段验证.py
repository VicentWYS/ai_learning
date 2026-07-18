import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, field_validator, ValidationError


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


# ==================================================================================
# 示例3 - Pydantic 字段验证
# ==================================================================================
class User(BaseModel):
    """
    用户信息（带验证）
    """

    name: str = Field(
        description="用户名", min_length=2, max_length=20
    )  # 最小长度2，最大长度20
    age: int = Field(description="年龄", gt=0, lt=150)  # 大于0，小于150
    email: str = Field(description="邮箱")

    # 定义了一个 Pydantic 的自定义字段验证器，用来验证 email 字段
    @field_validator(
        "email"
    )  # pydantic 的字段验证装饰器，表示下面的函数用来校验模型中的 email 字段
    @classmethod  # 将该方法定义为类方法
    def validate_email(cls, v: str) -> str:
        """
        自定义邮箱验证

        cls: 类本身，是配合 field_validator 使用的常见写法
        v: 要验证的值，即 email 字段的值，这里 v 只是一个普通的形参名，你可以换成任何你喜欢的名字
        """
        if "@" not in v:
            raise ValueError("邮箱必须包含 @")

        return v


def example_3_pydantic_validation():
    """
    示例3 - Pydantic 字段验证

    - 使用 Field 约束和自定义验证器
    """
    print("\n" + "-" * 40)
    print("示例3 - Pydantic 字段验证")

    print("\n测试1：有效数据")
    try:
        user = User(name="张三", age=20, email="zhangsan@example.com")
        print(f"验证通过：{user.name}, {user.age}, {user.email}")
    except ValidationError as e:
        print(f"验证失败：{e}")

    print("\n测试2：年龄超出范围")
    try:
        user = User(name="张三", age=151, email="zhangsan@example.com")
        print(f"验证通过：{user.name}, {user.age}, {user.email}")
    except ValidationError as e:
        print(f"验证失败，年龄必须在 0 到 150 之间")
        print(f"错误详情：{e.errors()[0]['msg']}")

    print("\n测试3：邮箱格式错误")
    try:
        user = User(name="张三", age=20, email="zhangsanexample.com")
        print(f"验证通过：{user.name}, {user.age}, {user.email}")
    except ValidationError as e:
        print(f"验证失败，邮箱格式错误")
        print(f"错误详情：{e.errors()[0]['msg']}")


# ==================================================================================
# 主程序
# ==================================================================================
def main():
    try:
        example_3_pydantic_validation()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
