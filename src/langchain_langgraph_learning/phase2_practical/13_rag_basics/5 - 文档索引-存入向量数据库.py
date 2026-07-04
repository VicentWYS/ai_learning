"""
- 这个脚本从业务角度在做什么？
用业务语言来讲，这个文件实现的是一个「把知识文档变成可被 AI 检索的企业知识库」的完整小流程，核心做了这几件事：

- 准备知识内容：
把一段关于 LangChain 和 RAG 的介绍文字，保存成一份本地文档，作为“企业知识”的示例来源。

- 把长文档拆成小知识块：
为了以后更精确地检索，它把整篇文档智能地切分成多个较小的“知识片段”（段落级/句子级的小块），并保留每块的元数据。

- 在向量数据库中创建一个“知识索引库”：
连接 Pinecone（向量数据库云服务），检查是否已有名为 langchain-rag-demo 的索引；如果没有就在线创建一个合适配置的索引，用来存储后续的“知识向量”。

- 把知识块转换成“可搜索的向量”并入库：
使用一个文本向量模型，将每个知识块转成向量表示，然后批量写入刚才创建好的 Pinecone 索引中，相当于完成了“建库 + 建索引”。

- 验证知识库是否能“按需回答问题”：
用一个业务问题（例如“LangChain 的核心组件是什么？”）去向量库里做相似度检索，拿回最相关的 2 个知识块，打印出来，验证这个知识库已经可以根据自然语言问题找到对应内容。

- 整体流程编排：
main() 函数把这几个步骤串起来：加载文档 → 分块 → 创建/连接向量索引 → 写入向量 → 测试检索，形成一个端到端的“构建 RAG 知识库 Demo 流程”。
从业务视角来看，这段代码本质上是在演示：如何把一份原始文本资料，自动加工成一个可被大模型检索和问答的“结构化知识库（向量知识库）”，为后续的智能问答、企业内部知识检索等场景打基础。
"""

import os
import time
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np


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

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY or PINECONE_API_KEY == "your_pinecone_api_key_here":
    print("\n[警告] 未设置 PINECONE_API_KEY")
    print("如需运行 Pinecone 相关示例，请：")
    print("1. 访问 https://www.pinecone.io/ 注册免费账号")
    print("2. 获取 API Key")
    print("3. 在 .env 文件中设置 PINECONE_API_KEY=你的key")
    print("\n当前将跳过需要 Pinecone 的示例\n")

    raise ValueError(
        "\n请先在 .env 文件中设置有效的 PINECONE_API_KEY"
        "访问 https://www.pinecone.io/ 获取免费密钥"
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
# 示例4 - Pinecone 向量存储 - 创建索引
# ===================================================================
def example_4_pinecone_setup():
    """
    示例4 - Pinecone 设置

    - 创建 Pinecone serverless 索引（免费层级），准备嵌入模型

    - 关键点:
        - Pinecone 提供免费 serverless 层级
        - dimension 必须与 embedding 模型匹配
        - metric='cosine' 用于相似度计算
        - ServerlessSpec 配置云和区域
    """
    print("\n" + "-" * 40)
    print("示例4 - Pinecone 向量存储 - 创建索引")

    # 检查 Pinecone API Key 是否设置
    if not PINECONE_API_KEY or PINECONE_API_KEY == "your_pinecone_api_key_here":
        print("\n[警告] 未设置 PINECONE_API_KEY")
        print("如需运行 Pinecone 相关示例，请：")
        print("1. 访问 https://www.pinecone.io/ 注册免费账号")
        print("2. 获取 API Key")
        print("3. 在 .env 文件中设置 PINECONE_API_KEY=你的key")
        print("\n当前将跳过需要 Pinecone 的示例\n")

        return None, None

    # 初始化 Pinecone 客户端
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # 索引配置
    index_name = "langchain-rag-demo"  # 索引名称
    dimension = 384  # 维度（与 all-MiniLM-L6-v2 模型维度一致）

    # 获取所有索引名称
    existing_indexes = [idx.name for idx in pc.list_indexes()]

    # 如果索引不存在，则创建
    if index_name in existing_indexes:
        print(f"索引 {index_name} 已存在，直接使用")
        index = pc.Index(index_name) # 获取索引对象
    else:
        # Pinecone 云端没有索引时，会先走这个分支来创建索引
        print("\n创建新索引...")
        pc.create_index(
            name=index_name,  # 设置人工命名
            dimension=dimension,  # 设置人工给定的向量维度
            metric="cosine",  # 相似度度量
            spec=ServerlessSpec(  # 免费层级配置
                cloud="aws",  # 云提供商
                region="us-east-1",  # 免费层级可用区域
            ),
        )

        # 等待索引创建完成
        print("等待索引初始化...")

        time.sleep(10)  # 等待10秒，让索引初始化完成
        index = pc.Index(index_name)  # 获取索引对象

        print(f"索引 {index_name} 创建完成")

    # 获取索引统计
    stats = index.describe_index_stats()
    print(f"\n索引统计：")
    # 0 是get()的默认值，如果索引统计中没有total_vector_count，则返回0
    # 'N/A' 是get()的默认值，如果索引统计中没有dimension，则返回'N/A'
    print(f"向量数量：{stats.get('total_vector_count', 0)}")
    print(f"维度：{stats.get('dimension', 'N/A')}")

    # 创建与之匹配的嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"  # 输出384维向量
    )

    return index_name, embeddings


# ===================================================================
# 示例5 - 文档索引-存入向量数据库
# ===================================================================
def example_5_index_documents(index_name, embeddings, chunks):
    """
    示例5 - 文档索引-存入向量数据库

    - 将文档分块后，转换为向量，并存入 Pinecone 索引

    - 关键点:
        - 将文档分块后，转换为向量
        - 将向量存入 Pinecone 索引
    """
    print("\n" + "-" * 40)
    print("示例5 - 文档索引-存入向量数据库")

    # 检查索引名称和嵌入模型是否配置
    if not index_name or not embeddings:
        print("\n需要配置索引名称和嵌入模型")
        return None

    print(f"准备索引{len(chunks)}个文档块")
    
    # 将文档分块后，转换为向量，并存入 Pinecone 索引
    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
    )
    print("文档已索引到 Pinecone")

    # 测试检索
    query = "LangChain 的核心组件是什么？"
    results = vectorstore.similarity_search(query, k=2)  # k=2 表示返回2个最相似的文档

    print(f"\n检索结果：返回了 {len(results)} 个最相似的文档块：\n")
    for i, result in enumerate(results, 1):
        print(f"\n第 {i} 个文档块：")
        print(f"内容：{result.page_content[:80]}...")

    return vectorstore


# ===================================================================
# 主函数
# ===================================================================
def main():
    try:
        # 文档加载
        documents = example_1_document_loaders()

        # 文本分割
        chunks = example_2_text_splitters(documents)

        # Pinecone 向量存储 - 创建索引
        index_name, embeddings = example_4_pinecone_setup()

        # 文档索引-存入向量数据库
        vectorstore = example_5_index_documents(index_name, embeddings, chunks)
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
