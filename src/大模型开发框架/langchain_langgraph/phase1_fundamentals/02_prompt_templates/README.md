# LangChain 1.0 提示词模板（Prompt Templates）知识总结

> Prompt 在 LangChain 中**不是字符串**，而是**一等公民对象**

---

## 一、为什么需要 PromptTemplate？（设计思想）

### ❌ 字符串拼接的问题

```python
prompt = f"你是一个{difficulty}导师，解释{topic}"
```

问题：

* 不可复用
* 不可维护
* 容易漏变量
* 难测试
* 和业务逻辑强耦合

---

### ✅ PromptTemplate 的本质

```python
template = PromptTemplate.from_template(
    "你是一个{difficulty}导师，解释{topic}"
)
```

PromptTemplate =

> **Prompt 的“类定义”**

数据和模板分离：

| 模板  | 数据  |
| --- | --- |
| 固定  | 变化  |
| 可复用 | 可替换 |

---

## 二、PromptTemplate（纯文本模板）

适用场景：

> 单条提示词（非聊天）

### 创建方式

#### 方式1（推荐）

```python
PromptTemplate.from_template("翻译为{language}: {text}")
```

自动识别变量。

---

#### 方式2（严格模式）

```python
PromptTemplate(
    input_variables=["language", "text"],
    template="翻译为{language}: {text}"
)
```

手动声明变量，更安全。

---

#### 方式3：直接 invoke

```python
prompt = template.invoke({...})
model.invoke(prompt)
```

**invoke 会直接返回可用的 PromptValue**

---

## 三、ChatPromptTemplate（聊天模板，核心）

> 这是 LangChain Prompt 系统最重要的类

用于构造：

```
system
user
assistant
```

多角色消息。

---

### 推荐写法（元组）

```python
ChatPromptTemplate.from_messages([
    ("system", "你是{role}"),
    ("user", "{task}")
])
```

---

### 格式化后得到

```python
messages = template.format_messages(...)
```

返回：

```
[SystemMessage, HumanMessage, ...]
```

可以直接喂给模型：

```python
model.invoke(messages)
```

---

## 四、多轮对话模板（核心理解）

你这段代码非常关键：

```python
[
 ("system", "..."),
 ("user", "{question1}"),
 ("assistant", "{answer1}"),
 ("user", "{question2}")
]
```

这揭示一个重要思想：

> **对话历史，本质上也是 Prompt 的一部分**

LangChain 不“记忆”对话
而是**你把历史显式写进 Prompt 模板**

---

## 五、MessagePromptTemplate（高级组件化）

拆解 ChatPromptTemplate：

```python
SystemMessagePromptTemplate
HumanMessagePromptTemplate
AIMessagePromptTemplate
```

用于：

> **构建可组合的 Prompt 组件**

适合复杂系统 / Agent / 框架开发。

---

## 六、Partial Variables（极其重要）

```python
partial_template = template.partial(role="科技作者")
```

作用：

> **固化一部分变量，生成模板变体**

场景：

* 系统角色固定
* 用户群体固定
* 只让用户输入 task

这是**企业级 Prompt 设计必备技巧**。

---

## 七、Prompt + Model 的 LCEL 链式调用（未来主流）

```python
chain = template | model
chain.invoke({...})
```

这不是语法糖，这是 LangChain 未来架构核心：

> 所有组件都可以用 `|` 串起来

Prompt → Model → Parser → Tool → Memory

---

## 八、核心类之间的关系图

```
PromptTemplate              (单文本)
        ↓
ChatPromptTemplate          (多消息)
        ↓
MessagePromptTemplate       (组件化)
        ↓
Partial Variables           (模板变体)
        ↓
LCEL |                      (链式系统)
```

---

## 九、什么时候用什么？

| 场景    | 使用                      |   |
| ----- | ----------------------- | - |
| 单句提示词 | PromptTemplate          |   |
| 聊天机器人 | ChatPromptTemplate      |   |
| 多轮对话  | ChatPromptTemplate + 历史 |   |
| 复杂系统  | MessagePromptTemplate   |   |
| 固定角色  | partial                 |   |
| 工程化链路 | LCEL `                  | ` |

---

## 十、最重要的认知升级（非常关键）

在 LangChain 里：

> Prompt 不是字符串
> Prompt 是**结构化对象**

这意味着你可以：

* 检查变量
* 复用模板
* 组合模板
* 部分填充
* 和模型无缝对接
* 接入链式系统

---

## 十一、典型工程范式（标准写法）

```python
template = ChatPromptTemplate.from_messages([...])

chain = template | model

result = chain.invoke({...})
```

这是 LangChain 1.0 推荐写法。

---

## 十二、一句话理解本文件所有示例

> 你不是在学“如何写提示词”
> 而是在学**如何把提示词工程化、模块化、组件化**

这才是 LangChain Prompt 系统的真正目的。
