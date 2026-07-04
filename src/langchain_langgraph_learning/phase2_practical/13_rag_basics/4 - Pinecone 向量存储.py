"""
一、什么是“向量存储”？
向量存储就是把向量存储到数据库中，以便于后续的检索和相似度计算。


二、工程实践如何选？

1. 小项目 / 学习 / PoC：
用 Pinecone / Qdrant Cloud 这种托管服务，或者本地 FAISS 都可以，先跑通流程最重要。
2. 公司内部、需要私有化部署：
通常会选 Qdrant / Milvus / Weaviate / pgvector 这类自建方案。
3. 已经大量用 Postgres / MySQL：
很多团队会偏向 直接给现有数据库加向量扩展，减少新组件。


三、Pinecone 是什么？

Pinecone 是一个托管的向量数据库（Vector Database）服务，用来高效存储、索引和检索向量嵌入（embeddings），主要用于“相似度搜索”和各种 RAG / 推荐 / 语义搜索场景。（Pinecone官网：https://www.pinecone.io/）

四、以下代码在做什么？

为 RAG 示例准备 Pinecone 环境——创建或连接名为 langchain-rag-demo 的 384 维、cosine 度量的 Serverless 索引，并返回索引名和 all-MiniLM-L6-v2 的 embeddings，为后续「文档 → 向量 → 存入 Pinecone → 检索」铺好路。

五、代码中嵌入模型 embeddings与Pinecone是如何建立起联系的？

在这段代码里，嵌入模型和 Pinecone 并没有直接“互相调用”，它们的对应关系是靠 【向量维度】 约定好的。
每个嵌入模型都会输出一个固定维度的向量，比如 all-MiniLM-L6-v2 模型输出 384 维向量，Qwen 模型输出 1024 维向量。这个维度必须与 Pinecone 索引的维度一致，否则无法存储和检索。
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

    print(f"索引配置：")
    print(f"名称：{index_name}")
    print(f"维度：{dimension}")
    print(f"类型：Serverless（免费层级）")

    # 获取所有索引名称
    existing_indexes = [idx.name for idx in pc.list_indexes()]

    # 如果索引不存在，则创建
    if index_name in existing_indexes:
        print(f"索引 {index_name} 已存在，直接使用")
        index = pc.Index(index_name)
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
# 主函数
# ===================================================================
def main():
    try:
        index_name, embeddings = example_4_pinecone_setup()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
