"""
单次大模型调用
"""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# 加载环境变量
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL")

# 校验 key 和 url
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_api_key_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_API_KEY\n")

if not DEEPSEEK_BASE_URL or DEEPSEEK_BASE_URL == "your_base_url_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_BASE_URL\n")

# 初始化模型
model = init_chat_model(
    model="deepseek-v4-flash",
    model_provider="openai",
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
    temperature=0.8,
)


# 最简单的大模型调用
def example_1_simple_invoke():
    response = model.invoke("请用一句话介绍成语“望梅止渴”")
    print(f"\nAI回复内容：{response.content}")
    print(f"\nAI回复类型：{type(response)}")
    print(f"\nAI回复：{response}")


# 主程序
def main():
    try:
        example_1_simple_invoke()
    except Exception as e:
        print(f"\n运行出错：{e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()


# 注意，这里“AI回复”中格式做了美化
"""
AI回复内容：成语“望梅止渴”源于曹操用前方梅林激励士兵的故事，比喻用空想或虚幻的期望来安慰自己或他人。

AI回复类型：<class 'langchain_core.messages.ai.AIMessage'>

AI回复：content='成语“望梅止渴”源于曹操用前方梅林激励士兵的故事，比喻用空想或虚幻的期望来安慰自己或他人。' additional_kwargs={
    "refusal": None
} 

response_metadata={
    "token_usage": {
        "completion_tokens": 78,
        "prompt_tokens": 15,
        "total_tokens": 93,
        "completion_tokens_details": {
            "accepted_prediction_tokens": None,
            "audio_tokens": None,
            "reasoning_tokens": 45,
            "rejected_prediction_tokens": None
        },
        "prompt_tokens_details": {
            "audio_tokens": None,
            "cached_tokens": 0
        },
        "prompt_cache_hit_tokens": 0,
        "prompt_cache_miss_tokens": 15
    },
    "model_provider": "openai",
    "model_name": "deepseek-v4-flash",
    "system_fingerprint": "fp_8b330d02d0_prod0820_fp8_kvcache_20260402",
    "id": "2eb911f2-956b-4a24-9439-4de219a0977e",
    "finish_reason": "stop",
    "logprobs": None
} 

id="lc_run--019f1443-eba5-7c42-8f28-5e5ea64f6644-0" 

tool_calls=[] 

invalid_tool_calls=[] 

usage_metadata={
    "input_tokens": 15,
    "output_tokens": 78,
    "total_tokens": 93,
    "input_token_details": {
        "cache_read": 0
    },
    "output_token_details": {
        "reasoning": 45
    }
}
"""
