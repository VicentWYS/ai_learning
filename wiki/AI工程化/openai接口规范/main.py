"""
知识模块: OpenAI 接口规范

=== 核心概念 ===

OpenAI 定义了 Chat Completions API 的事实行业标准：
  - 端点: POST /v1/chat/completions
  - 认证: Authorization: Bearer {api_key}
  - 请求: JSON { model, messages, temperature, ... }
  - 响应: JSON { choices[{message}], usage }

messages 中 role 三要素：
  system   → 设定 AI 角色
  user     → 用户输入
  assistant → AI 历史回复（多轮对话用）

每个函数独立封装一个可验证的知识点，按需调用。
"""

import sys
import json
import http.client
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Windows 终端 UTF-8 支持
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")
BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

_AUTH_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}


def _parse_url():
    """解析 base_url，返回 (host, port, scheme)"""
    p = urlparse(BASE_URL)
    return p.hostname, p.port, p.scheme


def _post(path: str, payload: dict):
    """发送 HTTP POST 请求，返回响应的 bytes"""
    host, port, scheme = _parse_url()
    body = json.dumps(payload)
    conn_cls = http.client.HTTPSConnection if scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(host, port=port)
    try:
        conn.request("POST", path, body, _AUTH_HEADERS)
        res = conn.getresponse()
        return res.read()
    finally:
        conn.close()


def _print_separator(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


# ============================================================================
# 验证 1 — 基础非流式调用
# 演示最核心的 Chat Completions 请求：构造 messages → POST → 解析 choices
# ============================================================================

def verify_basic_chat():
    _print_separator("验证 1：基础非流式 Chat Completion")

    payload = {
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "system", "content": "你是一个严谨的技术专家，回答简洁准确。"},
            {"role": "user", "content": "什么是 API？请用一句话回答。"},
        ],
        "temperature": 0.8,
        "max_tokens": 200,
        "stream": False,
    }

    data = _post("/v1/chat/completions", payload)
    resp = json.loads(data.decode("utf-8"))

    # 提取核心字段
    content = resp["choices"][0]["message"]["content"]
    usage = resp["usage"]
    model = resp["model"]

    print(f"模型: {model}")
    print(f"回复: {content}")
    print(f"Token: prompt={usage['prompt_tokens']} completion={usage['completion_tokens']} total={usage['total_tokens']}")


# ============================================================================
# 验证 2 — 流式调用 (SSE)
# stream=True 时响应以 Server-Sent Events 逐 chunk 返回
# ============================================================================

def verify_stream():
    _print_separator("验证 2：流式 SSE 响应")

    payload = {
        "model": "deepseek-v4-flash",
        "messages": [
            {"role": "user", "content": "用50字介绍杭州西湖。"},
        ],
        "temperature": 0.8,
        "max_tokens": 200,
        "stream": True,
    }

    host, port, scheme = _parse_url()
    body = json.dumps(payload)
    conn_cls = http.client.HTTPSConnection if scheme == "https" else http.client.HTTPConnection
    conn = conn_cls(host, port=port)

    try:
        conn.request("POST", "/v1/chat/completions", body, _AUTH_HEADERS)
        res = conn.getresponse()

        print("实时流式输出: ", end="", flush=True)
        while True:
            line = res.readline().decode("utf-8").strip()
            if not line:
                continue
            if line == "data: [DONE]":
                break
            if line.startswith("data: "):
                chunk = json.loads(line[6:])
                delta = chunk["choices"][0].get("delta", {})
                if "content" in delta:
                    print(delta["content"], end="", flush=True)
        print("\n")
    finally:
        conn.close()


# ============================================================================
# 验证 3 — system message 的角色控制
# system message 设定 AI 的人设，改变 model 行为
# ============================================================================

def verify_system_role():
    _print_separator("验证 3：system message 控制 AI 角色")

    test_cases = [
        ("诗人模式", "你是一位古代诗人，请用七言绝句回答。"       ),
        ("极客模式", "你是一个RTFM风格的Linux极客，请用纯技术语言回答。"),
        ("默认模式", "请直接回答。"                             ),
    ]

    for label, system_prompt in test_cases:
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "介绍一下云。"},
            ],
            "temperature": 0.9,
            "max_tokens": 120,
            "stream": False,
        }
        data = _post("/v1/chat/completions", payload)
        resp = json.loads(data.decode("utf-8"))
        content = resp["choices"][0]["message"]["content"]
        print(f"  [{label}]\n    {content}\n")


# ============================================================================
# 验证 4 — temperature 参数效果
# temperature 控制随机性：低=确定, 高=多样
# ============================================================================

def verify_temperature():
    _print_separator("验证 4：temperature 参数对比")

    for temp in [0.1, 1.5]:
        payload = {
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "user", "content": "用一个比喻描述编程。"},
            ],
            "temperature": temp,
            "max_tokens": 60,
            "stream": False,
        }
        data = _post("/v1/chat/completions", payload)
        resp = json.loads(data.decode("utf-8"))
        content = resp["choices"][0]["message"]["content"]
        print(f"  temperature={temp}: {content}\n")


# ============================================================================
# 验证 5 — 多轮对话 (带历史消息)
# 将 assistant 的历史回复放入 messages，实现上下文连续对话
# ============================================================================

