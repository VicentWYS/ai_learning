# OpenAI 接口规范

## 它是什么

**OpenAI 接口规范**不是一份官方标准文档，而是 OpenAI 在发布 ChatGPT API 时定义的一套 **HTTP RESTful API 约定**。由于 OpenAI 第一个把大模型 API 做到了"开发者友好"，这套规范迅速成为行业事实标准——国内外几乎所有模型厂商（DeepSeek、通义千问、Moonshot、Groq、Together AI……）都选择**兼容这套格式**。

核心只有一个端点：

```
POST https://api.openai.com/v1/chat/completions
```

你的代码只需修改 `base_url` 和 `api_key`，就能从调用 OpenAI 切换到调用 DeepSeek——无需修改请求体结构。

## 核心结构：一次请求的一生

```
┌─────────────────────────────────────────────────────────────────────┐
│  请求 (HTTP POST)                                                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ POST /v1/chat/completions                                    │    │
│  │ Content-Type: application/json                               │    │
│  │ Authorization: Bearer sk-xxxxxxxx                            │    │
│  │                                                              │    │
│  │ {                                                            │    │
│  │   "model": "gpt-4o",                                        │    │
│  │   "messages": [                                              │    │
│  │     {"role": "system", "content": "你是..."},                 │    │
│  │     {"role": "user",   "content": "你好"}                    │    │
│  │   ],                                                         │    │
│  │   "temperature": 0.8,                                        │    │
│  │   "max_tokens": 1000,                                        │    │
│  │   "stream": false                                            │    │
│  │ }                                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │                                      │
│                              ▼                                      │
│  响应 (HTTP 200)                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ {                                                            │    │
│  │   "id": "chatcmpl-xxx",                                      │    │
│  │   "object": "chat.completion",                               │    │
│  │   "created": 1718000000,                                     │    │
│  │   "model": "gpt-4o",                                        │    │
│  │   "choices": [                                               │    │
│  │     {                                                        │    │
│  │       "index": 0,                                            │    │
│  │       "message": {                                           │    │
│  │         "role": "assistant",                                 │    │
│  │         "content": "你好！有什么可以帮你的？"                   │    │
│  │       },                                                     │    │
│  │       "finish_reason": "stop"                                │    │
│  │     }                                                        │    │
│  │   ],                                                         │    │
│  │   "usage": {                                                 │    │
│  │     "prompt_tokens": 15,                                     │    │
│  │     "completion_tokens": 20,                                 │    │
│  │     "total_tokens": 35                                       │    │
│  │   }                                                          │    │
│  │ }                                                            │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

## 关键参数速查

| 参数 | 类型 | 必填 | 说明 |
|------|------|:---:|------|
| `model` | string | ✅ | 模型名称，如 `gpt-4o`、`deepseek-v4-flash` |
| `messages` | array | ✅ | 对话消息列表，每条包含 `role` + `content` |
| `temperature` | float | ❌ | 0~2，越高越随机（0 = 确定性强，适合代码；0.8 = 适合对话） |
| `max_tokens` | int | ❌ | 限制模型输出的最大 token 数 |
| `stream` | bool | ❌ | `true` 时返回 SSE 流式输出，逐字返回 |
| `top_p` | float | ❌ | 核采样阈值，与 temperature 二选一 |

**messages 中的 role：**

| role | 含义 | 示例 |
|------|------|------|
| `system` | 设定 AI 角色/行为规则 | "你是一个严谨的技术专家" |
| `user` | 用户输入的消息 | "什么是注意力机制？" |
| `assistant` | AI 此前的回复（用于多轮对话） | "注意力机制是…" |

## 两种调用模式

**模式 1：非流式（`stream: false`）— 一次性返回**

收到完整响应后一次解析。适合脚本、批处理。

**模式 2：流式（`stream: true`）— SSE 逐字推送**

响应以 Server-Sent Events (SSE) 格式逐 chunk 返回，每个 chunk 是一个 delta（增量）。适合聊天界面、实时交互。

```
data: {"choices":[{"delta":{"content":"你好"}}]}
data: {"choices":[{"delta":{"content":"！"}}]}
data: [DONE]
```

## 调用架构：SDK vs 原生 HTTP

```
┌──────────────────────┐
│      你的代码         │
│  ┌────────────────┐  │
│  │  openai SDK     │  │  ← 高层：对象化调用
│  │  (推荐)         │  │
│  └───────┬────────┘  │
│          │            │
│  ┌───────▼────────┐  │
│  │  http.client    │  │  ← 底层：原生 HTTP 调用
│  │  requests / httpx│ │
│  └───────┬────────┘  │
│          │            │
└──────────┼────────────┘
           ▼
    OpenAI API 服务端
