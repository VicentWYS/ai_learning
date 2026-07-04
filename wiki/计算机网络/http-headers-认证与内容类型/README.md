# HTTP Headers — Content-Type 与 Authorization

## 问题

当你向 LLM API 发送 POST 请求时，服务器需要知道两件事：
1. **你发的是什么格式**？—— 用 `Content-Type` 告诉服务器：这是 JSON
2. **你是谁/有没有权限**？—— 用 `Authorization` 出示你的身份凭证

```python
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
```

这两行看似简单，但它们是 HTTP 协议中最重要的两个请求头——缺任意一个，API 都会拒绝你。

## 两个 Header 的分工

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTP POST 请求                           │
├─────────────────────────────────────────────────────────────┤
│  Content-Type: application/json    ← "我发的数据是 JSON"    │
│  Authorization: Bearer sk-xxx...   ← "这是我的 API 令牌"    │
│                                                             │
│  {"model": "deepseek-v4", "messages": [...]}   ← 请求体     │
└─────────────────────────────────────────────────────────────┘
```

### Content-Type

| 值 | 含义 |
|---|---|
| `application/json` | 请求体是 JSON（LLM API 的标准格式） |
| `application/x-www-form-urlencoded` | HTML 表单默认格式 |
| `multipart/form-data` | 文件上传 |
| `text/plain` | 纯文本 |

### Authorization

| 方案 | 格式 | 安全性 |
|---|---|---|
| `Bearer {token}` | 直接出示令牌 | 依赖 HTTPS 加密传输 |
| `Basic {base64(user:pass)}` | 用户名密码 Base64 编码 | **明文等效**，仅 HTTPS 下可用 |
| `Digest` | 挑战-应答哈希 | 密码不传输，但已很少使用 |
| `AWS4-HMAC-SHA256` | 签名认证 | 密钥不传输，AWS 签名 V4 |

> **Bearer Token 为什么是主流**：简单、无状态、Token 可以独立签发和撤销。LLM API 几乎全部使用 Bearer Token——你的 `api_key` 就是 Token。

## 关键行为

- **缺少 `Content-Type`**：服务器可能把 JSON 当纯文本解析，返回 `400 Bad Request` 或解析失败
- **错误的 `Content-Type`**（如 `text/plain` 发 JSON）：行为取决于服务端，LLM API 通常返回 `400`
- **缺少 `Authorization`**：LLM API 返回 `401 Unauthorized`
- **错误的 API Key**：返回 `401` 或 `403 Forbidden`

## 要点

- `Content-Type: application/json` 和 `Authorization: Bearer {key}` 是调用任何 LLM API 的**最低必配**
- Bearer Token 的安全性**完全依赖 HTTPS**——确保你的 `base_url` 使用 `https://`
- 不要把 API Key 硬编码在代码里——用环境变量（`os.getenv()`）管理

## 环境自检

```python
import os
import json
import http.client
from urllib.parse import urlparse

# 构造请求
payload = json.dumps({"model": "test", "messages": []})
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('API_KEY', 'test-key')}"
}

# 打印 headers（脱敏后）
safe_headers = {k: (v[:15] + "***" if k == "Authorization" else v) for k, v in headers.items()}
print(safe_headers)
# → {'Content-Type': 'application/json', 'Authorization': 'Bearer sk-xxx***'}
```

---

## 代码演进史：从 RFC 到 LLM API

HTTP Headers 的演进是一个**从简陋到精密**的过程：

| 年代 | 里程碑 | 你代码里的体现 |
|------|--------|---------------|
| **1991** | HTTP/0.9：只有 `GET /path`，没有 Header，没有版本号 | — |
| **1996** | RFC 1945（HTTP/1.0）：引入 Header 概念，`Content-Type` 从 MIME（RFC 1341）迁移而来 | `Content-Type` |
| **1999** | RFC 2616（HTTP/1.1）+ RFC 2617（Basic/Digest Auth） | `Authorization` 头出现 |
| **2005** | JSON 开始流行，`application/json` MIME 类型正式注册（RFC 4627） | `application/json` |
| **2012** | RFC 6750：OAuth 2.0 Bearer Token 使用规范 | `Bearer {api_key}` |
| **2020+** | LLM API 时代：OpenAI 定义 `Authorization: Bearer sk-xxx` 成为事实标准 | 你看到的这行代码 |

