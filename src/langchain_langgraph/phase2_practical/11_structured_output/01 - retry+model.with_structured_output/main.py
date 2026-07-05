"""
LangChain 1.0 - Structured Output (结构化输出)
=======================================================

所谓 retry 的本质：把 LLM 纳入 DDD + 六边形架构的软件体系

=======================================================
Self-healing Structured Output 自修复结构化输出
Retry机制：不是“多试几次”，而是引导模型修正，让 LLM 根据 Pydantic 的错误提示，自动修复自己的输出

Pydantic 让 LLM 变成“函数”，等价于：def llm(text) -> Product:...

以下示例是 langchain 作为框架，将【大模型的概率预测能力】和【代码的精确控制能力】融合的一个典范
Pydantic 是概率世界和确定性世界之间的“空气锁”：LLM（概率） → Pydantic（物理定律） → 程序（确定性）
Pydantic 除了验证结构，还可以验证业务逻辑

Prompt 是“劝 LLM 听话”
Pydantic 是“强制 LLM 守法”
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field, ValidationError


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
# 示例1 - 使用 retry 机制实现结构化输出
# ===================================================================================
def example_1_retry():
    """
    示例1 - 使用 retry 机制实现结构化输出

    - pydantic:让 LLM 变成“函数”
        - 没有 Pydantic，LLM 只能写 Demo
        - 有 Pydantic，LLM 才能进生产

    - Pydantic 模型是“边界层”，model_dump() 是“出边界”的标准动作
    """

    # 验证业务逻辑：规定 name 最少2个字符，price 必须 > 0
    # LLM 输出只要违反，立刻抛 ValidationError，这里 LLM 说了不算，Pydantic 说了算
    # Pydantic 作为 LLM 输出结果的校验和规范化的角色
    class Product(BaseModel):
        name: str = Field(min_length=2)
        price: float = Field(gt=0) # 大于等于 0

    # 自动把 Product 的 Pydantic Schema 转成 JSON Schema
    # 自动生成 Prompt 告诉 LLM：你必须按这个 JSON 输出
    # 自动在返回后用 Pydantic 校验
    # 等价于：def llm(text) -> Product:
    # 此时：
    # ❌ 返回值不再是 AIMessage
    # ✅ 返回值直接就是 Product 对象
    # 也就是说，LangChain 在背后已经帮你做完了这件事：
    # LLM文本 → JSON → Pydantic校验 → Product实例
    # Pydantic 模型是“边界层”：LLM 在边界外胡说八道都没关系，能不能进系统，Pydantic 说了算
    # model_dump() 是“出边界”的标准动作
    structured_llm = model.with_structured_output(Product)

    # 设置最大容错次数
    max_retries = 3

    # 故意给一个错误输入
    text = "产品价格是 -23 元"

    for i in range(1, max_retries + 1):
        print(f"\n--------------------- 第{i}次尝试 ---------------------")
        try:
            response = structured_llm.invoke(f"提取产品信息：{text}")
            # 验证通过
            print(f"AI 回复：{response}")  # 应该是一个 Product 对象
            print(
                response.model_dump()
            )  # 输出 dict 类型数据：{'name': 'xxx', 'price': xxx},并支持递归处理嵌套结构
            print(f"name: {response.name}, price: {response.price}")
            # retry 退出条件：（retry成功出口）一旦成功，就跳出 for 重试循环
            break
        except ValidationError as e:
            # 发生报错，获取报错信息
            error_msg = e.errors()[0]["msg"]
            # 这里报错信息为：Input should be greater than 0
            # 将报错信息巧妙地作为提示词补充到用户提示词中，从而起到修正模型输出的作用
            text = (
                f"{text}\n注意：{error_msg}，按照提示将输入内容进行修改完善以适配要求。"
            )
            print(f"error_msg: {error_msg}")
            print(f"text: {text}")

            # Fail Fast：（retry失败出口）当 LLM 连续多次都无法满足 Pydantic 的业务约束时，
            # 明确告诉上层：这次任务失败了，不要再假装还能继续。
            if i == max_retries:
                # 不使用 raise e，因为会抛出同一个异常对象，但丢失原始栈信息
                # 使用 raise，会原样抛出，并保留完整报错栈
                # 这里表示重试次数用完，把当前捕获到的异常（这里就是 ValidationError ）“原封不动重新抛出去，让上层知道这次重试彻底失败了”
                raise


# ===================================================================================
# 主程序
# ===================================================================================
def main():
    try:
        example_1_retry()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
