## 一、概念

`__class__` 是 **Python 中每个对象天然自带的属性**，它指向：

> **创建该对象的“类对象”**

```python
a = 10
print(a.__class__)          # <class 'int'>
print(a.__class__.__name__) # int
```

等价于：

```python
type(a)
```

但 `__class__` 是**面向对象内部使用方式**，是 Python 对象模型的一部分。

---

## 二、Python 对象模型（必须理解）

在 Python 中：

```
实例对象  --->  类对象  --->  type（元类）
```

验证：

```python
class Person:
    pass

p = Person()

print(p.__class__)                 # <class '__main__.Person'>
print(p.__class__.__name__)       # Person
print(p.__class__.__class__)      # <class 'type'>
```

说明：

* `p` 是对象
* `Person` 也是对象（类对象）
* `Person` 的类型是 `type`

这体现了：

> Python：万物皆对象

---

## 三、基础示例：查看对象类型

```python
x = [1, 2, 3]
y = "hello"

print(x.__class__.__name__)  # list
print(y.__class__.__name__)  # str
```

运行结果：

```
list
str
```

---

## 四、函数中动态获取对象类型（调试常用）

```python
def show_type(obj):
    print(f"对象类型是: {obj.__class__.__name__}")

show_type(3.14)      # float
show_type({"a": 1})  # dict
```

运行结果：

```
对象类型是: float
对象类型是: dict
```

---

## 五、在类内部使用（工程高频）

```python
class Animal:
    def who_am_i(self):
        print(f"我是 {self.__class__.__name__}")

class Dog(Animal):
    pass

Dog().who_am_i()
```

运行结果：

```
我是 Dog
```

父类**无需知道子类名字**。

---

## 六、日志系统中的典型用法

```python
class Logger:
    @staticmethod
    def log(obj):
        print(f"[LOG] 来自类: {obj.__class__.__name__}")

class User:
    pass

Logger.log(User())
```

运行结果：

```
[LOG] 来自类: User
```

---

## 七、根据对象“再创建同类对象”（高级用法）

```python
class Cat:
    def speak(self):
        print("meow")

c1 = Cat()

# 不知道类名，创建同类对象
c2 = c1.__class__()
c2.speak()
```

运行结果：

```
meow
```

---

## 八、配合异常定位来源类（真实项目高频）

```python
class Service:
    def run(self):
        try:
            1 / 0
        except Exception as e:
            print(f"错误来自类: {self.__class__.__name__}")
            print(f"异常类型: {e.__class__.__name__}")

Service().run()
```

运行结果：

```
错误来自类: Service
异常类型: ZeroDivisionError
```

---

## 九、运行时“切换对象的类”（极其动态）

> Java/C++ 完全做不到

```python
class A:
    def hello(self):
        print("A")

class B:
    def hello(self):
        print("B")

obj = A()
obj.hello()   # A

obj.__class__ = B
obj.hello()   # B
```

---

## 十、为什么框架源码大量使用它？

应用场景：

* Django ORM：根据类名映射表名
* FastAPI：根据类名生成路由信息
* 日志系统：打印来源类
* 中间件 / 插件系统：父类感知子类
* LangChain / Agent 框架：通用基类识别具体实现类

核心原因：

> **写通用代码，但能感知“当前具体子类是谁”**

---

## 十一、与 `type()` 的区别

| 写法                     | 输出                        | 使用场景       |
| ------------------------ | --------------------------- | -------------- |
| `type(obj)`              | `<class '__main__.Person'>` | 外部类型判断   |
| `obj.__class__`          | `<class '__main__.Person'>` | 面向对象内部   |
| `obj.__class__.__name__` | `Person`                    | 日志/调试/框架 |

---

## 十二、本质总结（非常重要）

`__class__` 体现了 Python 的三大核心能力：

1. 万物皆对象（类也是对象）
2. 运行时自省（Introspection）
3. 元编程（操作类型本身）

一句话记忆：

> `__class__` 是对象指向其“类对象”的内置引用，是 Python 支持运行时反射与元编程的基础。

---

## 十三、你在源码中看到这句代码时的理解

```python
self.__class__.__name__
```

含义是：

> **获取当前对象所属类名（不关心具体类名，自动适配子类）**

这是**专业 Python 工程代码的标志写法**。
