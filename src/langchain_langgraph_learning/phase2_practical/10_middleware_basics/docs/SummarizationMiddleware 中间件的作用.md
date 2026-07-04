# 问题
请介绍 SummarizationMiddleware 这个中间件是如何发挥作用的？


很好，这一步非常关键。

当你理解了：

> **Agent = 带 state 的状态机**
> **Middleware = 可以干预 state 生命周期**

再看 `SummarizationMiddleware`，你会突然发现：

> 它根本不是“做摘要”这么简单，
> 它是在**主动改写 Agent 的 state 结构**。

这就是它强大的地方。

---

## 先给结论（一句话）

> **SummarizationMiddleware 的本质：在 state 过大之前，主动“压缩 state”**

不是压缩输出，
不是压缩 messages，
而是：

> **压缩整个 Agent 的运行现场（state）**

---

## 没有它会发生什么？

随着多轮对话：

```
state.messages 越来越长
token 越来越多
模型越来越慢
费用越来越高
甚至超过上下文限制
```

因为：

> Agent 每次 invoke 都会把完整 state 交给模型

---

## SummarizationMiddleware 在干嘛？

它工作在这个关键位置：

```
加载旧 state
   ↓
【SummarizationMiddleware 触发】
   ↓
把很长的历史 messages → 摘要 summary
   ↓
修改 state
   ↓
再交给模型
```

注意这个顺序非常重要：

> **先改 state，再喂给模型**

---

## 它到底改了 state 的什么？

原始 state：

```
messages = [
  Human: ...
  AI: ...
  Tool: ...
  Human: ...
  AI: ...
  ... 很长很长
]
```

被改成：

```
messages = [
  System: "以下是之前对话的摘要：......",
  Human: 最近一次提问,
]
```

也就是说：

> **它把“历史”变成了“记忆”**

这是一种**state 结构重写**。

---

## Middleware 是怎么做到的？

你已经知道 Middleware 可以：

> 修改 state

`SummarizationMiddleware` 正是在：

```
before_model(state)
```

阶段做了：

```python
if len(state.messages) > 阈值:
    summary = 调用模型做摘要
    state.messages = [summary_message, last_user_message]
```

然后模型看到的就是“压缩后”的 state。

---

## 关键理解：它不是减少对话，而是重构对话

这点非常反直觉。

不是：

> 删掉旧消息

而是：

> 把旧消息“变形”为一条高信息密度的 System Message

模型依然**知道历史**，但 token 极少。

---

## 为什么它必须是 Middleware，而不是普通函数？

因为它必须卡在这个位置：

> **state 刚加载，还没进模型**

只有 Middleware 能精确插在这里。

普通代码做不到。

---

## 加入它之后，整个 invoke 流程变成：

```
① checkpointer 读取完整历史 state
② SummarizationMiddleware 判断是否过长
③ 若过长 → 调模型生成摘要 → 重写 state.messages
④ 模型基于“压缩后的 state”推理
⑤ 保存新的 state（已经被压缩过）
```

注意第⑤步：

> 保存的是**压缩后的 state**

所以对话会**越来越轻**，而不是越来越重。

---

## 这就是 LangGraph 设计的精妙之处

因为有：

* state
* checkpointer
* middleware

才可能实现：

> **自动对话压缩机制**

在 0.x 时代，这是根本做不到的。

---

## 一句话理解 SummarizationMiddleware 的真实作用

> 它是 Agent 的**自动长期记忆压缩器**

让 Agent 具备：

* 长对话能力
* 低 token 消耗
* 可无限轮对话
* 可生产部署

---

## 和 thread_id / SqliteSaver 的配合

效果更恐怖：

即使：

* 重启程序
* 跨进程
* 对话上万轮

state 依然**很小**，因为被不断摘要过。

这就是：

> SqliteSaver + SummarizationMiddleware = 生产级长对话 Agent 标配

---

## 最终你要形成的认知模型

以后看到它，不要想：

> “哦，这是个摘要中间件”

而要想：

> **这是一个在状态机层面做“记忆压缩”的组件**。

它改的不是输出。

它改的是：

> **Agent 的大脑结构（state）**。
