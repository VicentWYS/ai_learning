"""
文件名：hasattr_demo.py

本文件演示 Python 内置函数 hasattr() 的常见使用场景。

hasattr(object, name) 的作用：
    判断 object 对象中是否存在名为 name 的属性（或方法）

返回值：
    True  -> 存在该属性/方法
    False -> 不存在

备注：
    hasattr() 是 Python 动态语言能力的核心函数之一。
    这里的后缀 "attr"，就是 “属性” 、"attribute" 的意思。
    典型思想叫：“不关心你是什么类，只关心你有没有这个能力”。这就是 Python 的 鸭子类型哲学。
"""

# =========================
# 示例1：判断对象是否有某个属性
# =========================


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age


p = Person("Alice", 25)

print("示例1：判断属性是否存在")
print(hasattr(p, "name"))  # True，对象中有 name 属性
print(hasattr(p, "gender"))  # False，对象中没有 gender 属性

# 运行结果：
# True
# False


# =========================
# 示例2：判断对象是否有某个方法
# =========================


class Dog:
    def bark(self):
        print("Woof!")


d = Dog()

print("\n示例2：判断方法是否存在")
print(hasattr(d, "bark"))  # True，存在 bark 方法
print(hasattr(d, "run"))  # False，不存在 run 方法

# 运行结果：
# True
# False


# =========================
# 示例3：配合 getattr() 安全调用方法（非常重要的用法）
# =========================


class Cat:
    def meow(self):
        print("Meow!")


c = Cat()

print("\n示例3：安全调用方法")

if hasattr(c, "meow"):
    getattr(c, "meow")()  # 动态调用方法
else:
    print("没有这个方法")

# 运行结果：
# Meow!


# =========================
# 示例4：防止程序因为属性不存在而报错
# =========================


class Car:
    def __init__(self):
        self.brand = "BMW"


car = Car()

print("\n示例4：防止属性错误")

if hasattr(car, "price"):
    print(car.price)
else:
    print("price 属性不存在，避免了 AttributeError")

# 运行结果：
# price 属性不存在，避免了 AttributeError


# =========================
# 示例5：在框架/插件/动态代码中非常常见
# =========================


class PluginA:
    def run(self):
        print("PluginA running")


class PluginB:
    def start(self):
        print("PluginB starting")


plugins = [PluginA(), PluginB()]

print("\n示例5：统一调用插件的 run 方法（如果存在）")

for plugin in plugins:
    if hasattr(plugin, "run"):
        plugin.run()
    else:
        print(f"{plugin.__class__.__name__} 没有 run 方法")

# 运行结果：
# PluginA running
# PluginB 没有 run 方法
