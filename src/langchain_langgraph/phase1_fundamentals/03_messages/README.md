# 🧠 LangChain 1.0 消息类型与对话管理 — 核心知识总结

> 本质一句话：
> **大模型没有记忆，记忆 = 你每次传给它的 messages**

---

## 一、LangChain 中的三种消息类型

LangChain 底层只认三种角色：

| 类型            | 作用             | 对应 role     | 谁写的 |
| ------------- | -------------- | ----------- | --- |
| SystemMessage | 定义 AI 行为、规则、人设 | `system`    | 开发者 |
| HumanMessage  | 用户输入           | `user`      | 用户  |
| AIMessage     | AI 回复          | `assistant` | 模型  |

### 两种写法（推荐第二种）

#### ❌ 消息对象写法（啰嗦）

```python
SystemMessage(content="你是一名 Python 导师。")
HumanMessage(content="什么是 langchain")
```

#### ✅ 字典写法（强烈推荐）

```python
[
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."}
]
```

> LangChain 1.0 / OpenAI / Qwen / Claude / Gemini **全部统一这种格式**

---

## 二、最重要的认知：模型没有记忆

### ❗错误理解（99% 新手会犯）

```python
model.invoke("我叫张三")
model.invoke("我叫什么名字？")
```

AI：我不知道。

### ✅ 正确理解

```python
conversation = [
    {"role": "user", "content": "我叫张三"},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "我叫什么名字？"},
]
model.invoke(conversation)
```

> **模型不是记住了你，而是你把历史再次发给了模型**

---

## 三、对话历史管理 = LangChain 最核心能力

### 正确流程（必须背下来）

```text
用户输入
   ↓
加入 conversation
   ↓
调用 model.invoke(conversation)
   ↓
把 AI 回复加入 conversation
```

### 代码模板（黄金模板）

```python
conversation.append({"role": "user", "content": user_input})

response = model.invoke(conversation)

conversation.append({"role": "assistant", "content": response.content})
```

> 这 3 行代码 = 80% Agent / Chatbot / RAG 的底层原理

---

## 四、为什么 AI 会“失忆”

因为你用了：

```python
model.invoke("字符串提示词")
```

而不是：

```python
model.invoke(messages)
```

**字符串提示词无法携带历史消息。**

---

## 五、真正的难点：对话历史会越来越长（Token 爆炸）

长对话会导致：

* Token 费用飙升
* 响应变慢
* 上下文污染
* 模型注意力下降

### 核心思想：

> ❗不是保留所有历史
> ❗而是保留**有用的最近历史**

---

## 六、优化历史的黄金策略

### 必须永远保留

```text
SystemMessage（人设、规则）
```

### 只保留最近 N 轮对话

一轮 = user + assistant

```python
def keep_recent_messages(messages, max_pairs=3):
    system_msgs = [m for m in messages if m["role"] == "system"]
    conv_msgs = [m for m in messages if m["role"] != "system"]

    recent = conv_msgs[-max_pairs*2:]
    return system_msgs + recent
```

> 这是所有商业 AI 产品的标准做法

---

## 七、为什么示例 4 非常重要（面试级理解）

这是你第一次接触：

> **上下文窗口管理（Context Window Management）**

这也是：

* LangGraph
* Agent Memory
* SummarizationMiddleware
* trim_messages

存在的根本原因。

---

## 八、简易 ChatBot 的完整工作原理

```python
conversation = [{"role": "system", "content": "..."}]

while True:
    user_input = input()

    conversation.append({"role": "user", "content": user_input})

    response = model.invoke(conversation)

    conversation.append({"role": "assistant", "content": response.content})
```

AI “记住你” 的原因只有一个：

> 你一直在维护这个 `conversation` 列表。

---

## 九、本质理解（非常关键）

### ❗LangChain 不负责记忆

### ❗模型不负责记忆

### 👉 **你负责记忆**

LangChain 只是帮你：

* 组织 messages
* 管理历史
* 修剪历史
* 自动摘要历史（进阶）

---

## 十、本文件 5 个示例对应的真实能力

| 示例  | 教会你的能力  | 真实项目用途                |
| --- | ------- | --------------------- |
| 示例1 | 消息类型    | 所有 LLM 调用基础           |
| 示例2 | 手动管理历史  | Chatbot / Agent / RAG |
| 示例3 | 为什么会失忆  | 避免 90% 新手错误           |
| 示例4 | 修剪历史    | 商业级上下文管理              |
| 示例5 | 完整聊天机器人 | 最小可用 AI 应用            |

---

## 十一、一句话总结整个文件

> **LangChain 的对话能力，本质就是：维护一个 messages 列表**

没有它：

* Agent 不成立
* 记忆不存在
* 多轮对话是假的

---

## 十二、你以后看到这些概念时，要立刻联想到本文件

| 看到这个词           | 立刻想到             |
| --------------- | ---------------- |
| Memory          | messages 列表      |
| Context         | messages 列表      |
| Chat History    | messages 列表      |
| trim_messages   | 修剪 messages      |
| Summarization   | 压缩 messages      |
| LangGraph state | 更高级的 messages 管理 |

---

## ✅ 最终心法（背下来）

```text
模型没有记忆
记忆 = messages
对话能力 = 维护 messages
商业优化 = 修剪 messages
高级玩法 = 压缩 messages
```

---

这份笔记，等你学到：

* SummarizationMiddleware
* trim_messages
* LangGraph Memory

再回来看，你会**瞬间通透**。
