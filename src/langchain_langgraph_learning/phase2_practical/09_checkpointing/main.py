"""
LangChain 1.0 - Checkpointing(检查点持久化)
=====================================================

本模块重点讲解：
1. SqliteSaver - SQLite 持久化（LangGraph 提供）
2. 与 InMemorySaver 的区别
3. 跨进程、跨重启的对话持久化
4. 实际应用场景

API 说明：
- 本模块使用 `create_agent`
- Checkpointing 是 LangGraph 的核心特性
- 配合 create_agent 可以完整展示状态持久化

工作流程：
  1. invoke 前：LangGraph 自动调用 checkpointer.get(thread_id="user_123")
    - 查询数据库，读取该 thread_id 的历史消息
    - 如果是第一次，返回空列表
  2. invoke 中：Agent 处理时会看到完整历史
  state = {
      "messages": [历史消息1, 历史消息2, 新消息]  # 自动合并
  }
  3. invoke 后：LangGraph 自动调用 checkpointer.put(thread_id, state)
    - 将新的完整状态写入数据库
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.checkpoint.sqlite import SqliteSaver
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


@tool
def get_order_status(order_id: str) -> str:
    """查询订单状态"""
    orders = {
        "202602016789": "已发货，预计明天送达",
        "202501155678": "配送中，今天下午送达",
    }
    return orders.get(order_id, "订单不存在")


# ============================================================================
# 示例 1：InMemorySaver 的局限（对比）
# ============================================================================
def example_1_inmemory_limitation():
    """
    示例1：InMemorySaver 的局限

    - 局限：
        - 程序重启后丢失
        - 无法跨进程共享
        - 不适合生产环境

    - 解决方案：使用 SqliteSaver 持久化到数据库
    """
    print("\n" + "=" * 40)
    print("示例 1：InMemorySaver 的局限")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。你必须记住用户告诉你的信息。",
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "user_1212"}}

    print("\n第一轮对话：")
    agent.invoke(
        {"messages": [{"role": "user", "content": "我叫张国强"}]}, config=config
    )
    print("用户：我叫张国强")

    print("\n第二轮对话（同一进程内）：")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫什么？"}]}, config=config
    )
    print(f"Agent 回复：{response["messages"][-1].content}")


# ============================================================================
# 示例2：使用 SqliteSaver 实现持久化
# ============================================================================
def example_2_sqlite_saver():
    """
    示例2：使用 SqliteSaver 实现持久化

    - 关键点：
        - 对话保存到文件：{db_path}
        - 程序重启后仍可恢复
        - 可以跨进程访问
        - 适合生产环境
    """
    print("\n" + "=" * 40)
    print("示例 2：SqliteSaver - 持久化到 SQLite")
    print("=" * 40)

    # 创建持久化的 checkpointer（使用 with 语句）
    db_path = "checkpoints.sqlite"  # 相对路径

    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        agent = create_agent(
            model=model,
            tools=[],
            system_prompt="你是一名智能助手。",
            checkpointer=checkpointer,  # 使用 sqlite 持久化
        )

        config = {"configurable": {"thread_id": "persistent_session"}}

        print("\n第一轮对话：")
        print("用户：我叫张国强")
        agent.invoke(
            {"messages": [{"role": "user", "content": "我叫张国强"}]}, config=config
        )

        print("\n第二轮对话：")
        print("用户：我叫什么？")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": "我叫什么？"}]}, config=config
        )
        print(f"Agent 回复：{response["messages"][-1].content}")


# ============================================================================
# 示例3：验证跨进程持久化
# ============================================================================
def example_3_verify_persistence():
    """
    示例3：验证持久化效果

    - 模拟程序重启后，从数据库恢复对话

    - 关键点：
        - Agent 记得之前的对话
        - 即使创建了新的 agent 实例
        - 因为 SQLite 保存了完整历史
    """
    print("\n" + "=" * 40)
    print("示例 3：验证持久化（模拟重启后恢复）")
    print("=" * 40)

    db_path = "checkpoints.sqlite"

    # 模拟“重新启动”：创建新的 agent 和 checkpointer
    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        agent = create_agent(
            model=model,
            tools=[],
            system_prompt="你是一名智能助手。",
            checkpointer=checkpointer,
        )

        # 使用相同的 thread_id
        config = {"configurable": {"thread_id": "persistent_session"}}

        print("\n第三轮对话（新进程，但 thread_id 相同）：")
        print("用户：我之前提到我叫什么？")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": "我之前提到我叫什么？"}]},
            config=config,
        )

        print(f"Agent 回复：{response["messages"][-1].content}")


# ============================================================================
# 示例4：多用户会话管理
# ============================================================================
def example_4_multi_user_sessions():
    """
    示例4：管理多个用户的持久化会话

    - 每个用户有独立的 thread_id

    - 关键点：
        - 不同 thread_id 的会话独立存储
        - 所有会话持久化在同一数据库
        - 数据库文件：{db_path}
    """
    print("\n" + "=" * 40)
    print("示例 4：多用户会话管理")
    print("=" * 40)

    db_path = "multi_user.sqlite"

    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        agent = create_agent(
            model=model,
            tools=[],
            system_prompt="你是一名智能助手。",
            checkpointer=checkpointer,
        )

        # 用户 A
        print("\n[用户 A 的对话]")
        config_a = {"configurable": {"thread_id": "user_alice"}}
        agent.invoke(
            {"messages": [{"role": "user", "content": "我是Alice，我喜欢编程"}]},
            config=config_a,
        )
        print("Alice 用户输入：我是Alice，我喜欢编程")

        # 用户 B
        print("\n[用户 B 的对话]")
        config_b = {"configurable": {"thread_id": "user_bob"}}
        agent.invoke(
            {"messages": [{"role": "user", "content": "我是Bob，我喜欢设计"}]},
            config=config_b,
        )
        print("Bob 用户输入：我是Bob，我喜欢设计")

        # 回到用户 A
        print("\n[用户 A 继续对话]")
        response_a = agent.invoke(
            {"messages": [{"role": "user", "content": "我喜欢什么？"}]}, config=config_a
        )
        print(f"Alice 输入：我喜欢什么？")
        print(f"Agent 回复：{response_a["messages"][-1].content}")

        # 回到用户 B
        print("\n[用户 B 继续对话]")
        response_b = agent.invoke(
            {"messages": [{"role": "user", "content": "我喜欢什么？"}]}, config=config_b
        )
        print(f"Bob 输入：我喜欢什么？")
        print(f"Agent 回复：{response_b["messages"][-1].content}")


# ============================================================================
# 示例5：带工具的持久化 Agent
# ============================================================================
def exmaple_5_tools_with_persistence():
    """
    示例5：工具调用 + 持久化

    - Agent 记住工具调用历史

    - 关键点：
        - Agent 记住了订单 12345 的查询结果
        - 工具调用历史也被持久化
        - 无需重复调用工具
    """
    print("\n" + "=" * 40)
    print("示例 5：工具调用 + 持久化")
    print("=" * 40)

    db_path = "tools.sqlite"

    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        agent = create_agent(
            model=model,
            tools=[get_order_status],
            system_prompt="你是一名智能助手。",
            checkpointer=checkpointer,
        )

        config = {"configurable": {"thread_id": "customer_2026012203"}}

        print("第一轮：查询订单：")
        print("客户：查询订单 202602016789 的状态")
        response1 = agent.invoke(
            {"messages": [{"role": "user", "content": "查询订单 202602016789 的状态"}]},
            config=config,
        )
        print(f"Agent 回复：{response1["messages"][-1].content}")

        print("第二轮：查询订单：")
        print("客户：我的订单什么时候到？")
        response2 = agent.invoke(
            {"messages": [{"role": "user", "content": "我的订单什么时候到？"}]},
            config=config,
        )
        print(f"Agent 回复：{response2["messages"][-1].content}")


# ============================================================================
# 示例6：实际应用 - 客服系统
# ============================================================================
def example_6_customer_service():
    """
    示例6：实际应用 - 持久化客服系统

    - 场景：客户可能分多次咨询，需要记住历史

    - 关键点：
        - 客户无需重复订单号
        - 系统记住了上午的咨询
        - 即使客服系统重启也不影响
        - 生产级应用的标准做法
    """
    print("\n" + "=" * 40)
    print("示例 6：实际应用 - 持久化客服系统")
    print("=" * 40)

    db_path = "customer_service.sqlite"

    with SqliteSaver.from_conn_string(db_path) as checkpointer:
        agent = create_agent(
            model=model,
            tools=[get_order_status],
            system_prompt="""
            你是客服助手。
