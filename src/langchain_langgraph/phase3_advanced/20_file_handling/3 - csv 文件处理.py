"""
模块 20：文件处理

学习如何加载和处理各种文件类型
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core import documents
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.runnables.config import P
from langchain_text_splitters import RecursiveCharacterTextSplitter
import csv

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
def create_sample_csv_file():
    """创建示例 csv 文件，保存到脚本同级的 files/csv 目录"""

    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
    files_dir = os.path.join(script_dir, "files/csv")  # 创建目录
    os.makedirs(files_dir, exist_ok=True)  # 创建目录（若不存在）

    csv_content = """姓名,年龄,城市,职业
张三,28,北京,工程师
李四,32,上海,产品经理
王五,25,广州,设计师
赵六,35,深圳,数据分析师
"""
    csv_path = os.path.join(files_dir, "employees.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)

    return csv_path


# csv 文件处理
def csv_processing(csv_path: str):
    """
    处理 csv 文件
    """
    # 读取 csv
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 将每行转为 Document
    documents = []
    for i, row in enumerate(rows):
        doc = Document(
            page_content=str(row), metadata={"source": csv_path, "row": i + 1}
        )
        documents.append(doc)

    print(f"已加载：{len(documents)} 条记录")

    print("\n前 3 条记录：")
    for doc in documents[:3]:
        print(f"第 {doc.metadata["row"]} 行：{doc.page_content}")

    # 使用 LLM 分析 csv 数据
    csv_content = "\n".join([doc.page_content for doc in documents])

    messages = [
        SystemMessage(
            content="你是一个数据分析专家。请分析以下数据并给出见解。用中文回答。"
        ),
        HumanMessage(content=f"数据内容：\n{csv_content}"),
    ]

    response = model.invoke(messages)
    print(f"\nAI 分析：{response.content}")

    return documents


# 主函数
if __name__ == "__main__":
    # 创建示例文件
    csv_path = create_sample_csv_file()

    # 运行示例
    documents = csv_processing(csv_path)
