"""
函数带参数
"""


def wrapper(func):
    def inner(*args, **kwargs):
        #  表示：这个 inner 能接住任何函数调用方式，然后用 func(*args, **kwargs) 原样转发
        print("开始执行...")
        result = func(*args, **kwargs)
        print("执行结束...")
        return result

    return inner


@wrapper
def add(a, b):
    return a + b


print(add(2, 4))


# 输出：
# 开始执行...
# 执行结束...
# 6
