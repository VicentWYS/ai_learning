# 📦 LangChain 1.0 自定义工具（@tool）知识总结

> 核心一句话：
> **@tool = 把普通 Python 函数，变成 LLM 可理解、可调用的能力模块**

👉 **@tool 装饰器 = LLM 能力扩展的入口**

---

## 🧠 一、@tool 本质做了什么？

当你写：

```python
@tool
def get_current_time() -> str:
    """获取当前时间"""
```

LangChain 会自动：

| 提取内容 | 来源        | 用途            |
| ---- | --------- | ------------- |
| 工具名称 | 函数名       | LLM 调用时使用     |
| 工具描述 | docstring | LLM 判断是否该用此工具 |
| 参数结构 | 类型注解      | 生成 JSON 参数    |
| 返回值  | 函数返回      | 作为工具结果喂给 LLM  |

👉 **函数 → Tool 对象（拥有 `.invoke()`）**

---

## ✍️ 二、docstring 为什么极其重要？

> ❗LLM 不看你的函数代码，只看 docstring

标准格式：

```python
@tool
def my_tool(param1: str) -> str:
    """
    工具的简短描述

    参数:
        param1: 参数说明

    返回:
        返回值说明
    """
```

LLM 通过它判断：

* 什么时候该用这个工具
* 如何构造参数 JSON
* 这个工具能解决什么问题

---

## 🧩 三、参数类型注解的作用

```python
def calculator(operation: str, a: int, b: int) -> str:
```

类型注解会被转成：

```json
{
  "operation": "string",
  "a": "integer",
  "b": "integer"
}
```

👉 LLM 根据这个 **自动生成调用参数**

支持类型：

* `str`
* `int`
* `float`
* `bool`
* `Optional[type]`

---

## 🛠 四、工具如何测试？

被 `@tool` 修饰后：

```python
result = tool.invoke({...})
```

这一步非常关键：

> **开发工具时，永远先 .invoke() 测试，而不是先给 Agent 用**

---

## 🧮 五、多参数工具示例（计算器）

```python
calculator.invoke({
    "operation": "add",
    "a": 10,
    "b": 5
})
```

说明：

* LLM 会自己构造这个 JSON
* 前提是你 docstring 和类型写得足够清晰

---

## ⚙️ 六、可选参数设计（非常重要）

```python
def web_search(query: str, num_results: Optional[int] = 3) -> str:
```

LLM 行为：

* 用户没说 → 用默认值
* 用户说了 → 覆盖默认值

👉 **这是工具设计的高级技巧**

---

## 🔗 七、工具绑定到模型（让 LLM 知道它可以用工具）

```python
model_with_tools = model.bind_tools([get_weather, calculator])
```

此时 LLM 获得能力：

> “我可以决定是否调用这些工具”

检查是否触发工具：

```python
if response.tool_calls:
```

---

## 🧱 八、工具开发黄金原则（非常重要）

### ✅ 1. 清晰 docstring（最重要）

### ✅ 2. 明确类型注解

### ✅ 3. 永远返回 `str`

> 复杂数据 → JSON 字符串

### ✅ 4. 工具内部要做异常处理

```python
try:
    ...
except Exception as e:
    return f"错误：{e}"
```

### ✅ 5. 一个工具只做一件事（单一职责）

错误示例：

```python
def search_and_calculate_and_save():
```

正确做法：拆成多个 tool。

---

## 🧪 九、开发顺序（专业流程）

1. 写普通函数
2. 加 `@tool`
3. 补全 docstring
4. `.invoke()` 单测
5. bind 到 model
6. 再交给 Agent

---

## 🪟 十、Windows 终端 UTF-8 处理的意义

这段代码：

```python
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
```

解决：

> Windows 默认 GBK，LLM 输出 UTF-8 → 中文乱码

---

## 🧠 十一、这一节的真正核心思想

> **LangChain 的 Agent 本质 = LLM + 一堆 @tool**

不是：

> Agent 很复杂

而是：

> 工具设计决定 Agent 上限

---

## 🧭 十二、你需要形成的认知模型

```
Python函数
   ↓ @tool
LangChain Tool
   ↓ bind_tools
LLM 获得“外部能力”
   ↓ Agent
LLM 自动调用工具完成复杂任务
```

---

## 📝 Checklist（写工具前必看）

* [ ] 函数功能是否单一？
* [ ] docstring 是否清晰描述“何时用”？
* [ ] 参数是否有类型注解？
* [ ] 是否有默认参数？
* [ ] 是否只返回字符串？
* [ ] 是否可单独 `.invoke()` 测试？

---

## 🚀 一句话总结

> **你不是在写函数，你是在给 LLM 安装“外挂能力模块”**
