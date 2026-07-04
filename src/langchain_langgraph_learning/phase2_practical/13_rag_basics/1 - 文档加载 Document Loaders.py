from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os


# 加载环境变量
load_dotenv()

QWEN_API_KEY = os.getenv("QWEN_API_KEY")
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL")

if not QWEN_API_KEY or QWEN_API_KEY == "your_qwen_api_key_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_API_KEY"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/api-key 获取免费密钥"
    )

if not QWEN_BASE_URL or QWEN_BASE_URL == "your_qwen_base_url_here":
    raise ValueError(
        "\n请先在 .env 文件中设置有效的 QWEN_BASE_URL"
        "访问 https://bailian.console.aliyun.com/cn-beijing/?tab=model#/model-market/detail/qwen-plus 获取适配 OpenAI 的 url"
    )

model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# 获取脚本所在目录
# __file__ 是当前文件的绝对路径
# 在当前文件的父目录下创建一个 data 目录
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"


# 确保 data 目录存在
# parents=True 表示创建父目录，
# exist_ok=True 表示如果目录已存在，则不创建
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ===================================================================
# 示例1：文档加载 Document Loaders
# ===================================================================
def example_1_document_loaders():
    """
    示例1：文档加载 Document Loaders

    - Document Loaders 是 LangChain 中用于加载文档的组件。
    - 它可以将各种数据源（如文本文件、PDF、Word 文档、CSV、JSON 等）加载为 LangChain 可以理解的格式。
    """
    print("\n" + "-" * 40)
    print("示例1：文档加载 Document Loaders")

    # 创建一个实例文本
    sample_text = """LangChain 是一个用于构建 LLM 应用的框架。

它提供了以下核心组件：
1. Models - 语言模型接口
2. Prompts - 提示词模板
3. Chains - 链式调用
4. Agents - 智能代理
5. Memory - 记忆管理

LangChain 1.0 引入了重大改进，包括：
- 更简洁的 API
- 更好的性能
- 内置的 LangGraph 支持
- 强大的中间件系统

RAG (Retrieval-Augmented Generation) 是 LangChain 的核心应用场景之一。
它结合了检索和生成，让 LLM 能够访问外部知识库。"""

    # 将示例文本写入、保存到文件
    doc_path = DATA_DIR / "langchain_intro.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(sample_text)

    print(f"示例文本已保存到：{doc_path}")

    # 使用 TextLoader 加载文件
    loader = TextLoader(doc_path, encoding="utf-8")
    documents = loader.load()  # list

    print("\n加载结果：")
    for i, doc in enumerate(documents, 1):
        print(f"\n文档 {i}：")
        print(f"文档内容预览：{doc.page_content[:100]}...")
        print(
            f"文档元数据：{doc.metadata}"
        )  # {'source': 'd:\\Me\\Project\\langchain_learning_me\\langchain_learning_me\\phase2_practical\\13_rag_basics\\data\\langchain_intro.txt'}
        print(f"内容长度：{len(doc.page_content)}")

    # 返回加载的文档列表，供后续文本分割使用
    return documents


# ===================================================================
# 主程序
# ===================================================================
def main():
    try:
        example_1_document_loaders()

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
