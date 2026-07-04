"""
文件名：enumerate_demo.py

本文件用于演示 Python 内置函数 enumerate 的常见用法。
通过多个可运行示例，理解 enumerate 在实际开发中的作用。

核心作用：
    在遍历可迭代对象（如 list、tuple、str）时，
    同时获得「索引 index」和「元素 value」。
"""


def example_1_basic_usage():
    """
    示例1：最基础用法
    enumerate 会在遍历列表时，同时返回索引和值
    """
    print("\n【示例1：基础用法】")

    fruits = ["apple", "banana", "orange"]

    for index, value in enumerate(fruits):
        print(f"索引：{index}，值：{value}")

    # 输出说明：
    # 索引：0，值：apple
    # 索引：1，值：banana
    # 索引：2，值：orange


def example_2_with_start_index():
    """
    示例2：指定起始索引
    enumerate 的第二个参数可以指定起始 index
    """
    print("\n【示例2：指定起始索引】")

    fruits = ["apple", "banana", "orange"]

    for index, value in enumerate(fruits, start=1):
        print(f"序号：{index}，值：{value}")

    # 输出说明：
    # 序号：1，值：apple
    # 序号：2，值：banana
    # 序号：3，值：orange


def example_3_traditional_way_vs_enumerate():
    """
    示例3：传统写法 vs enumerate 写法
    对比为什么 enumerate 更优雅
    """
    print("\n【示例3：对比传统写法】")

    fruits = ["apple", "banana", "orange"]

    print("传统写法：")
    for i in range(len(fruits)):
        print(f"索引：{i}，值：{fruits[i]}")

    print("\nenumerate 写法：")
    for i, v in enumerate(fruits):
        print(f"索引：{i}，值：{v}")


def example_4_iterating_string():
    """
    示例4：遍历字符串
    字符串也是可迭代对象
    """
    print("\n【示例4：遍历字符串】")

    text = "Python"

    for index, char in enumerate(text):
        print(f"索引：{index}，字符：{char}")

    # 输出说明：
    # 索引：0，字符：P
    # 索引：1，字符：y
    # 索引：2，字符：t
    # 索引：3，字符：h
    # 索引：4，字符：o
    # 索引：5，字符：n


def example_5_use_in_real_project():
    """
    示例5：在实际项目中的常见场景
    例如：打印日志编号、处理批量数据、生成序号
    """
    print("\n【示例5：实际项目场景】")

    tasks = ["读取数据", "清洗数据", "训练模型", "保存结果"]

    for step, task in enumerate(tasks, start=1):
        print(f"步骤 {step}：{task}")

    # 输出说明：
    # 步骤 1：读取数据
    # 步骤 2：清洗数据
    # 步骤 3：训练模型
    # 步骤 4：保存结果


def example_6_convert_to_list():
    """
    示例6：将 enumerate 对象转为 list
    enumerate 返回的是一个迭代器对象
    """
    print("\n【示例6：转换为 list】")

    fruits = ["apple", "banana", "orange"]

    enum_obj = enumerate(fruits)
    print(list(enum_obj))

    # 输出说明：
    # [(0, 'apple'), (1, 'banana'), (2, 'orange')]


if __name__ == "__main__":
    """
    主函数：依次运行所有示例
    """
    example_1_basic_usage()
    example_2_with_start_index()
    example_3_traditional_way_vs_enumerate()
    example_4_iterating_string()
    example_5_use_in_real_project()
    example_6_convert_to_list()
