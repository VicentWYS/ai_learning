# LangChain 1.0 - Simple Agent 知识点总结

## 1. 核心概念

### 1.1 Agent

* **定义**：Agent 是一个智能实体，能够根据用户输入自动决定是否调用工具，并生成回答。
* **创建方式（1.0 API）**：`create_agent(model, tools, system_prompt, checkpointer=None)`

  * `model`：聊天模型实例
  * `tools`：工具列表（如天气查询、计算器、网页搜索）
  * `system_prompt`：系统提示词，用于控制 Agent 的行为和语气
  * `checkpointer`：可选，多轮对话记忆存储（如 `MemorySaver`）

### 1.2 工具（Tool）

* **作用**：Agent 可以调用工具完成特定任务。
* **特点**：

  * 每个工具带有 docstring 描述功能
  * Agent 会自动判断是否需要使用工具
* **示例工具**：

  * `get_weather`：天气查询
  * `calculator`：计算器
  * `web_search`：网页搜索

### 1.3 多轮对话

* **关键点**：

  * 使用 `MemorySaver` 保持对话历史
  * `thread_id` 区分不同用户或会话
  * Agent 自动记忆上下文，无需手动传递历史消息

---

## 2. 创建 Agent 示例

### 示例1：最简单 Agent

```python
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="你是一名智能助手，可以查询天气信息。",
)
```

* **特点**：

  * 只配置一个工具
  * Agent 自动判断是否使用工具
  * 普通问题直接回答，无需工具

---

### 示例2：多工具 Agent

```python
agent = create_agent(
    model=model,
    tools=[get_weather, calculator, web_search],
    system_prompt="你是一名智能助手。",
)
```

* **特点**：

  * 根据问题自动选择合适工具
  * 工具 docstring 帮助 Agent 理解用途
  * 可处理多种类型问题（如天气查询、计算、搜索）

---

### 示例3：自定义 Agent 行为（系统提示）

```python
system_messages = """你是一个友好的智能助手。
特点：
  - 回答简介明了
  - 使用工具前会先说明
  - 结果用表格或列表清晰展示"""
agent = create_agent(
    model=model,
    tools=[get_weather, calculator, web_search],
    system_prompt=system_messages,
)
```

* **system_prompt** 可是字符串或 `SystemMessage` 对象
* 控制 Agent 输出风格、语气和流程

---

### 示例4：Agent 执行流程详解

* **执行循环**：

  1. 用户提问 → `HumanMessage`
  2. AI 判断是否调用工具 → `AIMessage`（含 `tool_calls`）
  3. 执行工具 → `ToolMessage`（返回结果）
  4. AI 根据结果生成最终回答 → `AIMessage`

* **消息类型**：

  * `HumanMessage`：用户输入
  * `AIMessage`：模型生成
  * `ToolMessage`：工具返回结果

---

### 示例5：多轮对话 Agent（MemorySaver）

```python
memory = MemorySaver()
agent = create_agent(
    model=model,
    tools=[calculator],
    system_prompt="你是一个智能助手。",
    checkpointer=memory,
)
```

* **多轮对话特点**：

  * `thread_id` 用于区分不同对话
  * Agent 自动记住上下文
  * 可连续提问，例如：

    * 第1轮：`10 + 5 = ?`
    * 第2轮：`再乘以 3 呢？` → 会基于上一轮记忆计算

---

## 3. 使用建议与注意点

1. **工具配置**

   * 工具 docstring 很重要，Agent 根据 docstring 理解用途
   * 工具数量过多可能影响性能，推荐核心必需工具

2. **系统提示**

   * `system_prompt` 用于：

     * 控制语气（友好/简洁/正式）
     * 指定回答格式（列表/表格/文本）
     * 指定工作流程（先说明再使用工具等）

3. **多轮对话管理**

   * 使用 `MemorySaver` 或自定义 checkpointer
   * `thread_id` 区分不同用户或会话
   * 可以实现长期上下文记忆

4. **调试执行流程**

   * 通过查看消息历史（`response["messages"]`）理解 Agent 决策过程
   * 检查 `tool_calls` 来确认工具是否被调用

---

## 4. 总结

* **LangChain 1.0 重点更新**：

  * 使用 `create_agent` 替代旧版 `create_react_agent`
  * 支持多工具自动选择
  * 支持自定义系统提示
  * 支持多轮对话记忆（MemorySaver）
* **Agent 核心能力**：

  * 自动判断是否使用工具
  * 基于工具执行操作并生成答案
  * 可保持上下文，实现连续对话
