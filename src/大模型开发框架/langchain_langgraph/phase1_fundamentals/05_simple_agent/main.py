"""
LangChain 1.0 - Simple Agent (使用 creat_agent)
================================================================

本模块重点讲解：
1. 使用 create_agent 创建 Agent（LangChain 1.0 新 API）
2. Agent 自动决定何时使用工具
3. Agent 执行循环的工作原理

重要更新：
- LangChain 1.0 中，Agent 创建使用 `create_agent`
- 它来自 `langchain_agents` 模块（LangChain 1.0 新增）
- 旧的 `create_react_agent` （langgraph.prebuilt）已弃用
"""

import os
import sys
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent  # LangChain 1.0 API
from langgraph.checkpoint.memory import InInMemorySaver  # 用于多轮对话

# 导入自定义工具
from tools.weather import get_weather
from tools.calculator import calculator
from tools.web_search import web_search

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


# ============================================================================
# 示例 1：创建第一个 Agent
# ============================================================================
def example_1_basic_agent():
    """
    示例1：创建最简单的 Agent

    - 关键：
        1. 使用 create_agent() 函数（LangChain 1.0 API）
        2. 传入 model 和 tools
        3. Agent 会自动决定是否使用工具
    """
    print("\n" + "=" * 40)
    print("示例1：创建第一个 Agent")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[get_weather],  # 只给一个工具
        system_prompt="你是一名智能助手，可以查询天气信息。",  # 在创建时就指定了系统提示词
    )

    print("\nAgent 创建成功！")
    print("配置的工具：get_weather")
    print("使用 LangChain 1.0 API: create_agent")

    # 测试：需要工具的问题
    print("\n测试1：询问天气（需要工具）")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "北京今天的天气怎么样？"}]}
    )

    print(f"\nAgent 回复：{response["messages"][-1].content}")

    # 测试：不需要工具的问题
    print("\n测试2：普通问题（不需要工具）")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "你好，介绍你自己"}]}
    )

    print(f"\nAgent 回复：{response["messages"][-1].content}")

    print("\n关键点：")
    print("  - Agent 自动判断是否需要使用工具")
    print("  - 需要工具时：调用工具 → 获取结果 → 生成回答")
    print("  - 不需要时：直接回答")


# ============================================================================
# 示例2：多工具 Agent
# ============================================================================
def example_2_multi_tool_agent():
    """
    示例2：配置多个工具的 Agent

    - Agent 会根据问题选择合适的工具
    - 关键点：
        - Agent 从多个工具中选择最合适的
        - 基于工具的 docstring 理解工具用途
    """
    print("\n" + "=" * 40)
    print("示例2：多工具 Agent")
    print("=" * 40)

    # 创建配置多个工具的 Agent
    agent = create_agent(
        model=model,
        tools=[get_weather, calculator, web_search],
        system_prompt="你是一名智能助手。",
    )

    print("\n配置的工具：")
    print("- get_weather（天气查询）")
    print("- calculator（计算器）")
    print("- web_search（网页搜索）")

    # 测试不同类型的问题
    tests = [
        "上海的天气怎么样？",  # 应该用 get_weather
        "15*30等于多少？",  # 应该用 calculator
    ]

    for i, question in enumerate(tests, 1):
        print("\n" + "=" * 40)
        print(f"测试 {i}: {question}")
        print("=" * 40)

        response = agent.invoke({"messages": [{"role": "user", "content": question}]})

        # 显示最终回答
        print(f"\nAgent 回复：{response["messages"][-1].content}")


