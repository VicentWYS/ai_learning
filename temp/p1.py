import http.client
import json
import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv

# 修复 Windows 终端 GBK 编码无法输出 emoji 的问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 加载环境变量
load_dotenv()

# 从环境变量获取API配置
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("DEEPSEEK_BASE_URL")

if not api_key or api_key == "your_api_key_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_API_KEY\n")

if not base_url or base_url == "your_base_url_here":
    raise ValueError("\n请先在 .env 文件中设置有效的 DEEPSEEK_BASE_URL\n")

# 解析 BASE_URL 获取 host 和端口
parsed_url = urlparse(base_url)
host = parsed_url.hostname  # api.deepseek.com
port = parsed_url.port  # None


# 构造请求体
payload = json.dumps(
    {
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "讲一个小笑话"}],
        "max_tokens": 1688,
        "temperature": 0.5,
        "stream": False,
    }
)

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

try:
    # 根据协议选择 HTTP 或 HTTPS 连接
    if parsed_url.scheme == "https":
        conn = http.client.HTTPSConnection(host, port=port)
    else:
        conn = http.client.HTTPConnection(host, port=port)

    conn.request("POST", "/v1/chat/completions", payload, headers)
    res = conn.getresponse()
    data = res.read()

    # 打印原始响应
    print("原始响应:")
    print(data.decode("utf-8"))

    # 解析JSON并提取消息内容
    response_json = json.loads(data.decode("utf-8"))
    message_content = response_json["choices"][0]["message"]["content"]
    print("\n提取的消息内容:")
    print(message_content)

except http.client.HTTPException as e:
    print(f"\nHTTP 请求错误: {e}")
except json.JSONDecodeError as e:
    print(f"\nJSON 解析错误: {e}")
    print("原始响应内容:")
    print(data.decode("utf-8"))
except KeyError as e:
    print(f"\n响应格式错误，缺少字段: {e}")
    print("完整响应:")
    print(json.dumps(response_json, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"\n未知错误: {e}")
    import traceback

    traceback.print_exc()
finally:
    conn.close()