> **为什么是 `Bearer` 而不是别的**：`Bearer` 在英文中是"持有者"的意思——谁持有这个 Token，谁就拥有对应的权限。这个名字来自 OAuth 2.0 工作组，他们刻意选了"Bearer"来强调 Token 的**不记名**特性：服务器不验证"你是谁"，只验证"Token 对不对"。

---

## 历史故事：邮递员的问题——MIME 如何从电子邮件走进了你的 HTTP Header

**1991 年，Nathaniel Borenstein 遇到了一个麻烦。**

Borenstein 是 Bellcore（贝尔通信研究所）的一名研究员。他正在做一件事：**让电子邮件能发送图片、音频、视频——而不仅仅是 ASCII 文本**。

当时（80 年代末到 90 年代初）的电子邮件系统有一个巨大的局限：**只能发送 7-bit 的 ASCII 英文文本**。你不能发一张照片，不能发一段录音，甚至不能发带有变音符号的法语字母 é。

Borenstein 和同事 Ned Freed 设计了一套方案来解决这个问题，他们把它叫做 **MIME**（Multipurpose Internet Mail Extensions，多用途互联网邮件扩展）。MIME 的核心思想可以用一句话概括：

> **在每个消息的开头，加一行标签，告诉接收方："我是什么格式"。**

这行标签的格式就是 `Content-Type: type/subtype`。比如：
- `Content-Type: text/plain` —— 我是纯文本
- `Content-Type: image/jpeg` —— 我是 JPEG 图片
- `Content-Type: audio/mpeg` —— 我是 MP3 音频

MIME 被由 **RFC 1341（1992年）** 和 **RFC 1342（1992年）** 正式标准化。

**然后，一个意外的事情发生了。**

**1993-1996 年间**，当 Tim Berners-Lee 和 HTTP 工作组在设计 HTTP/1.0 的时候，他们面临了一个完全相同的问题：

> 服务器发给浏览器的内容，格式多种多样——HTML 文件、图片、纯文本、二进制数据。浏览器怎么知道该用什么方式去渲染它？

答案几乎是现成的：**直接用 MIME 的 `Content-Type`**。HTTP/1.0（RFC 1945, 1996）直接把 MIME 的内容类型机制搬进了 HTTP Header——一字不改。

这就是为什么你代码里的 `Content-Type: application/json` 看起来和邮件里的 `Content-Type: image/jpeg` 是**同一种东西**——它们的祖宗都是 Borenstein 在 1991 年为电子邮件设计的 MIME。

**但故事还没完。JSON 的加入，是另一段传奇。**

2001 年，Douglas Crockford 发现了 JavaScript 对象字面量的潜力，创造了 JSON 格式。到 2005-2006 年，JSON 已经取代 XML 成为 Web API 的首选数据格式。但它的 MIME 类型是什么？社区开始了一场著名的"MIME 类型战争"。

2006 年，Crockford 向 IANA（互联网号码分配局）正式注册 `application/json`。这个 MIME 类型被 RFC 4627 确认。从此，REST API 的请求和响应有了统一的内容类型标签。

所以，你今天写下的这行代码：

```python
headers = {"Content-Type": "application/json"}
```

实际上是四段历史的交汇：

1. **1991**：Borenstein 的 MIME 解决了"邮件怎么发图片"的问题
2. **1996**：HTTP/1.0 把 MIME 搬进了 Web，成了 HTTP Header
3. **2006**：Crockford 的 JSON 拿到了自己的 MIME 类型 `application/json`
4. **2012**：RFC 6750 定义了 Bearer Token，解决了"API 怎么认证"的问题

而 `Bearer` 这个词——它在金融领域的意思是"不记名票据"（持有即拥有），被 OAuth 工作组借用来强调 Token 的特性：谁持有 Token，谁就拥有权限。

> Borenstein 后来在接受采访时说，MIME 最让他骄傲的不是技术设计，而是一个基本原则：**"Be conservative in what you send, liberal in what you accept."**（发送时要严格，接收时要宽松）。这句话后来被写进了 HTTP 规范，成为了互联网协议设计的黄金法则——**Postel 定律**。
>
> 你今天调用 LLM API 时，服务器严格检查你的 `Content-Type` 和 `Authorization`，这就是"发送时要严格"；而当你拼错一个小写字母 `bearer` 写成 `Bearer`（有些服务器大小写不敏感）时偶尔也能通过，这就是"接收时要宽松"。
