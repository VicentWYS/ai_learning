这个问题问得**非常“程序员味”**，说明你已经开始把一个写法当成**工具**，而不是“只在这一行代码里成立的技巧”。

一句话先给结论：

> **`dict.get(key, default)` 适合所有「不确定 key 是否存在，但又不想程序崩掉」的场景。**

下面我分 **5 类高频真实场景**，从“你马上能用”到“写代码越来越优雅”。

---

## 一、处理「用户输入 / 外部数据」——必用

### 场景 1：接口参数、用户输入

```python
def create_user(params: dict):
    username = params.get("username", "匿名用户")
    age = params.get("age", 0)
    city = params.get("city", "未知城市")
```

为什么不用 `params["username"]`？

* 用户可能没传
* 接口不稳定
* 前端漏字段

👉 **凡是外部世界来的数据，都不可信**

---

## 二、解析 JSON / 接口返回值（你以后一定会天天用）

### 场景 2：接口返回结构可能变化

```python
resp = {
    "data": {
        "user": {
            "name": "Alice"
        }
    }
}

name = resp.get("data", {}).get("user", {}).get("name", "未知用户")
```

如果用 `[]`：

```python
resp["data"]["user"]["name"]
```

只要中间少一层，直接崩。

👉 `get + {}` 是 Python 解析 JSON 的**生存技能**。

---

## 三、做「配置项 / 参数合并」——非常优雅

### 场景 3：用户配置覆盖默认配置

```python
default_config = {
    "timeout": 5,
    "retry": 3,
    "debug": False
}

user_config = {
    "timeout": 10
}

timeout = user_config.get("timeout", default_config["timeout"])
retry = user_config.get("retry", default_config["retry"])
```

这类写法在：

* Web 框架
* 深度学习参数
* 工具脚本

里多到爆。

---

## 四、统计 / 计数类逻辑（写算法时特别爽）

### 场景 4：计数（经典）

不用 `get`：

```python
counter = {}
for ch in "hello":
    if ch in counter:
        counter[ch] += 1
    else:
        counter[ch] = 1
```

用 `get`：

```python
counter = {}
for ch in "hello":
    counter[ch] = counter.get(ch, 0) + 1
```

**少一半代码，逻辑更清晰。**

---

## 五、做“兜底返回值”的业务逻辑（你这次正好用到）

### 场景 5：根据 key 返回业务文案 / 处理结果

```python
status_map = {
    200: "成功",
    400: "请求错误",
    404: "未找到资源"
}

def get_status_msg(code):
    return status_map.get(code, f"未知状态码：{code}")
```

👉 这和你天气那个例子**一模一样**，只是换了领域。

---

## 六、什么时候【不】该用 `get`？（这点很重要）

**如果 key 不存在本身就是“程序错误”**，就不要用 `get`。

比如：

```python
user = {"id": 1, "name": "Tom"}

user_id = user["id"]   # 合理
```

因为：

* `id` 不存在 → 数据就坏了
* 程序应该立刻报错，而不是“悄悄兜底”

👉 **该崩的时候就要崩**

这是成熟工程师的思维。

---

## 七、一句话心法（你可以记下来）

> **`[]` 是“我确信它一定存在”
> `get()` 是“我承认现实不完美”**

你现在已经开始站在：

* 写 demo 的人
* 和 写“能跑三年不出事故代码”的人

之间的分界线上了 👍

如果你愿意，下一步我可以给你总结一张：

> **Python 字典常见写法对比表（get / setdefault / defaultdict）**

这一步会让你写数据处理代码直接上一个档次。