def verify_multi_turn():
    _print_separator("验证 5：多轮对话")

    messages = [
        {"role": "system", "content": "你是一个乐于助人的助手。"},
        {"role": "user", "content": "我叫小明。"},
    ]

    # 第一轮
    payload1 = {"model": "deepseek-v4-flash", "messages": messages,
                "temperature": 0.8, "max_tokens": 80, "stream": False}
    resp1 = json.loads(_post("/v1/chat/completions", payload1).decode("utf-8"))
    assistant_reply = resp1["choices"][0]["message"]["content"]
    print(f"  用户: 我叫小明。")
    print(f"  AI: {assistant_reply}")

    # 把 assistant 的回复加入历史
    messages.append({"role": "assistant", "content": assistant_reply})
    messages.append({"role": "user", "content": "我叫什么名字？"})

    # 第二轮
    payload2 = {"model": "deepseek-v4-flash", "messages": messages,
                "temperature": 0.8, "max_tokens": 80, "stream": False}
    resp2 = json.loads(_post("/v1/chat/completions", payload2).decode("utf-8"))
    print(f"  用户: 我叫什么名字？")
    print(f"  AI: {resp2['choices'][0]['message']['content']}")


# ============================================================================
# 验证 6 — 响应 JSON 结构解析
# 完整理解 response payload 的每个字段
# ============================================================================

def verify_response_structure():
    _print_separator("验证 6：响应 JSON 结构解析")

    payload = {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "Hi"}],
        "temperature": 0.8,
        "max_tokens": 50,
        "stream": False,
    }

    data = _post("/v1/chat/completions", payload)
    resp = json.loads(data.decode("utf-8"))

    print(f"  id:              {resp['id']}")
    print(f"  object:          {resp['object']}")
    print(f"  created:         {resp['created']} (Unix 时间戳)")
    print(f"  model:           {resp['model']}")
    print(f"  choices[0].index:        {resp['choices'][0]['index']}")
    print(f"  choices[0].message.role: {resp['choices'][0]['message']['role']}")
    print(f"  choices[0].message.content: {resp['choices'][0]['message']['content'][:50]}...")
    print(f"  choices[0].finish_reason: {resp['choices'][0]['finish_reason']}")
    print(f"  usage.prompt_tokens:      {resp['usage']['prompt_tokens']}")
    print(f"  usage.completion_tokens:  {resp['usage']['completion_tokens']}")
    print(f"  usage.total_tokens:       {resp['usage']['total_tokens']}")


# ============================================================================
# 验证 7 — finish_reason 含义
# stop=正常完成, length=max_tokens截断, content_filter=内容过滤
# ============================================================================

def verify_finish_reason():
    _print_separator("验证 7：finish_reason 对比")

    # 场景 1：正常完成 (stop)
    resp1 = json.loads(_post("/v1/chat/completions", {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "说一个字。"}],
        "temperature": 0.8, "max_tokens": 100, "stream": False,
    }).decode("utf-8"))
    print(f"  正常完成: finish_reason={resp1['choices'][0]['finish_reason']} "
          f"(completion_tokens={resp1['usage']['completion_tokens']})")

    # 场景 2：被 max_tokens 截断 (length)
    resp2 = json.loads(_post("/v1/chat/completions", {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "从1数到100。"}],
        "temperature": 0.8, "max_tokens": 10, "stream": False,
    }).decode("utf-8"))
    print(f"  max_tokens 截断: finish_reason={resp2['choices'][0]['finish_reason']} "
          f"(completion_tokens={resp2['usage']['completion_tokens']})")
    content = resp2['choices'][0]['message']['content']
    print(f"  被截断的内容: {content}...")


# ============================================================================
# 验证 8 — OpenAI Python SDK 调用（与原生 HTTP 对比）
# SDK 封装了 HTTP 细节，提供对象化接口
# ============================================================================

def verify_openai_sdk():
    _print_separator("验证 8：OpenAI SDK 调用")

    try:
        from openai import OpenAI
    except ImportError:
        print("  ❌ 请先安装: pip install openai")
        return

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # 非流式
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": "用一句话解释什么是接口规范。"}],
        temperature=0.8,
        max_tokens=80,
    )
    print(f"  非流式: {response.choices[0].message.content}")

    # 流式
    print("\n  流式: ", end="", flush=True)
    stream = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": "说一句鼓励程序员的话。"}],
        temperature=0.8,
        max_tokens=60,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")


# ============================================================================
# 主入口 — 按编号选择要验证的知识点
# ============================================================================

if __name__ == "__main__":
    if not API_KEY or API_KEY == "your_api_key_here":
        print("❌ 请先在 .env 文件中设置 DEEPSEEK_API_KEY")
        sys.exit(1)
    if not BASE_URL:
        print("❌ 请先在 .env 文件中设置 DEEPSEEK_BASE_URL")
        sys.exit(1)

    VERIFY_FUNCTIONS = {
        "1": ("基础非流式调用", verify_basic_chat),
        "2": ("流式 SSE 响应", verify_stream),
        "3": ("system message 角色控制", verify_system_role),
        "4": ("temperature 参数对比", verify_temperature),
        "5": ("多轮对话", verify_multi_turn),
        "6": ("响应 JSON 结构解析", verify_response_structure),
        "7": ("finish_reason 对比", verify_finish_reason),
        "8": ("OpenAI SDK 调用", verify_openai_sdk),
    }

    print("\n可验证的知识点：")
    for k, (desc, _) in VERIFY_FUNCTIONS.items():
        print(f"  [{k}] {desc}")
    print(f"  [A] 全部依次验证")

    choice = input("\n请选择编号: ").strip().upper()

    if choice == "A":
        for k, (desc, fn) in VERIFY_FUNCTIONS.items():
            fn()
    elif choice in VERIFY_FUNCTIONS:
        VERIFY_FUNCTIONS[choice][1]()
    else:
        print(f"无效选择: {choice}")
