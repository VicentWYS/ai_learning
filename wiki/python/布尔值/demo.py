"""
bool_examples.py

演示 Python 中 bool（布尔值）的常见用法
建议：运行文件，对照“输出结果注释”理解
"""

# ==============================
# 1. 基本布尔值
# ==============================

a = True
b = False

print("1. 基本布尔值")
print("a =", a)  # 输出: a = True
print("b =", b)  # 输出: b = False
print("-" * 50)  # 输出: --------------------------------------------------


# ==============================
# 2. 比较运算会返回布尔值
# ==============================

print("2. 比较运算")

print("3 > 1 :", 3 > 1)  # 输出: 3 > 1 : True   （3确实大于1）
print("3 < 1 :", 3 < 1)  # 输出: 3 < 1 : False  （3不小于1）
print("5 == 5 :", 5 == 5)  # 输出: 5 == 5 : True  （相等）
print("5 != 5 :", 5 != 5)  # 输出: 5 != 5 : False （不不等于）
print("-" * 50)


# ==============================
# 3. 逻辑运算符 and / or / not
# ==============================

print("3. 逻辑运算")

x = True
y = False

print("x and y :", x and y)  # 输出: x and y : False （都为True才为True）
print("x or y  :", x or y)  # 输出: x or y  : True  （有一个True即可）
print("not x   :", not x)  # 输出: not x   : False （取反）
print("-" * 50)


# ==============================
# 4. bool() 函数：判断“真假”
# ==============================

print("4. bool() 函数判断真假")

print("bool(1)      :", bool(1))  # 输出: True  （非0整数为True）
print("bool(0)      :", bool(0))  # 输出: False （0为False）
print("bool(-1)     :", bool(-1))  # 输出: True  （非0整数为True）
print("bool(100)    :", bool(100))  # 输出: True
print("-" * 50)


# ==============================
# 5. 空值在 Python 中都是 False
# ==============================

print("5. 空值判断")

print("bool(None)      :", bool(None))  # 输出: False （空对象）
print("bool('')        :", bool(""))  # 输出: False （空字符串）
print("bool([])        :", bool([]))  # 输出: False （空列表）
print("bool({})        :", bool({}))  # 输出: False （空字典）
print("bool(())        :", bool(()))  # 输出: False （空元组）
print("-" * 50)


# ==============================
# 6. 非空值都是 True
# ==============================

print("6. 非空值判断")

print("bool('hello')   :", bool("hello"))  # 输出: True （非空字符串）
print("bool([1, 2, 3]) :", bool([1, 2, 3]))  # 输出: True （非空列表）
print("bool({'a': 1})  :", bool({"a": 1}))  # 输出: True （非空字典）
print("-" * 50)


# ==============================
# 7. 在 if 语句中的使用（最常见）
# ==============================

print("7. if 语句中的布尔判断")

num = 10

if num:
    print("num 为 True，因为 num 不为 0")
    # 输出: num 为 True，因为 num 不为 0

empty_list = []

if not empty_list:
    print("empty_list 为 False，因为它是空列表")
    # 输出: empty_list 为 False，因为它是空列表
print("-" * 50)


# ==============================
# 8. 布尔值参与表达式（短路特性）
# ==============================

print("8. 短路特性（非常重要）")


def test():
    print("test() 被调用了")
    return True


print("False and test():")
False and test()
# 输出: False and test():
# （不会出现“test() 被调用了”，因为 and 短路）

print("True or test():")
True or test()
# 输出: True or test():
# （不会出现“test() 被调用了”，因为 or 短路）
print("-" * 50)


# ==============================
# 9. 布尔值本质上是整数
# ==============================

print("9. bool 本质是 int 的子类")

print("True + True =", True + True)  # 输出: True + True = 2
print("True * 10 =", True * 10)  # 输出: True * 10 = 10
print("False + 5 =", False + 5)  # 输出: False + 5 = 5
print("-" * 50)


# ==============================
# 10. 实战风格示例（非常常见）
# ==============================

print("10. 实战示例")

user_input = ""

if user_input:
    print("用户输入了内容")
else:
    print("用户没有输入内容")
# 输出: 用户没有输入内容 （因为空字符串为False）

data = [1, 2, 3]

if data:
    print("数据不为空，可以处理")
# 输出: 数据不为空，可以处理 （因为列表非空为True）
