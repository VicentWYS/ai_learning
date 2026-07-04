# 📘 LangChain 1.0 基础知识总结 —— 第一个 LLM 调用

> 本文对应学习代码：LangChain 1.0 第一次 LLM 调用完整示例
> 目标：理解 **LangChain 如何统一管理不同厂商模型的调用**

---

## 🧠 一句话理解 LangChain 1.0

> **LangChain 1.0 不再关心“你是什么模型”，只关心“你是否兼容 OpenAI 协议”。**

所有模型（Qwen / Groq / OpenAI / Claude）都通过同一个入口：

```python
init_chat_model()
```

---

## 🔑 第一步：环境变量与鉴权（生产级必做）

```python
load_dotenv()
QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")
```

### 为什么必须提前校验？

防止三类**极难排查的错误**：

| 错误来源        | 现象             | 排查难度 |
| ----------- | -------------- | ---- |
| .env 未加载    | api_key 为 None | 很高   |
| 忘记替换模板 key  | 鉴权失败           | 很高   |
| base_url 配错 | 模型初始化报错        | 很高   |

✅ **最佳实践：在模型初始化前就 raise**

---

## 🏭 第二步：LangChain 统一模型工厂

```python
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)
```

### 🚨 关键认知（非常重要）

| 认知                        | 含义                    |
| ------------------------- | --------------------- |
| Qwen 不是 OpenAI 模型         | 但它**伪装成 OpenAI 协议**   |
| LangChain 不看模型厂商          | 只看协议                  |
| `model_provider="openai"` | 表示走 OpenAI SDK 协议     |
| `base_url`                | 指向 Qwen 的 OpenAI 兼容端点 |

> **LangChain 1.x 的核心设计哲学：协议抽象，而不是厂商抽象**

---

## 🚀 示例1：最简单的调用方式

```python
response = model.invoke("你好！请用一句话介绍什么是人工智能")
```

### 特点

* 直接传字符串
* 适合单轮对话
* 最简单的 LLM 调用形式

---

## 💬 示例2：使用 Message 构建对话（重要）

```python
messages = [
    SystemMessage(content="你是 Python 助手"),
    HumanMessage(content="什么是装饰器？"),
]
response = model.invoke(messages)
```

### 三种消息类型

| 类型            | 作用           |
| ------------- | ------------ |
| SystemMessage | 设定 AI 人设     |
| HumanMessage  | 用户输入         |
| AIMessage     | AI 回复（可加入历史） |

### 多轮对话本质

```python
messages.append(response)
messages.append(HumanMessage(content="请给示例"))
```

> **对话记忆 = 手动维护 messages 列表**

---

## 🧾 示例3：推荐的字典消息格式（🔥推荐）

```python
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
]
```

### 为什么推荐？

* 与 OpenAI API 格式完全一致
* 更轻量
* 更适合工程化
* 方便与 Agent / LangGraph 对接

---

## 🎛 示例4：模型参数对输出的影响

| 参数               | 作用     | 场景        |
| ---------------- | ------ | --------- |
| temperature=0.0  | 极度稳定   | 数据抽取 / 判断 |
| temperature=1.0  | 平衡     | 日常对话      |
| temperature=1.5+ | 高创造性   | 写作 / 创意   |
| max_tokens       | 限制输出长度 | 防止废话      |

> **你在做 Prompt 工程时，这一节非常关键**

---

## 📦 示例5：理解 invoke 的返回值（极重要）

```python
response = model.invoke(...)
```

返回的是：

```python
AIMessage
```

### 关键字段

| 字段                         | 含义           |
| -------------------------- | ------------ |
| response.content           | 模型文本         |
| response.response_metadata | token / 模型信息 |
| response.id                | 消息ID         |
| response.additional_kwargs | 扩展参数         |

### Token 统计（做成本优化必看）

```python
usage = response.response_metadata["token_usage"]
```

---

## 🛡 示例6：生产级错误处理

必须捕获：

```python
try:
    model.invoke(...)
except ValueError:
except ConnectionError:
except Exception:
```

> 真实项目中：**80% 的问题来自鉴权和网络**

---

## 🔄 示例7：一键切换不同模型（LangChain 最大优势）

```python
models_to_test = [
    "groq:llama-3.3-70b-versatile",
    "groq:mixtral-8x7b-32768",
]
```

LangChain 的真正威力：

> **只改模型名，不改代码**

---

## 🧠 本文件真正教会你的 8 个核心认知

1. LangChain 通过 `init_chat_model` 统一所有模型
2. LangChain 只关心协议，不关心厂商
3. Qwen 必须走 OpenAI-compatible endpoint
4. `invoke` 可以接收字符串 / Message / dict
5. 对话记忆的本质是维护 messages
6. 推荐使用 dict message 格式
7. temperature 决定输出风格
8. `invoke` 返回的是 AIMessage，不是字符串

---

## 🗺 LangChain LLM 调用完整流程图

```
.env → 校验 → init_chat_model → invoke → AIMessage → 读取 content
```

多轮对话：

```
messages 列表 ← AIMessage 追加 ← 再次 invoke
```

---

## ✅ 最佳实践模板（可直接复用）

```python
model = init_chat_model(...)

messages = [
    {"role": "system", "content": "你是..."},
    {"role": "user", "content": "..."}
]

response = model.invoke(messages)
print(response.content)
```

---

## 🎯 你需要记住的不是代码，而是这句话

> **LangChain 1.0 = OpenAI 协议 + init_chat_model + invoke + messages**
