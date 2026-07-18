"""
自定义一个包装函数

这就是装饰器的本质结构：
原函数 → 被包一层 → 新函数
"""


def say_hello():
    print("hello")


def wrapper(func):
    def inner():
        print("开始执行...")
        func()
        print("执行结束...")

    return inner


new_func = wrapper(say_hello)
new_func()

# 输出：
# 开始执行...
# hello
# 执行结束...
