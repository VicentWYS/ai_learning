"""
LangChain 1.0 - Context Management (上下文管理)
==========================================================

本模块重点讲解：
1. SummarizationMiddleware - 自动摘要中间件（LangChain 1.0 新增）
2. trim_messages - 消息修剪工具
3. 管理对话长度，避免超 token
4. 中间件的使用
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_core.tools import tool
from langchain_core.messages.utils import trim_messages
from langchain_core.messages import HumanMessage, AIMessage
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


# 自定义工具
@tool
def calculator(operation: str, a: float, b: float) -> str:
    """
    执行数学计算
    """
    ops = {
        "add": lambda x, y: x + y,
        "multiply": lambda x, y: x * y,
    }
    result = ops.get(operation, lambda x, y: 0)(a, b)
    return f"{a} {operation} {b} = {result}"


# ============================================================================
# 示例1：问题演示 - 对话历史无限增长
# ============================================================================
def example_1_problem_unlimited_growth():
    """
    示例1：问题演示 - 对话历史无限增长

    - 问题：
        - 消息越来越多，内存占用增加
        - 超过模型 token 限制会报错
        - 每次调用都要传输全部历史，成本增加
    """
    print("\n" + "=" * 40)
    print("示例 1：问题演示 - 对话历史无限增长")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="你是一名智能助手。",
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "long_conversation"}}

    conversations = [
        "你好，我叫小李。",
        "我是一名高中数学老师。",
        "我最近在减肥，不吃晚饭。",
        "我现在住在成都。",
        "我最近在学习Python和LangChain。",
    ]

    # 模拟多轮对话
    print("\n模拟多轮对话")
    for i, conversation in enumerate(conversations, 1):
        agent.invoke(
            {"messages": [{"role": "user", "content": conversation}]},
            config=config,
        )

    # 查看消息数量
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "总结一下"}]}, config=config
    )

    print(f"\n总消息数：{len(response["messages"])}")
    print("(包含用户消息 + AI 回复)")


# ============================================================================
# 示例2：解决方案 1 - SummarizationMiddleware (推荐)
# ============================================================================
def example_2_summarization_middleware():
    """
    示例2：使用 SummarizationMiddleware 自动摘要

    - 关键：LangChain 1.0 新增的中间件
        - 当消息数超过阈值时，自动摘要旧消息
        - SummarizationMiddleware 会自动摘要旧消息
        - 保持对话历史在可控范围内
        - 重要信息通过摘要保留

    - 参数详解：
        1. model (必需)
        - 用于生成摘要的模型
        - 可以用便宜的模型（如 gpt-3.5）降低成本
        2. max_tokens_before_summary
        - 触发摘要的 token 数阈值
        - 默认: 1000
        - 建议：根据模型上下文窗口设置（如 4k 模型设为 3000）
        3. summarization_prompt (可选)
        - 自定义摘要提示词
        - 默认：简洁摘要对话历史
    """
    print("\n" + "=" * 40)
    print("示例 2：SummarizationMiddleware - 自动摘要")
    print("=" * 40)

    summary_model = init_chat_model(
        model="qwen-plus",
        model_provider="openai",
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0.1,
    )

    summarization_middleware = SummarizationMiddleware(
        model=summary_model,
        max_tokens_before_summary=1000,  # 超过 1000 tokens 就生成摘要
        summary_prompt="""
你正在为一个智能体构建**长期记忆摘要**。

请将以下历史对话压缩为“长期记忆”，要求：

