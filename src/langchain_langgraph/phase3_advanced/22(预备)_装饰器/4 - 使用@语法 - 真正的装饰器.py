"""
使用 @ 语法（真正的装饰器）

@xxx 就是语法糖（简写）
"""


def wrapper(func):
    """
    定义套件功能
    """

    def inner():
        print("开始执行...")
        func()
        print("执行结束...")

    return inner


@wrapper
def say_hello():
    print("hello")  # wrapper相当于是给这个函数加的一个套件


say_hello()  # 只要声明函数时加上了套件 @wrapper，后面再用这个函数时就可以不用管了

# 输出：
# 开始执行...
# hello
# 执行结束...