特点：
- 能够记住客户之前的咨询
- 友好、耐心
- 使用工具查询订单
            """,
            checkpointer=checkpointer,
        )

        customer_id = "customer_20251202_12345"
        config = {"configurable": {"thread_id": customer_id}}

        print("\n第一次咨询（今天上午）：")
        conversations_morning = ["你好，我想查询订单", "订单号是 202501155678"]

        for msg in conversations_morning:
            print(f"\n客户：{msg}")
            response = agent.invoke(
                {"messages": [{"role": "user", "content": msg}]}, config=config
            )
            print(f"客服回复：{response["messages"][-1].content}")

        print("\n" + "-" * 40)
        print("[几个小时后...]")
        print("-" * 40)

        print("\n第二次咨询（今天下午）：")
        print("客户：我的订单到哪儿了？")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": "我的订单到哪儿了？"}]},
            config=config,
        )
        print(f"客服回复：{response["messages"][-1].content}")


# ============================================================================
# 示例 7：SqliteSaver 参数说明
# ============================================================================
def example_7_sqlite_parameters():
    """
    示例7：SqliteSaver 参数和最佳实践
    """
    print("\n" + "=" * 40)
    print("示例 7：SqliteSaver 参数详解")
    print("=" * 40)

    print(
        """
SqliteSaver 创建方式：

