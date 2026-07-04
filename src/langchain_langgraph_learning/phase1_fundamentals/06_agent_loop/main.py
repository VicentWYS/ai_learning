"""
LangChain 1.0 - Agent 执行循环（ReAct 模式）
========================================================

ReAct 循环：
    Reason（推理） -> Act（行动） -> Observe（观察）->循环直到完成

本模块重点讲解：
    1. ReAct 执行循环的详细过程（ReAct -> Act -> Observe）
    2. 流式输出（streaming）
    3. 查看中间步骤
    4. 理解消息流转

核心要点：
    - Agent 执行循环：问题 → 工具调用 → 结果 → 答案
    - messages 记录完整历史
    - stream() 用于实时输出
    - 理解 HumanMessage、AIMessage、ToolMessage
    - 使用 create_agent（LangChain 1.0 API）

注意：
    - 在学习本代码时，需时刻对照 agent.stream(...) 返回的 chunk/chunk.items() 的值，从而可以观察到代码中 tool_calls 和 content 的获取方法
"""

import os
import sys

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from tools.calculator import calculator
from tools.weather import get_weather

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


# ==============================================================================
# 示例1：理解执行循环 - 查看完整消息历史
# ==============================================================================
def example_1_understand_loop():
    """
    示例1：查看 Agent 执行循环的每一步

    - 关键：response["messages"] 包含完整的对话历史
    - 执行流程：
        1. HumanMessage    → 用户问题
        2. AIMessage       → AI 决定调用工具（包含 tool_calls）
        3. ToolMessage     → 工具执行结果
        4. AIMessage       → AI 基于结果生成最终答案
    - 关键点：
        - Agent 自动完成这个循环
        - 所有步骤都记录在 messages 中
        - 最后一条消息是最终答案
    """
    print("\n" + "=" * 40)
    print("示例1：Agent 执行循环详解")
    print("=" * 40)

    agent = create_agent(
        model=model, tools=[calculator], system_prompt="你是一个智能助手。"
    )

    print("\n问题：25 * 8 等于多少？")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "125 * 8 等于多少？"}]}
    )

    print("\n完整消息历史：")
    for i, msg in enumerate(response["messages"], 1):
        print("\n" + "=" * 40)
        print(f"消息{i}: {msg.__class__.__name__}")
        print("=" * 40)

        if hasattr(msg, "content") and msg.content:
            print(f"内容：{msg.content}")

        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"工具调用：")
            for tc in msg.tool_calls:
                print(f"    - 工具：{tc["name"]}")
                print(f"    - 参数：{tc["args"]}")
        if hasattr(msg, "name"):
            print(f"工具名：{msg.name}")


# ==============================================================================
# 示例2：一个典型的工具调用流式输出 Graph State（查看 Graph 节点工作状态）
# ==============================================================================
def example_2_streaming():
    """
    示例2：一个典型的工具调用流式输出 Graph State（查看 Graph 节点工作状态）

    - 使用 .stream() 方法
    - 关键点：
        - stream() 逐步返回结果(Graph State)
        - 用于实时显示进度
        - 适合长时间运行的任务
    """
    print("\n" + "=" * 40)
    print("示例2：流式输出 Graph State")
    print("=" * 40)

    agent = create_agent(
        model=model, tools=[calculator, get_weather], system_prompt="你是一名智能助手。"
    )

    print("\n问题：北京天气如何？然后计算 4 * 25")
    print("\n流式输出Graph State")
    print("-" * 40)

    # 使用 stream 方法
    # chunk 是一个字典 dict
    # chunk.__class__.__name__ == dict
    # {'model': {'messages': [AIMessage(...)]}}
    # {'tools': {'messages': [ToolMessage(...)]}}
    # {'model': {'messages': [AIMessage(...)]}}

    # 将 dict 变为 key-value 键值对
    # chunk.items().__class__.__name__ == dict.items()
    # dict_items([('model', {'messages': [AIMessage(...)]})])
    # dict_items([('tools', {'messages': [ToolMessage(...)]})])
    # dict_items([('model', {'messages': [AIMessage(...)]})])

    # 返回：
    # [model][AIMessage]: [{'name': 'get_weather', 'args': {'city': '北京'}, 'id': '...', 'type': 'tool_call'}]
    # [tools][ToolMessage]: 晴天，温度 15°C，空气质量良好
    # [model][AIMessage]: 北京当前天气为晴天，温度为15°C，空气质量良好。
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "北京天气如何？"}]}
    ):
        for node, state in chunk.items():
            if "messages" in state:
                # 获取 messages 列表中当前最新的消息: AIMessage/ToolMessage/...
                msg = state["messages"][-1]

                # 若有：输出 tool_calls 信息
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"\n[{node}][{msg.__class__.__name__}]: {msg.tool_calls}")
                # 若有：输出 content 信息
                elif hasattr(msg, "content") and msg.content:
                    print(f"\n[{node}][{msg.__class__.__name__}]: {msg.content}")