# ============================================================================
# 示例3：带系统提示的 Agent
# ============================================================================
def example_3_agent_with_system_prompt():
    """
    示例3：自定义 Agent 的行为

    - 使用 prompt 参数（注意，不是 system_prompt）
    - 关键点：
        - system_prompt 参数定义 Agent 的系统提示词
        - 可以指定输出格式、语气、工作流程等
        - 也可以传入 SystemMessage 对象
    """
    print("\n" + "=" * 40)
    print("示例3：自定义 Agent 行为")
    print("=" * 40)

    # create_agent 使用 system_prompt 参数（字符串或SystemMessage）
    system_messages = """你是一个友好的智能助手。
    特点：
        - 回答简介明了
        - 使用工具前会先说明
        - 结果用表格或列表清晰展示"""

    agent = create_agent(
        model=model,
        tools=[get_weather, calculator, web_search],
        system_prompt=system_messages,  # 使用 system_prompt 参数
    )

    print("\n测试：自定义行为的 Agent")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "北京天气如何？顺便算一个100+50"}]}
    )

    print(f"\nAgent 回复：{response["messages"][-1].content}")


# ============================================================================
# 示例4：Agent 执行过程详解
# ============================================================================
def example_4_agent_execution_details():
    """
    示例4：查看 Agent 执行的完整过程

    - 理解 Agent 如何一步步工作
    - 执行循环：
        1. 用户提问 -> HumanMessage
        2. AI 决定调用工具 -> AIMessage（包含 tool_calls）
        3. 执行工具 -> ToolMessage（包含结果）
        4. AI 基于结果生成答案 ->  AIMessage（最终回答）
    """
    print("\n" + "=" * 40)
    print("示例4：Agent 执行过程详解")
    print("=" * 40)

    agent = create_agent(
        model=model, tools=[calculator], system_prompt="你是一个智能助手。"
    )

    print("\n问题：25*8等于多少？")
    print("\nAgent 执行过程：")

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "25*8等于多少？"}]}
    )

    # 显示完整的消息历史
    print("\n完整消息历史：")
    for i, msg in enumerate(response["messages"], 1):
        print(f"\n--- 消息 {i} ({msg.__class__.__name__}) ---")
        if hasattr(msg, "content"):
            print(f"内容：{msg.content}")  # hasattr() 函数体现了 Python 的动态语言能力
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"工具调用：{msg.tool_calls}")


# ============================================================================
# 示例5：多轮对话 Agent（使用 InMemorySaver）
# ============================================================================
def example_5_multi_turn_agent():
    """
    示例5： 多轮对话 Agent

    - 关键：使用 InMemorySaver 保持对话历史
    - 关键点：
        - 使用 InMemorySaver 作为 checkpointer
        - 通过 thread_id 区分不同的对话
        - Agent 自动记住上下文
        - 不需要手动传递历史消息 
    """
    print("\n" + "=" * 40)
    print("示例5：多轮对话 Agent")
    print("=" * 40)

    # 创建内存检查点
    memory = InMemorySaver()
    # 创建带记忆的 Agent
    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="你是一个智能助手。",
        checkpointer=memory,  # 添加检查点以支持多轮对话
    )

    # 使用 thread_id 来保持对话
    # 这里的 conversation-1 只是一个指定字符串，没有任何特殊含义。
    # 在真实系统中，往往是：thread_id = user_id/session_id/chat_id...
    # 例如：thread_id = user_id(具体id的值)，这里就可以设置每个用户都有独立长期记忆
    config = {"configurable": {"thread_id": "conversation-1"}}

    # 第一轮
    print("\n用户：10 加 5 等于多少？")
    response1 = agent.invoke(
        {"messages": [{"role": "user", "content": "10 加 5 等于多少？"}]},
        config=config,
    )
    print(f"Agent 回复: {response1["messages"][-1].content}")

    # 第二轮：继续上一轮的对话（记忆自动保持）
    print("\n用户：再乘以 3 呢？")
    response2 = agent.invoke(
        {"messages": [{"role": "user", "content": "再乘以 3 呢？"}]},
        config=config,  # 使用相同的 thread_id
    )

    print(f"Agent: {response2["messages"][-1].content}")


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 80)
    print("LangChain 1.0 - Simple Agent (create_agent)")
    print("=" * 80)

    try:
        # example_1_basic_agent()
        # example_2_multi_tool_agent()
        # example_3_agent_with_system_prompt()
        # example_4_agent_execution_details()
        example_5_multi_turn_agent()

        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
