"""
join_examples.py

本文件用于系统记录 Python 中 str.join() 的各种使用方式与场景示例。
建议：直接运行本文件，对照注释观察输出结果，加深理解。
"""

print("====== 示例1：最基础的 join 使用 ======")
# join 的基本语法：'分隔符'.join(可迭代对象)
names = ["Alice", "Bob", "Charlie"]
result = ", ".join(names)
print(result)

# 运行结果：
# Alice, Bob, Charlie


print("\n====== 示例2：用空格连接字符串 ======")
words = ["Hello", "world", "Python"]
result = " ".join(words)
print(result)

# 运行结果：
# Hello world Python


print("\n====== 示例3：用空字符串连接（常用于拼接字符） ======")
chars = ["P", "y", "t", "h", "o", "n"]
result = "".join(chars)
print(result)

# 运行结果：
# Python


print("\n====== 示例4：join 连接数字（必须先转成字符串） ======")
numbers = [1, 2, 3, 4]

# 错误写法（会报错）：
# ",".join(numbers)

# 正确写法：先把数字转成字符串
result = ",".join(str(num) for num in numbers)
print(result)

# 运行结果：
# 1,2,3,4


print("\n====== 示例5：join 与列表推导式结合 ======")
# 拼接平方数
result = " | ".join(str(x * x) for x in range(5))
print(result)

# 运行结果：
# 0 | 1 | 4 | 9 | 16


print("\n====== 示例6：join 处理文件路径 ======")
folders = ["home", "user", "documents", "file.txt"]
path = "/".join(folders)
print(path)

# 运行结果：
# home/user/documents/file.txt


print("\n====== 示例7：join 处理字符串列表，生成 SQL 语句的一部分 ======")
fields = ["id", "name", "age"]
sql_part = ", ".join(fields)
print(sql_part)

# 运行结果：
# id, name, age


print("\n====== 示例8：join 与 split 配合使用 ======")
sentence = "Python is very powerful"
words = sentence.split(" ")
reconstructed = "-".join(words)
print(reconstructed)

# 运行结果：
# Python-is-very-powerful


print("\n====== 示例9：join 过滤空字符串 ======")
items = ["apple", "", "banana", "", "cherry"]

# 过滤空字符串再拼接
result = ", ".join(item for item in items if item)
print(result)

# 运行结果：
# apple, banana, cherry


print("\n====== 示例10：join 拼接多行文本（非常常用） ======")
lines = ["第一行内容", "第二行内容", "第三行内容"]
text = "\n".join(lines)
print(text)

# 运行结果：
# 第一行内容
# 第二行内容
# 第三行内容


print("\n====== 示例11：join 处理字典的键 ======")
data = {"name": "Alice", "age": 25, "city": "Paris"}
keys = ", ".join(data.keys())
print(keys)

# 运行结果：
# name, age, city


print("\n====== 示例12：join 处理字典的值 ======")
values = ", ".join(str(v) for v in data.values())
print(values)

# 运行结果：
# Alice, 25, Paris


print("\n====== 示例13：join 在日志输出中的应用 ======")
log_parts = ["INFO", "2026-01-26", "User login success"]
log_line = " | ".join(log_parts)
print(log_line)

# 运行结果：
# INFO | 2026-01-26 | User login success