# ==============================================================================
# 示例3：多步骤执行
# ==============================================================================
def example_3_multi_step():
    """
    示例3：Agent 执行多个工具调用

    - 理解复杂任务的执行过程
    - 关键点：
        - Agent 可以多次调用工具
        - 每次调用的结果会影响下一步
        - 直到得到最终答案
    """
    print("\n" + "=" * 40)
    print("示例 3：多步骤执行")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="你是一名数学助手，当遇到复杂计算时，采用分步骤进行计算。",
    )

    print("\n问题：先算 10 加 20，然后把结果乘以 3")

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "先算 10 加 20，然后把结果乘以 3"}]}
    )

    # 统计工具调用次数
    tool_calls_count = 0
    for msg in response["messages"]:  # 这里需要遍历全部历史
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_calls_count += len(msg.tool_calls)

    print(f"\n工具调用次数：{tool_calls_count}")
    print(f"最终回答：{response["messages"][-1].content}")


# ==============================================================================
# 示例4：查看中间状态
# ==============================================================================
def example_4_inspect_state():
    """
    示例4：在执行过程中查看 Graph State 状态

    - 使用 .stream() 方法
    - 关键点：
        - stream() 逐步返回结果(Graph State)
        - 用于实时显示进度
        - 适合长时间运行的任务
    """
    print("\n" + "=" * 40)
    print("示例 4：查看中间状态")
    print("=" * 40)

    agent = create_agent(
        model=model, tools=[calculator], system_prompt="你是一名智能助手。"
    )

    print("\n问题：100 除以 5 等于多少？")
    print("\n执行步骤：")

    step = 0
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "100 除以 5 等于多少？"}]}
    ):
        step += 1
        print(f"\n步骤 {step}：")

        for node, state in chunk.items():
            if "messages" in state:
                msg = state["messages"][-1]

                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    print(f"\n[{node}][{msg.__class__.__name__}]: {msg.tool_calls}")
                elif hasattr(msg, "content") and msg.content:
                    content_preview = (
                        msg.content[:50] if len(msg.content) > 50 else msg.content
                    )
                    print(f"\n[{node}][{msg.__class__.__name__}]: {content_preview}...")


# ==============================================================================
# 示例5：理解消息类型
# ==============================================================================
def example_5_message_types():
    """
    示例5：详解各种消息类型

    - Agent 执行循环中的消息类型
    - 消息类型总结：
        - HumanMessage  → 用户的输入
        - AIMessage     → AI 的输出（可能包含 tool_calls 或最终答案）
        - ToolMessage   → 工具的执行结果
        - SystemMessage → 系统指令（通过 prompt 参数设置）
    """
    print("\n" + "=" * 40)
    print("示例 5：消息类型详解")
    print("=" * 40)

    agent = create_agent(
        model=model, tools=[get_weather], system_prompt="你是一名智能助手。"
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "上海天气如何？"}]}
    )

    print("\n消息类型分析：")

    # 消息类型分析：
    # 返回结果如下：
    # [HumanMessage] 用户输入
    # 内容：上海天气如何？
    #
    # [AIMessage] AI 决定调用工具
    # 工具：get_weather
    # 参数：{'city': '上海'}
    #
    # [ToolMessage] 工具执行结果
    # 工具：get_weather
    # 结果：多云，温度 18°C，有轻微雾霾
    #
    # [AIMessage] AI 的最终回答
    # 最终回答：上海目前天气为多云，温度为18°C，但有轻微雾霾，建议外出时注意防护，保持室内空气流通。
    for msg in response["messages"]:
        msg_type = msg.__class__.__name__

        if msg_type == "HumanMessage":
            print("\n[HumanMessage] 用户输入")
            print(f"内容：{msg.content}")

        elif msg_type == "AIMessage":
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"\n[AIMessage] AI 决定调用工具")
                print(f"工具：{msg.tool_calls[0]["name"]}")
                print(f"参数：{msg.tool_calls[0]["args"]}")
            else:
                print(f"\n[AIMessage] AI 的最终回答")
                print(f"最终回答：{msg.content}")

        elif msg_type == "ToolMessage":
            print(f"\n[ToolMessage] 工具执行结果")
            print(f"工具：{msg.name}")
            print(f"结果：{msg.content}")


# ==============================================================================
# 主程序
# ==============================================================================
def main():
    print("\n" + "=" * 80)
    print("LangChain 1.0 - Agent 执行循环")
    print("=" * 80)

    try:
        # example_1_understand_loop()
        # example_2_streaming()
        # example_3_multi_step()
        # example_4_inspect_state()
        example_5_message_types()

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
