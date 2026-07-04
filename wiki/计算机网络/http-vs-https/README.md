# HTTP vs HTTPS — 功能、联系与区别

## 问题

你在调用 LLM API 时，`base_url` 总是以 `https://` 开头。如果误写成 `http://`，请求会被拒绝或重定向。你隐约知道 HTTPS 比 HTTP "更安全"，但它们之间到底差了什么？为什么几乎所有 API 都强制 HTTPS？

## 一句话总结

**HTTPS = HTTP + TLS**。HTTP 负责传输超文本，TLS 负责加密信道。两者的应用层语义完全相同（同样的 Method、Header、Status Code），区别仅在**传输层的安全性**。

## 核心对比

```
┌─────────────────────────────────────────────────────────────────┐
│                        HTTP （明文传输）                          │
│  Client ──── plaintext ────→ Server                             │
│  任何人抓包都能看到：{"api_key": "sk-1234..."}                    │
├─────────────────────────────────────────────────────────────────┤
│                        HTTPS （加密传输）                         │
│  Client ──── TLS 加密 ────→ Server                              │
│  抓包只能看到：a3f7c9...（加密后的乱码）                          │
└─────────────────────────────────────────────────────────────────┘
```

| 维度 | HTTP | HTTPS |
|------|------|-------|
| 全称 | Hypertext Transfer Protocol | HTTP over TLS/SSL |
| 默认端口 | 80 | 443 |
| 传输内容 | 明文 | TLS 加密 |
| 身份验证 | 无 | CA 证书验证服务器身份 |
| 数据完整性 | 无保障 | TLS 校验和防篡改 |
| 性能 | 更快（无加密开销） | 略慢（TLS 握手） |
| SEO | 搜索引擎降权 | 排名优先（Google 2014起） |
| URL 前缀 | `http://` | `https://` |

## 工作流程

**HTTP**：TCP 三次握手 → 发送明文请求 → 接收明文响应。

**HTTPS**：多了 TLS 握手层：

```
Client                                  Server
  │─── TCP SYN ───────────────────────────→│
  │←── TCP SYN-ACK ────────────────────────│
  │─── TCP ACK ───────────────────────────→│  ← TCP 三次握手（同 HTTP）
  │                                          │
  │─── ClientHello（支持的加密套件）────────→│
  │←── ServerHello + 证书（含公钥）─────────│
  │─── 验证证书 ←── CA 根证书链 ────────────│  ← TLS 握手（HTTPS 特有）
  │─── 生成对称密钥，用公钥加密后发送 ──────→│
  │←── 确认加密信道建立 ────────────────────│
  │                                          │
  │←══════ 加密数据传输 ════════════════════→│  ← 应用数据
```

## 要点

- **HTTPS 不改变 HTTP 语义**：Method、Header、Status Code、URL 结构在 HTTP 和 HTTPS 下完全一致
- **加密的是传输信道，不是数据本身**：`https://` 保护数据在网络上不被窃听，但服务器端收到的仍是明文 JSON
- **证书验证身份，不验证内容**：CA 证书确认你连接的是 `api.deepseek.com` 本人，但不检查你发的 JSON 合不合法
- **所有 LLM API 强制 HTTPS** 不是出于性能考虑，而是因为 API Key 在 HTTP 下等于**明文传输密码**
- **Python 中 `http.client` 需手动选择**：`HTTPConnection` vs `HTTPSConnection`——选错协议会连接失败

## 环境自检

```python
import http.client

# 对比：HTTP 请求（不加密）vs HTTPS 请求（加密）
# 注意：大部分网站会强制将 HTTP 重定向到 HTTPS

# 1. HTTP → 会被 301 重定向到 HTTPS
conn = http.client.HTTPConnection("httpbin.org", timeout=5)
conn.request("GET", "/get")
resp = conn.getresponse()
print(f"HTTP:  {resp.status} {resp.reason}")  # 通常 301 Moved Permanently
conn.close()

# 2. HTTPS → 正常响应
conn = http.client.HTTPSConnection("httpbin.org", timeout=5)
conn.request("GET", "/get")
resp = conn.getresponse()
print(f"HTTPS: {resp.status} {resp.reason}")  # 200 OK
conn.close()
```

---

## 代码演进史：从明文书信到加密信封

HTTP 和 HTTPS 的演进是一部**互联网安全意识的觉醒史**：

