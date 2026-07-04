"""
pipe_operator_examples.py

本文件演示 Python 中 | 运算符的所有常见用法。
| 在不同数据类型下，语义完全不同，是 Python 非常重要的一个运算符。
"""

print("=" * 60)
print("示例1：整数的按位或（Bitwise OR）")
print("=" * 60)

a = 5  # 二进制：0101
b = 3  # 二进制：0011

result = a | b
print(result)
# 输出结果：7
# 解释：0101 | 0011 = 0111（二进制）= 7（十进制）


print("\n" + "=" * 60)
print("示例2：集合的并集运算")
print("=" * 60)

set1 = {1, 2, 3}
set2 = {3, 4, 5}

union_set = set1 | set2
print(union_set)
# 输出结果：{1, 2, 3, 4, 5}
# 解释：| 在集合中表示并集（union）


print("\n" + "=" * 60)
print("示例3：字典的合并（Python 3.9+ 新特性）")
print("=" * 60)

dict1 = {"name": "Alice", "age": 20}
dict2 = {"age": 25, "city": "Beijing"}

merged_dict = dict1 | dict2
print(merged_dict)
# 输出结果：{'name': 'Alice', 'age': 25, 'city': 'Beijing'}
# 解释：| 用于合并字典，若 key 冲突，右侧字典覆盖左侧


print("\n" + "=" * 60)
print("示例4：布尔值参与 | 运算（容易误解）")
print("=" * 60)

print(True | False)
# 输出结果：True
# 解释：布尔值本质是整数 True=1, False=0，进行的是位运算，而不是逻辑 or

print(True | True)
# 输出结果：True

print(False | False)
# 输出结果：False


print("\n" + "=" * 60)
print("示例5：与逻辑 or 的区别（非常重要）")
print("=" * 60)

x = 0
y = 10

print(x or y)
# 输出结果：10
# 解释：or 返回的是“第一个为真”的值

print(x | y)
# 输出结果：10
# 解释：这里是位运算：0 | 10 = 10（二进制）


print("\n" + "=" * 60)
print("示例6：类型注解中的 Union（Python 3.10+）")
print("=" * 60)


def print_id(user_id: int | str):
    """
    user_id 可以是 int 或 str 类型
    """
    print(f"user_id = {user_id}")


print_id(123)
# 输出结果：user_id = 123

print_id("A001")
# 输出结果：user_id = A001
# 解释：| 在类型注解中表示 Union 类型


print("\n" + "=" * 60)
print("示例7：集合更新写法（|=）")
print("=" * 60)

s = {1, 2}
s |= {2, 3, 4}
print(s)
# 输出结果：{1, 2, 3, 4}
# 解释：|= 表示原地并集更新


print("\n" + "=" * 60)
print("示例8：字典原地合并（|=）")
print("=" * 60)

d = {"a": 1}
d |= {"b": 2}
print(d)
# 输出结果：{'a': 1, 'b': 2}
# 解释：|= 原地合并字典
