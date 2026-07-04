"""
模块 19：图像输入
学习如何使用视觉模型处理图像

重要提示：
1. 本模块需要支持视觉的模型
2. 请在 images/ 目录下放置你自己的测试图片

使用前准备：
1. 在 images/ 目录下放置以下图片（或使用你自己的图片）:
   - sample.jpg: 任意测试图片
   - text_image.jpg: 包含文字的图片（用于OCR测试）
   - chart.jpg: 图表图片（用于图表分析）
"""

import base64
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from pathlib import Path
from langchain_core.messages import HumanMessage


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
    model="qwen3.5-flash",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)

# 图片目录
IMAGES_DIR = Path(__file__).parent / "images"


# 辅助函数
def encode_image_to_base64(image_path: str) -> str:
    """
    将本地图像编码为 base64

    # 从磁盘读入一张图片，并返回其 Base64 文本（不含 data: 前缀），供后续把图片以文本形式传给需要 Base64 的接口（例如视觉模型）
    """
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")


def get_mime_type(image_path: str) -> str:
    """ """
    # 从路径里取出扩展名（如 .jpg、.PNG），并统一成小写
    ext = Path(image_path).suffix.lower()

    # mime_types 字典，把常见图片后缀映射到标准 MIME
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    # 若扩展名在字典里，返回对应 MIME；否则返回默认值
    return mime_types.get(ext, "image/jpeg")


def create_image_message(text: str, image_path: str) -> HumanMessage:
    """
    创建包含本地图像的消息
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在：{image_path}")

    image_base64 = encode_image_to_base64(image_path)
    mime_type = get_mime_type(image_path)

    # （很多视觉理解模型）视觉接口要求：同一条用户消息里要同时带“文本块”和“图片块”，不能再用一句字符串把图塞进去。因此约定是 content 为一个列表，每项是一个小字典
    content = [
        {"type": "text", "text": text},  # 文本块
        {
            "type": "image_url",  # 图片块
            "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
        },
    ]

    return HumanMessage(content=content)


def check_image_exists(filename: str) -> str:
    """
    检查图片是否存在，返回完整路径
    若不存在，则提示用户
    """
    image_path = IMAGES_DIR / filename
    if not image_path.exists():
        print(f"\n图片不存在：{image_path}")
        print(f"请将图片 '{filename}' 放入 images/ 目录")
        print("或者修改代码使用你自己的图片路径\n")
        return None
    return str(image_path)


# 提取基本图像描述
def example_1_image_description():
    # 检查图片是否存在
    image_path = check_image_exists("sample.jpg")
    if not image_path:
        print("跳过此示例")
        return None

    message = create_image_message(
        text="请详细描述这张图片中的内容。用中文回复。", image_path=image_path
    )

    print("开始分析图片...")

    # 这里应写 model.invoke([message])；若只有纯文本且接受「整段就是一个字符串」，才可以写 model.invoke("...")，但你这份是图文多模态 HumanMessage，必须用列表包起来
    response = model.invoke([message])
    print(f"AI 回复：{response.content}")

    return response.content


# 主程序
if __name__ == "__main__":
    # 创建图片目录（若不存在）
    IMAGES_DIR.mkdir(exist_ok=True)

    example_1_image_description()
