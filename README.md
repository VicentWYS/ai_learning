# 快速开始本项目

## 项目简介
本项目为AI学习项目，包含与AI相关的各类知识模块，并配有对应示例代码和说明文档。


## 快速开始
### 环境要求

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) 包管理器（推荐）

### 1. 安装 uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 克隆项目

克隆到本地：
```bash
git clone <repo-url>
cd langchain_learning_uv
```

### 3. 安装依赖

`uv sync` 会自动读取 `.python-version` 创建/使用对应版本的 Python 虚拟环境，并根据 `pyproject.toml` 和 `uv.lock` 安装所有依赖：

```bash
uv sync
```

激活项目：
```bash
.venv\Scripts\activate
```

### 4. 配置 API Keys
复制环境变量模板

```bash
cp .env.example .env
```

编辑 .env，填入你的 API Key
```
# QWEN_API_KEY: https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key
# DEEPSEEK_API_KEY: https://platform.deepseek.com/api_keys
```

> `.env` 已被 `.gitignore` 忽略，不会被提交到仓库。

### 5. 运行

```bash
# 运行基本调用示例
uv run python src/1_basic/基本调用.py

# 或直接运行入口
uv run python main.py
```
