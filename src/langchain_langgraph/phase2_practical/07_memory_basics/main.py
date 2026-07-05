"""
LangChain 1.0 - Memory Basics(内存管理基础)
======================================================

本模块重点讲解：
1. InMemorySaver - LangGraph 提供的内存管理
2. checkpointer 参数 - 为 Agent 添加内存
3. thread_id - 会话管理
4. 多轮对话状态保持
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver


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


# 创建一个简单的工具
@tool
def get_user_info(user_id: str) -> str:
    """
    获取用户信息
    """
    users = {"1205": "哈利，15岁，魔法师", "1206": "罗恩，16岁，魔法师"}
    return users.get(user_id, "用户不存在")


# ============================================================================
# 示例1：没有内存的 Agent(对照组)
# ============================================================================
def example_1_no_memory():
    """
    示例1：没有内存的 Agent - 它不会记得之前的对话

    - 关键：每次调用都是独立的
        - Agent 不记得第一轮对话
        - 每次 invoke 都是全新的开始
        - 需要手动传入历史消息才能记住
    """
    print("\n" + "=" * 40)
    print("示例 1：没有内存的 Agent")
    print("=" * 40)

    # 创建没有 checkpointer 的 Agent
    agent = create_agent(model=model, tools=[], system_prompt="你是一名智能助手。")

    print("\n第一轮对话：")
    response1 = agent.invoke({"messages": [{"role": "user", "content": "我叫哈利"}]})
    print(f"Agent 回复：{response1["messages"][-1].content}")

    print("\n第二轮对话：")
    response2 = agent.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]})
    print(f"Agent 回复：{response2["messages"][-1].content}")


# ============================================================================
# 示例2：使用 InMemorySaver 添加短期内存
# ============================================================================
def example_2_with_memory():
    """
    示例2：使用 InMemorySaver 添加短期内存

    - 关键点：
        - Agent 记住了第一轮对话！
        - checkpointer 自动保存对话历史
        - thread_id 用于区分不同的会话
    """
    print("\n" + "=" * 40)
    print("示例 2：使用 InMemorySaver 添加短期内存")
    print("=" * 40)

    # 创建带内存的 Agent
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        checkpointer=InMemorySaver(),  # 添加内存管理
    )

    # config 中指定 thread_id
    config = {"configurable": {"thread_id": "conversation-1"}}

    print("\n第一轮对话：")
    response1 = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫哈利"}]},
        config=config,  # 传入 config
    )
    print(f"Agent 回复：{response1["messages"][-1].content}")

    print("\n第二轮对话：")
    response2 = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫什么？"}]},
        config=config,  # 使用相同的 thread_id
    )
    print(f"Agent 回复：{response2["messages"][-1].content}")


# ============================================================================
# 示例3：多个会话（不同 thread_id）
# ============================================================================
def example_3_multiple_threads():
    """
    示例3：管理多个独立的会话

    - 关键点：
        - 不同的 thread_id = 不同的对话
        - 不同 thread_id 的会话完全独立
        - Agent 能正确记住每个会话的内容
        - 适合多用户聊天场景
    """
    print("\n" + "=" * 40)
    print("示例 3：多个独立会话")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        checkpointer=InMemorySaver(),
    )

    # 会话 1
    config1 = {"configurable": {"thread_id": "user_alice"}}
    print("\n[会话1 - Alice]")
    agent.invoke(
        {"messages": [{"role": "user", "content": "我叫 Alice"}]}, config=config1
    )
    print("Alice: 我叫 Alice")

    # 会话2
    config2 = {"configurable": {"thread_id": "user_bob"}}
    print("\n[会话 2 - Bob]")
    agent.invoke(
        {"messages": [{"role": "user", "content": "我叫 Bob"}]}, config=config2
    )
    print("Bob: 我叫 Bob")

    # 回到会话1
    print("\n[回到会话1 - Alice]")
    response1 = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫什么？"}]}, config=config1
    )
    print(f"Agent 回复：{response1["messages"][-1].content}")

    # 回到会话2
    print("\n[回到会话2 - Bob]")
    response2 = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫什么？"}]}, config=config2
    )
    print(f"Agent 回复：{response2["messages"][-1].content}")


# ============================================================================
# 示例4：带工具的内存 Agent
# ============================================================================
def example_4_memory_with_tools():
    """
    示例4：内存 + 工具调用

    - 关键点：
        - Agent 能记住之前调用工具的结果
        - 不需要重新调用工具
        - 对话上下文包含工具使用历史
    """
    print("\n" + "=" * 40)
    print("示例 4：内存 + 工具调用")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[get_user_info],
        system_prompt="你是一名智能助手。",
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "session_1"}}

    print("\n第一轮：查询用户信息")
    response1 = agent.invoke(
        {"messages": [{"role": "user", "content": "查询 id 为 1205 的用户信息"}]},
        config=config,
    )
    print(f"Agent 回复：{response1["messages"][-1].content}")

    print("\n第二轮：询问之前的信息")
    response2 = agent.invoke(
        {
            "messages": [
                {"role": "user", "content": "刚才查询的用户多大了？是做什么的？"}
            ]
        },
        config=config,
    )
    print(f"Agent 回复：{response2["messages"][-1].content}")


# ============================================================================
# 示例5：查看内存状态
# ============================================================================
def example_5_inspect_memory():
    """
    示例5：查看和理解内存中保存的内容

    - 理解 checkpointer 中保存了什么

    - 关键点：
        - checkpointer 保存有完整的消息历史
        - response['messages'] 中包含所有的历史消息
        - agent 的每次调用都会追加新消息
    """
    print("\n" + "=" * 40)
    print("示例 5：查看内存状态")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "inspect_thread"}}

    # 进行几轮对话
    print("\n进行对话...")
    agent.invoke({"messages": [{"role": "user", "content": "你好"}]}, config=config)
    agent.invoke(
        {"messages": [{"role": "user", "content": "我喜欢编程"}]}, config=config
    )

    # 再次调用，查看返回的完整状态
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "我喜欢什么？"}]}, config=config
    )

    print(f"\n对话历史中的消息数量：{len(response["messages"])}")
    print("\n全部历史消息：")
    for msg in response["messages"]:
        msg_type = msg.__class__.__name__
        content = msg.content[:70] + "..." if len(msg.content) > 70 else msg.content
        print(f"{msg_type}: {content}")


# ============================================================================
# 示例6： 实际应用场景 - 客服机器人
# ============================================================================
def example_6_practical_use():
    """
    示例6：实际应用场景 - 客服机器人

    - 模拟一个需要记住用户信息的客服场景

    - 关键点：
        - Agent 记住了用户的 ID
        - Agent 记住了查询的结果
        - 实现了流畅的多轮对话
    """
    print("\n" + "=" * 80)
    print("示例 6：实际应用 - 客服机器人")
    print("=" * 80)

    agent = create_agent(
        model=model,
        tools=[get_user_info],
        system_prompt="""你是一个客服助手。
        特点：
        - 能够记住用户说过的话。
        - 友好，有耐心。
        - 使用 get_user_info 工具查询用户信息时需要用户 ID
""",
        checkpointer=InMemorySaver(),
    )

    # 模拟用户会话
    user_id = "user_8728"
    config = {"configurable": {"thread_id": user_id}}

    conversations = [
        "你好，我想咨询一下",
        "我的用户 ID 是 1206",
        "帮我查一下我的信息",
        "我多大来着？",  # 测试记忆
    ]

    for i, user_msg in enumerate(conversations, 1):
        print(f"\n轮次：{i}")
        print(f"用户：{user_msg}")

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_msg}]}, config=config
        )

        print(f"客服回复：{response["messages"][-1].content}")


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 80)
    print(" LangChain 1.0 - Memory Basics")
    print("=" * 80)

    try:
        # example_1_no_memory()
        # example_2_with_memory()
        # example_3_multiple_threads()
        # example_4_memory_with_tools()
        # example_5_inspect_memory()
        example_6_practical_use()

        print("\n" + "=" * 80)
        print(" 完成！")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
