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
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.agents import create_agent
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings


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
    """
    print("\n" + "-" * 40)
    print("示例1：文档加载 Document Loaders")

    sample_text = """## 前言
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

## 拥抱自然语言编程时代
锚定生产逻辑的变化后，人才培养就出现了新方向——未来市场需要的不再是会敲代码的人，而是会用AI解决复杂问题的人。

目前高校的计算机课程以Java、C++等编程语言为主，但随着AI生成代码的占比加速扩大，初级程序员岗位需求骤降，加之应届毕业生的实习经验有限，对代码之外的岗位内容所涉不深，求职时将面临更残酷的优胜劣汰。

那么培养体系的优化方向在哪？

首先是提高产品思维，它的作用是将用户需求翻译并体现在功能设计上，回答用户要什么，以及业务为何这样做的问题；其次是架构与工程能力，如何根据产品定位来搭建系统。对应在课程内容上，就是压缩编程语言语法的占比，将更多资源倾向需求分析和架构基础，补充提示词工程、智能体调度等课程，培养学生给AI定规则和校验AI产出结果的能力。这些革新的本质，是在提高从业者对AI的驾驭能力，学会做AI的管理者。

课程模式之外，还需兼顾实践模式的创新，例如校企合作开发中小体量的智能化平台，让高校学生从自身需求入手感知软件工程的落地。

最关键的在于，打破对技术门槛的固有认知，重新定义职业竞争力。自然语言编程时代来临，编程语言不再是软件开发的必需品，随着GitHub Copilot、Cursor、通义灵码等AI编程工具不断渗透，人人都能化身程序员。在工具不断迭代升级的背景下，唯一可确定的是人类的生产主体性，这也是软件工程转型的核心前提。

有从业者悲观地认为：“各行各业的Agent都在不断涌现，真正到了不需要程序员那天，指挥AI的又何必是人呢？”但这种说法忽略了一点，即风险与收益永远成正比。

一位专做产品观察的业内人士指出：“当你的速度提升10倍时，你面临的风 险和瓶颈，可能也放大了10倍。”AI虽然改变了软件工程的生产效益，颠覆了以往的业务模式，但想要驾驭这部分上涨的生产力，需要提供足以与之匹配的开发体系和风险应对机制，而这一切依然需要人类来主导完善。

## 编辑点评：
黄仁勋用“AI工厂”来定义智能时代的未来，他认为这个工厂将通过向各行各业注入数字劳动力来颠覆价值创造，以1万亿美元的IT产业规模去撬动百倍的全球经济体量。这一说法印证了，AI时代的机会并不在IT行业本身，而是以数字劳动力为媒介，奔向更广阔的实体产业。从业者需要跳出纯技术视角，懂业务、懂场景，才能在这个融合趋势中抓住属于自己的机会。对软件人才而言，当前最紧要的任务是在AI带来的“创造性破坏”中寻找未来，前路已开，恐慌者看见终结，远见者看见重生。"""

    # 将示例文本写入、保存到文件
    doc_path = DATA_DIR / "langchain_intro.txt"
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(sample_text)

    print(f"示例文本已保存到：{doc_path}")

    # 使用 TextLoader 加载文件
    loader = TextLoader(doc_path, encoding="utf-8")
    documents = loader.load()  # list

    return documents


# ===================================================================
# 示例2 - 文本分割 Text Splitters
# ===================================================================
def example_2_text_splitters(documents):
    """
    示例2 - 文本分割 Text Splitters
    """
    print("\n" + "-" * 40)
    print("示例2 - 文本分割 Text Splitters")

    # 创建分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,  # 每个小块的字符数
        chunk_overlap=50,  # 每个小块之间的重叠字符数，防止分割后的文本片段之间丢失信息
        length_function=len,  # 计算字符长度的函数
        separators=[
            "\n\n",
            "\n",
            " ",
            "。",
            "！",
            "？",
            "",
        ],  # 告诉分割器应该优先按哪些符号去切分文本
    )

    # 分割文档
    chunks = splitter.split_documents(documents)  # list

    return chunks


# ===================================================================
# 示例4 - Pinecone 向量存储 - 创建索引
# ===================================================================
def example_4_pinecone_setup():
    """
    示例4 - Pinecone 设置

    - 创建 Pinecone serverless 索引（免费层级），准备嵌入模型
    """
    print("\n" + "-" * 40)
    print("示例4 - Pinecone 向量存储 - 创建索引")

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
        index = pc.Index(index_name)  # 获取索引对象
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

    return vectorstore


# ===================================================================
# 示例6 - RAG 问答_使用检索工具
# ===================================================================
def example_6_rag_question_answer(vectorstore):
    """
    示例6 - RAG 问答_使用检索工具

    - 将向量存储转为工具，供 Agent 使用

    - 关键点:
      - 将 vectorstore 封装为工具
      - Agent 自动调用工具检索
      - 基于检索结果生成答案
      - 这就是 RAG (检索增强生成)
    """
    print("\n" + "-" * 40)
    print("示例6 - RAG 问答_使用检索工具")

    if not vectorstore:
        print("\n需要配置向量存储 Pinecone vectorstore")
        return

    # 创建检索工具
    @tool
    def search_knowledge_base(query: str) -> str:
        """
        在知识库中搜索相关信息
        """
        docs = vectorstore.similarity_search(query, k=3)
        return "\n\n".join([doc.page_content for doc in docs])

    # 创建 Agent
    agent = create_agent(
        model=model,
        tools=[search_knowledge_base],
        system_prompt="""你是一个助手，可以访问知识库。
当用户提问时：
1. 必须使用 search_knowledge_base 工具搜索相关信息
2. 基于搜索结果回答问题
3. 如果知识库中没有相关信息，诚实告知""",
    )

    # 测试问答
    questions = [
        "黄仁勋关于写代码的看法是什么？",
        "在AI时代的软件工程转型中，程序员的作用是什么？",
        "高校计算机课程的培养方向应该如何调整？",
    ]

    for question in questions:
        print(f"\n问题：{question}")
        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )
            print(f"\nAgent 回复：{response["messages"][-1].content}")
        except Exception as e:
            print(f"\n错误：{str(e)[:100]}...")
            print("解决方案：1)重试 2)使用英文提问 3)换用其他模型")


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

        # RAG 问答
        example_6_rag_question_answer(vectorstore)
    except KeyboardInterrupt:
        print("\n\n程序中断")
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
