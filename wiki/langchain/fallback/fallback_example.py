"""
LangChain 中 Fallback 的两种常见用法示例
==========================================

1. LLM 级 Fallback：主模型调用失败时自动切换备用模型（如 API 超时、限流）
2. 结构化输出 Fallback：解析失败时用备用方式从文本中提取结构化数据
"""

import os
import json
import re
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableWithFallbacks
from pydantic import BaseModel, Field
from typing import TypeVar, Type

load_dotenv()

T = TypeVar("T", bound=BaseModel)


# =============================================================================
# 一、LLM 级 Fallback：with_fallbacks()
# =============================================================================
# 当主模型（如 Qwen）因网络/限流/故障失败时，自动尝试备用模型，保证可用性。


def setup_llm_with_fallback():
    """
    主模型 + 备用模型，任一可用即可。
    主模型失败时会按列表顺序依次尝试 fallback。
    """
    # 主模型（例如 Qwen）
    primary = init_chat_model(
        model="qwen-plus",
        model_provider="openai",
        api_key=os.getenv("QWEN_API_KEY"),
        base_url=os.getenv("QWEN_BASE_URL"),
        temperature=0.7,
        max_retries=0,  # 不重试，失败直接走 fallback
    )

    # 备用模型（例如 Groq 或另一个端点）
    # 若只有一套 key，可用同一厂商不同 model 或同一 base_url 做演示
    fallback = init_chat_model(
        model="qwen-turbo",  # 换一个 model 作备用
        model_provider="openai",
        api_key=os.getenv("QWEN_API_KEY"),
        base_url=os.getenv("QWEN_BASE_URL"),
        temperature=0.7,
        max_retries=0,
    )

    # 绑定 fallback：primary 失败时自动调用 fallback
    llm_with_fallback: RunnableWithFallbacks = primary.with_fallbacks([fallback])
    return llm_with_fallback


def example_llm_fallback():
    """调用示例：主模型失败时自动用备用模型"""
    llm = setup_llm_with_fallback()
    # 正常调用，内部会先试 primary，失败再试 fallback
    response = llm.invoke("用一句话说清什么是 LangChain")
    print("LLM Fallback 示例回复:", response.content)


# =============================================================================
# 二、结构化输出 Fallback：解析失败时兜底
# =============================================================================
# 当 with_structured_output 因格式不合法抛异常时，用 json.loads / 正则等兜底解析。


class Person(BaseModel):
    """示例输出结构"""
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")


def extract_json_from_text(text: str) -> dict | None:
    """从可能带 markdown 或多余文字的回复中尝试提取 JSON"""
    # 尝试 ```json ... ``` 代码块
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
    # 尝试整段解析
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # 尝试找第一个 { ... }
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def safe_structured_output(
    llm,
    prompt: str,
    output_class: Type[T],
) -> T | None:
    """
    带 fallback 的结构化输出：
    1. 优先用 with_structured_output 得到 Pydantic 对象
    2. 若解析失败，用普通 invoke 拿文本，再尝试从文本中抠 JSON 转成 output_class
    """
    structured_llm = llm.with_structured_output(output_class)
    try:
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"结构化解析失败，使用 fallback: {e}")
    # Fallback：先拿原始文本
    try:
        raw = llm.invoke(prompt)
        text = raw.content if hasattr(raw, "content") else str(raw)
        data = extract_json_from_text(text)
        if data is not None:
            return output_class.model_validate(data)
    except Exception as e2:
        print(f"Fallback 解析也失败: {e2}")
    return None


def example_structured_output_fallback(llm):
    """结构化输出 + fallback 示例"""
    prompt = "请输出一个人的信息：张三，28岁，工程师。"
    result = safe_structured_output(llm, prompt, Person)
    if result:
        print("结构化输出 Fallback 示例:", result.model_dump())
    else:
        print("两次解析均失败")


# =============================================================================
# 三、链式 Fallback（多个备用）
# =============================================================================


def example_multiple_fallbacks():
    """多个 fallback 按顺序尝试"""
    models = [
        init_chat_model(
            model="qwen-plus",
            model_provider="openai",
            api_key=os.getenv("QWEN_API_KEY"),
            base_url=os.getenv("QWEN_BASE_URL"),
            max_retries=0,
        ),
        init_chat_model(
            model="qwen-turbo",
            model_provider="openai",
            api_key=os.getenv("QWEN_API_KEY"),
            base_url=os.getenv("QWEN_BASE_URL"),
            max_retries=0,
        ),
    ]
    # 第一个为主，其余为 fallback 列表
    chain = models[0].with_fallbacks(models[1:])
    response = chain.invoke("你好")
    print("多级 Fallback 回复:", response.content[:80], "...")


# =============================================================================
# 主程序
# =============================================================================


def main():
    # 确保有 key
    if not os.getenv("QWEN_API_KEY") or os.getenv("QWEN_API_KEY") == "your_qwen_api_key_here":
        print("请设置 .env 中的 QWEN_API_KEY、QWEN_BASE_URL 后重试")
        return

    print("=== 1. LLM 级 Fallback (with_fallbacks) ===")
    example_llm_fallback()

    print("\n=== 2. 结构化输出 Fallback ===")
    llm = setup_llm_with_fallback()
    example_structured_output_fallback(llm)

    print("\n=== 3. 多级 Fallback ===")
    example_multiple_fallbacks()


if __name__ == "__main__":
    main()
