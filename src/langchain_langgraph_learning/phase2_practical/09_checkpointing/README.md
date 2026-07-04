# LangChain 1.0 总结 —— Checkpointing（检查点持久化）

> 核心思想：
> **LangGraph = Agent 的大脑**
> **Checkpointer = Agent 的长期记忆存储器**

---

## 一、什么是 Checkpointing？

Checkpointing 是 **LangGraph 的核心机制**，用于：

> **自动保存 + 自动恢复 Agent 的完整对话状态**

不需要你手动管理历史消息。

在 `create_agent` 中只要传入：

```python
checkpointer=SqliteSaver(...)
```

LangGraph 会自动完成：

| 时机       | LangGraph 自动行为                              |
| -------- | ------------------------------------------- |
| invoke 前 | `checkpointer.get(thread_id)` 读取历史消息        |
| invoke 中 | 自动拼接：历史消息 + 新消息                             |
| invoke 后 | `checkpointer.put(thread_id, state)` 保存完整状态 |

你**完全不需要写 memory 代码**。

---

## 二、Checkpointer 工作流程（必须理解）

```text
用户发消息
    ↓
LangGraph 从数据库读取该 thread_id 的历史
    ↓
拼接成完整 messages
    ↓
Agent 推理 / 调用工具
    ↓
LangGraph 将新的完整 state 写回数据库
```

**重点：保存的不是消息，而是整个 Agent 状态（state）**

---

## 三、InMemorySaver vs SqliteSaver

| 特性    | InMemorySaver | SqliteSaver |
| ----- | ------------- | ----------- |
| 是否持久化 | ❌ 否           | ✅ 是         |
| 程序重启后 | 丢失            | 保留          |
| 跨进程   | 不支持           | 支持          |
| 生产环境  | 不适合           | 标准方案        |
| 存储位置  | 内存            | SQLite 文件   |
| 多用户会话 | 不安全           | 完全支持        |

> InMemorySaver 只用于**教学、调试**

---

## 四、thread_id 是会话的关键

```python
config = {"configurable": {"thread_id": "user_123"}}
```

LangGraph 用它来区分：

* 不同用户
* 不同会话
* 不同上下文

**thread_id = 用户会话主键**

---

## 五、SqliteSaver 正确使用方式（高频考点）

### ✅ 推荐写法

```python
with SqliteSaver.from_conn_string("checkpoints.sqlite") as checkpointer:
    agent = create_agent(
        model=model,
        checkpointer=checkpointer,
    )
```

### ⚠️ 注意

* **不要写**：`sqlite:///checkpoints.sqlite`
* 直接传：`"checkpoints.sqlite"`
* 必须用 `with` 管理连接

---

## 六、跨重启持久化的本质

即使你：

* 关闭程序
* 新建 agent
* 新建 checkpointer

只要：

```python
thread_id 相同
db_path 相同
```

Agent 就能**完整恢复历史**。

---

## 七、多用户会话管理（真实生产场景）

```python
config_a = {"configurable": {"thread_id": "user_alice"}}
config_b = {"configurable": {"thread_id": "user_bob"}}
```

同一个数据库文件：

```
multi_user.sqlite
```

可以同时存储**所有用户的会话**，完全隔离。

---

## 八、工具调用也会被持久化（非常重要）

这一点很多人不知道：

> **工具调用结果也被写入 state！**

效果是：

* 第一次查订单 → 调用工具
* 第二次问“什么时候到” → **不再调用工具**
* 因为历史里已经有工具返回结果

这就是**真正的智能记忆**。

---

## 九、典型应用场景（生产级）

### 1️⃣ 客服系统

客户上午问过订单号，下午再问：

> 不需要重复提供订单号

### 2️⃣ AI 助手长期记忆

记住：

* 用户姓名
* 偏好
* 历史问题

### 3️⃣ 多轮复杂 Agent 任务

Agent 能记住：

* 上一步推理
* 工具结果
* 决策路径

---

## 十、SqliteSaver 参数与最佳实践

| 场景   | 写法                       |
| ---- | ------------------------ |
| 开发   | `"checkpoints.sqlite"`   |
| 生产   | 绝对路径                     |
| 单元测试 | `":memory:"`             |
| 高级用法 | `sqlite3.connect()` 手动传入 |

### 最佳实践

* ✅ 始终使用 `with`
* ✅ 定期备份 sqlite 文件
* ✅ 使用绝对路径用于生产
* ❌ 不要加 `sqlite:///`

---

## 十一、为什么说这是 LangChain 1.0 的“王炸”能力？

以前（Memory 时代）你需要：

* 手动保存历史
* 手动拼接消息
* 手动控制长度
* 手动存数据库

现在：

> **一行 checkpointer = 生产级记忆系统**

这就是 LangGraph 的设计哲学。

---

## 十二、一句话理解

> **Checkpointer = 自动状态持久化的大脑快照系统**

不是 memory。

是 **Agent State Persistence**。

---

## 十三、最小生产模板（必须会写）

```python
with SqliteSaver.from_conn_string("prod.sqlite") as checkpointer:
    agent = create_agent(
        model=model,
        tools=[...],
        system_prompt="...",
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": user_id}}

    agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
    )
```

这就是：

> **生产级多轮 Agent 的标准写法**

---

## 十四、核心认知总结（面试级）

* Checkpointer 属于 **LangGraph**，不是 LangChain Memory
* 保存的是 **state**，不是 message
* thread_id 是会话主键
* SqliteSaver 支持跨进程、跨重启
* 工具调用历史也被保存
* 这是构建 AI 客服 / AI 助手 / Agent 系统的基础设施

---

## 最终理解（非常关键）

> **LangChain 负责调用模型**
> **LangGraph 负责管理状态**
> **Checkpointer 负责持久化状态**

三者缺一不可。
