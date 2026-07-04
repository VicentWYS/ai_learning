# urlparse — URL 解析

## 问题

当你拿到一个 URL 字符串（如 `https://api.deepseek.com/v1/chat/completions`），你需要从中提取**主机名**、**端口**、**路径**等信息来建立 HTTP 连接。手动用字符串切割（`split("/")`）不仅繁琐，还容易出错——URL 的格式远比你想象的复杂。

## 解决方案：`urllib.parse.urlparse()`

Python 标准库内置的 `urlparse()` 将一个 URL 字符串解析为结构化的**命名元组**，包含 6 个核心组件：

```
┌──────────────────────────────────────────────────────────────┐
│  urlparse("https://api.deepseek.com:443/v1/chat?q=hi#top")  │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
    scheme ──────── "https"
    netloc ──────── "api.deepseek.com:443"
    hostname ────── "api.deepseek.com"    ← 纯主机名，不含端口
    port ────────── 443                    ← 端口号（int 或 None）
    path ────────── "/v1/chat"
    query ───────── "q=hi"
    fragment ────── "top"
```

## 快速上手

```python
from urllib.parse import urlparse

parsed = urlparse("https://api.deepseek.com/v1/chat/completions")

print(parsed.scheme)    # "https"
print(parsed.hostname)  # "api.deepseek.com"
print(parsed.port)      # None  ← 未显式指定端口时为 None
print(parsed.path)      # "/v1/chat/completions"
```

## 核心 API

| 属性 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `scheme` | `str` | 协议（强制小写） | `"https"` |
| `netloc` | `str` | 网络位置（host:port） | `"api.deepseek.com:443"` |
| `hostname` | `str` | 纯主机名（不含端口） | `"api.deepseek.com"` |
| `port` | `int` 或 `None` | 端口号 | `443` 或 `None` |
| `path` | `str` | 路径部分 | `"/v1/chat/completions"` |
| `query` | `str` | 查询参数（不含 `?`） | `"q=hello&page=1"` |
| `fragment` | `str` | 锚点（不含 `#`） | `"section-2"` |

## 关键行为

| 场景 | `hostname` | `port` |
|------|-----------|--------|
| `https://api.deepseek.com` | `"api.deepseek.com"` | `None` |
| `https://api.deepseek.com:443` | `"api.deepseek.com"` | `443` |
| `https://127.0.0.1:8000` | `"127.0.0.1"` | `8000` |
| `https://[::1]:8000` | `"::1"`（IPv6 裸地址） | `8000` |

> **`port` 为 `None` 的含义**：URL 中未显式指定端口——`http.client.HTTPSConnection(host, port=None)` 会使用该协议的默认端口（HTTPS → 443，HTTP → 80）。

## 要点

- `parsed.hostname` 返回**纯主机名**，不含端口号——适合直接传给 `http.client.HTTPSConnection()`
- `parsed.port` 返回 `int` 或 `None`——为 `None` 时连接库会自动使用协议默认端口
- `urlparse` 是标准库 `urllib.parse` 的一部分，**无需额外安装任何包**
- 与手写字符串切割相比，`urlparse` 正确处理了 IPv6 地址、端口、认证信息等边缘情况

## 环境自检

```python
from urllib.parse import urlparse

test_urls = [
    "https://api.deepseek.com/v1/chat/completions",
    "http://localhost:8000/api",
    "https://127.0.0.1:443",
    "https://[::1]:8080/path",
]

for url in test_urls:
    p = urlparse(url)
    print(f"{url}")
    print(f"  → scheme={p.scheme}, hostname={p.hostname}, port={p.port}, path={p.path}")
```

---

## 真实历史小故事：一个斜杠，差点毁了整个 Web

这个故事要从 **1989 年**讲起。

那一年，CERN（欧洲核子研究中心）的一个英国软件工程师 **Tim Berners-Lee** 写了一篇内部备忘录，标题是 *"Information Management: A Proposal"*。他的老板在封面上写了一句后来成为传奇的批注：**"Vague, but exciting."**（模糊，但令人兴奋。）

