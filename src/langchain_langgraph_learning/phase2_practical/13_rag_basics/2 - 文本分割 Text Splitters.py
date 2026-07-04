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
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"

# 确保 data 目录存在
DATA_DIR.mkdir(exist_ok=True)


# ===================================================================
# 文档加载 Document Loaders
# ===================================================================
def example_1_document_loaders():
    """
    文档加载 Document Loaders

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
# 示例2 - 文本分割 Text Splitters
# ===================================================================
def example_2_text_splitters(documents):
    """
    示例2 - 文本分割 Text Splitters

    - 将长文档分割成多个小块，便于嵌入和检索
    - 分割优先级: 段落 -> 行 -> 句子 -> 空格 -> 字符

    - 关键点:
      - chunk_size 控制块大小
      - chunk_overlap 防止信息被截断
      - separators 定义分割优先级
      - RecursiveCharacterTextSplitter 智能分割
    """
    print("\n" + "-" * 40)
    print("示例2 - 文本分割 Text Splitters")

    # 创建分割器
    # separators 是一个从“粗”到“细”的分割优先级列表，分割时会按顺序尝试：
    # "\n\n"：优先按“空行”（段落）切；
    # "\n"：不行再按“单换行”切；
    # " "：再按空格切（单词级别）；
    # ""：最后退化为按单个字符强制切分；
    # "。", "！", "？"：再加上中文句号、感叹号、问号作为额外的切分点（帮助在中文里尽量按句子边界拆分）。
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,  # 每个小块的字符数
        chunk_overlap=50,  # 每个小块之间的重叠字符数，防止分割后的文本片段之间丢失信息
        length_function=len,  # 计算字符长度的函数
        separators=[
            "\n\n",
            "\n",
            " ",
            "",
            "。",
            "！",
            "？",
        ],  # 告诉分割器应该优先按哪些符号去切分文本
    )

    # 分割文档
    chunks = splitter.split_documents(documents)  # list

    print(f"\n分割结果：")
    print(f"原文档个数：{len(documents)}")
    print(f"分割后的小块数量：{len(chunks)}")

    print("\n前 3 块内容：")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"\n第 {i} 块内容：")
        print(f"内容：{chunk.page_content[:80]}")
        print(f"内容长度：{len(chunk.page_content)}")
        print(f"元数据：{chunk.metadata}")

    # 返回分割后的小块
    return chunks


# ===================================================================
# 主函数
# ===================================================================
def main():
    try:
        documents = example_1_document_loaders()
        chunks = example_2_text_splitters(documents)

    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
