"""
聊天相关的 Pydantic 数据模型
"""

from pydoc import describe

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    聊天请求模型

    Attritubes:
        message: 用户消息，1-4000 字符（必填）
        session_id: 会话ID，用于区分不同对话，默认为 "default"
    """

    # ...: 表示该字段是必填的（没有默认值）。如果请求中缺少 message，Pydantic 会直接报验证错误。
    # description: 表示字段的文字描述，用于生成 JSON Schema / API 文档（如 Swagger），方便前后端理解字段用途。
    message: str = Field(..., min_length=1, max_length=4000, description="用户消息")

    # default: 该字段的默认值。如果不传 session_id，自动使用 "default"。与 message 的 ... 相反——这里没有 ...，说明它是可选的。
    session_id: str = Field(default="default", description="会话ID，区分不同对话")


class ChatResponse(BaseModel):
    """
    聊天响应模型

    Attritubes:
        reply: AI 助教的回复文本（必填）
    """

    reply: str = Field(..., description="AI 回复")
