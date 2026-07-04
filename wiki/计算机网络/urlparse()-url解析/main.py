"""
知识模块: urlparse — URL 解析

=== 核心知识点 ===

urlparse 将 URL 字符串解析为结构化组件（scheme, hostname, port, path...）
标准库 urllib.parse 的一部分，无需安装任何第三方包。

关键属性:
  - .hostname → 纯主机名（不含端口），直接用于网络连接
  - .port     → int 或 None，None 表示使用协议默认端口
  - .scheme   → 协议（"http" 或 "https"），用于选择连接类型

=== 演示 ===
"""

from urllib.parse import urlparse

# ============================================================================
# 第 1 段：基础解析
# ============================================================================
print("=" * 60)
print("第 1 段：基础解析")
print()

base_url = "https://api.deepseek.com/v1/chat/completions"
parsed = urlparse(base_url)

print(f"  原始 URL:   {base_url}")
print(f"  .scheme:    {parsed.scheme}")     # https
print(f"  .hostname:  {parsed.hostname}")   # api.deepseek.com
print(f"  .port:      {parsed.port}")       # None（未显式指定）
print(f"  .path:      {parsed.path}")       # /v1/chat/completions
print(f"  .netloc:    {parsed.netloc}")     # api.deepseek.com
print()

# ============================================================================
# 第 2 段：显式指定端口 vs 默认端口
# ============================================================================
print("=" * 60)
print("第 2 段：端口对比")
print()

test_cases = [
    "https://api.deepseek.com",            # 无端口
    "https://api.deepseek.com:443",        # 显式 443
    "http://localhost:8000",               # 自定义端口
    "https://127.0.0.1:3000/v1/chat",      # IP + 端口 + 路径
    "https://[::1]:8080/api",              # IPv6 + 端口 + 路径
]

for url in test_cases:
    p = urlparse(url)
    print(f"  {url}")
    print(f"    → hostname={p.hostname!r:<25} port={p.port!r:<6} path={p.path!r}")
print()

# 关键结论：port 为 None 时，http.client 会自动使用协议默认端口
#   HTTPS → 443, HTTP → 80

# ============================================================================
# 第 3 段：urlparse 返回的是命名元组
# ============================================================================
print("=" * 60)
print("第 3 段：命名元组特性")
print()

p = urlparse("https://example.com:8080/search?q=python#results")
print(f"  按索引访问:  p[0]={p[0]}, p[1]={p[1]}, p[2]={p[2]}")
print(f"  按名称访问:  p.scheme={p.scheme}, p.hostname={p.hostname}, p.port={p.port}")
print(f"  完整元组:    {tuple(p)}")
print()

# ============================================================================
# 第 4 段：与 http.client 配合使用（真实场景）
# ============================================================================
print("=" * 60)
print("第 4 段：与 http.client 配合")
print()

import http.client

base_url = "https://api.deepseek.com/v1/chat/completions"
parsed = urlparse(base_url)

print(f"  解析结果:")
print(f"    scheme   = {parsed.scheme}")
print(f"    hostname = {parsed.hostname}")
print(f"    port     = {parsed.port}")

# 根据协议选择连接类型
if parsed.scheme == "https":
    conn = http.client.HTTPSConnection(parsed.hostname, port=parsed.port)
    print(f"  → 使用 HTTPSConnection(host={parsed.hostname!r}, port={parsed.port!r})")
else:
    conn = http.client.HTTPConnection(parsed.hostname, port=parsed.port)
    print(f"  → 使用 HTTPConnection(host={parsed.hostname!r}, port={parsed.port!r})")

# 注意：这里只演示连接对象的创建，不实际发送请求
conn.close()
print()

# ============================================================================
# 自检：运行下面的代码，验证 urlparse 对各种 URL 的解析结果
# ============================================================================
print("=" * 60)
print("自检：各种 URL 格式的解析结果")
print()

urls = [
    "https://api.deepseek.com/v1/chat/completions",
    "http://localhost:8000/api",
    "https://user:pass@example.com:8443/secret?debug=1#top",
    "https://[2001:db8::1]:443/path",
    "ftp://files.example.com/pub/data.zip",
]

for url in urls:
    p = urlparse(url)
    print(f"  {url}")
    print(f"    scheme={p.scheme!r}, hostname={p.hostname!r}, port={p.port!r}")
    if p.username:
        print(f"    username={p.username!r}, password={'***' if p.password else None}")
    print(f"    path={p.path!r}, query={p.query!r}, fragment={p.fragment!r}")
    print()
