"""
知识模块: HTTP vs HTTPS — 功能、联系与区别

=== 核心知识点 ===

HTTPS = HTTP + TLS。应用层语义完全相同（Method、Header、Status Code），
区别仅在传输层：HTTP 明文传输（端口 80），HTTPS 经 TLS 加密（端口 443）。

关键差异:
  - HTTP  → 明文传输，任何人都能抓包看到内容
  - HTTPS → TLS 加密 + CA 证书验证服务器身份 + 数据完整性校验
  - Python 中需手动选择 HTTPConnection（HTTP）还是 HTTPSConnection（HTTPS）

=== 演示 ===
"""

import http.client
import ssl
import socket
import json

# ============================================================================
# 第 1 段：HTTP vs HTTPS — 端口差异
# ============================================================================
print("=" * 60)
print("第 1 段：HTTP vs HTTPS — 默认端口对比")
print()

print(f"  HTTP  默认端口: {http.client.HTTP_PORT}")    # 80
print(f"  HTTPS 默认端口: {http.client.HTTPS_PORT}")   # 443
print()

# ============================================================================
# 第 2 段：HTTP 请求 → 通常被 301 重定向到 HTTPS
# ============================================================================
print("=" * 60)
print("第 2 段：HTTP 请求 → 服务端强制升级为 HTTPS")
print()

try:
    conn = http.client.HTTPConnection("httpbin.org", timeout=5)
    conn.request("GET", "/get")
    resp = conn.getresponse()
    body = resp.read().decode()

    print(f"  请求: http://httpbin.org/get")
    print(f"  状态: {resp.status} {resp.reason}")

    if resp.status in (301, 302, 307, 308):
        redirect_url = resp.getheader("Location")
        print(f"  重定向到: {redirect_url}")
        print(f"  → 服务端强制要求 HTTPS，不允许明文 HTTP")
    else:
        data = json.loads(body)
        print(f"  → 得到了明文响应（说明该服务器仍兼容 HTTP）")

    conn.close()
except Exception as e:
    print(f"  连接失败: {e}")
print()

# ============================================================================
# 第 3 段：HTTPS 请求 → 正常加密通信
# ============================================================================
print("=" * 60)
print("第 3 段：HTTPS 请求 — 加密通信正常返回")
print()

try:
    conn = http.client.HTTPSConnection("httpbin.org", timeout=5)
    conn.request("GET", "/get")
    resp = conn.getresponse()
    body = resp.read().decode()
    data = json.loads(body)

    print(f"  请求: https://httpbin.org/get")
    print(f"  状态: {resp.status} {resp.reason}")
    print(f"  TLS 加密: 已建立（底层 socket 已包装为 SSLSocket）")
    print(f"  服务器返回的 headers:")

    # 只打印关键 headers，保持简洁
    for key in ("Content-Type", "Server", "Date"):
        if key in data.get("headers", {}):
            print(f"    {key}: {data['headers'][key]}")

    conn.close()
except Exception as e:
    print(f"  连接失败: {e}")
print()

# ============================================================================
# 第 4 段：用 SSLSocket 获取 TLS 证书信息
# ============================================================================
print("=" * 60)
print("第 4 段：获取服务器 TLS 证书信息")
print()

try:
    hostname = "api.deepseek.com"
    port = 443

    # 获取证书
    ctx = ssl.create_default_context()
    with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
        s.settimeout(5)
        s.connect((hostname, port))
        cert = s.getpeercert()

    print(f"  目标服务器: {hostname}:{port}")
    print(f"  subject:    {cert.get('subject')}")
    print(f"  issuer:     {cert.get('issuer')}")

    # 证书有效期
    not_before = cert.get("notBefore", "")
    not_after = cert.get("notAfter", "")
    print(f"  有效期:     {not_before} → {not_after}")
    print()
    print(f"  → 浏览器地址栏的锁图标，检查的就是这个证书")
except Exception as e:
    print(f"  获取证书失败: {e}")
print()

# ============================================================================
# 第 5 段：对比 — 同一个请求，HTTP vs HTTPS 的安全性差异
# ============================================================================
print("=" * 60)
print("第 5 段：安全性差异 — 抓包视角对比")
print()

# 模拟：如果在 HTTP 下传输 API Key
fake_api_key = "sk-proj-abc123def456"
http_headers = f"""
  假设在 HTTP 下发送:
    POST /v1/chat HTTP/1.1
    Content-Type: application/json
    Authorization: Bearer {fake_api_key}
  ↑ 抓包者直接看到你的 API Key！"""

https_headers = """
  假设在 HTTPS 下发送:
    原始数据经 TLS 加密后:
    a3 f7 c9 01 b2 88 4e d3 1f a0 ...（全是乱码）
  ↑ 抓包者只能看到加密后的二进制数据，无法还原"""

print(http_headers)
print(https_headers)
print(f"  → 这就是为什么所有 LLM API 强制 HTTPS——API Key 必须加密传输")
print()

# ============================================================================
# 自检：用 openssl 命令（如果可用）验证 TLS 版本
# ============================================================================
print("=" * 60)
print("自检：Python ssl 模块支持的 TLS 版本")
print()

# 不同 Python 版本支持的 TLS 版本
try:
    print(f"  TLS 1.2: {'available' if hasattr(ssl, 'PROTOCOL_TLSv1_2') else 'N/A'}")
except Exception:
    print(f"  TLS 1.2: N/A")

try:
    print(f"  TLS 1.3: {'available' if hasattr(ssl, 'PROTOCOL_TLSv1_3') else 'N/A'}")
except Exception:
    print(f"  TLS 1.3: N/A")

print(f"  默认上下文协议: {ssl.create_default_context().protocol}")
print(f"  默认验证模式:   {ssl.create_default_context().verify_mode}")
print()
print("  提示: Python 3.6+ 默认使用系统最安全的 TLS 版本")
print("        调用 HTTPSConnection 时自动协商，无需手动指定")
