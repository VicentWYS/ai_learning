"""
LangChain 1.0 基础教程 - 第一个 LLM 调用
==============================================

本文件演示使用LangChain 1.0 进行基本的 LLM 调用
涵盖以下核心概念：
1. init_chat_model - 初始化聊天模型
2. invoke - 同步调用模型
3. Messages - 消息类型（System, Human, AI）
4. 基本配置和参数
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


# 加载环境变量
# 1. 查找 .env 文件，将其中的内容加载到 os.environ
# 2. 从环境变量中读取密钥，若不存在，则返回None
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")


# 校验 QWEN_API_KEY 是否被正确配置
# 1. 防止 .env 未加载导致为 None
# 2. 防止开发者未替换模板中的占位符
# 3. 提前中断程序，避免模型初始化阶段出现难以定位的鉴权错误
if not QWEN_API_KEY or QWEN_API_KEY == "your_qwen_api_key_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_API_KEY\n"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key 获取免费秘钥"
    )

if not QWEN_BASE_URL or QWEN_BASE_URL == "your_qwen_base_url_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_BASE_URL\n"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/model-market/detail/qwen-plus 获取适配 OpenAI 的 url"
    )


# 初始化模型
# init_chat_model 是LangChain 1.0 提供的标准跨厂商统一模型入口工厂函数，是所有模型统一入口
# LangChain 会自动帮你选择对应厂商的 ChatModel 类，并完成实例化
# Qwen 不是 OpenAI 协议直连，需要走 OpenAI-compatible endpoint，这一步很多人会踩坑
# LangChain 1.x 不再关心“你是什么模型”，只关心协议。Qwen 是 OpenAI 协议伪装模型
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ===================================================================================
# 示例1：最简单的 LLM 调用
# ===================================================================================
def example_1_simple_invoke():
    """
    示例1：最简单的模型调用

    核心概念：
    - init_chat_model: 用于初始化聊天模型的统一接口
    - invoke: 同步调用模型的方法
    """
    print("\n" + "=" * 40)
    print("示例1：最简单的模型调用")
    print("=" * 40)

    # 初始化模型
    # 格式：init_chat_model(...)
    # 这里就使用上面初始化的那个 model

    # 使用字符串直接调用模型
    response = model.invoke("你好！请用一句话介绍什么是人工智能")

    print(f"用户输入：你好！请用一句话介绍什么是人工智能")
    print(f"AI 回答：{response.content}")
    print(f"\n返回对象类型：{type(response)}")
    print(f"返回对象：{response}")


# ===================================================================================
# 示例2：使用消息列表进行对话
# ===================================================================================
def example_2_messages():
    """
    示例2：使用消息列表

    核心概念：
    - SystemMessage: 系统消息，用于设定 AI 的角色和行为
    - HumanMessage: 用户消息
    - AIMessage: AI 的回复消息

    消息列表允许你构建多轮对话历史
    """
    print("\n" + "=" * 40)
    print("示例2：使用消息列表进行对话")
    print("=" * 40)

    # 模型已经在开头初始化

    # 构建消息列表
    messages = [
        SystemMessage(
            content="你是一个友好的 Python 编程助手，擅长用简单易懂的方式解释编程概念。 回答字数不超过100字。"
        ),
        HumanMessage(content="什么是 Python 装饰器？"),
    ]

    print("系统提示词：", messages[0].content)
    print("用户提示词：", messages[1].content)

    # 调用模型
    response = model.invoke(messages)

    print(f"\nAI 回复：\n{response.content}")

    # 继续对话：将 AI 的回复添加到对话历史
    messages.append(response)
    messages.append(HumanMessage(content="请给出一个具体示例"))

    print("\n" + "=" * 40)
    print("继续对话...")
    print("用户问题：", messages[-1].content)

    response2 = model.invoke(messages)
    print(f"\nAI 回复：\n{response2.content}")


# ===================================================================================
# 示例3：使用字典格式的消息
# ===================================================================================
def example_3_dict_messages():
    """
    示例3：使用字典格式的消息

    LangChain 1.0 支持更简洁的字典格式：
    {"role": "system"/"user"/"assistant", "content": "消息内容"}

    这种格式与 OpenAI API 的格式一致，更易于使用
    """
    print("\n" + "=" * 40)
    print("示例3：使用字典格式的消息（推荐）")
    print("=" * 40)

    # model 已经在开头初始化

    # 使用字典格式构建消息
    messages = [
        {
            "role": "system",
            "content": "你是一名专业的高中数学教师，具有丰富的教学经验。",
        },
        {"role": "user", "content": "高中教学包含哪几个重要部分？"},
    ]

    print("消息列表：")

    for msg in messages:
        print(f"{msg['role']}:{msg['content']}")

    response = model.invoke(messages)

    print(f"\nAI 回复：\n{response.content}")


# ===================================================================================
# 示例4：配置模型参数
# ===================================================================================
def example_4_model_parameters():
    """
    示例4：配置模型参数

    init_chat_model 支持的常用参数：
    - temperature: 控制输出的随机性（0.0-2.0）
        - 0.0: 最有确定性，输出几乎不变
        - 1.0: 默认值，平衡创造性和一致性
        - 2.0: 最随机，最有创造性
    - max_tokens: 限制输出的最大 token 数量
    - model_kwargs: 传递给底层模型的额外参数
    """
    print("\n" + "=" * 40)
    print("示例4：配置模型参数")
    print("=" * 40)

    # 创建一个温度较低的模型（更有确定性）
    model_deterministic = init_chat_model(
        model="qwen-plus",
        model_provider="openai",
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0.0,  # 最有确定性
        max_tokens=100,  # 限制输出长度
    )

    prompt = "写一段关于春天景色的描写"

    print(f"提示词：{prompt}")
    print(f"\n使用 temperature = 0.0 （确定性输出）：")

    # 调用三次，观察输出的一致性
    for i in range(3):
        response = model_deterministic.invoke(prompt)
        print(f"第 {i+1} 次：{response.content}")

    print("\n" + "=" * 40)

    # 创建一个温度较高的模型（更随机）
    model_creative = init_chat_model(
        model="qwen-plus",
        model_provider="openai",
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=1.5,  # 更有创造性
        max_tokens=100,  # 限制输出长度
    )

    print(f"\n使用 temperature = 1.5 （创造性输出）：")

    # 调用三次，观察输出的差异
    for i in range(3):
        response = model_creative.invoke(prompt)
        print(f"第 {i+1} 次：{response.content}")


# ===================================================================================
# 示例5：理解 invoke 方法的返回值
# ===================================================================================
def example_5_response_structure():
    """
    示例5：深入理解 invoke 返回值

    invoke 方法返回一个 AIMessage 对象，包含：
        - content: 模型的文本回复
        - response_metadata: 响应元数据（如 token 使用量、模型信息等）
        - additional_kwargs: 额外的关键字参数
        - id: 消息 ID
    """
    print("\n" + "=" * 40)
    print("示例5：invoke 返回值详解")
    print("=" * 40)

    # model 已经在开头初始化

    response = model.invoke("用一句话解释什么是递归")

    print(f"1. 主要内容（content）：")
    print(f"    {response.content}\n")

    print(f"2. 响应元数据（response_metadata）：")
    for key, value in response.response_metadata.items():
        print(f"{key}: {value}")

    print(f"\n3. 消息类型：{type(response).__name__}")
    print(f"\n4. 消息 ID：{response.id}")

    # 检查 token 使用情况（如果可用）
    # 如果键存在，返回值，否则返回 N/A
    if "token_usage" in response.response_metadata:
        usage = response.response_metadata["token_usage"]
        print(f"\n5. Token 使用情况")
        print(f"    提示 tokens: {usage.get('prompt_tokens', 'N/A')}")
        print(f"    完成 tokens: {usage.get('completion_tokens', 'N/A')}")
        print(f"    总计 tokens: {usage.get('total_tokens', 'N/A')}")


# ===================================================================================
# 示例6：错误处理
# ===================================================================================
def example_6_error_handling():
    """
    示例6：正确的错误处理

    在实际应用中，应该处理可能的错误：
        - API 密钥无效
        - 网络连接问题
        - 速率限制
        - 模型不可用
    """
    print("\n" + "=" * 40)
    print("示例6：错误处理最佳实践")
    print("=" * 40)

    try:
        # 模型已经在开头初始化

        response = model.invoke("请用一句话介绍什么是智能体")
        print(f"成功调用模型！")
        print(f"AI 回复：{response.content}")

    except ValueError as e:
        print(f"配置错误：{e}")

    except ConnectionError as e:
        print(f"网络错误：{e}")

    except Exception as e:
        print(f"未知错误：{type(e).__name__}: {e}")


# ===================================================================================
# 示例7：多模型对比
# ===================================================================================
def example_7_multiple_models():
    """
    示例7：使用不同的模型

    LangChain 1.0 的优势是可以轻松切换不同的模型提供商
        - 只需要修改模型设定参数
    """
    print("\n" + "=" * 40)
    print("示例 7：对比不同模型的输出")
    print("=" * 40)

    # Groq 上可用的不同模型
    models_to_test = [
        "groq:llama-3.3-70b-versatile",
        "groq:mixtral-8x7b-32768",
    ]

    prompt = "用一句话解释什么是智能体"
    print(f"提示词：{prompt}\n")

    for model_name in models_to_test:
        try:
            print(f"\n使用模型：{model_name}")
            print("=" * 40)

            # 模型已经在开头初始化

            response = model.invoke(prompt)
            print(f"回复：{response.content}")

        except Exception as e:
            print(f"模型 {model_name} 调用失败：{e}")


def main():
    """
    主程序：运行所有示例
    """
    print("\n" + "=" * 80)
    print(" LangChain 1.0 基础教程 - 第一个 LLM 调用")
    print("=" * 80)

    try:
        # 运行所有示例
        # example_1_simple_invoke()
        # example_2_messages()
        # example_3_dict_messages()
        # example_4_model_parameters()
        # example_5_response_structure()
        # example_6_error_handling()
        example_7_multiple_models()

        print("\n" + "=" * 80)
        print("所有示例运行完成！")
        print("=" * 80)

    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
