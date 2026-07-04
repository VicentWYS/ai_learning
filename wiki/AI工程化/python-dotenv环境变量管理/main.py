"""
知识模块: python-dotenv 环境变量管理

=== 背景说明 ===

在开发中，API Key、数据库密码等敏感信息不应硬编码在代码里。
业界最佳实践是将它们放在 .env 文件中，通过 python-dotenv 的 load_dotenv() 加载到
os.environ，代码通过 os.getenv() 读取。

这源自 12-Factor App 方法论（2011 年）：配置应与代码分离，存储在环境变量中。

=== 核心用法 ===

  1. pip install python-dotenv
  2. 项目根目录创建 .env 文件（写入 KEY=VALUE，不要加引号）
  3. 代码中 load_dotenv() → os.getenv("KEY")
  4. .env 加入 .gitignore（防止密钥泄露）

=== 演示 ===

以下代码展示三种常用模式：
  第 1 段 — 基础用法：load_dotenv() + os.getenv()
  第 2 段 — 带默认值的安全回退
  第 3 段 — 自定义 .env 路径（多环境场景）
"""

import os
from pathlib import Path

# ================================================================================
# 第 1 段：基础用法
# load_dotenv() 默认从当前工作目录查找 .env 文件，将其中的键值对注入 os.environ
# ================================================================================

# 导入并加载
from dotenv import load_dotenv

load_dotenv()

# .env 中的值现在可以通过 os.getenv() 读取
# 假设 .env 中写有: DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxx
api_key = os.getenv("DEEPSEEK_API_KEY")
print(f"  DEEPSEEK_API_KEY      = {'✅ 已加载' if api_key else '❌ 未设置'}")

# os.getenv() 与 os.environ.get() 的区别：
#   os.getenv("KEY")       → 优先查 os.environ，支持默认值
#   os.environ["KEY"]      → 直接访问字典，KEY 不存在时抛出 KeyError
#   os.environ.get("KEY")  → 字典方法，行为与 os.getenv() 几乎相同
print()


# ================================================================================
# 第 2 段：带默认值的安全回退
# 生产环境通常用系统环境变量，开发环境用 .env 文件
# ================================================================================

# 模式：环境变量优先，代码内默认值兜底（默认值不应是真实密钥）
api_key = os.getenv("DEEPSEEK_API_KEY", "your_api_key_here")
base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

# 检查是否还是占位符——若是则说明用户未配置
if api_key == "your_api_key_here":
    print("  ⚠️  DEEPSEEK_API_KEY 未配置，请先在 .env 文件中设置")
else:
    print(f"  DEEPSEEK_API_KEY      = ✅ 已配置")

print(f"  DEEPSEEK_BASE_URL      = {base_url}")
print()

# ================================================================================
# 第 3 段：自定义 .env 路径（多环境场景）
# 开发 / 测试 / 生产环境的 .env 可能不同
# ================================================================================

# 方式一：指定文件名（相对于当前工作目录）
# load_dotenv(".env.development")

# 方式二：使用 dotenv_values() 不注入 os.environ，只返回字典
from dotenv import dotenv_values

config = dotenv_values(".env")  # 返回 dict，不修改 os.environ
# 优点：不会"污染"全局环境变量，适合同时加载多个 .env 对比
print(f"  dotenv_values('.env') 加载了 {len(config)} 个变量")

# 打印 .env 中的全部变量名称
if config:
    for k in list(config.keys()):
        print(f"    - {k}")
print()

# 方式三：find_dotenv() 自动向上查找最近的 .env（类似 git 查找 .gitignore）
from dotenv import find_dotenv

env_path = find_dotenv()
print(f"  find_dotenv() 找到的路径: {env_path or '未找到 .env 文件'}")
print()
