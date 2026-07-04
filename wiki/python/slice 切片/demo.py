# file: slice_usage_examples.py
"""
本文件用于演示 Python 中切片（slice）语法的常见用法

重点关注类似：
    [:100]
    [start:end]
    [start:end:step]

切片常用于：
- 字符串截断（日志、摘要）
- 列表取子集
- 数据预览
"""


def example_1_string_slice():
    """
    示例 1：字符串切片 [:100]

    使用场景：
    - 控制日志输出长度
    - 显示文本摘要
    """
    print("\n" + "=" * 40)
    print("示例 1：字符串切片 [:100]")
    print("=" * 40)

    text = (
        "LangChain 是一个用于构建基于大语言模型（LLM）应用的框架，"
        "它提供了 Prompt、模型封装、链式调用、Agent 等能力，"
        "能够帮助开发者更高效地构建 AI 应用。"
    )

    preview = text[:100]

    print("原始字符串长度：", len(text))
    print("切片后字符串：", preview)
    # 说明：[:100] 表示从索引 0 开始，最多取 100 个字符
    # 如果字符串长度不足 100，不会报错，直接返回全部内容


def example_2_list_slice():
    """
    示例 2：列表切片 [start:end]

    使用场景：
    - 取前 N 条数据
    - 分页处理
    """
    print("\n" + "=" * 40)
    print("示例 2：列表切片 [start:end]")
    print("=" * 40)

    numbers = list(range(20))  # [0, 1, 2, ..., 19]

    first_five = numbers[:5]
    middle_part = numbers[5:10]

    print("原始列表：", numbers)
    print("前 5 个元素：", first_five)  # [0, 1, 2, 3, 4]
    print("第 6 到第 10 个元素：", middle_part)  # [5, 6, 7, 8, 9]


def example_3_negative_slice():
    """
    示例 3：负索引切片

    使用场景：
    - 取末尾数据
    - 查看最近的日志
    """
    print("\n" + "=" * 40)
    print("示例 3：负索引切片")
    print("=" * 40)

    logs = [
        "INFO: start service",
        "INFO: load config",
        "WARNING: config deprecated",
        "INFO: service running",
        "ERROR: connection timeout",
    ]

    last_two_logs = logs[-2:]

    print("所有日志：", logs)
    print("最近两条日志：", last_two_logs)
    # 说明：[-2:] 表示从倒数第 2 个元素开始，一直到结尾


def example_4_slice_with_step():
    """
    示例 4：带步长的切片 [start:end:step]

    使用场景：
    - 间隔取值
    - 数据采样
    """
    print("\n" + "=" * 40)
    print("示例 4：切片步长 [start:end:step]")
    print("=" * 40)

    numbers = list(range(10))

    even_index_numbers = numbers[::2]
    reverse_numbers = numbers[::-1]

    print("原始列表：", numbers)
    print("每隔一个取一个：", even_index_numbers)
    # 说明：step=2，表示每两个元素取一个

    print("反转列表：", reverse_numbers)
    # 说明：step=-1，表示从后往前取


def example_5_real_project_style():
    """
    示例 5：真实项目风格示例（结合 LLM 输出）

    使用场景：
    - 防止大模型输出过长
    - 控制终端打印长度
    """
    print("\n" + "=" * 40)
    print("示例 5：真实项目中的 [:100] 用法")
    print("=" * 40)

    llm_response = (
        "在智能体系统中，Agent 通常具备感知、决策和执行能力，"
        "能够基于环境反馈不断调整自身行为，从而完成复杂任务。"
        "智能体的核心在于其规划能力和工具使用能力。"
    )

    print("完整输出：")
    print(llm_response)

    print("\n限制长度后的输出：")
    print(llm_response[:100] + "...")
    # 说明：
    # - [:100] 控制最大输出长度
    # - + "..." 用于提示内容被截断


if __name__ == "__main__":
    example_1_string_slice()
    example_2_list_slice()
    example_3_negative_slice()
    example_4_slice_with_step()
    example_5_real_project_style()
