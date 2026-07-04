"""
getattr_examples.py

本文件演示 Python 内置函数 getattr() 的常见使用场景。

getattr(object, name[, default]) 的作用：
    从对象中，通过字符串形式的属性名，动态获取属性值。

等价于：
    object.name

但 getattr 更强大，因为：
    - 属性名可以是变量（字符串）
    - 可以提供默认值，避免报错
"""

print("=" * 60)
print("示例1：最基本的 getattr 使用")
print("=" * 60)


class Person:
    def __init__(self):
        self.name = "Alice"
        self.age = 20


p = Person()

# 普通方式访问
print(p.name)  # 输出: Alice

# getattr 方式访问
print(getattr(p, "name"))  # 输出: Alice


print("\n" + "=" * 60)
print("示例2：属性名来自变量（动态访问）")
print("=" * 60)

attr_name = "age"

# 动态通过字符串访问属性
print(getattr(p, attr_name))  # 输出: 20


print("\n" + "=" * 60)
print("示例3：访问不存在的属性（不提供 default 会报错）")
print("=" * 60)

try:
    print(getattr(p, "address"))
except AttributeError as e:
    print("报错信息：", e)
    # 输出：AttributeError: 'Person' object has no attribute 'address'


print("\n" + "=" * 60)
print("示例4：提供 default，避免报错（非常重要）")
print("=" * 60)

result = getattr(p, "address", "No Address")
print(result)
# 输出: No Address


print("\n" + "=" * 60)
print("示例5：getattr 获取方法（函数）并调用")
print("=" * 60)


class Dog:
    def bark(self):
        return "Woof!"


d = Dog()

# 通过 getattr 获取方法
method = getattr(d, "bark")
print(method)       # 输出: <bound method Dog.bark of ...>
print(method())     # 输出: Woof!


print("\n" + "=" * 60)
print("示例6：结合 hasattr 使用（常见组合）")
print("=" * 60)

if hasattr(p, "name"):
    print(getattr(p, "name"))  # 输出: Alice


print("\n" + "=" * 60)
print("示例7：在配置驱动 / 插件化设计中的典型用法")
print("=" * 60)


class MathOps:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


ops = MathOps()

# 假设这个来自配置文件或用户输入
operation_name = "multiply"

operation = getattr(ops, operation_name)
print(operation(3, 5))  # 输出: 15


print("\n" + "=" * 60)
print("示例8：在框架源码中常见的用法（反射思想）")
print("=" * 60)


class Controller:
    def get(self):
        return "GET request"

    def post(self):
        return "POST request"


ctrl = Controller()

# 模拟 HTTP 请求方法
http_method = "post"

handler = getattr(ctrl, http_method)
print(handler())  # 输出: POST request


print("\n" + "=" * 60)
print("示例9：对象字典与 getattr 的关系")
print("=" * 60)

print(p.__dict__)  # 输出: {'name': 'Alice', 'age': 20}
print(getattr(p, "name"))  # 本质上就是从这里取值


print("\n" + "=" * 60)
print("示例10：为什么 getattr 在框架 / 中间件 / Agent 中极其重要")
print("=" * 60)

"""
在很多框架（如 Django / Flask / FastAPI / LangChain / LangGraph）中：

系统经常需要：
    根据字符串 -> 找到对象的方法 -> 执行

例如：
    "tool_name" -> getattr(tools, tool_name) -> 调用

这就是 Python 的“反射能力”。
"""

print("getattr 是 Python 实现反射和动态调度的核心工具。")
