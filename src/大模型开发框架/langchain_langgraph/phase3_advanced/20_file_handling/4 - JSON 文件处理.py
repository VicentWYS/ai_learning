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
import json

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
def create_sample_json_file():
    """创建示例 json 文件，保存到脚本同级的 files/json 目录"""

    script_dir = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
    files_dir = os.path.join(script_dir, "files/json")  # 创建目录
    os.makedirs(files_dir, exist_ok=True)  # 创建目录（若不存在）

    json_content = """{
    "company": "科技有限公司",
    "founded": 2020,
    "products": [
        {"name": "产品A", "price": 99.9, "category": "软件"},
        {"name": "产品B", "price": 199.9, "category": "服务"},
        {"name": "产品C", "price": 299.9, "category": "硬件"}
    ],
    "locations": ["北京", "上海", "深圳"]
}"""
    json_path = os.path.join(files_dir, "company.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(json_content)

    return json_path


# JSON 文件处理
def json_processing(json_path: str):
    """
    处理 JSON 文件
    """
    # 读取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 将 JSON 转为格式化文本
    formatted_json = json.dumps(data, ensure_ascii=False, indent=2)

    doc = Document(
        page_content=formatted_json,
        metadata={"source": json_path, "type": "json", "keys": list(data.keys())},
    )

    print("\nJSON 结构：")
    print(f"顶级键：{doc.metadata["keys"]}")
    print(f"\n内容预览：\n{formatted_json[:200]}")

    # 使用 LLM 理解 JSON 结构
    messages = [
        SystemMessage(
            content="你是一个数据结构专家。请解释这个 JSON 的结构和用途。用中文回答。"
        ),
        HumanMessage(content=f"JSON 内容：\n{formatted_json}"),
    ]

    response = model.invoke(messages)

    print(f"AI 回复：{response.content}")

    return doc


# 主函数
if __name__ == "__main__":
    # 创建示例文件
    json_path = create_sample_json_file()

    # 运行示例
    doc = json_processing(json_path)
