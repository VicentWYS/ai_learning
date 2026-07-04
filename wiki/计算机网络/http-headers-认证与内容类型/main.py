"""
============================================================
第 1 段：HTTP Headers 的结构

  Content-Type:   application/json
  Authorization:  Bearer sk-test-demo-key-12345

  含义：
    Content-Type   → 请求体格式是 JSON
    Authorization  → 使用 Bearer Token 认证

============================================================
第 2 段：Content-Type 常见值

  application/json                          JSON 数据（LLM API 标准格式）
  application/x-www-form-urlencoded         HTML 表单提交
  multipart/form-data                       文件上传
  text/plain                                纯文本
  text/html                                 HTML 文档

============================================================
第 3 段：Authorization 认证方案对比

  Bearer {token}                出示令牌，简单无状态（LLM API 标配）
  Basic {base64}                用户名:密码 Base64 编码（需 HTTPS）
  Digest {hash}                 挑战-应答哈希（已很少使用）
  AWS4-HMAC-SHA256 {...}        AWS 签名 V4，密钥不传输

============================================================
第 4 段：完整请求构造示例

  请求方法:  POST
  请求路径:  /v1/chat/completions
  Host:      api.deepseek.com
  Headers:   {'Content-Type': 'application/json', 'Authorization': 'Bearer sk-your-key-h***'}
  Body:      {"model": "deepseek-v4-flash", "messages": [{"role": "user",...

============================================================
第 5 段：常见错误状态码

  400 Bad Request         Content-Type 缺失或格式不对，服务器无法解析请求体
  401 Unauthorized        Authorization 缺失或 Token 无效
  403 Forbidden           Token 有效但权限不足
  405 Method Not Allowed  用了 GET 而不是 POST

============================================================
第 6 段：Bearer Token 安全性

  ⚠  Bearer Token 的安全性完全依赖 HTTPS
  ⚠  永远不要把 API Key 硬编码在代码里 → 用 os.getenv()
  ⚠  不要 commit .env 文件到 git → 加入 .gitignore
  ⚠  Token 泄露后应立即在平台重新生成

============================================================
自检：Headers 格式验证

  ✓ Content-Type = 'application/json'
  ✓ Authorization = Bearer sk-your-key-here...

  HTTP Headers 的职责:
    Content-Type   → 描述请求体的媒体类型
    Authorization  → 携带身份认证信息

  ✓ 全部验证通过！
"""