这份备忘录描述了一个超文本系统——文档之间通过"链接"互相引用，用户点击链接就能跳转到另一篇文档。但要实现这个想法，Tim 需要一个关键的东西：**一种统一的方式来定位网络上的任何资源**。

当时 CERN 内部已经有几十种不同的文档定位方式：文件路径（`/usr/local/doc/paper.tex`）、FTP 地址（`ftp://ftp.cern.ch/pub/`）、Gopher 菜单、WAIS 查询……每一种都有自己独特的格式，互不兼容。如果超文本系统要工作，必须有一种**通用标识符**能描述所有这些资源的地址。

Tim 在 1990 年到 1994 年间逐步演化出了三个概念：

1. **URI**（Uniform Resource Identifier）——统一资源标识符，最广义的概念
2. **URL**（Uniform Resource Locator）——统一资源定位符，告诉你"东西在哪里"
3. **URN**（Uniform Resource Name）——统一资源名称，告诉你"东西叫什么"

我们今天在浏览器地址栏里敲的 `https://api.deepseek.com/v1/chat`，就是一个 URL——它是 URI 的一个子集。

**1994 年**，Tim Berners-Lee 和同事在 **RFC 1738** 中正式定义了 URL 的标准格式：

```
scheme://host:port/path?query#fragment
```

这个格式看似简单，但它蕴含了一个深刻的设计智慧：**用一个统一的语法，容纳所有协议的寻址需求**——无论是 HTTP、FTP、Gopher、News、Mailto，都是这六部分的排列组合。

但故事真正精彩的部分在 **2000 年代的安全危机**。

当 Web 应用开始处理用户输入的 URL 时，一个不起眼的问题出现了：**URL 解析歧义（URL Parsing Confusion）**。

2008 年，安全研究员发现了一个攻击模式：有些 HTTP 库对 `http://evil.com#@trusted.com` 的解析结果不同——一个库认为 host 是 `evil.com`，另一个认为是 `trusted.com`。攻击者利用这种不一致性，构造了一个看起来指向安全地址、实际指向恶意服务器的 URL。

这个问题催生了 **URL 解析的标准化运动**。WHATWG（Web 超文本应用技术工作组）在 2010 年代发布了 **URL Living Standard**，用**精确到每一个字符的算法**定义了 URL 应该如何被解析——包括如何处理非法字符、如何 normalize、如何处理边缘情况。这份标准的测试套件包含了**超过 500 个 URL 解析测试用例**。

Python 的 `urlparse` 模块（最早出现在 Python 1.6, 2000 年）也在持续跟进这些标准。你看到的 `parsed.hostname` 返回纯主机名、`parsed.port` 正确识别 IPv6 裸地址——这些看似理所当然的行为，背后是二十多年的标准演进和安全攻防。

一个历史注脚：Tim Berners-Lee 后来在采访中承认，URL 格式中**双斜杠 `//` 其实是不必要的**——`https:api.deepseek.com/v1/chat` 在语法上同样可以工作。他加 `//` 的唯一理由是**模仿 Apollo 计算机网络的文件路径语法**（Apollo Domain 系统用 `//node/path` 表示远程文件）。Tim 说这是他做过的"唯一一个多余的、不必要的设计决定"。

> *"If I had known that people would be typing URLs by hand, I would have left out the double slash."*
> — Tim Berners-Lee, 2009

所以，你今天写下 `urlparse(base_url)` 的时候，调用的是：
- 1990 年，一个 CERN 工程师的"模糊但令人兴奋"的超文本构想
- 1994 年，RFC 1738 定义的 `scheme://host:port/path` 标准格式
- 2000-2010 年代，无数次安全漏洞倒逼出的标准化 URL 解析器
- 以及 Tim Berners-Lee 至今还在后悔的那两个斜杠

你看到的每一个正常工作的 URL，都是三十五年互联网演进史的切片。
