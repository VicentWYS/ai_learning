"""
函数可以像变量一样传递

函数是“对象”
可以赋值、传参、返回
"""


def say_hello():
    print("hello")


f = say_hello
f()
