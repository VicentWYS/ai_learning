"""
LangChain 1.0 - 自定义工具（@tool 装饰器）
==============================================

本模块重点讲解：
1. 使用 @tool 装饰器创建工具（LangChain 1.0 推荐方式）
2. 工具的参数和文档字符串（docstring）的重要性
3. 测试工具
"""

import os
import sys


# Windows 终端编码支持
# 解决 Windows 终端中文乱码问题
# 背景：Windows 的 CMD / PowerShell 默认不是 UTF-8 编码
# Python 默认的 stdout、stderr 是按照 Windows 本地编码（GBK）输出的
# 这段代码强行把输出流重包一层，改成 UTF-8
# 意思是：“以后你往终端 print 的所有内容，统一按 UTF-8 输出”
if sys.platform == "win32":
    import io

    sys.stdou = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

# 导入自定义工具
from tools.weather import get_weather
from tools.calculator import calculator
from tools.web_search import web_search


# 加载环境变量
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")

if not QWEN_API_KEY or QWEN_API_KEY == "your_qwen_api_key_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_API_KEY\n"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key 获取免费密钥"
    )

if not QWEN_BASE_URL or QWEN_BASE_URL == "your_qwen_base_url_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_BASE_URL\n"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/model-market/detail/qwen-plus 获取适配 OpenAI 的 url"
    )


# 初始化模型
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ============================================================================
# 示例 1：创建第一个工具
# ============================================================================
def example_1_simple_tool():
    """
    示例1：使用 @tool 装饰器创建工具

    - 关键：
        1. 使用 @tool 装饰器
        2. 必须有 docstring（文档字符串）
        3. 参数要有类型注解
    """
    print("\n" + "=" * 40)
    print("示例1：创建第一个工具")
    print("=" * 40)

    @tool
    def get_current_time() -> str:
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("\n工具名称：", get_current_time.name)
    print("工具描述：", get_current_time.description)
    print("工具参数：", get_current_time.args)

    # 调用工具
    result = get_current_time.invoke({})
    # 被 @tool 装饰器装饰的函数会被转换为 LangChain 的 Tool 对象
    # 这个对象有 .invoke() 方法
    print(f"\n调用结果：{result}")

    print("\n💡 关键点：")
    print("  1. @tool 装饰器会自动提取函数名、docstring、参数")
    print("  2. docstring 很重要！AI 用它理解工具的功能")
    print("  3. 类型注解帮助 AI 理解参数类型")


# ============================================================================
# 示例 2：带参数的工具
# ============================================================================
def example_2_tool_with_params():
    """
    示例2：带参数的工具

    重点：参数的文档说明
    """
    print("\n" + "=" * 40)
    print("示例 2：带参数的工具")
    print("=" * 40)

    print("\n查看天气工具的信息：")
    print(f"名称：{get_weather.name}")
    print(f"描述：{get_weather.description}")
    print(f"参数：{get_weather.args}")

    # 测试工具
    print("\n测试工具：")
    result1 = get_weather.invoke({"city": "北京"})
    print(f"北京天气：{result1}")

    result2 = get_weather.invoke({"city": "上海"})
    print(f"上海天气：{result2}")

    print("\n💡 docstring 格式：")
    print(
        '''
    @tool
    def my_tool(param1: str) -> str:
        """
        工具的简短描述

        参数:
            param1: 参数说明

        返回:
            返回值说明
        """
    '''
    )


# ============================================================================
# 示例 3：多参数工具
# ============================================================================
def example_3_multiple_params():
    """
    示例3：多参数工具
    """
    print("\n" + "=" * 40)
    print("示例 3：多参数工具 - 计算器")
    print("=" * 40)

    print("\n计算器工具信息：")
    print(f"名称：{calculator.name}")
    print(f"描述：{calculator.description}")

    # 测试不同运算
    print("\n测试计算：")
    tests = [
        {"operation": "add", "a": 10, "b": 5},
        {"operation": "subtract", "a": 10, "b": 5},
        {"operation": "multiply", "a": 10, "b": 5},
        {"operation": "divide", "a": 10, "b": 5},
    ]

    for test in tests:
        result = calculator.invoke(test)
        print(f"{result}")


# ============================================================================
# 示例 4：可选参数工具
# ============================================================================
def example_4_optional_params():
    """
    示例4：可选参数

    使用 Optional[类型] 和默认值
    """
    print("\n" + "=" * 40)
    print("示例 4：可选参数 - 搜索工具")
    print("=" * 40)

    # 使用默认参数
    print("\n使用默认参数（返回 3 条结果）：")
    result1 = web_search.invoke({"query": "Python"})
    print(result1)

    # 指定参数
    print("\n指定返回 2 个结果：")
    result2 = web_search.invoke({"query": "LangChain", "num_results": 2})
    print(result2)


# ============================================================================
# 示例 5：工具绑定到模型（预览）
# ============================================================================
def example_5_bind_tools():
    """
    示例5：将工具绑定到模型

    这是让 AI 使用工具的第一步
    """
    print("\n" + "=" * 40)
    print("示例 5：工具绑定到模型（预览）")
    print("=" * 40)

    # 绑定工具到模型
    model_with_tools = model.bind_tools([get_weather, calculator])

    print("模型已绑定工具：")
    print(" - get_weather")
    print(" - calculator")

    # 调用模型（模型可以选择使用工具）
    print("\n测试：AI 是否会调用天气工具？")
    response = model_with_tools.invoke("北京今天天气怎么样？")

    # 检查模型是否要求调用工具
    if response.tool_calls:
        print(f"\nAI 决定使用工具！")
        print(f"工具调用：{response.tool_calls}")
    else:
        print(f"\nAI 直接回答（未使用工具）")
        print(f"回复：{response.content}")

    print("\n💡 下一步：")
    print("在 05_simple_agent 中，我们将学习如何让 AI 自动执行工具")


# ============================================================================
# 示例 6：工具的最佳实践
# ============================================================================
def example_6_best_practices():
    """
    示例6：工具开发最佳实践
    """
    print("\n" + "=" * 40)
    print("示例 6：工具开发最佳实践")
    print("=" * 40)

    print("\n✅ 好的工具设计：")
    print(
        """
1. 清晰的 docstring
   @tool
   def search_products(query: str, max_results: int = 10) -> str:
       '''
       在产品数据库中搜索产品

       参数:
           query: 搜索关键词
           max_results: 最大返回数量，默认10

       返回:
           产品列表的JSON字符串
       '''

2. 明确的参数类型
   - 使用类型注解：str, int, float, bool
   - 可选参数用 Optional[类型]

3. 返回字符串
   - 工具应该返回 str（AI 最容易理解）
   - 复杂数据可以返回 JSON 字符串

4. 错误处理
   - 在工具内部捕获异常
   - 返回友好的错误消息

5. 功能单一
   - 一个工具做一件事
   - 不要把多个功能塞进一个工具
    """
    )


# ============================================================================
# 主程序
# ============================================================================
def main():
    print("\n" + "=" * 80)
    print("LangChain 1.0 - 自定义工具")
    print("=" * 80)

    try:
        # example_1_simple_tool()
        # example_2_tool_with_params()
        # example_3_multiple_params()
        # example_4_optional_params()
        # example_5_bind_tools()
        example_6_best_practices()

        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)

        print("✅ 使用 @tool 装饰器创建工具")
        print("✅ 必须有清晰的 docstring")
        print("✅ 参数要有类型注解")
        print("✅ 工具返回字符串")

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
