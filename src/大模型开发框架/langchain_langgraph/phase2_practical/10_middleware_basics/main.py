"""
LangChain 1.0 - Middleware Basics(中间件基础)
========================================================

本模块重点讲解：
1. 什么是中间件（Middleware）
2. before_model 和 after_model 钩子
3. 自定义中间件的创建
4. 多个中间件的组合
5. 内置中间件的使用
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware import SummarizationMiddleware
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
def get_weather(city: str) -> str:
    """
    查询城市天气
    """
    weather_data = {"北京": "晴天，15°C", "上海": "多云，18°C", "深圳": "雨天，22°C"}
    return weather_data.get(city, "未知城市")


# ====================================================================================
# 示例1：最简单的中间件
# ====================================================================================
class LoggingMiddleware(AgentMiddleware):
    """
    日志中间件 - 记录每次模型调用

    - before_model: 模型调用前执行
    - after_model: 模型响应后执行
    """

    def before_model(self, state, runtime):
        """模型调用前"""
        print("\n[中间件] before model: 准备调用模型")
        print(f"[中间件] 当前消息数：{len(state.get("messages", []))}")
        return None  # 返回 None 表示继续正常流程

    def after_model(self, state, runtime):
        """模型响应后"""
        print("[中间件] after_model: 模型已响应")
        last_message = state.get("messages", [])[-1]  # 当前最新执行的操作信息
        print(f"[中间件] 响应类型：{last_message.__class__.__name__}")
        return None  # 返回 None 表示不修改状态


def example_1_basic_middleware():
    """
    示例1：基础中间件 - 日志记录

    - 展示 before_model 和 after_model 的基本用法

    - 关键点：
        - before_model 在模型调用前执行
        - after_model 在模型响应后执行
        - 返回 None 表示不修改状态

    - 关键规则：
        1. 必须继承 AgentMiddleware ← 这个固定
        2. 方法名固定 (before_model, after_model) ← 这个固定
        3. 类名随意 ← 这个不固定

    - LangGraph 只看：
        - 是否继承 AgentMiddleware？
        - 是否有 before_model / after_model 方法？
    """
    print("\n" + "=" * 40)
    print("示例 1：基础中间件 - 日志记录")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[LoggingMiddleware()],  # 添加中间件
    )

    print("\n用户：你好")
    response = agent.invoke({"messages": [{"role": "user", "content": "你好"}]})
    print(f"Agent: {response['messages'][-1].content}")


# ====================================================================================
# 示例2：修改状态的中间件
# ====================================================================================
class CallCounterMiddleware(AgentMiddleware):
    """
    计数中间件 - 统计模型调用次数

    - 在中间件内部维护计数器（简单版本）
    """

    def __init__(self):
        super().__init__()
        self.count = 0  # 简单计数器

    def after_model(self, state, runtime):
        """
        模型响应后，增加计数
        """
        self.count += 1  # 只是借用中间件功能顺手实现计数功能
        print(f"\n[计数器] 模型调用次数：{self.count}")
        return None  # 不修改 state


def example_2_state_modification():
    """
    示例2：中间件内部状态 - 计数器

    - 展示如何在中间件内部维护状态（不依赖 Agent state）

    - 关键点：
        - 中间件内部维护计数器（self.count）
        - 不依赖 Agent state（更可靠）
        - 返回 None 表示不修改 Agent 状态
    """
    print("\n" + "=" * 40)
    print("示例 2：中间件内部状态 - 模型调用计数")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[CallCounterMiddleware()],
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "counter_test"}}

    print("\n第一次调用：")
    agent.invoke({"messages": [{"role": "user", "content": "你好"}]}, config=config)

    print("\n第二次调用：")
    agent.invoke({"messages": [{"role": "user", "content": "今天天气"}]}, config=config)

    print("\n第三次调用：")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "谢谢"}]}, config=config
    )


# ====================================================================================
# 示例3：消息修剪中间件
# ====================================================================================
class MessageTrimmerMiddleware(AgentMiddleware):
    """
    示例3：消息修剪中间件 - 限制消息数量

    - before_model: 修改消息列表
    - 注意：需要配合无 checkpointer 使用，否则历史会被恢复
    """

    def __init__(self, max_messages=5):
        super().__init__()
        self.max_messages = max_messages
        self.trimmed_count = 0  # 统计修剪次数

    def before_model(self, state, runtime):
        """
        模型调用前：修剪消息
        """
        messages = state.get("messages", [])

        if len(messages) > self.max_messages:
            # 保留最近 N 条消息
            trimmed_messages = messages[-self.max_messages :]
            self.trimmed_count += 1
            print(
                f"\n[修剪] 消息从 {len(messages)} 条减少到 {len(trimmed_messages)} 条（第 {self.trimmed_count} 次修剪）"
            )
            return {"messages": trimmed_messages}

        return None


def example_3_message_trimming():
    """
    示例3：消息修剪 - 防止消息过多

    - 展示如何在调用前修改消息列表
    - 重点：手动累积消息，观察修剪效果

    - 关键点：
        - before_model 在传给模型前修剪消息
        - max_messages=4 限制发送给模型的消息数
        - 但返回的 response 会包含新生成的消息
        - 不使用 checkpointer 避免历史恢复
    - 生产建议：
        - 简单修剪用这种方式
        - 复杂场景用 SummarizationMiddleware（第8章）
    """
    print("\n" + "=" * 40)
    print("示例 3：消息修剪 - 限制消息数量")
    print("=" * 40)

    print("\n[说明] 不使用 checkpointer, 手动管理消息历史\n")

    middleware = MessageTrimmerMiddleware(max_messages=4)  # 最多保留 4 条

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[middleware],
        # 不使用 checkpointer
    )

    # 手动管理消息历史
    messages = []
    for i in range(6):
        print(f"\n --- 第 {i+1} 次对话 --- ")

        # 新增用户消息
        new_msg = {"role": "user", "content": f"消息{i+1}: 讲一个一句话的小笑话。"}
        messages.append(new_msg)

        print(f"调用前消息数：{len(messages)}")

        # 调用 agent (middleware 会修剪)
        response = agent.invoke({"messages": messages})

        # 获取完整对话（包含 AI 响应）
        messages = response["messages"]

        print(f"调用后消息数：{len(messages)}")

        if len(messages) <= 4:
            print(f"消息列表：{[msg.content[:15] for msg in messages]}")

    print(f"\n修剪统计：共修剪了 {middleware.trimmed_count} 次")


# ====================================================================================
# 示例4：输出验证中间件
# ====================================================================================
class OutputValidationMiddleware(AgentMiddleware):
    """
    输出验证中间件 - 检查响应长度

    - after_model 验证输出
    """

    def __init__(self, max_length=100):
        super().__init__()
        self.max_length = max_length

    def after_model(self, state, runtime):
        """
        模型响应后，验证输出
        """
        messages = state.get("messages", [])
        if not messages:
            return None

        last_messages = messages[-1]
        content = getattr(last_messages, "content", "")

        if (len(content)) > self.max_length:
            print(
                f"\n警告：响应过长 ({len(content)} 个字符)，已截断到 {self.max_length}"
            )
            # 这里可以实现截断或重试逻辑

        return None


def example_4_output_validation():
    """
    示例4：输出验证 - 检查响应质量

    - 展示如何验证模型输出

    - 关键点：
        - after_model 可以验证输出
        - 可以实现重试、截断等逻辑
        - 保证输出质量
    """
    print("\n" + "=" * 40)
    print("示例 4：输出验证 - 响应长度检查")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[OutputValidationMiddleware(max_length=50)],
    )

    print("\n用户：请介绍 Python 编程语言的历史、特点和应用")
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请详细介绍 Python 编程语言的历史、特点和应用",
                }
            ]
        }
    )

    print(f"Agent: {response["messages"][-1].content[:100]}...")


# ====================================================================================
# 示例5：多个中间件组合
# ====================================================================================
class TimingMiddleware(AgentMiddleware):
    """
    计时中间件
    """

    def before_model(self, state, runtime):
        import time

        # 记录开始时间（实际应该使用 runtime 的上下文管理）
        print("\n计时：开始调用模型...")
        return None

    def after_model(self, state, runtime):
        print("计时：模型调用完成")
        return None


def example_5_multiple_middleware():
    """
    示例5：多个中间件 - 执行顺序

    - 功能：展示中间件的执行顺序

    - 关键点：
        - before_model: 正序执行（1→2→3）
        - after_model: 逆序执行（3→2→1）
        - 类似洋葱模型：1→2→3→模型→3→2→1
    """
    print("\n" + "=" * 40)
    print("示例 5：多个中间件 - 执行顺序")
    print("=" * 40)

    class Middleware1(AgentMiddleware):
        def before_model(self, state, runtime):
            print("\n中间件1：在调用之前")
            return None

        def after_model(self, state, runtime):
            print("中间件1：在调用之后")

    class Middleware2(AgentMiddleware):
        def before_model(self, state, runtime):
            print("\n中间件2：在调用之前")
            return None

        def after_model(self, state, runtime):
            print("中间件2：在调用之后")

    class Middleware3(AgentMiddleware):
        def before_model(self, state, runtime):
            print("\n中间件3：在调用之前")
            return None

        def after_model(self, state, runtime):
            print("中间件3：在调用之后")

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[Middleware1(), Middleware2(), Middleware3()],
    )

    print("\n执行一次调用，观察顺序：")
    agent.invoke({"messages": [{"role": "user", "content": "讲一个一句话的小笑话"}]})


# ====================================================================================
# 示例6：条件跳转（高级）
# ====================================================================================
class MaxCallsMiddleware(AgentMiddleware):
    """
    最大调用限制中间件

    - 通过抛出异常来阻止模型调用（更可靠）
    """

    def __init__(self, max_calls=3):
        super().__init__()
        self.max_calls = max_calls
        self.count = 0  # 简单计数器

    def before_agent(self, state, runtime):
        """
        检查调用次数，超过限制则抛出异常
        """
        if self.count >= self.max_calls:
            print(f"\n已达到最大调用次数 {self.max_calls}, 停止调用")
            # 抛出自定义异常来阻止继续执行
            raise ValueError(f"已达到最大调用次数限制：{self.max_calls}, 停止调用")

        print(f"当前调用次数：{self.count}/{self.max_calls}")
        return None

    def after_model(self, state, runtime):
        """
        增加计数
        """
        self.count += 1
        print("次数+1")
        return None


def example_6_conditional_jump():
    """
    示例6：调用限制 - 通过异常来阻止调用

    - 展示如何使用异常来阻止模型调用（比 jump_to 更可靠）

    - 关键点：
        - before_model 中抛出异常可以阻止模型调用
        - 比 jump_to 更可靠（在 LangChain 1.0 中）
        - 中间件内部维护计数（self.count）
        - 用于实现熔断、限流等逻辑

    - 注意：
        - jump_to 在 middleware 中可能不按预期工作
        - 推荐用异常来实现流程控制
    """
    print("\n" + "=" * 40)
    print("示例 6：调用限制 - 最大调用次数")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[MaxCallsMiddleware()],
        checkpointer=InMemorySaver(),
    )

    config = {"configurable": {"thread_id": "limit_test"}}

    # 模拟多次调用
    for i in range(4):
        print(f"\n --------------- 第 {i+1} 次尝试调用 --------------- ")
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": f"消息{i+1}"}]}, config=config
            )

            if response.get("messages"):
                print(f"\n响应：{response["messages"][-1].content[:50]}...")

        except ValueError as e:
            print(f"已阻止：{e}")
        except Exception as e:
            print(f"调用失败：{e}")


# ====================================================================================
# 示例7：内置中间件使用
# ====================================================================================


def example_7_builtin_middleware():
    """
    示例7：内置中间件 - SummarizationMiddleware

    - 使用 LangChain 提供的内置中间件

    - 关键点：
        - SummarizationMiddleware 自动摘要旧消息
        - 防止消息历史无限增长
        - 第 08 章详细学习过
    """
    print("\n" + "=" * 40)
    print("示例 7：内置中间件 - 自动摘要")
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
        max_tokens_before_summary=200,
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

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[summarization_middleware],
        checkpointer=InMemorySaver()
    )

    config = {"configurable": {"thread_id": "summary_test"}}

    # 连续多轮对话
    conversations = [
        "我叫李国强",
        "我今年20岁",
        "我喜欢宅家里",
        "尤其喜欢在家里看剧",
    ]

    for i, msg in enumerate(conversations, 1):
        print(f"\n ---------------- 第 {i} 轮对话 ---------------- ")
        print(f"用户：{msg}")
        response = agent.invoke(
            {"messages": [{"role": "user", "content": msg}]}, config=config
        )
        print(f"Agent 回复：{response["messages"][-1].content[:100]}...")
        print(f"总消息数：{len(response["messages"])}")


# ====================================================================================
# 示例8：剖析state
# ====================================================================================
class PrintStateMiddleware(AgentMiddleware):
    def __init__(self):
        super().__init__()
        self.count = 0

    def before_model(self, state, runtime):
        print(f"\n ------------ 开始调用，已调用次数：{self.count} ------------")
        print(f"state: {state}")
        return None

    def after_model(self, state, runtime):
        self.count += 1  # 自动加 1
        print(f"\n ------------ 调用结束，已调用次数：{self.count} ------------")
        print(f"state: {state}")
        return None


def example_8_print_state():
    print("\n" + "=" * 40)
    print("示例 8：剖析state")
    print("=" * 40)

    agent = create_agent(
        model=model,
        tools=[],
        system_prompt="你是一名智能助手。",
        middleware=[PrintStateMiddleware()],
        checkpointer=InMemorySaver()
    )

    config = {"configurable": {"thread_id": "print_state"}}

    # 模拟多轮对话
    conversations = [
        "我叫李明",
        "今年18岁",
        "我喜欢编程，尤其喜欢 Python",
        "介绍我的情况"
    ]

    # 模拟多次调用
    for i, msg in enumerate(conversations, 1):
        print(f"\n\n --------------- 第 {i} 次调用 --------------- ")

        response = agent.invoke(
            {"messages": [{"role": "user", "content": msg}]}, config=config
        )

        print(f"\nAgent 回复：{response["messages"][-1].content}")


# ====================================================================================
# 主程序
# ====================================================================================
def main():
    print("\n" + "=" * 80)
    print("LangChain 1.0 - Middleware Basics (中间件)")
    print("=" * 80)

    try:
        # example_1_basic_middleware()
        # example_2_state_modification()
        # example_3_message_trimming()
        # example_4_output_validation()
        # example_5_multiple_middleware()
        # example_6_conditional_jump()
        # example_7_builtin_middleware()
        example_8_print_state()

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
