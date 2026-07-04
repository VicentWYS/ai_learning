# python-dotenv 环境变量管理

## 问题

在开发 AI 应用时，你需要调用大模型 API——这意味着代码中需要一个 **API Key**。如果把密钥直接写在代码里：

```python
# ❌ 危险的写法
api_key = "sk-1234567890abcdef"  # 这是你的真实密钥
```

你会立即面临三个问题：

| 问题 | 后果 |
|------|------|
| **密钥泄露到 Git** | 推送代码时密钥被上传到公开仓库，任何人都能看到 |
| **多环境切换困难** | 开发/测试/生产环境的密钥不同，每次切换都要改代码 |
| **团队协作冲突** | 同事用他自己的密钥，但代码里写的是你的——每次提交都产生冲突 |

## 解决方案：`.env` 文件 + `load_dotenv()`

`python-dotenv` 是 Python 生态中最流行的环境变量管理库，它做一件简单的事：**读取 `.env` 文件，将其中的键值对注入到 `os.environ`**。

```
┌──────────────┐     load_dotenv()     ┌──────────────┐     os.getenv()    ┌──────────────┐
│   .env 文件   │ ──────────────────→ │  os.environ   │ ────────────────→ │  你的代码     │
│              │                      │  (进程环境变量) │                    │              │
│ KEY=VALUE    │                      └──────────────┘                    │ api_key      │
└──────────────┘                                                          └──────────────┘
```

### 快速上手三步

**1. 安装**

```bash
pip install python-dotenv
```

**2. 创建 `.env` 文件**（项目根目录）

```bash
# .env — 不要提交到 Git！
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

**3. 代码中加载**

```python
from dotenv import load_dotenv
import os

load_dotenv()                              # 读取 .env → 注入 os.environ
api_key = os.getenv("DEEPSEEK_API_KEY")    # 从环境变量读取
```

## 核心 API

| API | 用途 | 修改 os.environ? |
|-----|------|:---:|
| `load_dotenv()` | 加载 `.env` 到 `os.environ` | ✅ 是 |
| `load_dotenv(".env.dev")` | 加载指定文件 | ✅ 是 |
| `dotenv_values(".env")` | 读取 `.env` 返回 dict，不注入环境 | ❌ 否 |
| `find_dotenv()` | 自动向上查找最近的 `.env` 文件 | — |
| `os.getenv("KEY", "默认值")` | 安全读取，不存在时返回默认值 | — |

## `os.getenv()` vs `os.environ["KEY"]` vs `os.environ.get()`

```python
# 推荐：不存在时返回 None，不会报错
api_key = os.getenv("DEEPSEEK_API_KEY")

# 不推荐：KEY 不存在时抛出 KeyError
api_key = os.environ["DEEPSEEK_API_KEY"]

# 也可以：字典方法，效果与 os.getenv() 几乎一致
api_key = os.environ.get("DEEPSEEK_API_KEY")
```

## 要点

- `.env` 文件**必须加入 `.gitignore`**——这是防止密钥泄露的最后一道防线
- 在仓库中提供 `.env.example` 模板，标明需要哪些变量（值为占位符）
- `.env` 文件中**不要加引号**，不要加 `export` 前缀——它是键值对，不是 shell 脚本
- `load_dotenv()` 不会覆盖已存在的系统环境变量——系统变量优先级更高
- 生产环境建议用**系统环境变量**或 **Secret Manager**（如 AWS Secrets Manager），而非 `.env` 文件
- 这源自 **12-Factor App** 方法论（2011 年）的第三条：**配置与代码严格分离**

## 为什么是环境变量而不是配置文件？

| 方案 | 密钥安全 | 多环境切换 | 与 Docker/K8s 兼容 |
|------|:---:|:---:|:---:|
| 硬编码在代码里 | ❌ | ❌ | ❌ |
| JSON/YAML 配置文件 | ⚠️ 容易误提交 | ✅ | ⚠️ |
| **环境变量 (.env)** | ✅ .gitignore 防护 | ✅ | ✅ 原生支持 |
| Secret Manager | ✅ 最佳 | ✅ | ✅ |

## 环境自检

```python
import os
from dotenv import load_dotenv, find_dotenv

# 1. 找到 .env 文件位置
env_path = find_dotenv()
print(f".env 路径: {env_path or '未找到'}")

