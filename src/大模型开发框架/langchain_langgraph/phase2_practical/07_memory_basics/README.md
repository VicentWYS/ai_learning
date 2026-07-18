# 🧠 LangChain 1.0 内存管理基础总结

在 LangChain 1.0（特别是配合 LangGraph 使用时），内存管理的核心思路是：**通过 Checkpointer（检查点）机制自动持久化对话状态。**

## 一、 核心概念

| 概念 | 说明 | 关键点 |
| --- | --- | --- |
| **Checkpointer** | 状态保存器 | 负责保存 Agent 的每一轮状态（包括消息、工具调用等）。 |
| **InMemorySaver** | 内存存储实现 | 最简单的 Checkpointer，将数据存在内存中。**程序重启后数据会丢失。** |
| **thread_id** | 会话唯一标识 | 内存中的“钥匙”。相同的 `thread_id` 对应同一个对话上下文。 |
| **Config** | 配置对象 | 在调用 `invoke` 时传入，包含 `thread_id`，告诉 Agent 该去哪读写内存。 |

---

## 二、 关键代码实现

### 1. 初始化带内存的 Agent

使用 `create_agent` 时，通过 `checkpointer` 参数注入内存管理能力。

```python
from langgraph.checkpoint.memory import InMemorySaver

# 1. 创建内存保存实例
memory = InMemorySaver()

# 2. 注入 Agent
agent = create_agent(
    model=model,
    tools=[get_user_info],
    checkpointer=memory  # 关键步骤
)

```

### 2. 管理多轮会话

必须在 `invoke` 时传入 `config` 参数，否则 Agent 依然无法“回想起”之前的对话。

```python
# 定义会话 ID
config = {"configurable": {"thread_id": "user_12345"}}

# 第一轮：Agent 会保存状态到 "user_12345"
agent.invoke({"messages": [{"role": "user", "content": "我叫哈利"}]}, config=config)

# 第二轮：Agent 会从 "user_12345" 读取状态
response = agent.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, config=config)

```

---

## 三、 深度理解：内存里到底存了什么？

当使用 `checkpointer` 时，Agent 不仅仅记住了文本，它记住的是**完整的消息序列**：

1. **SystemMessage**: 系统提示词。
2. **HumanMessage**: 用户的提问。
3. **AIMessage**: 模型生成的回复。
4. **ToolMessage**: 工具调用的返回结果（**重要：这使得 Agent 不需要重复调用工具就能回答关于旧数据的问题**）。

> **💡 提示：** 你可以通过查看 `response["messages"]` 的长度来观察历史记录的堆叠情况。随着对话增长，该列表会越来越长。

---

## 四、 典型应用场景

### 场景 A：独立多用户对话

* **实现：** 为每个用户分配唯一的 `thread_id`（如 `user_id` 或 `session_id`）。
* **效果：** 用户 A 的对话不会干扰用户 B，Agent 能同时维护成千上万个独立的记忆。

### 场景 B：带工具的复杂任务

* **实现：** 在多轮对话中使用 `checkpointer`。
* **效果：** 第一轮通过工具查到了用户 ID 是 1206，第二轮用户问“我多大了？”，Agent 直接根据第一轮生成的 `ToolMessage` 即可回答，无需再次触发 API。

---

## 五、 复习心得（速记口诀）

* **无内存**：每次 `invoke` 都是初次见面。
* **有内存**：`checkpointer` 是存折，`thread_id` 是账号。
* **想复用**：`config` 必须传，账号对上才能取钱（记忆）。
* **生产环境**：如果需要重启不丢数据，把 `InMemorySaver` 换成 `PostgresSaver` 或 `RedisSaver`。
