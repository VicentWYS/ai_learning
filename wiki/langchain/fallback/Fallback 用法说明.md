# LangChain 中 Fallback 用法说明

本文对应示例代码：`fallback_example.py`  
目标：理解 **LangChain 中两种 Fallback 的用法与实现方式**。

---

## 一、LLM 级 Fallback：`with_fallbacks()`

当**主模型**调用失败（如 API 超时、限流、服务不可用）时，自动按顺序尝试**备用模型**，提高可用性。

### 基本写法

```python
from langchain.chat_models import init_chat_model

primary = init_chat_model(model="qwen-plus", ..., max_retries=0)
fallback = init_chat_model(model="qwen-turbo", ..., max_retries=0)

# 主模型失败时自动用 fallback
llm = primary.with_fallbacks([fallback])
response = llm.invoke("你的问题")
```

### 要点

- **主、备用都必须是同一类 Runnable**（例如都是 ChatModel），这样接口一致才能无缝切换。
- 建议主模型设置 **`max_retries=0`**，失败后直接走 fallback，而不是先重试再失败。
- 可以传入**多个备用**：`with_fallbacks([backup1, backup2])`，按列表顺序依次尝试。

---

## 二、结构化输出 Fallback：解析失败时兜底

当使用 **`with_structured_output`** 时，若模型返回内容无法被解析成目标 Pydantic 模型（如多了 markdown、非标准 JSON），会抛异常。此时可以用「先拿原始文本，再用 JSON/正则等方式提取」做**兜底解析**。

### 思路

1. **优先**：`llm.with_structured_output(YourModel).invoke(prompt)`，直接得到 Pydantic 对象。
2. **失败时**：用普通 `llm.invoke(prompt)` 拿到原始文本，再用 `json.loads` 或正则从文本中抠出 JSON，最后用 `YourModel.model_validate(data)` 得到结构化对象。

### 示例代码逻辑

```python
# 1) 优先用 with_structured_output
structured_llm = llm.with_structured_output(Person)
try:
    return structured_llm.invoke(prompt)
except Exception:
    pass
# 2) Fallback：普通 invoke 拿文本，再用 json.loads / 正则提取
raw = llm.invoke(prompt)
data = extract_json_from_text(raw.content)
return Person.model_validate(data)
```

---

## 三、示例文件与运行方式

完整可运行示例在本目录下的 **`fallback_example.py`**，包含：

| 内容 | 说明 |
|------|------|
| **LLM 级 Fallback** | `setup_llm_with_fallback()`、`example_llm_fallback()` |
| **结构化输出 Fallback** | `safe_structured_output()`、`extract_json_from_text()` |
| **多级 Fallback** | `example_multiple_fallbacks()`（主模型 + 多个备用依次尝试） |

在项目根目录执行（需已配置 `.env` 中的 `QWEN_API_KEY`、`QWEN_BASE_URL`）：

```bash
python "phase2_practical/11_structured_output/03 - 基础结构化输出/fallback_example.py"
```

---

## 四、总结

- **LLM Fallback**：用 `with_fallbacks([...])` 做模型级容错，主模型挂了自动切备用。
- **结构化输出 Fallback**：解析失败时用「原始文本 + 自定义解析」兜底，避免因格式不标准导致整条流程失败。