# 2. 加载并检查
load_dotenv()
for key in ["DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"]:
    val = os.getenv(key)
    if val:
        masked = val[:6] + "****" if len(val) > 10 else "***"
        print(f"  {key:<22} = {masked}")
    else:
        print(f"  {key:<22} = ❌ 未设置")
```

---

## 真实历史小故事：一次 GitHub 搜索，改变了整个行业的配置管理方式

这个故事要从 **2011 年**讲起。

那一年，一个叫 **Adam Wiggins** 的程序员在 Heroku（当时最火的 PaaS 平台）工作。他和团队每天都在重复处理同一个问题：用户把数据库密码、AWS 密钥、API Token 硬编码在代码里，然后跑来问"为什么我的应用在 Heroku 上跑不起来？"

原因很简单——你本地的配置和 Heroku 的配置不一样。数据库地址不同，端口不同，密钥不同。你把代码 push 到 Heroku 之后，代码里写的还是 `localhost:5432`，但 Heroku 的数据库在完全不同的地址上。

Adam 坐下来，和 Heroku 的同事们总结了一套原则，写成了 **[The Twelve-Factor App](https://12factor.net/)**（十二要素应用）——12 条构建 SaaS 应用的黄金法则。其中第三条写道：

> **"配置应与代码严格分离。配置应存储在环境变量中。"**
> 
> — III. Config, The Twelve-Factor App (2011)

这个思想像野火一样传播开来。到 2014 年，主流 Web 框架（Rails、Django、Express）都在文档中推荐环境变量模式。但实施起来有一个痛点：**开发时怎么方便地设置环境变量？** 你当然可以在终端里 `export`，但每次打开新终端都要重新敲一遍——繁琐且容易遗漏。

于是衍生出了各种"开发环境变量管理器"：Ruby 有 `dotenv` gem（2012 年由 Brandon Keepers 创建），Node.js 有 `dotenv` npm 包（2013 年），Python 有 `python-dotenv`（2014 年由 Saurabh Kumar 从 Ruby 版移植）。它们的核心理念完全一致：

> **一个`.env`文件，一行一个键值对，一行代码加载，不提交到版本控制。**

这套方案之所以能成为行业标准，还有一个**惨痛的推动力**——密钥泄露事故。

**2014 年**，一个安全研究员做了一个实验：他在 GitHub 上搜索 `"api_key"` 关键词，结果令人震惊——仅仅几分钟就找到了**数千个包含有效 AWS 密钥的公开仓库**。这些密钥可以用来启动 EC2 实例、读取 S3 存储桶，甚至删除整个基础设施。

同年，Uber 的一名实习生把包含生产环境数据库密码的配置文件推送到了公开的 GitHub 仓库，导致 **5 万名司机的个人信息泄露**。Uber 为此支付了 1.48 亿美元的和解金。

**2019 年**，安全公司 North Carolina State University 发表了一项研究：他们扫描 GitHub 发现，**每小时有数千个新的 API 密钥和密码被意外上传**。其中大部分来自**配置文件硬编码**——如果这些开发者用了 `.env` + `.gitignore`，这些泄露根本不会发生。

这些事故不断提醒整个行业：**密钥管理的底线不是"加密"或"权限控制"，而是"密钥不要出现在代码仓库里"。**

到 **2020 年代**，`.env` 模式已经成为**所有编程语言的通用惯例**：Python 有 `python-dotenv`，Node.js 有 `dotenv`，Go 有 `godotenv`，Rust 有 `dotenvy`……无论你用什么语言，打开任何一个开源 AI 项目，你都会在根目录看到 `load_dotenv()` 和 `.env.example`。

所以，你今天写下的这行 `load_dotenv()`，背后是：
- 2011 年，Heroku 工程师总结出"配置与代码分离"原则
- 2012-2014 年，Ruby / Node / Python 社区各自实现了 `.env` 文件加载器
- 2014 年起，GitHub 上大量密钥泄露事故倒逼行业采用 `.gitignore` + `.env`
- 到今天，这已经不是为了"高级"或"最佳实践"——它只是**正确的、唯一的写法**

你看到的每一个 `.env` 文件，都是一次行业共识的胜利：**让密钥待在该待的地方，远离代码仓库。**