| 年代 | 里程碑 | 你的代码里对应的东西 |
|------|--------|---------------------|
| **1991** | HTTP/0.9：只有 `GET /path`，无 Header，无版本号 | — |
| **1994** | Netscape 发明 SSL 1.0（从未公开发布，因安全漏洞被废弃） | — |
| **1995** | SSL 2.0 随 Netscape Navigator 2.0 发布 → 第一个可用加密方案 | `ssl` 模块的祖先 |
| **1996** | HTTP/1.0（RFC 1945）+ SSL 3.0（完全重写，修复 2.0 多个漏洞） | `HTTPSConnection` 出现 |
| **1999** | HTTP/1.1（RFC 2616）+ TLS 1.0（RFC 2246，SSL 3.0 的标准化升级） | `ssl.PROTOCOL_TLSv1` |
| **2008** | TLS 1.2（RFC 5246）：引入 AES-GCM、SHA-256，淘汰 MD5/SHA-1 | `ssl.PROTOCOL_TLSv1_2` |
| **2014** | Google 宣布 HTTPS 为搜索排名信号 → "HTTPS Everywhere" 运动 | — |
| **2015** | HTTP/2（RFC 7540）：多路复用、头部压缩，主流浏览器**仅支持 HTTP/2 over TLS** | — |
| **2018** | TLS 1.3（RFC 8446）：握手从 2-RTT 减到 1-RTT，移除所有不安全算法 | `ssl.PROTOCOL_TLSv1_3` |
| **2022** | HTTP/3（RFC 9114）：基于 QUIC，**内建加密，无明文模式** | `--enable-quic` |

> **Python 中的体现**：Python 3.6+ 的 `ssl` 模块默认使用系统最安全的 TLS 版本。你在 `https://` URL 上调用 `HTTPSConnection` 时，底层自动协商 TLS 1.2 或 1.3——不需要你手动选择协议版本。

---

## 历史故事：一个在线卖书网站，逼出了整个互联网的加密层

**1994 年夏天，Netscape 公司内部爆发了一场争吵。**

当时 Netscape Navigator 刚发布不到一年，已经占据了 80% 的浏览器市场。但公司创始人 Jim Clark 和工程师团队面临一个棘手的问题：**如何让人们在互联网上安全地输入信用卡号？**

这不是一个理论问题。1994 年 8 月，第一个在线比萨订购服务 PizzaNet 上线；同年，一个叫 Amazon.com 的网站开始尝试在网上卖书。电子商务的雏形出现了——但只要数据是明文传输，没有任何一个理性的人会在网上输入信用卡号。

Netscape 的安全工程师 **Taher Elgamal**（一位埃及裔密码学家）被指定负责解决这个问题。他的答案是：**在 TCP 层和 HTTP 层之间，插入一个加密层**。

Elgamal 带领的小组在 1994 年底完成了第一版 SSL（Secure Sockets Layer）协议。但 SSL 1.0 从未公开发布——内部安全审查发现了严重的密钥管理漏洞，直接废掉了整个版本。

**1995 年 2 月，SSL 2.0 随 Netscape Navigator 2.0 正式发布。** 这是人类历史上第一次，普通用户可以在浏览器地址栏看到一个锁形图标，点击后能看到"此连接已加密"。

但 SSL 2.0 的设计仍然有多个安全缺陷，其中最严重的一个是：**中间人可以降级攻击，迫使连接使用最弱的加密算法**。这促使 Netscape 找到了外部的密码学家来彻底重构协议。1996 年，SSL 3.0 发布——这是第一个真正安全的版本，也为后来的 TLS 1.0 奠定了基础。

在这之后，协议的控制权从 Netscape 转移到了 IETF（互联网工程任务组），SSL 被重新命名为 TLS（Transport Layer Security）。这个改名有一个政治背景：**Netscape 拥有 SSL 的商标，IETF 希望创建一个开放的、不被任何公司控制的标准化协议**。

**从 1995 年到 2014 年，HTTPS 的使用范围发生了一个有趣的转变：**

- **1995-2005**：HTTPS 只用于"需要保护的东西"——银行网站、购物结账、登录页面。
- **2010**：Firefox 插件 "HTTPS Everywhere"（由 EFF 开发）掀起了"默认加密"运动。
- **2014**：Google 宣布 HTTPS 将成为搜索排名信号——一夜之间，全世界的网站开始迁移。
- **2017**：Chrome 开始在所有 HTTP 页面上显示"不安全"警告。

到 2024 年，**超过 95% 的 Web 流量通过 HTTPS 传输**。"例外"变成了"默认"。

> **对 LLM 开发者的启示**：你今天调用的每个 LLM API（OpenAI、DeepSeek、Claude）都强制 HTTPS——这不仅是因为 API Key 需要保护，更是因为 2010 年代的安全文化已经将"明文传输 API 令牌"视为一种工程失职。你代码里的 `https://` 前缀，是三十年安全演进的结果——从一个在线卖书网站的信用卡输入框，到全球 95% 的 Web 流量加密。
>
> Elgamal 在 2015 年的一次采访中说："SSL 的设计初衷就是为了卖书。我们当时完全没想到，它后来会保护全世界的电子邮件、即时通讯、API 调用、甚至政治异见者的通信。"
