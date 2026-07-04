# strip_demo.py
# 演示 Python 中 strip() / lstrip() / rstrip() 的常见用法
# 每个示例都附带运行结果说明

print("===== 示例1：去除字符串两端的空格 =====")
s1 = "   Hello Python   "
result1 = s1.strip()
print(result1)
# 运行结果：
# Hello Python
# 说明：默认去除两端的 空格、\n、\t 等空白字符


print("\n===== 示例2：去除两端的换行符和制表符 =====")
s2 = "\n\tHello World\t\n"
result2 = s2.strip()
print(result2)
# 运行结果：
# Hello World
# 说明：strip 默认会清除：空格、\n、\t


print("\n===== 示例3：指定去除的字符 =====")
s3 = "###Python###"
result3 = s3.strip("#")
print(result3)
# 运行结果：
# Python
# 说明：strip("#") 表示去除两端所有的 # 号


print("\n===== 示例4：注意！strip 不是去除子串，而是去除字符集合 =====")
s4 = "abcPythoncba"
result4 = s4.strip("abc")
print(result4)
# 运行结果：
# Python
# 说明：
# 不是去掉 "abc"，而是：
# 两端只要是 a 或 b 或 c 都会被移除，直到遇到不是这几个字符为止


print("\n===== 示例5：只去除左边 =====")
s5 = "   data"
result5 = s5.lstrip()
print(result5)
# 运行结果：
# data
# 说明：lstrip 只处理左侧


print("\n===== 示例6：只去除右边 =====")
s6 = "data   "
result6 = s6.rstrip()
print(result6)
# 运行结果：
# data
# 说明：rstrip 只处理右侧


print("\n===== 示例7：清洗用户输入（工程中非常常见） =====")
user_input = "   Beijing  "
clean_city = user_input.strip()
print(clean_city)
# 运行结果：
# Beijing
# 说明：处理用户输入时必须 strip，否则容易匹配失败


print("\n===== 示例8：读取文件行时必须 strip =====")
line = "Shanghai\n"
city = line.strip()
print(city)
# 运行结果：
# Shanghai
# 说明：读取文件每一行时，末尾一定带 \n，必须 strip


print("\n===== 示例9：清洗日志文本 =====")
log_line = "   ERROR: file not found   \n"
clean_log = log_line.strip()
print(clean_log)
# 运行结果：
# ERROR: file not found
# 说明：日志处理、NLP、数据预处理高频操作


print("\n===== 示例10：常见错误演示 =====")
s10 = "www.example.com"
result10 = s10.strip("www.")
print(result10)
# 运行结果：
# example.com
# 说明：
# strip("www.") 会移除 w 和 . 的任意组合，而不是去掉 'www.'
# 如果字符串两端出现 w 或 . 都会被删掉
