"""
装饰器带参数


三层结构：

外层：接收参数
  ↓
中层：接收函数
  ↓
内层：执行逻辑
"""


def decorator_with_args(prefix):
    """外层：接收参数"""

    def decorator(func):
        """中层：接收函数"""

        def wrapper(*args, **kwargs):
            """内层：执行逻辑"""
            print(f"{prefix} 开始执行...")
            result = func(*args, **kwargs)
            print(f"{prefix} 执行结束...")
            return result

        return wrapper

    return decorator


@decorator_with_args("🔥")
def add(a, b):
    return a + b


print(add(2, 3))

# 🔥开始执行...
# 🔥执行结束...
# 5
