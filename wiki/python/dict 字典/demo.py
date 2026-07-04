# dict_examples.py
# 本文件用于演示 Python 中 dict（字典）的常见与核心用法
# 建议：直接运行本文件，通过输出结果理解每种用法

print("===== 1. 创建字典的方式 =====")

# 方式1：使用 {}
student = {"name": "Alice", "age": 20, "score": 95}
print(student)  # 输出：{'name': 'Alice', 'age': 20, 'score': 95}

# 方式2：使用 dict() 构造函数
teacher = dict(name="Bob", age=35, subject="Math")
print(teacher)  # 输出：{'name': 'Bob', 'age': 35, 'subject': 'Math'}

print("\n===== 2. 访问字典中的值 =====")

# 通过 key 访问 value
print(student["name"])  # 输出：Alice

# 使用 get 方法（推荐，避免 KeyError）
print(student.get("age"))  # 输出：20
print(student.get("gender"))  # 输出：None（不存在不会报错）

print("\n===== 3. 新增 / 修改 字典元素 =====")

# 新增元素
student["gender"] = "female"
print(student)  # 输出包含 gender

# 修改元素
student["score"] = 98
print(student)  # score 被更新为 98

print("\n===== 4. 删除字典元素 =====")

# 使用 del 删除
del student["gender"]
print(student)  # gender 被删除

# 使用 pop 删除并获取值
age = student.pop("age")
print(age)  # 输出：20（被删除的值）
print(student)  # age 已被移除

print("\n===== 5. 遍历字典 =====")

# 遍历 key
for key in student.keys():
    print(key)  # 输出每个 key

# 遍历 value
for value in student.values():
    print(value)  # 输出每个 value

# 同时遍历 key 和 value（最常用）
for key, value in student.items():
    print(key, value)  # 输出：name Alice / score 98

print("\n===== 6. 判断 key 是否存在 =====")

print("name" in student)  # 输出：True
print("age" in student)  # 输出：False

print("\n===== 7. 字典长度 =====")

print(len(student))  # 输出字典中键值对的数量

print("\n===== 8. 字典嵌套（非常重要，项目中大量使用） =====")

users = {"user1": {"name": "Alice", "age": 20}, "user2": {"name": "Bob", "age": 25}}

print(users["user1"]["name"])  # 输出：Alice

print("\n===== 9. 使用 update 合并字典 =====")

dict_a = {"a": 1, "b": 2}
dict_b = {"b": 3, "c": 4}

dict_a.update(dict_b)
print(dict_a)  # 输出：{'a': 1, 'b': 3, 'c': 4}

print("\n===== 10. 使用 setdefault =====")

# 如果 key 不存在，则插入默认值
student.setdefault("city", "Beijing")
print(student)  # 新增 city

# 如果 key 存在，则不会覆盖
student.setdefault("name", "Tom")
print(student)  # name 仍然是 Alice

print("\n===== 11. 字典推导式（高级用法） =====")

# 创建 1~5 的平方字典
square_dict = {x: x * x for x in range(1, 6)}
print(square_dict)  # 输出：{1:1, 2:4, 3:9, 4:16, 5:25}

print("\n===== 12. 字典排序 =====")

scores = {"Alice": 88, "Bob": 95, "Cindy": 90}

# 按 value 排序
sorted_scores = sorted(scores.items(), key=lambda item: item[1])
print(sorted_scores)
# 输出：[('Alice', 88), ('Cindy', 90), ('Bob', 95)]

print("\n===== 13. 清空字典 =====")

scores.clear()
print(scores)  # 输出：{}

print("\n===== 14. 字典常见使用场景示例 =====")

# 场景：统计字符串中每个字符出现的次数
text = "hello world"
char_count = {}

for ch in text:
    if ch in char_count:
        char_count[ch] += 1
    else:
        char_count[ch] = 1

print(char_count)
# 输出：每个字符出现的次数

print("\n===== 15. 使用 dict 进行数据映射（项目中极其常见） =====")

status_map = {200: "请求成功", 404: "资源不存在", 500: "服务器错误"}

code = 404
print(status_map.get(code))  # 输出：资源不存在
