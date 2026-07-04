"""
optional_examples.py

本文件用于演示 Python 中 typing.Optional 的常见用法。
Optional 常用于：参数可为空、返回值可能为空、类属性可为空等场景。

Optional[T] 等价于：Union[T, None]
"""

from typing import Optional


# 示例1：函数参数可以为 None
def greet(name: Optional[str]) -> None:
    """
    如果 name 是字符串，正常问候
    如果 name 是 None，使用默认问候
    """
    if name is None:
        print("Hello, stranger!")
    else:
        print(f"Hello, {name}!")


# 运行示例
greet("Alice")
greet(None)

# 运行结果：
# Hello, Alice!
# Hello, stranger!


# 示例2：函数返回值可能为 None
def find_even_number(numbers: list[int]) -> Optional[int]:
    """
    在列表中寻找第一个偶数，如果找不到，返回 None
    """
    for num in numbers:
        if num % 2 == 0:
            return num
    return None


result1 = find_even_number([1, 3, 5, 8, 9])
result2 = find_even_number([1, 3, 5, 7])

print(result1)
print(result2)

# 运行结果：
# 8
# None


# 示例3：类属性可能为空
class User:
    def __init__(self, username: str, email: Optional[str] = None):
        """
        email 是可选的
        """
        self.username = username
        self.email = email

    def show_info(self) -> None:
        if self.email:
            print(f"User: {self.username}, Email: {self.email}")
        else:
            print(f"User: {self.username}, Email not provided")


user1 = User("Tom", "tom@example.com")
user2 = User("Jerry")

user1.show_info()
user2.show_info()

# 运行结果：
# User: Tom, Email: tom@example.com
# User: Jerry, Email not provided


# 示例4：结合默认参数使用 Optional
def connect_database(host: Optional[str] = None) -> None:
    """
    如果没有提供 host，使用默认地址
    """
    if host is None:
        host = "localhost"
    print(f"Connecting to database at {host}")


connect_database("192.168.1.10")
connect_database()

# 运行结果：
# Connecting to database at 192.168.1.10
# Connecting to database at localhost


# 示例5：错误示范（理解 Optional 的意义）
def print_length(text: Optional[str]) -> None:
    """
    如果不判断 None，会报错
    """
    # print(len(text))  # ❌ 如果 text 是 None，这行会报错

    if text is not None:
        print(len(text))
    else:
        print("No text provided")


print_length("Python")
print_length(None)

# 运行结果：
# 6
# No text provided
