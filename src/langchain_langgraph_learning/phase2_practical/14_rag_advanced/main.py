"""
LangChain 1.0 - RAG Advanced (RAG 进阶)
=======================================

本模块重点讲解：
1. 混合搜索 (Hybrid Search) - BM25 + 向量搜索
2. EnsembleRetriever - 组合多个检索器
3. 检索对比 - 向量 vs 关键词 vs 混合
4. 参数优化 - 权重调整和 k 值选择
"""

import os
from pathlib import Path
import time

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.document_loaders import TextLoader
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

# 获取脚本所在目录
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
CHROMA_DIR = SCRIPT_DIR / "chromadb"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)  # exist_ok=True 表示如果目录已存在，则不创建
CHROMA_DIR.mkdir(exist_ok=True)

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

# 初始化模型
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ========================================= 1. 准备测试数据 =========================================
def example_1_prepare_data():
    """
    准备测试数据

    - 创建包含多种信息的测试文档，用于演示不同检索方法的效果
    """
    print("\n" + "-" * 40 + " 准备测试数据" + "-" * 40 + "\n")

    # 创建测试文档
    documents_text = """
## 前言
AI驱动的价值重构，与软件产业的曲折前进交叠，加剧了行业震荡，伴随着与日俱增的裁员数量，不少从业者在不确定的未来中坠入恐慌。

正如英伟达创始人兼 CEO 黄仁勋在与思科 CEO 查克·罗宾斯的对话直播中说的那样：“写代码本质上就是打字，已经不值钱了。”当以往那套技术范式因为 AI 的强势介入不再奏效，再花金钱和时间精力去培养一个可被替代的人才，就变得毫无性价比。

事实上，AI对程序员的替代危机，不仅仅是能写代码这么简单，它重构的是包括计算范式、软件形态、组织架构等在内的整套生产逻辑。于是，市场的人力资源需求以及对应的人才培养方向也由此被颠覆。当传统模式走向崩塌，产业与教育的出路又在何方？

## 从“写代码”到“管代码”

既然AI已经能编写代码，甚至解决大部分日常代码需求，那么人工的作用还剩下什么？我们又该培养怎样的软件人才？

AI的能力边界在于“把事做对”，也就是完成理解指令、根据指令写代码，至多再保证较高水平的正确率，但代码实现只是产业价值创造的一部分，剩下的人类不可被替代的部分在于“做对的事”，即判断哪些事是对的、有益于业务发展的。具体而言，就是把控方向，从而将模糊的需求转换为清晰的技术问题并提出解决方案。

处理模糊的需求得理解用户真正的痛点是，再结合企业的资源和盈利目标设计业务模式，面对风云变幻的市场进行战略选择，判断某个功能或某项业务要不要做、值不值得做，会面临什么风险。即使AI可以在代码实现上100%替代人类，这些需求对接、业务架构设计、审核与调试、交互体验优化、风控把握，还有软件上线后出现的各种复杂的售后问题，也都需要程序员来兜底。

另一方面，AI只能基于已有的数据生成代码，即使可以组合出看似全新的代码结构，但其灵感仍来自自己已有的知识和模式，而市场的应用需求是不断演变深化的，面对全新的、从未出现过的技术问题时，其准确率就会受到严重影响，这就需要人类不断创新，包括但不限于新的架构、新的算法、新的场景开发、新的行业方案等等等。

由此，程序员的工作重心就转向这些人类似乎无法被替代的环节，梳理清楚技术方案后，只用给AI下达指令，再审查它输出的结果即可。这种变化使程序员的任务中增加了不少原本属于产品经理的内容，当AI把写代码的环节压缩后，节省出的人力资源开始向上下游两边移动，原本的岗位边界被打破，开发流程从过去“产品→研发→测试→运维”的流水线分工，转向闭环化的协同融合。

例如，前期的需求环节不再是产品人员单独写长篇文档定义需求，技术方的加入可以提前过滤掉不可行、逻辑矛盾的需求；研发环节变为定规范、接口、安全、模块边界，让AI在规则内干活；测试和运维环节，大量重复性工作交给AI自动化，程序员只负责设计极端场景、代码审查、把控风险、保证稳定。协作模式也出现新变化，大团队拆小，串联变并联，沟通成本降低，迭代速度迅速提升。
    """

    # 保存文档
    doc_path = DATA_DIR / "test_document.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(documents_text)

    print(f"测试文档已保存到：{doc_path}")
    print(f"文档长度：{len(documents_text)}")

    # 加载和分割
    loader = TextLoader(doc_path, encoding="utf-8")
    documents = loader.load()

    # 创建分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""],
    )

    # 切成小块
    chunks = splitter.split_documents(documents)

    print(f"\n分割结果：")
    print(f"原文档：{len(documents)}")
    print(f"分割后：{len(chunks)} 块")

    print("\n前 3 块内容：")
    for i, chunk in enumerate(chunks[:3], 1):
        preview = chunk.page_content[:80].replace("\n", " ")
        print(f"块 {i}：{preview}...")

    return chunks


