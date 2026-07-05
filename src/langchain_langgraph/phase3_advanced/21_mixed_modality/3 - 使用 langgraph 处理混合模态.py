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
from typing import Optional, TypedDict, Literal, List
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END


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


# 使用 langgraph 处理混合模态
class MultimodalState(TypedDict):
    """混合模态状态"""

    text_input: str
    image_paths: List[str]
    analysis_result: Optional[str]
    summary: Optional[str]


def example_3_langgraph_multimodal():
    """
    使用 langgraph 构建混合模态处理流程
    """
    # 检查图片
    image_path = check_image_exists("sample.jpg")
    if not image_path:
        print("缺失图片，请在 images/ 目录下放置图片")
        print("跳过此示例")
        return None

    # 定义节点函数
    def analyze_content(state: MultimodalState) -> MultimodalState:
        """
        分析多模态内容

        接收文字和图片模态信息，送给大模型进行分析，
        获得大模型分析结果
        """
        print("\n正在分析内容...")

        content = [{"type": "text", "text": state["text_input"]}]

        for img_path in state["image_paths"]:
            if os.path.exists(img_path):
                content.append(create_image_content(img_path))

        messages = HumanMessage(content=content)
        response = model.invoke([messages])

        state["analysis_result"] = response.content
        return state

    def summarize(state: MultimodalState) -> MultimodalState:
        """总结分析结果"""
        print("\n正在生成总结...")

        message = HumanMessage(
            content=f"请用3句话总结以下分析：\n\n{state["analysis_result"]}"
        )
        response = model.invoke([message])

        state["summary"] = response.content

        return state

    # 构建图
    graph = StateGraph(MultimodalState)

    graph.add_node("analyze", analyze_content)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "analyze")
    graph.add_edge("analyze", "summarize")
    graph.add_edge("summarize", END)

    workflow = graph.compile()

    # 运行
    initial_state = {
        "text_input": "请详细描述这张图片，包括主要内容、色彩和氛围。",
        "image_paths": [image_path],
        "analysis_result": None,
        "summary": None,
    }

    result = workflow.invoke(initial_state)

    print("\nlanggraph 启动...")
    print(f"\n详细分析：\n{result["analysis_result"]}")
    print(f"\n总结：\n{result["summary"]}")

    return result


# 主函数
if __name__ == "__main__":
    # 创建图片目录
    IMAGES_DIR.mkdir(exist_ok=True)

    # 运行示例
    example_3_langgraph_multimodal()