1. from_conn_string + with 语句（推荐）
   with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
       system_prompt="你是一个有帮助的助手。"
       agent = create_agent(model=model, checkpointer=checkpointer)
       agent.invoke(...)

   - 自动管理连接和资源
   - 支持相对路径和绝对路径
   - 最简单安全的方式
   - 确保正确释放数据库连接
   - 注意：直接传文件路径，不要加 sqlite:/// 前缀

2. 使用 sqlite3.connect（高级）
   import sqlite3
   conn = sqlite3.connect("checkpoints.sqlite")
   checkpointer = SqliteSaver(conn)

   - 需要手动管理连接
   - 适合需要自定义连接参数的场景

数据库文件路径：
- 相对路径：checkpoints.sqlite（当前目录）
- 绝对路径：C:/Users/xxx/data/checkpoints.sqlite（Windows）
- 内存数据库：:memory:（测试用，程序退出即丢失）

最佳实践：
✅ 始终使用 with 语句管理 SqliteSaver
✅ 直接传文件路径，不要加 sqlite:/// 前缀
✅ 生产环境：使用绝对路径
✅ 开发测试：使用相对路径
✅ 单元测试：使用 :memory:
✅ 定期备份数据库文件
    """
    )


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 80)
    print(" LangChain 1.0 - Checkpointing (持久化)")
    print("=" * 80)

    try:
        # example_1_inmemory_limitation()
        # example_2_sqlite_saver()
        # example_3_verify_persistence()
        # example_4_multi_user_sessions()
        # exmaple_5_tools_with_persistence()
        # example_6_customer_service()
        example_7_sqlite_parameters()

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