# ========================================= 2. 向量检索器（语义搜索） =========================================
def example_2_vector_retriever(chunks):
    """
    示例2 - 向量检索器

    使用向量嵌入进行语义搜索
    """
    print("\n" + "-" * 40 + "向量检索" + "-" * 40 + "\n")

    # 创建嵌入模型
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # 创建 Chroma 向量存储
    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=embeddings, persist_directory=str(CHROMA_DIR)
    )

    # 创建检索器
    vector_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )  # k=3 表示返回3个最相似的文档

    # 测试检索
    test_queries = [
        "AI 驱动的价值重构体现在哪些方面？",
        "从“写代码”到“管代码”的转变中，程序员的角色发生了哪些变化？",
        "AI 对程序员的替代危机具体体现在哪些方面？",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n测试第 {i} 个查询：{query}")
        results = vector_retriever.invoke(query)
        print(f"\n检索结果：返回了 {len(results)} 个最相似的文档块：\n")
        if results:
            preview = results[0].page_content[:80].replace("\n", " ")
            print(f"相似块：{preview}...")

    return vector_retriever, vectorstore


# ========================================= 3. BM25 检索器（关键词搜索） =========================================
def example_3_bm25_retriever(chunks):
    """
    示例3 - BM25 检索器

    使用关键词搜索

    BM25 是一种基于关键词的检索方法，它通过计算关键词与文档的相似度来检索文档。
    """
    print("\n" + "-" * 40 + "BM25 检索" + "-" * 40 + "\n")

    # 创建 BM25 检索器
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = 3  # k=3 表示返回3个最相似的文档

    # 测试查询
    test_queries = [
        "AI 驱动的价值重构体现在哪些方面？",
        "从“写代码”到“管代码”的转变中，程序员的角色发生了哪些变化？",
        "AI 对程序员的替代危机具体体现在哪些方面？",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n测试第 {i} 个查询：{query}")
        results = bm25_retriever.invoke(query)
        print(f"\n检索结果：返回了 {len(results)} 个最相似的文档块：\n")
        if results:
            preview = results[0].page_content[:80].replace("\n", " ")
            print(f"相似块：{preview}...")

    return bm25_retriever


# ========================================= 4. 混合检索器（BM25 + 向量搜索） =========================================
def example_4_ensemble_retriever(vector_retriever, bm25_retriever):
    """
    示例4 - 混合检索器

    - 组合向量搜索和 BM25，使用 RRF (Reciprocal Rank Fusion) 算法
        - 1. 向量搜索: 擅长语义理解、同义词、概念
        - 2. BM25 搜索: 擅长精确匹配、专有名词、代码
        - 3. RRF 算法: 融合两者的排名结果

    - 权重说明：
        - weights=[0.5, 0.5] - 平衡
        - weights=[0.7, 0.3] - 偏向向量
        - weights=[0.3, 0.7] - 偏向 BM25

    - 关键点:
        - 混合检索结合了两者的优势
        - 对大多数查询都能获得更好的结果
        - 适用于生产环境
    """
    print("\n" + "-" * 40 + "混合检索器" + "-" * 40 + "\n")

    # 创建混合检索器
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.4, 0.6],  # 稍微偏向向量搜索
    )

    # 对比测试
    test_queries = [
        ("语义查询", "AI 驱动的价值重构体现在哪些方面？"),
        ("精确匹配", "从“写代码”到“管代码”的转变中，程序员的角色发生了哪些变化？"),
        ("混合查询", "AI 对程序员的替代危机具体体现在哪些方面？"),
    ]

    print("\n对比测试：")
    for query_type, query in test_queries:
        print(f"\n[{query_type}]: {query}")

        # BM25 结果
        bm25_results = bm25_retriever.invoke(query)
        bm25_preview = (
            bm25_results[0].page_content[:80].replace("\n", " ")
            if bm25_results
            else "无"
        )

        # 向量结果
        vector_results = vector_retriever.invoke(query)
        vector_preview = (
            vector_results[0].page_content[:80].replace("\n", " ")
            if vector_results
            else "无"
        )

        # 混合结果
        ensemble_results = ensemble_retriever.invoke(query)
        ensemble_preview = (
            ensemble_results[0].page_content[:80].replace("\n", " ")
            if ensemble_results
            else "无"
        )

        print(f"\nBM25 结果：{bm25_preview}...")
        print(f"向量结果：{vector_preview}...")
        print(f"混合结果：{ensemble_preview}...")

    return ensemble_retriever