```

**用 SDK（推荐）：**

```python
from openai import OpenAI

client = OpenAI(api_key="sk-xxx", base_url="https://api.deepseek.com")
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}],
)
print(response.choices[0].message.content)
```

**不用 SDK（原生 HTTP）：**

需要手工构造 JSON body、设置 Headers、解析 SSE 流。SDK 帮你处理了重试、超时、流式解析、错误分类等细节。

## 要点

- **行业标准**：几乎所有大模型厂商都兼容此格式，换模型 = 改 `base_url` + `api_key`
- **stateless**：API 不保存对话历史，多轮对话需要每次把历史上传
- **token 计费**：响应中的 `usage` 字段报告消耗——按 prompt + completion 分别计费
- **Content-Type: application/json**：请求体必须是 JSON，这是 API 的硬要求
- **Authorization: Bearer xxx**：认证方式固定，Bearer Token 放在请求头中
- **temperature=0 ≠ 完全确定性**：受浮点精度影响，相同 prompt 仍可能输出不同

---

## 代码演进历史

### OpenAI Python SDK 版本变迁

| 版本 | 时间 | 关键变化 |
|------|------|----------|
| **0.x** (openai) | 2020-2022 | 最初版本，`openai.ChatCompletion.create()`，全局配置 `openai.api_key` |
| **1.0.0** | 2023.11 | **破坏性更新**：引入 `OpenAI()` 客户端类，废弃全局配置。`openai.ChatCompletion.create()` → `client.chat.completions.create()` |
| **1.x** | 2023-2024 | 新增 `stream` 上下文管理器、自动重试、类型注解（TypedDict）支持 |
| **2.0.0** | 2025.01 | 移除旧的同步实现，底层完全切换为 `httpx`；正式支持 `responses` API |

**v0.x → v1.0 最核心的变化：**

```python
# v0.x — 全局配置（已废弃）
import openai
openai.api_key = "sk-xxx"
response = openai.ChatCompletion.create(model="gpt-4", messages=[...])

