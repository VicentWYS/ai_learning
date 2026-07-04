"""
可复用的提示词模板库
==============================================

这个文件包含常用的、经过优化的提示词模板
可以直接在项目中导入使用

使用方法：

from examples.template_library import TemplateLibrary

messages = TemplateLibrary.TRANSLATOR.format_messages(
    source_lang="英语",
    target_lang="中文",
    text="Hello World"
)
"""

from langchain_core.prompts import ChatPromptTemplate


class TemplateLibrary:
    """
    可复用的提示词模板库
    """

    # ========================================================================
    # 翻译类模板
    # ========================================================================
    TRANSLATOR = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一名专业的翻译专家，精通{source_lang}和{target_lang}。\n"
                "翻译要求：\n"
                "1. 准确传达原文意思\n"
                "2. 符合目标语言习惯\n"
                "3. 保持原文风格和语气",
            ),
            ("user", "请将以下{source_lang}文本翻译为{target_lang}:\n\n{text}"),
        ]
    )
    """
    翻译模板：

    变量：
        source_lang: 源语言（如：英语、中文）
        target_lang: 目标语言
        text: 要翻译的文本

    示例：
        messages = TRANSLATOR.format_messages(
            source_lang="英语",
            target_lang="中文",
            text="Hello, how are you?"
        )
    """


if __name__ == "__main__":
    """测试模板库"""

    print("\n" + "=" * 80)
    print("提示词模板库示例")
    print("=" * 80)

    # 示例1：翻译模板
    print("\n【示例1：翻译模板】")
    messages = TemplateLibrary.TRANSLATOR.format_messages(
        source_lang="中文", target_lang="英文", text="那个塞尔达荒野之息好玩吗？"
    )

    print("生成的提示词：")
    for msg in messages:
        print(f"{msg.type}: {msg.content[:100]}...")

    print("\n" + "=" * 80)
    print("提示：在实际项目中，直接导入使用这些模板")
    print("from examples.template_library import TemplateLibrary")
    print("=" * 80)