# ========================================= 5. 权重优化实验 =========================================
def example_5_weight_optimization(vector_retriever, bm25_retriever):
    """
    示例5 - 权重优化

    - 测试不同权重配置的效果

    - 推荐配置:
        - 技术文档: [0.4, 0.6] - 稍偏向语义
        - 代码搜索: [0.6, 0.4] - 稍偏向精确匹配
        - 通用场景: [0.5, 0.5] - 平衡
    """
    print("\n" + "-" * 40 + "权重优化实验" + "-" * 40 + "\n")

    weight_configs = [
        (0.0, 1.0, "纯向量"),
        (0.3, 0.7, "偏向向量"),
        (0.5, 0.5, "平衡"),
        (0.7, 0.3, "偏向 BM25"),
        (1.0, 0.0, "纯 BM25"),
    ]

    test_query = "AI 驱动的价值重构体现在哪些方面？"

    for bm25_weight, vector_weight, desc in weight_configs:
        ensemble = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[bm25_weight, vector_weight],
        )

        results = ensemble.invoke(test_query)
        if results:
            preview = results[0].page_content[:60].replace("\n", " ")
            print(f"\n {desc} [{bm25_weight:.1f}, {vector_weight:.1f}]:")
            print(f"最相关：{preview}...")


# ========================================= 6. RAG Agent with Hybrid Search =========================================
def example_6_rag_agent_hybrid(ensemble_retriever):
    """
    示例6 - 使用混合检索的 RAG Agent

    - 将混合检索集成到 Agent 中

    - 关键点:
        - 混合检索提供更全面的上下文
        - 同时覆盖语义和精确匹配
        - 提高 RAG 系统的准确性和鲁棒性
    """
    print("\n" + "-" * 40 + "RAG Agent with Hybrid Search" + "-" * 40 + "\n")

    # 创建检索工具
    @tool
    def search_knowledge_base(query: str) -> str:
        """
        在知识库中搜索相关信息（混合检索）
        """
        docs = ensemble_retriever.invoke(query)
        return "\n\n".join([doc.page_content for doc in docs[:2]])  # 只取前2个

    # 创建 Agent
    agent = create_agent(
        model=model,
        tools=[search_knowledge_base],
        system_prompt="""
你是一个 LangChain 专家助手。

必须使用 search_knowledge_base 工具搜索相关信息，然后回答问题。

注意：
1. 优先使用检索到的信息
2. 如果信息不足，诚实告知
3. 回答要简洁准确
        """,
    )

    # 测试问答
    questions = [
        "AI 驱动的价值重构体现在哪些方面？",
        "从“写代码”到“管代码”的转变中，程序员的角色发生了哪些变化？",
    ]

    for question in questions:
        print(f"问题：{question}")
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )

            print(f"Agent 回复：{response["messages"][-1].content}\n")
        except Exception as e:
            print(f"[错误] 查询失败\n")
            print(f"错误：{e}")


# ========================================= 主函数 =========================================
def main():
    """
    主函数
    """
    try:
        # 准备数据
        chunks = example_1_prepare_data()

        # 向量检索
        vector_retriever, vectorstore = example_2_vector_retriever(chunks)
        bm25_retriever = example_3_bm25_retriever(chunks)

        # 混合检索
        ensemble_retriever = example_4_ensemble_retriever(
            vector_retriever, bm25_retriever
        )

        # 权重优化
        example_5_weight_optimization(vector_retriever, bm25_retriever)

        # RAG Agent
        example_6_rag_agent_hybrid(ensemble_retriever)
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n\n程序结束")


if __name__ == "__main__":
    main()
