# 快速开始本项目

## 项目简介
本项目为AI学习项目，包含与AI相关的各类知识模块，并配有对应示例代码和说明文档。


## 快速开始
### 环境要求

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) 包管理器（推荐）

### 开发工具
- 推荐使用 [VS Code](https://code.visualstudio.com/) 作为开发工具。

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

---

## 前端项目 (Vue3)

### 环境要求

- [Node.js](https://nodejs.org/) `^22.18.0` 或 `>=24.12.0`
- npm（随 Node.js 一起安装）

### IDE 配置

推荐安装 [Vue - Official (Volar)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) VS Code 插件，提供 `.vue` 文件的语法高亮、类型检查和组件提示。

### 1. 进入前端项目

```bash
cd 项目
```

### 2. 安装依赖

```bash
npm install
```

### 3. 启动开发服务器

```bash
npm run dev
```

启动后浏览器访问终端输出的本地地址（默认 `http://localhost:5173`），即可查看 Vue 练习页面。

关闭服务：`q + Enter`

### 4. 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录，可部署至任意静态服务器。

### 5. 预览生产构建

```bash
npm run preview
```

在本地预览构建结果，确认无误后再部署。

### 6. 类型检查

```bash
npm run type-check
```

对项目进行 TypeScript + Vue 类型检查，确保类型正确。
