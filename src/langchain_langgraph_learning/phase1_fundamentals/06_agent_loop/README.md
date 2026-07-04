# LangChain 1.0 - Agent 执行循环（ReAct 模式）知识点总结

## 1. ReAct 执行循环概念

* ReAct 循环：**Reason → Act → Observe → 循环**
* 核心流程：

  1. **Reason（推理）**：AI 分析用户输入，决定是否调用工具。
  2. **Act（行动）**：调用工具或生成回答。
  3. **Observe（观察）**：获取工具结果或观察环境。
* 循环直到生成最终答案。

---

## 2. Agent 执行流程

* **问题 → 工具调用 → 结果 → 最终答案**
* 所有中间步骤都被记录在 **messages** 列表中。
* 主要消息类型：

  * `HumanMessage` → 用户输入
  * `AIMessage` → AI 输出（可能包含 tool_calls 或最终答案）
  * `ToolMessage` → 工具执行结果
  * `SystemMessage` → 系统指令（通过 system_prompt 设置）

---

## 3. 消息流转与历史记录

* **完整对话历史**存储在 `response["messages"]` 中。
* **每条消息**可能包含：

  * `content`：文本内容
  * `tool_calls`：工具调用信息（name + args）
  * `name`：工具名（ToolMessage）
* 最后一条消息通常是 **最终答案**。

---

## 4. 流式输出（Streaming）

* 使用 `agent.stream()` 可逐步获取 Graph State，适合长时间运行任务。
* `chunk` 是字典，结构类似：

  ```python
  {
      'model': {'messages': [AIMessage(...) ]},
      'tools': {'messages': [ToolMessage(...)]}
  }
  ```
* 处理方法：

  ```python
  for chunk in agent.stream(input_messages):
      for node, state in chunk.items():
          msg = state["messages"][-1]
          # 查看 tool_calls 或 content
  ```
* 优点：

  * 可实时观察工具调用
  * 查看中间状态
  * 适合复杂、多步骤任务

---

## 5. 多步骤任务执行

* Agent 可连续调用多个工具，每一步结果会影响下一步。
* 示例：

  1. 先计算 `10 + 20` → 使用 calculator
  2. 再用结果乘以 3 → 继续使用 calculator
* 可统计工具调用次数：

  ```python
  tool_calls_count = sum(len(msg.tool_calls) for msg in response["messages"] if hasattr(msg, "tool_calls"))
  ```

---

## 6. Graph State 与节点

* **Graph State**：流式输出的内部状态，包含模型和工具节点。
* 每个节点 (`node`) 对应一个处理单元：

  * `model` → AIMessage
  * `tools` → ToolMessage
* 可用于调试、查看中间步骤。

---

## 7. 消息类型详解

| 消息类型          | 作用                | 示例内容                              |
| ------------- | ----------------- | --------------------------------- |
| HumanMessage  | 用户输入              | "上海天气如何？"                         |
| AIMessage     | AI 输出，可能包含工具调用或答案 | 工具调用：get_weather，参数：{'city':'上海'} |
| ToolMessage   | 工具执行结果            | "多云，温度18°C"                       |
| SystemMessage | 系统指令              | system_prompt 内容                  |

* **AIMessage** 的两种情况：

  1. **调用工具** → 包含 `tool_calls`
  2. **最终回答** → 直接包含 `content`

---

## 8. 创建 Agent

* 使用 `create_agent()` 初始化 Agent：

```python
agent = create_agent(
    model=model,
    tools=[calculator, get_weather],
    system_prompt="你是一名智能助手。"
)
```

* `model` → chat 模型
* `tools` → 可调用工具列表
* `system_prompt` → 系统提示/角色设定

---

## 9. 使用场景总结

1. **单步骤问题** → 简单工具调用（示例1）
2. **流式观察任务** → 实时查看中间状态（示例2、示例4）
3. **多步骤任务** → 连续调用工具并生成最终答案（示例3）
4. **消息分析与调试** → 理解每条消息类型及其作用（示例5）

---

## 10. 关键技巧

* **实时调试**：用 `agent.stream()` 可观察每一步输出。
* **完整历史追踪**：遍历 `response["messages"]`，便于统计工具调用次数和调试逻辑。
* **消息类型判断**：通过 `msg.__class__.__name__` 判断消息类型，处理不同逻辑。
* **工具调用信息**：

  ```python
  if hasattr(msg, "tool_calls") and msg.tool_calls:
      print(msg.tool_calls[0]["name"], msg.tool_calls[0]["args"])
  ```

---

这份总结覆盖了 **Agent 执行循环、消息类型、流式输出、工具调用、多步骤任务** 的核心知识点，方便你快速回顾和调试 LangChain 1.0 相关代码。