1. 保留用户的背景、目标、偏好
2. 保留已经完成/未完成的任务
3. 保留重要结论
4. 删除闲聊、重复内容
5. 用第三人称客观描述
6. 输出内容将作为 system memory 供后续对话理解上下文
""",
    )

    # 创建带摘要中间件的 Agent
    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        checkpointer=InMemorySaver(),
        middleware=[summarization_middleware],
    )

    config = {"configurable": {"thread_id": "with_summary"}}

    print("\n进行多轮对话")
    conversations = [
        "我叫张三，是工程师",
        "我在北京工作",
        "我喜欢编程和阅读",
        "我最近在学习 AI",
        "请总结一下我的信息",
    ]

    for msg in conversations:
        print(f"\n用户：{msg}")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": msg}]}, config=config
        )
        print(f"Agent 回复：{response["messages"][-1].content[:200]}...")

    print(f"\n消息数：{len(response["messages"])}")


# ============================================================================
# 示例3：手动消息修剪(trim_messages)
# ============================================================================
def example_3_manual_trimming():
    """
    示例3：使用 trim_messages 手动修剪消息

    - 适用场景：需要精确控制保留的消息 token 数量

    - 功能：这里是直接从开头或结尾截取指定数量的 token 来实现的修剪

    - 关键点：
        - trim_messages 手动控制消息 token 数量
        - 适合需要精确控制的场景
        - 需要自己管理修剪逻辑
    """
    print("\n" + "=" * 40)
    print("示例 3：手动消息修剪")
    print("=" * 40)

    # 模拟一个长对话历史
    messages = [
        HumanMessage(
            content="我最近在准备找工作，方向主要考虑数据相关岗位，比如数据分析、数据开发这些。"
        ),
        AIMessage(
            content="不错的方向！数据分析和数据开发在企业中需求都很大。你是计算机相关专业吗？平时有接触数据库或Python吗？"
        ),
        HumanMessage(
            content="是的，我是计算机硕士，做过深度学习医学图像处理，平时用Python比较多，数据库只学过MySQL基础。"
        ),
        AIMessage(
            content="那你的背景其实非常有优势。深度学习 + Python + 一点数据库，非常适合往数据分析、数据挖掘甚至AI相关数据岗位发展。"
        ),
        HumanMessage(
            content="不过我有点纠结，要不要继续做医学图像相关工作，还是转纯数据方向。"
        ),
        AIMessage(
            content="这是个典型的方向选择问题。医学图像属于非常垂直且专业的领域，而纯数据岗位更通用、岗位更多。关键看你未来是否打算读博或继续科研。"
        ),
        HumanMessage(content="我确实有读博的打算，可能工作两年后去读。"),
        AIMessage(
            content="那建议你优先选择和医学影像、AI、数据处理相关的岗位，这样你的工作经历可以直接为读博服务，而不是偏离研究方向。"
        ),
        HumanMessage(content="对了，我老家在海南，其实我也希望以后能回省内发展。"),
        AIMessage(
            content="明白了。如果考虑回海南发展，那么医疗影像、医院信息化、医疗AI相关方向会更有优势，因为这些在本地属于稀缺高端技术岗位。"
        ),
    ]

    print(f"\n原始消息数：{len(messages)}")

    def fake_token_counter(messages):
        # 非常粗略：按字符数近似 token
        return sum(len(m.content) for m in messages)

    trimmed = trim_messages(
        messages=messages,
        max_tokens=200,  # 用 token 控制
        token_counter=fake_token_counter,
        strategy="last",
    )

    print(f"修剪后的消息数：{len(trimmed)}")
    print("\n保留的消息：")
    for msg in trimmed:
        print(f"{msg.__class__.__name__}: {msg.content}")


# ============================================================================
# 示例4：对比不同策略
# ============================================================================
def example_4_comparison():
    """
    示例4：对比不同的上下文管理策略
    """
    print("\n" + "=" * 40)
    print("示例 4：策略对比")
    print("=" * 40)

    print(
        """
策略对比：

1. 不做处理（默认）
   优点：保留完整历史
   缺点：会超 token、成本高
   适用：短对话

2. SummarizationMiddleware（推荐）
   优点：
   - 自动化，无需手动管理
   - 保留重要信息（通过摘要）
   - 平滑过渡
   缺点：
   - 摘要可能丢失细节
   - 额外的摘要成本
   适用：长对话、需要保留上下文

3. trim_messages（手动修剪）
   优点：
   - 精确控制
   - 简单直接
   - 无额外成本
   缺点：
   - 旧消息完全丢失
   - 可能断开上下文
   适用：只需要指定数量的 token

4. 滑动窗口（自定义）
   优点：
   - 保留系统消息 + 最近消息
   - 可控成本
   缺点：
   - 需要自己实现
   适用：有明确规则的场景

推荐方案：
- 短对话（<10轮）：不处理
- 中长对话：SummarizationMiddleware
- 只要最近几轮：trim_messages
- （最新版本的 langchain 只聚焦 token 数的限制，不讲“对话轮数”这个概念了）
    """
    )


# ============================================================================
# 示例5：实际应用 - 客服机器人
# ============================================================================
def example_5_practical_customer_service():
    """
    示例5：实际应用 - 客服机器人

    - 场景：客服对话可能很长，需要管理上下文

    - 关键点：
        - 自动管理对话 token
        - 重要信息（订单号）通过摘要保留
        - 适合生产环境
    """
    print("\n" + "=" * 40)
    print("示例 5：实际应用 - 客服机器人")
    print("=" * 40)

    summary_model = init_chat_model(
        model="qwen-plus",
        model_provider="openai",
        api_key=QWEN_API_KEY,
        base_url=QWEN_BASE_URL,
        temperature=0.1,
    )

    summarization_middleware = SummarizationMiddleware(
        model=summary_model,
        max_tokens_before_summary=800,  # 超过 800 tokens 就生成摘要
        summary_prompt="""
你正在为一个智能体构建**长期记忆摘要**。

请将以下历史对话压缩为“长期记忆”，要求：

1. 保留用户的背景、目标、偏好、订单信息
2. 保留已经完成/未完成的任务
3. 保留重要结论
4. 删除闲聊、重复内容
5. 用第三人称客观描述
6. 输出内容将作为 system memory 供后续对话理解上下文
""",
    )

    # 创建客服 Agent
    agent = create_agent(
        model=model,
        tools=[calculator],
        system_prompt="""
你是客服助手。
特点：
- 记住用户问题
- 简洁回答
- 使用工具计算
""",
        checkpointer=InMemorySaver(),
        middleware=[summarization_middleware],
    )

    config = {"configurable": {"thread_id": "customer_2011"}}

    # 模拟客服对话
    conversations = [
        "你好，我想咨询订单",
        "我的订单号是 12345",
        "帮我算一下 100 乘以 2 的优惠价",
        "谢谢",
    ]

    for msg in conversations:
        print(f"客户：{msg}")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": msg}]}, config=config
        )
        print(f"客服：{response["messages"][-1].content}")

    print(f"\n总消息数：{len(response["messages"])}")


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 80)
    print("LangChain 1.0 - Context Management")
    print("=" * 80)

    try:
        # example_1_problem_unlimited_growth()
        # example_2_summarization_middleware()
        # example_3_manual_trimming()
        # example_4_comparison()
        example_5_practical_customer_service()

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
