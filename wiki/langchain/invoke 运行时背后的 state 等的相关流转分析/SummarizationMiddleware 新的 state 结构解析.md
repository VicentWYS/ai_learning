# 问题
当在一次采用了 SummarizationMiddleware 的对话 HumanMessage、AIMessage 之后，langchain将新的state保存到了 checkpointer 中，那么这个 “新的state” 包含有哪些内容？它在保存到 checkpointer 时，发生了什么？对 checkpointer 有哪些影响？


这是一个**非常深入**、而且**直指 LangGraph 设计核心**的问题。

你现在问的，其实是：

> **SummarizationMiddleware 改写 state 之后，checkpointer 里到底被保存了什么？**

这一步如果想清楚，你对 LangChain 1.0 的理解会非常完整。

---

## 先给结论（非常重要）

在一次触发摘要后的 `invoke` 结束时，**被保存到 checkpointer 的 state：**

> ❗**已经不再包含完整历史对话**
> ❗**而是包含：摘要 + 最近几条真实消息 + Agent 运行轨迹**

也就是说：

> checkpointer 里的历史，被**物理性重写**了。

不是逻辑忽略。是**真的被替换掉了**。

---

## 原始（未摘要）state 长什么样？

在很多轮对话之后，原始 state 大概是：

```
state = {
  messages: [
    Human1, AI1,
    Human2, AI2,
    Human3, AI3,
    ...
    Human50, AI50
  ],
  intermediate_steps: [...],
  tool_calls: [...],
}
```

非常大。

---

## 触发 SummarizationMiddleware 的那一刻

在 `before_model(state)`：

1. 读取完整的 messages
2. 调用模型生成摘要
3. **重写 state.messages**

变成：

```
state.messages = [
  SystemMessage("以下是之前 50 轮对话的摘要：......"),
  Human50,
  AI50
]
```

注意：

> 前 49 轮 **彻底消失**

不是被隐藏，是**真的从 state 里删除**。

---

## 然后 invoke 继续执行

模型基于这个“压缩后的 state”：

```
[摘要, 最近对话]
```

生成新的 AIMessage。

---

## invoke 结束 → checkpointer.save(state)

此时保存的 state 是：

```
state = {
  messages: [
    System: 摘要,
    Human50,
    AI50,
    Human51,
    AI51
  ],
  intermediate_steps: 最新轨迹,
}
```

这就是被持久化到：

* InMemorySaver（内存）
* 或 SqliteSaver（磁盘）

的数据。

---

## 关键点：checkpointer 并不知道发生了摘要

checkpointer 完全**无感知**。

它只是做一件事：

> “你给我什么 state，我就存什么 state”

也就是说：

> **SummarizationMiddleware 在“骗” checkpointer**

把压缩后的 state 当成“真实历史”。

---

## 下一次 invoke 时会发生什么？

```
checkpointer.load(thread_id)
```

读出来的是：

```
[摘要, 最近几条消息]
```

而不是完整历史。

这意味着：

> **历史在物理层面已经被不可逆地压缩**

这就是为什么它能支持**无限轮对话**。

---

## 对 checkpointer 的影响（非常关键）

SummarizationMiddleware 带来 3 个巨大影响：

### ① state 体积永久变小

SQLite 里的数据不会随着对话轮数线性增长。

### ② 恢复速度变快

下次加载 state 很轻量。

### ③ token 成本永久下降

因为历史已经被“结构性改写”。

---

## 保存到 checkpointer 的 state 具体包含什么？

在一次摘要后的保存，state 典型包含：

```
messages:
    System(摘要)
    最近若干 Human/AI 消息

intermediate_steps:
    本轮工具调用轨迹

next_action:
    状态机下一步信息

其他 LangGraph 内部字段
```

**绝对不再包含**早期逐条对话。

---

## 用一句非常精确的话总结

> SummarizationMiddleware 不是“帮你减少传给模型的内容”

而是：

> **帮你永久改变 checkpointer 里存储的历史结构**

这是很多人完全没意识到的一点。

---

## 为什么这在架构上非常高级？

因为：

> “记忆压缩”发生在 **state 层**，而不是 **prompt 层**

这是状态机架构才能做到的事情。

---

## 最终认知模型（非常重要）

以后你要这样理解：

```
checkpointer 里存的不是“真实历史”
而是“经过多次压缩后的历史记忆形态”
```

这就是：

> Agent 的**长期记忆演化过程**。
