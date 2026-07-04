"""
模块 21：混合模态
学习如何处理文本、图像等多种模态的输入

重要提示：
1. 本模块需要支持视觉的模型
3. 请在 images/ 目录下放置你自己的测试图片

使用前准备：
1. 在 images/ 目录下放置测试图片
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
    """将本地图像编码为 base64"""
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")


def get_mime_type(image_path: str) -> str:
    """根据文件扩展名获取 MIME 类型"""
    ext = Path(image_path).suffix.lower()  # 获取文件扩展名
    mime_types = {  # 常见图片后缀映射到标准 MIME
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    return mime_types.get(ext, "image/jpeg")


def create_image_content(image_path: str) -> dict:
    """创建图像内容块"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片不存在：{image_path}")

    image_base64 = encode_image_to_base64(image_path)
    mime_type = get_mime_type(image_path)

    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
    }


def check_image_exists(filename: str) -> str:
    """检查图片是否存在"""
    image_path = IMAGES_DIR / filename
    if not image_path.exists():
        print(f"图片不存在：{image_path}")
        return None
    return str(image_path)


# 多图像对比分析
def example_2_multi_image():
    """
    对比多张图片
    """
    # 检查图片
    image1_path = check_image_exists("image1.jpg")
    image2_path = check_image_exists("image2.jpg")

    if not image1_path or not image2_path:
        print("缺失图片，请在 images/ 目录下放置图片")
        print("跳过此示例")
        return None

    content = [
        {"type": "text", "text": "请对比这两张图片，说明它们的相同点和不同点。"},
        create_image_content(image1_path),
        create_image_content(image2_path),
    ]

    message = HumanMessage(content=content)

    response = model.invoke([message])

    print(f"\n对比结果：{response.content}")

    return response.content


# 主函数
if __name__ == "__main__":
    # 创建图片目录
    IMAGES_DIR.mkdir(exist_ok=True)

    # 运行示例
    content = example_2_multi_image()
