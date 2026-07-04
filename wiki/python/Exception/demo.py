"""
文件名：try_except_examples.py

本文件演示 Python 中 try...except 的完整使用方式，
涵盖真实工程开发中最常见的异常处理场景。

学习目标：
1. 理解 try / except 的基本结构
2. 掌握捕获指定异常类型
3. 掌握捕获多个异常
4. 理解 as e 的作用
5. 学会使用 else / finally
6. 学会主动抛出异常 raise
"""

# ==============================
# 示例1：最基础的 try...except
# ==============================


def example_1_basic():
    """
    最基础的异常捕获
    """
    print("\n示例1：基础异常捕获")

    try:
        num = int("abc")  # 会触发 ValueError
    except ValueError as e:
        print("发生 ValueError 异常！")
        print("异常信息：", e)


# ==============================
# 示例2：捕获多个异常类型
# ==============================


def example_2_multiple_exceptions():
    """
    同一段代码可能触发不同异常
    """
    print("\n示例2：捕获多个异常")

    try:
        result = 10 / 0  # 会触发 ZeroDivisionError
    except ValueError as e:
        print("ValueError：", e)
    except ZeroDivisionError as e:
        print("ZeroDivisionError：", e)


# ==============================
# 示例3：用一个 except 捕获多个异常
# ==============================


def example_3_tuple_exceptions():
    """
    用元组同时捕获多个异常
    """
    print("\n示例3：元组方式捕获多个异常")

    try:
        data = [1, 2, 3]
        print(data[5])  # IndexError
    except (IndexError, KeyError) as e:
        print("索引或键错误：", e)


# ==============================
# 示例4：捕获所有未知异常
# ==============================


def example_4_catch_all():
    """
    Exception 是所有异常的父类
    用于兜底处理
    """
    print("\n示例4：捕获所有异常")

    try:
        open("not_exist_file.txt")
    except Exception as e:
        print("发生未知异常：", type(e).__name__, e)


# ==============================
# 示例5：try...except...else
# ==============================


def example_5_else():
    """
    else：当 try 没有异常时才执行
    """
    print("\n示例5：else 的使用")

    try:
        num = int("123")
    except ValueError as e:
        print("转换失败：", e)
    else:
        print("转换成功，num =", num)


# ==============================
# 示例6：try...except...finally
# ==============================


def example_6_finally():
    """
    finally：无论是否发生异常都会执行
    常用于资源释放（文件关闭、数据库关闭）
    """
    print("\n示例6：finally 的使用")

    try:
        file = open("test.txt", "w")
        file.write("Hello")
    except Exception as e:
        print("写文件出错：", e)
    finally:
        file.close()
        print("文件已关闭（finally 执行）")


# ==============================
# 示例7：主动抛出异常 raise
# ==============================


def example_7_raise():
    """
    主动抛出异常，用于业务校验
    """
    print("\n示例7：主动抛出异常")

    age = -5

    try:
        if age < 0:
            raise ValueError("年龄不能为负数！")
    except ValueError as e:
        print("业务校验失败：", e)


# ==============================
# 示例8：自定义异常
# ==============================


class CustomError(Exception):
    """自定义异常类"""

    pass


def example_8_custom_exception():
    """
    使用自定义异常
    """
    print("\n示例8：自定义异常")

    try:
        raise CustomError("这是一个自定义异常")
    except CustomError as e:
        print("捕获自定义异常：", e)


# ==============================
# 主函数：依次运行所有示例
# ==============================

if __name__ == "__main__":
    example_1_basic()
    example_2_multiple_exceptions()
    example_3_tuple_exceptions()
    example_4_catch_all()
    example_5_else()
    example_6_finally()
    example_7_raise()
    example_8_custom_exception()
