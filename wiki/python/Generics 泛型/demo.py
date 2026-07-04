"""
Python 中泛型（Generics）的使用
=============================================

泛型的本质：让“类型”也可以当参数传来传去。
    - 不是传数据，是传类型规则。

有上界约束的泛型（Upper Bound TypeVar）
    - 普通泛型：T 可以是任何类型
    - 带 bound 的泛型：T 必须是某种类型体系里的成员

示例：
    T = TypeVar("T", bound=BaseModel)

    - 意思不是：T 是 BaseModel
    - 而是：T 是 BaseModel 家族中的某个具体子类，并且这个具体类型会在使用时被确定下来。
    - 这正是：LangChain / FastAPI / Pydantic 能做“强类型框架”的根本原因。
"""

from typing import TypeVar, List, Generic
from pydantic import BaseModel


# ============================================================================================
# 示例1 - 未使用泛型的情况
# ============================================================================================
def first(items: list):
    return items[0]


def exmaple_1_without_generics():
    """
    示例1 - 未使用泛型的情况

    - 局限：这里无法确定最后输出的变量的类型，也没有格式限制方法
    """
    print("\n" + "-" * 40)
    print("示例1 - 未使用泛型的情况")
    print("-" * 40)

    demo_list_1 = ["a", "b", "c"]
    demo_list_2 = [
        {"role": "user", "content": "今天天气怎么样？"},
        {"role": "ai", "content": "今天天气晴朗，气温20度。"},
    ]
    demo_list_3 = [10, 20, 30]
    result = first(demo_list_3)
    print(result)
    print("type: " + result.__class__.__name__)


# ============================================================================================
# 示例2 - 初次使用泛型函数
# ============================================================================================
def example_2_typevar():
    """
    示例2 - 初次使用泛型函数

    - T 不是具体类型，T 是一个“类型占位符”。
    - TypeVar 可以限制传进来是什么类型，出来就是什么类型。
    - 类型参数化（Type Parameterization）：T 被自动“替换”为你传入的真实类型。
    """
    # T 不是具体类型，T是一个“类型占位符”
    T = TypeVar("T")

    def first(items: List[T]) -> T:
        return items[0]

    print("\n" + "-" * 40)
    print("示例2 - 初次使用泛型函数")
    print("-" * 40)

    demo_list_1 = ["a", "b", "c"]
    demo_list_2 = [
        {"role": "user", "content": "今天天气怎么样？"},
        {"role": "ai", "content": "今天天气晴朗，气温20度。"},
    ]
    demo_list_3 = [10, 20, 30]

    result = first(demo_list_3)
    print(result)
    print("type: " + result.__class__.__name__)


# ============================================================================================
# 示例3 - 给类填入类型
# ============================================================================================
def example_3_generic():
    """
    示例3 - 给类填入类型

    - Store[str, int] 是在“给类填入类型”。
    """
    K = TypeVar("K")
    V = TypeVar("V")

    class Store(Generic[K, V]):
        def __init__(self):
            super().__init__()
            self.data = {}

        def set(self, key: K, value: V):
            self.data[key] = value

        def get(self, key: K):
            return self.data[key]

    store = Store[str, int]()
    store.set("age", 18)

    x = store.get("age")
    print(x)
    print("type: " + x.__class__.__name__)


# ============================================================================================
# 示例4 - 泛型的类型约束检查
# ============================================================================================
def example_4_limit_check():
    """
    示例4 - 泛型的类型约束检查

    - 在泛型类约束的方法中，不得使用特点类型专用的方法，如 str 专用的 upper()。
    - 这种情况下会报错，因为不知道输入的是不是 str。
    - 这在 LangChain 源码里非常常见。
    """
    T = TypeVar("T")

    class Box(Generic[T]):
        def __init__(self):
            super().__init__()

        def do(self, x: T) -> T:
            print(x)
            print(x.upper())  # IDE 会报错

            return x

    box = Box()
    result = box.do("123")  # 正常执行
    # result = box.do(123) # 报错，输入为 int 类型，'int' object has no attribute 'upper'
    print(result)
    print(result.__class__.__name__)


# ============================================================================================
# 示例5 - 限制泛型类型，确保类型安全
# ============================================================================================
def example_5_bound():
    """
    示例5 - 限制泛型类型，确保类型安全

    - bound=BaseModel 的意思是：
        - T 只能是 BaseModel 或它的子类。
    """
    # T = TypeVar("T")
    T = TypeVar("T", bound=BaseModel)

    def print_model(x: T):
        return x.model_dump()

    class User(BaseModel):
        name: str
        age: int

    user = User(name="Tom", age=20)
    print(print_model(user))


# ============================================================================================
# 示例6 - 在类中使用 TypeVar
# ============================================================================================
def example_6_in_class():
    """
    示例6 - 在类中使用 TypeVar

    - 这个 Store 可以存任何 Pydantic 模型，而且类型绝对安全。
    """
    T = TypeVar("T", bound=BaseModel)

    class ModelStore(Generic[T]):
        def save(self, model: T):
            print(model.model_dump())

    # 可以正确执行
    class Product(BaseModel):
        title: str
        price: float

    # 无法正确执行
    class Product1:
        def __init__(self, title1: str, price1: float):
            self.title1 = title1
            self.price1 = price1

    store = ModelStore[Product]()
    store.save(Product(title="Book", price=14.5))


# ============================================================================================
# 主程序
# ============================================================================================
def main():
    print("=" * 30, " 程序开始 ", "=" * 30)

    try:
        # exmaple_1_without_generics()
        # example_2_typevar()
        # example_3_generic()
        # example_4_limit_check()
        # example_5_bound()
        example_6_in_class()

        print("=" * 30, " 程序结束 ", "=" * 30)
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")


if __name__ == "__main__":
    main()


# chatgpt 参考：https://chatgpt.com/c/69876704-1d98-8320-9427-b265a6359e48
