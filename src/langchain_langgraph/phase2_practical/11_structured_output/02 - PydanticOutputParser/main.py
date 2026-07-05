"""
LangChain 1.0 - outputparser 结构化输出
=======================================================

pydantic 实现结构化输出
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, ValidationError
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser


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


# ===================================================================================
# 示例 1 - 使用 outputparser 实现结构化输出
# ===================================================================================
class Person(BaseModel):
    """人物信息"""

    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


def example_1_without_outputparser():
    """
    示例1 - 【对照组】模型直接输出
    """
    print("\n" + "-" * 20 + " 模型直接输出 " + "-" * 20)

    # 提示词
    system_prompt = "根据用户输入内容，从中提取出主要信息。"
    user_prompt = "张国强是一名30岁的AI开发工程师。"

    # 调用模型，并解析结构化输出
    message_obj = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    response = model.invoke(message_obj)
    raw_content = response.content.strip()  # strip(): 移除字符串开头和结尾的空白字符

    print(f"\nuser_prompt: {user_prompt}")
    print(f"AI 回复：{raw_content}")


def example_2_outputparser():
    """
    示例2 - 使用 outputparser 实现结构化输出
    """
    print("\n" + "-" * 20 + " 测试结构化输出 " + "-" * 20)

    # 创建输出解析器
    # 这里的 PydanticOutputParser[Person] 是在告诉解析器它要解析的数据结构是 Person（上面定义的 Pydantic 模型）。
    # 如果去掉 [Person]、只写 parser = PydanticOutputParser(pydantic_object=Person) 通常也可以正常运行
    # ——因为 pydantic_object 参数已经指定了 Person 类型，类型推断就能完成类型判断。
    # 但加上 [Person] 可以让类型提示、自动补全等开发体验更好，也为代码阅读者更清晰地标明了解析目标类型。
    parser = PydanticOutputParser[Person](pydantic_object=Person)

    # 提示词
    system_prompt = "根据用户输入内容，从中提取出主要信息。"
    user_prompt = "张国强是一名30岁的AI开发工程师。"
    format_instructions = parser.get_format_instructions()
    user_prompt_full = (
        f"{user_prompt}\n\n{format_instructions}"  # 将 prompt 与解析器结合
    )
    message_obj = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt_full),
    ]

    # 调用模型，并解析结构化输出
    response = model.invoke(message_obj)
    raw_content = response.content.strip()

    # 解析结构化输出
    person_obj = parser.parse(raw_content)

    print(f"\nuser_prompt: {user_prompt}")
    print(f"full_prompt: {user_prompt_full}")
    print(f"AI 回复：{raw_content}")
    print(f"解析结果：{person_obj}")
    print(f"解析结果 model_dump()：{person_obj.model_dump()}")
    print(f"对象属性 - 姓名：{person_obj.name}")
    print(f"对象属性 - 年龄：{person_obj.age}")
    print(f"对象属性 - 职业：{person_obj.occupation}")


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    print("\n" + "=" * 40)
    print("outputparser 结构化输出")
    print("=" * 40)

    try:
        # example_1_without_outputparser()
        example_2_outputparser()

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