# v1.0+ — 客户端实例化
from openai import OpenAI
client = OpenAI(api_key="sk-xxx")
response = client.chat.completions.create(model="gpt-4", messages=[...])
```

这样改的原因：多客户端场景（多个 key、不同 base_url）在全局配置模式下会互相干扰——客户端实例天然隔离。

### `/v1/chat/completions` 端点演进

| 时间 | 里程碑 |
|------|--------|
| **2020.06** | GPT-3 API 发布（`/v1/completions`），只有文本补全，没有消息角色概念 |
| **2022.03** | `gpt-3.5-turbo` 发布，引入 `/v1/chat/completions`，`messages` 数组 + `role` 字段 |
| **2022.11** | ChatGPT 发布，Chat Completion API 成为主流 |
| **2023.07** | 新增 `function calling`（后改名为 `tools`）参数 |
| **2023.11** | 新增 `response_format: {"type": "json_object"}` JSON 模式 |
| **2024.05** | GPT-4o 发布，原生多模态（图片/音频直接放入 messages） |
| **2024.12** | `reasoning_effort` 参数用于 o1 系列推理模型 |

---

## 历史故事：一场 API 设计，终结了"百模大战"的碎片化

### 2022 年 11 月，全世界的开发者都在问同一个问题

ChatGPT 上线前，AI 开发者的世界是分裂的。每个模型——GPT-3、Jurassic、Claude、PaLM——各有各的 API，互不兼容。你给 GPT-3 写的代码，拿到 Jurassic 上要全部重写。**模型换不了，代码锁死了。**

开发者对这个"AI 界 VHS vs Betamax"烂局已经麻木了，觉得"反正每个模型都是黑盒子，API 不同是理所应当的"。

### 2022 年 3 月：不为 ChatGPT，只为一次重构

ChatGPT 在 2022 年 11 月引爆舆论，但它的 API 格式早在**同年 3 月**就已经上线——伴随 `gpt-3.5-turbo` 发布，OpenAI 推出了 `/v1/chat/completions`。

这个决定跟 ChatGPT 的产品团队关系不大，推动者是 **OpenAI 的 API 工程团队**。他们在 2021 年底做了一个关键判断：

> **"Completions API（纯文本续写）在对话场景下太难用了。开发者要自己拼 prompt 模板、手动管理对话轮次、在字符串里模拟角色切换——这太蠢了。我们需要给对话一个一等公民的抽象。"**

于是他们把"对话"这个概念标准化为一个 JSON 结构：

```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}
```

这个设计有三个关键决策：

1. **`messages` 是数组**，不是单条字符串——天然支持多轮对话
2. **`role` 字段区分说话者**——`system` / `user` / `assistant` 三元组覆盖所有对话语义
3. **无状态的 API**——服务器不保存历史，模型记忆完全由客户端通过 messages 数组管理

### "无心插柳"的行业标准

OpenAI 的 API 团队并没有刻意去"制定行业标准"——他们只是想解决自己平台的问题。但 ChatGPT 在 2022 年底的爆发改变了一切。

到 **2023 年 3 月**，ChatGPT 已经有 1 亿用户。开发者蜂拥而至，基于 OpenAI API 写了数万个开源项目。到 2023 年 6 月，"OpenAI 兼容"已经成为大模型产品的默认卖点——**不支持这套格式，开发者就不来用你的模型。**

DeepSeek、智谱 AI、百川、Moonshot……产品文档的第一行都是：**"兼容 OpenAI 接口格式，可以无缝迁移。"**

这带来了两个深远影响：

**第一：`base_url` 成了最强大的抽象。** 你不需要知道 DeepSeek 的服务器架构是什么样的，不需要学新的 SDK，不需要改请求格式——改一行 `base_url` 就够了。模型在 API 层面变得可替换。LangChain、Dify、LobeChat 这些中间件之所以能"一键切换模型"，靠的就是这套统一的接口规范。

**第二：厂商竞争的焦点从"格式锁定"变成了"模型质量"。** 以前厂商可以通过推出一套独家 API 格式来锁定生态（开发者迁移成本太高），OpenAI 接口成为标准后，这个策略失效了。DeepSeek 靠"价格 1/10"就能争夺 OpenAI 用户——因为迁移成本几乎为零。这倒逼所有厂商在**模型能力**和**价格**上竞争，而不是在格式上设壁垒。

### `/v1/completions` → `/v1/chat/completions`：一个 API 命名背后的范式转变

老一代的 GPT-3 API 只有 `/v1/completions`——"续写文本"语义。它的用法是：

```
Prompt: "把以下英文翻译成中文：\n\nHello World\n\n翻译结果："
```

开发者要靠拼 prompt 模板来"模拟"对话、翻译、总结等任务。**模型不知道你在跟它对话——它以为你在让它续写一段文本。**

`/v1/chat/completions` 把这个隐含的对话结构**显式化**了。`system` message 专门用于"指令层"（你希望 AI 扮演什么角色），`user` message 是"输入层"，`assistant` message 是"历史层"。这个三层的语义分离，实际上**重新定义了人机交互的 API 契约**。

今天当你写下 `messages = [{"role": "user", "content": "你好"}]` 时，你用的是 2022 年 3 月 OpenAI API 团队在设计会议上画在白板上的那个 JSON 结构。他们当时没想到这会成为行业标准——他们只是觉得"这样设计更好用"。

**而"更好用"——恰恰是制定任何标准的唯一正确出发点。**
