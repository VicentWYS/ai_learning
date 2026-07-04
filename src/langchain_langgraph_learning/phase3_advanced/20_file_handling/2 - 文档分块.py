"""
模块 20：文件处理

学习如何加载和处理各种文件类型
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter

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


# 辅助函数
def create_sample_txt_file():
    """创建示例 txt 文件，保存到脚本同级的 files/txt 目录"""

    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
    files_dir = os.path.join(script_dir, "files/txt")  # 创建目录
    os.makedirs(files_dir, exist_ok=True)  # 创建目录（若不存在）

    sample_text = """Seedance 2.0 目前并非独立的 App，而是直接嵌入字节头条旗下即梦、豆包等平台中，以工具的身份方便用户使用。需要注意的是，即梦 Seedance 2.0 于 2026 年 2 月 6 日全球首发，2 月 7 日起在字节即梦 AI 平台开放分阶段公测。获得体验资格的用户，在即梦 Web 端点选创作类型下拉菜单，选中“视频生成”后，再在模型下拉菜单中选择“Seedance 2.0”即可，而未获得体验资格的用户，则可绕道火山引擎的体验中心，同样能在第一时间体验到 Seedance 2.0（如图 1）。在实测环节，笔者直接使用了初中语文课本上朱自清《背影》的片段及文言文《狼》（选自蒲松龄《聊斋志异》）全文，分别测试 Seedance 2.0 对于现代文和文言文的理解。从生成结果看，Seedance 2.0 对细节的把控的确极为出色。朱自清《背影》中父亲“穿着黑布大马褂，深青布棉袍”的衣着与“过铁道时，他先将橘子散放在地上，自己慢慢爬下，再抱起橘子走”的一致性在 Seedance 2.0 视频中得到了很好的展现，特别是斑驳的石阶、因攀爬而褶皱的衣服都刻画得淋漓尽致。尤其让人惊喜的是，朱自清《背影》中并未提及父亲的鞋子，Seedance 2.0 选用的是非常符合父亲穿着及那个年代特色的棉布鞋，甚至通过被撑大的鞋子来体现父亲的脚不好，细节考虑之周到，令笔者叹服（如图 2）。而对于《狼》一文的理解同样到位，且非常准确地用面部特写和背景虚化体现了屠夫的惊恐，对于希望用视频课件帮助孩子理解文言文的老师而言，Seedance 2.0 会是相当不错的助手。"""

    # 创建示例 txt 文件
    txt_path = os.path.join(files_dir, "gen_videos_model_intro.txt")

    # 将示例文本写入、保存到文件
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(sample_text)

    return txt_path


# 文档分块
def document_chunking(txt_path: str):
    """
    将长文档分割成小块
    """
    # 读取文件
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc = Document(page_content=content, metadata={"source": txt_path})

    # 创建文本分割器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", " "],
        length_function=len,
    )

    # 分割文档
    chunks = splitter.split_documents([doc])

    print(f"原文档长度：{len(content)} 个字符")
    print(f"分割成： {len(chunks)} 个块")
    print("每个块的信息：")

    for i, chunk in enumerate(chunks[:5]):  # 只显示前 5 个
        print(f"块：{i+1}: {len(chunk.page_content)} 个字符")
        print(f"开头：{chunk.page_content[:50]}...")

    if len(chunks) > 5:
        print(f"...还有 {len(chunks)-5} 个块")

    return chunks


# 主函数
if __name__ == "__main__":
    # 创建示例文件
    txt_path = create_sample_txt_file()

    # 运行示例
    chunks = document_chunking(txt_path)
