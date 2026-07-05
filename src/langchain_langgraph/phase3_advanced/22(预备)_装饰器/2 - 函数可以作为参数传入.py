"""
函数可以作为参数传入
"""


def say_hello():
    print("hello")


def run_func(func):
    print("开始执行...")
    func()
    print("执行结束...")


run_func(say_hello)
