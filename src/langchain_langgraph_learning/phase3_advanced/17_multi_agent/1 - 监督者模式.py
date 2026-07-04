"""
多智能体 - 监督者模式
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from typing import TypedDict, Annotated, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
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
    model="qwen-plus",
    model_provider="openai",
    api_key=QWEN_API_KEY,
    base_url=QWEN_BASE_URL,
    temperature=0.8,
)


# ====================================================================
# 定义工具
# ====================================================================
@tool
def search_web(query: str) -> str:
    """
    搜索网络获取最新信息

    它期望的方法调用参数输入是：{"query": "...要搜索的内容..."}

    举例：
        search_result = search_web.invoke({"query": state["task"]})
    """
    # 模拟搜索结果
    mock_results = {
        "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。主要领域包括机器学习、深度学习、自然语言处理等。",
        "机器学习": "机器学习是AI的子领域，通过算法让计算机从数据中学习。常见方法包括监督学习、无监督学习和强化学习。",
        "default": f"找到关于'{query}'的相关信息：这是一个重要的技术领域，正在快速发展中。",
    }

    for key in mock_results:
        if key in query:
            return mock_results[key]
    return mock_results["default"]


@tool
def check_grammar(text: str) -> str:
    """
    检查文本的语法和表达

    它期望的方法调用参数输入是：{"text": "...要检查的内容..."}

    举例：
        grammar_check = check_grammar.invoke({"text": "...要检查的内容..."})
    """
    # 模拟语法检查
    return f"语法检查完成。文本长度：{len(text)} 个字符。建议：表达清晰，结构合理。"


# ====================================================================
# 多智能体 - 监督者模式
# ====================================================================
def supervisor_pattern():
    """
    监督者模式：由一个 Supervisor 协调多个专业 Agent
    """

    class TeamState(TypedDict):
        task: str
        messages: Annotated[list, add_messages]
        research_result: str  # researcher
        draft: str  # writer
        final_content: str  # editor
        next_agent: str  # route_to_agent

    def supervisor(state: TeamState) -> dict:
        """监督者：决定下一步由哪个 Agent 处理"""
        if not state.get("research_result"):
            next_agent = "researcher"
        elif not state.get("draft"):
            next_agent = "writer"
        elif not state.get("final_content"):
            next_agent = "editor"
        else:
            next_agent = "complete"

        return {"next_agent": next_agent}

    def researcher(state: TeamState) -> dict:
        """研究员：收集和整理信息"""
        search_result = search_web.invoke({"query": state["task"]})

        messages = [
            SystemMessage(
                content="你是一个研究员，请根据搜索结果整理出关键信息要点。用中文回复。"
            ),
            HumanMessage(content=f"任务：{state["task"]}\n\n搜索结果：{search_result}"),
        ]
        response = model.invoke(messages)

        print(f"研究完成，整理出了 {len(response.content)} 字的资料。")

        return {
            "research_result": response.content,
            "messages": [AIMessage(content=f"[研究员] {response.content}")],
        }

    def writer(state: TeamState) -> dict:
        """作家：根据研究结果撰写内容"""
        messages = [
            SystemMessage(
                content="你是一个专业作家，请根据研究资料撰写一篇结构清晰的短文。用中文写作。"
            ),
            HumanMessage(
                content=f"主题：{state["task"]}\n\n研究资料：{state["research_result"]}"
            ),
        ]
        response = model.invoke(messages)

        print(f"作家完成初稿，共 {len(response.content)} 个字。")

        return {
            "draft": response.content,
            "messages": [AIMessage(content=f"[作家] {response.content}")],
        }

    def editor(state: TeamState) -> dict:
        """编辑：审核和优化内容"""
        grammar_check = check_grammar.invoke({"text": state["draft"]})

        messages = [
            SystemMessage(
                content="你是一个资深编辑，请审核并优化以下文章，使其更加专业和易读。用中文回复。"
            ),
            HumanMessage(
                content=f"初稿：{state["draft"]}\n\n语法检查：{grammar_check}"
            ),
        ]
        response = model.invoke(messages)

        print(f"编辑人员完成编辑，最终版本包含 {len(response.content)} 个字")

        return {
            "final_content": response.content,
            "messages": [AIMessage(content=f"[编辑] {response.content}")],
        }

    # 路由函数
    def route_to_agent(
        state: TeamState,
    ) -> Literal["researcher", "writer", "editor", "complete"]:
        """
        表示这个函数的返回值只能是这四个字符串之一，用来约束和提示
        """

        # 直接从状态里读取 next_agent 字段，并作为下一步要去的节点名称返回
        # 在上面定义的 supervisor 函数里，监督者会根据当前情况设置 state["next_agent"] 是 "researcher" / "writer" / "editor" / "complete"
        # 这里的 route_to_agent 只是把这个决定“翻译”成条件路由的返回值
        return state["next_agent"]

    # 构建图
    graph = StateGraph(TeamState)

    # 添加节点
    graph.add_node("supervisor", supervisor)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("editor", editor)

    # 从 START 到 supervisor
    graph.add_edge(START, "supervisor")

    # supervisor 根据条件路由
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "researcher": "researcher",
            "writer": "writer",
            "editor": "editor",
            "complete": END,
        },
    )

    # 各 Agent 完成后回到 supervisor
    graph.add_edge("researcher", "supervisor")
    graph.add_edge("writer", "supervisor")
    graph.add_edge("editor", "supervisor")

    app = graph.compile()

    result = app.invoke({"task": "写一篇关于人工智能发展的简短介绍", "messages": []})

    print(result["final_content"])

    return result


if __name__ == "__main__":
    supervisor_pattern()
