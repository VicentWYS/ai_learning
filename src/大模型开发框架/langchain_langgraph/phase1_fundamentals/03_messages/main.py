"""
Langchain 1.0 - 消息类型与对话管理
==============================================

本模块重点讲解：
1. 三种消息类型的实际使用
2. 对话历史管理（核心难点）
3. 消息的修剪和优化
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


# 加载环境变量
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")

if not QWEN_API_KEY or QWEN_API_KEY == "your_qwen_api_key_here":
    raise ValueError(
        "\n请现在 .env 文件中设置有效的 QWEN_API_KEY\n"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key 获取免费秘钥"
    )

if not QWEN_BASE_URL or QWEN_BASE_URL == "your_qwen_base_url_here":
    raise ValueError(
        "\n请现在 .env 文件中设置有效的 QWEN_BASE_URL\n"
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


# ============================================================================
# 示例 1：三种消息类型
# ============================================================================
def example_1_message_types():
    """
    三种消息类型：SystemMessage, HumanMessage, AIMessage

    重点：字典格式（推荐） vs 消息对象
    """
    print("\n" + "=" * 40)
    print("示例 1：三种消息类型对比")
    print("=" * 40)

    # 方式1：消息对象（啰嗦）
    print("\n【方式1：消息对象】")
    message_obj = [
        SystemMessage(content="你是一名 Python 导师。"),
        HumanMessage(content="用一句话介绍什么是langchain"),
    ]
    response = model.invoke(message_obj)
    print(f"\nAI 回复：{response.content[:100]}...")

    # 方式2：字典格式（推荐，简洁）
    print("\n【方式2：字典格式（推荐）】")
    message_dict = [
        {"role": "system", "content": "你是一名 Python 导师。"},
        {"role": "user", "content": "用一句话介绍智能体"},
    ]
    response = model.invoke(message_dict)
    print(f"AI 回复：{response.content[:100]}...")


# ============================================================================
# 示例 2：对话历史管理（核心难点）
# ============================================================================
def example_2_conversation_history():
    """
    示例2：如何正确管理对话历史

    - 关键：每次调用都要传递完整历史
    """
    print("\n" + "=" * 40)
    print("示例 2：对话历史管理（重点）")
    print("=" * 40)

    # 初始化对话历史
    conversation = [
        {
            "role": "system",
            "content": "你是一名表达简洁的智能助手，每次回答的字数都限制在50字以内。",
        }
    ]

    # 第一轮
    print("\n【第 1 轮】")
    conversation.append({"role": "user", "content": "什么是智能体？"})
    print(f"用户：{conversation[-1]["content"]}")

    r1 = model.invoke(conversation)
    print(f"AI 回复：{r1.content}\n")

    # 关键：保存 AI 回复结果到历史
    conversation.append({"role": "assistant", "content": r1.content})

    # 第二轮（测试记忆）
    print("\n【第 2 轮】")
    conversation.append({"role": "user", "content": "它有什么特点？"})
    print(f"用户：{conversation[-1]["content"]}")

    r2 = model.invoke(conversation)
    print(f"AI 回复：{r2.content}\n")

    conversation.append({"role": "assistant", "content": r2.content})

    # 第三轮（测试上下文）
    print("\n【第 3 轮】")
    conversation.append({"role": "user", "content": "我问的第一个问题是什么？"})
    print(f"用户：{conversation[-1]["content"]}")

    r3 = model.invoke(conversation)
    print(f"AI 回复：{r3.content}\n")

    print(f"对话历史中共有{len(conversation)}条消息")
    print("大模型记住了之前的内容，因为每次都传递了完整历史。")


# ============================================================================
# 示例 3：错误示范 - AI 失忆
# ============================================================================
def example_3_wrong_way():
    """
    错误示范：不保存对话历史

    - 结果：AI 会"失忆"
    - 这体现了提示词不使用模板时的局限性，简单字符串类型的提示词不适用于包含多轮历史消息
    """
    print("\n" + "=" * 70)
    print("示例 3：错误示范 - AI 失忆")
    print("=" * 70)

    print("\n错误做法：不保存历史")

    # 第一次
    r1 = model.invoke("我叫张三")
    print(f"用户: 我叫张三")
    print(f"AI: {r1.content[:50]}...")

    # 第二次（没有传递历史）
    r2 = model.invoke("我叫什么名字？")
    print(f"\n用户: 我叫什么名字？")
    print(f"AI: {r2.content[:80]}...")
    print("\nAI 不记得你叫张三！")


# ============================================================================
# 示例 4：对话历史的优化
# ============================================================================
def example_4_optimize_history():
    """
    难点：对话历史太长怎么办？

    - 解决方案：
        1. 只保留最近 N 条
        2. 总是保留 system 消息
    """
    print("\n" + "=" * 80)
    print("示例 4：优化对话历史（避免太长）")
    print("=" * 80)

    def keep_recent_messages(messages, max_pairs=3):
        """
        保留最近的 N 轮对话

        参数：
            - messages: 完整消息列表
            - max_pairs: 保留的对话轮数

        返回：
            - 优化后的消息列表
        """
        # 分离 system 消息和对话消息
        system_msgs = [m for m in messages if m.get("role") == "system"]
        conversation_msgs = [m for m in messages if m.get("role") != "system"]

        # 只保留最近的消息（每轮 = user + assistant）
        max_messages = max_pairs * 2
        recent_msgs = conversation_msgs[-max_messages:]

        # 返回：system + 最近对话
        return system_msgs + recent_msgs

    # 模拟长对话
    long_conversation = [
        {
            "role": "system",
            "content": "你是一名智能回答助手，擅长用一句话的形式回答用户的问题。",
        },
        {"role": "user", "content": "早上好，今天感觉有点困怎么办？"},
        {
            "role": "assistant",
            "content": "可以喝杯温水、拉开窗帘晒晒太阳，让身体快速清醒起来。",
        },
        {"role": "user", "content": "午饭吃什么比较合适？"},
        {
            "role": "assistant",
            "content": "选择清淡又有蛋白质的饭菜，比如鸡胸肉配蔬菜会更有精神。",
        },
        {"role": "user", "content": "下午工作总是犯困怎么办？"},
        {
            "role": "assistant",
            "content": "起来走动五分钟或做几次深呼吸能有效缓解困意。",
        },
        {"role": "user", "content": "晚上下班后适合做什么放松？"},
        {
            "role": "assistant",
            "content": "听点音乐或散步半小时能很好地释放一天的压力。",
        },
        {"role": "user", "content": "睡前玩手机影响大吗？"},
    ]

    print(f"原始消息数：{len(long_conversation)}")

    # 使用优化函数：只保留最近 2 轮
    optimized = keep_recent_messages(long_conversation, max_pairs=2)
    print(f"优化后的消息数：{len(optimized)}")
    print(f"保留的内容：system + 最近2轮对话")

    # 使用优化后的对话历史
    resonse = model.invoke(optimized)
    print(f"AI 回复：{resonse.content[:100]}...")
    print("\n技巧：对话太长时，只保留最近的几轮即可")


# ============================================================================
# 示例 5：实战 - 简单聊天机器人
# ============================================================================
def example_5_simple_chatbot():
    """
    实战：构建一个能记住对话的聊天机器人
    """
    print("\n" + "=" * 40)
    print("示例5：实战 - 简单聊天机器人")
    print("=" * 40)

    conversation = [{"role": "system", "content": "你是一个友好的智能回答助手。"}]

    questions = [
        "我叫李明，今年25岁",
        "我喜欢编程",
        "我叫什么名字？",
        "我今年多大？",
        "我喜欢什么？",
    ]

    for i, q in enumerate(questions, start=1):
        print(f"\n---- 第 {i} 轮 ----")
        print(f"用户输入：{q}")

        conversation.append({"role": "user", "content": q})
        response = model.invoke(conversation)

        print(f"AI 回复：{response.content[:100]}...")
        conversation.append({"role": "assistant", "content": response.content})

    print(f"\n总共 {len(conversation)} 条消息")
    print("AI 完美记住了所有信息！")


def main():
    """
    主程序：运行所有示例
    """
    print("\n" + "=" * 80)
    print("LangChain 1.0 - 消息类型与对话管理")
    print("=" * 80)

    try:
        # example_1_message_types()
        # example_2_conversation_history()
        # example_3_wrong_way()
        # example_4_optimize_history()
        example_5_simple_chatbot()

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n\n错误:{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
