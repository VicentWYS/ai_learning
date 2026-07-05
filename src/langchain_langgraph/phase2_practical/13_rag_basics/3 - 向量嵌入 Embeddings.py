"""
什么是“向量嵌入”？

向量嵌入就是把“文字 / 图片 / 用户”等离散东西，转换成一串数字（一个高维向量），让计算机能用“数学上的距离”来衡量它们在语义上的相似程度。
"""

from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os
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

model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ===================================================================
# 示例3 - 向量嵌入 Embeddings
# ===================================================================
def example_3_embeddings():
    """
    示例3 - 向量嵌入 Embeddings

    - 将文本转换为向量，便于计算相似度

    - 关键点:
        - embed_query() - 嵌入单个查询
        - embed_documents() - 批量嵌入文档
        - 向量可用于相似度搜索
        - 相同主题的文本相似度更高
    """
    print("\n" + "-" * 40)
    print("示例3 - 向量嵌入 Embeddings")

    # 创建嵌入模型
    #
    # 这里向量的维度是 384，是模型定义的，不是我们自己定义的
    # 一般不推荐自己拍脑袋选一个维度再从头训练
    # 工程实践中更常见的做法是：直接选用成熟的预训练嵌入模型
    #
    # 维度只是这些模型的一个“结果参数”，你关注的更多是：
    # 效果：检索/推荐/聚类的质量
    # 成本：存储空间、向量库大小、检索延迟
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 嵌入单个文本
    text = "LangChain 是一个 LLM 应用框架"
    vector = embeddings.embed_query(text)  # list

    print(f"\n嵌入示例：")
    print(f"嵌入文本：{text}")
    print(f"向量维度：{len(vector)}")  # 384
    print(
        f"向量前 5 个值：{vector[:5]}"
    )  # [0.06574848294258118, 0.066452257335186, 0.08259231597185135, -0.0250190831720829, 0.006829605437815189]

    # 嵌入多个文本
    texts = [
        "LangChain 是一个框架",
        "Python 是一种编程语言",
        "LangChain 用于构建 LLM 应用",
    ]

    vectors = embeddings.embed_documents(texts)  # list

    print(f"\n批量嵌入：")
    print(f"文本数：{len(texts)}")  # 3：3个文本
    print(f"向量数：{len(vectors)}")  # 3：（对应）3个向量
    print(f"向量维度：{len(vectors[0])}")  # 384
    print(f"向量维度：{len(vectors[1])}")  # 384
    print(f"向量维度：{len(vectors[2])}")  # 384

    # 计算相似度（简单示例）
    def cosin_similarity(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    sim_01 = cosin_similarity(
        vectors[0], vectors[1]
    )  # 比较列表中第1个和第2个向量的相似度
    sim_02 = cosin_similarity(
        vectors[0], vectors[2]
    )  # 比较列表中第1个和第3个向量的相似度

    print(f"\n相似度计算：")
    print(f"文本1 和 文本2 的相似度：{sim_01:.4f}")
    print(f"文本1 和 文本3 的相似度：{sim_02:.4f}")
    print("相同主题的文本相似度更高")

    return embeddings


# ===================================================================
# 主函数
# ===================================================================
def main():
    try:
        embeddings = example_3_embeddings()
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
