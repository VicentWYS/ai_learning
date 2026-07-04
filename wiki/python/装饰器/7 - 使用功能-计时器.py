"""
装饰器实现一个计时器
"""

import time


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"耗时：{time.time() - start:.2f} 秒")
        return result

    return wrapper


@timer
def slow_func():
    time.sleep(1)


slow_func()

# 输出：
# 耗时：1.00 秒