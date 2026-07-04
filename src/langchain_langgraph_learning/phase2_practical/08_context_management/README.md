# LangChain 1.0 — Context Management 知识总结

> 核心问题：**对话越来越长，如何不爆 token，又不丢重要信息？**

---

## 一、为什么必须做上下文管理？

### 不做处理时会发生什么？

随着对话轮数增加：

| 问题         | 本质原因               |
| ---------- | ------------------ |
| token 超限报错 | 每次都携带完整历史          |
| 成本飙升       | 历史越长，传输越多          |
| 内存增长       | checkpointer 不断存消息 |
| 延迟变大       | 模型输入越来越大           |

**LangChain 1.0 的核心思想：**

> 不再以“轮数”为标准，而是以 **token 数量** 为标准管理上下文。

---

## 二、LangChain 中对话是如何保存的？

```python
checkpointer=InMemorySaver()
```

这行代码的含义：

> LangGraph 会自动保存 **完整历史 messages**

所以默认行为是：

```
Human → AI → Human → AI → Human → AI → ...
全部永久保存
```

这就是问题的来源。

---

## 三、LangChain 1.0 提供的三种官方解决方案

| 方案                      | 是否自动 | 是否保留历史信息 | 推荐度   | 场景     |
| ----------------------- | ---- | -------- | ----- | ------ |
| 不处理                     | ❌    | ✅        | ⭐     | 极短对话   |
| SummarizationMiddleware | ✅    | ✅（通过摘要）  | ⭐⭐⭐⭐⭐ | 长对话/生产 |
| trim_messages           | ❌    | ❌        | ⭐⭐⭐   | 精确控制   |
| 滑动窗口                    | ❌    | 部分       | ⭐⭐⭐   | 自定义规则  |

---

## 四、SummarizationMiddleware（最重要）

### 本质

> **当 token 超过阈值时，把旧对话压缩成“长期记忆摘要”**

不是删除历史，而是：

```
旧历史 → 摘要 → system memory
```

模型后续看到的是：

```
System: [长期记忆摘要]
Human: 最近消息
AI: 最近消息
```

---

### 使用方式

```python
summarization_middleware = SummarizationMiddleware(
    model=summary_model,
    max_tokens_before_summary=1000,
    summary_prompt="..."
)

agent = create_agent(
    ...
    middleware=[summarization_middleware],
)
```

**只需要加 middleware，一切自动完成。**

---

### 参数深度理解

#### 1️⃣ model（用于摘要）

可以用**便宜模型**，因为只是做压缩。

#### 2️⃣ max_tokens_before_summary

触发摘要的阈值。

经验值：

| 模型上下文 | 推荐阈值  |
| ----- | ----- |
| 4k    | 3000  |
| 8k    | 6000  |
| 32k   | 24000 |

#### 3️⃣ summary_prompt（极其关键）

决定了：

> **模型以后还能不能“记住人”**

优秀的 prompt 必须要求保留：

* 用户背景
* 用户目标
* 偏好
* 已完成任务
* 重要结论

这是**长期记忆设计的核心**。

---

## 五、trim_messages（手术刀方案）

### 本质

> 直接截断 messages，只保留最后 N token

```python
trim_messages(
    messages,
    max_tokens=200,
    strategy="last",
)
```

### 特点

| 优点         | 缺点     |
| ---------- | ------ |
| 精确控制 token | 历史彻底丢失 |
| 无额外成本      | 容易断上下文 |

适合：

> 只关心**最近几轮**的场景（如工具调用、函数式对话）

---

## 六、为什么 LangChain 不再讲“轮数”？

因为：

```
1 轮话 = 20 token
1 轮话 = 2000 token
```

**轮数没有意义，token 才有意义。**

LangChain 1.0 全部围绕：

> token budget 管理

---

## 七、真实运行流程（非常关键）

当你使用：

```python
checkpointer + middleware
```

真实流程是：

```
用户发消息
   ↓
历史 messages 读取
   ↓
如果 token 超限
   ↓
SummarizationMiddleware 触发
   ↓
旧消息 → 摘要 → 替换为 system memory
   ↓
模型看到：摘要 + 新消息
```

这是**自动发生的**，你不用写任何逻辑。

---

## 八、为什么客服机器人是典型应用场景？

客服场景特点：

* 对话极长
* 必须记住订单号、用户信息
* 不能爆 token
* 必须保留长期记忆

SummarizationMiddleware 完美匹配。

---

## 九、你这套代码的架构意义（非常重要）

你实际上搭建的是：

> **具备长期记忆能力的 Agent 架构**

这已经是：

**生产级 Agent 的标准写法**

```
Agent
 ├─ checkpointer（记忆）
 ├─ middleware（自动摘要）
 ├─ tools
 └─ system_prompt
```

---

## 十、策略选择指南（面试级理解）

| 对话类型   | 方案                      |
| ------ | ----------------------- |
| <10 轮  | 不处理                     |
| 中长对话   | SummarizationMiddleware |
| 只要最近几轮 | trim_messages           |
| 强规则场景  | 滑动窗口                    |

---

## 十一、最核心的一句话总结

> **LangChain 1.0 的上下文管理 = 用摘要替代历史，而不是删除历史**

---

## 十二、进阶认知（很多人不知道）

SummarizationMiddleware 其实实现的是：

> **Memory Compression（记忆压缩）**

这是未来 Agent 架构的核心能力。

和传统：

> Sliding Window（滑动窗口）

是完全不同的思想层级。

---

## 十三、生产环境最佳实践

```python
summary_model = 便宜模型
主模型 = 强模型

max_tokens_before_summary = 上下文窗口 * 0.75
summary_prompt = 专门设计
```

这就是标准答案。

---

## 结语（一句话记住）

> **trim 是截断记忆，summary 是压缩记忆。**

生产环境，永远优先用 **SummarizationMiddleware**。
