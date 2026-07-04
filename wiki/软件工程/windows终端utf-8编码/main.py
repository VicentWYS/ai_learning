"""
知识模块: Windows 终端 UTF-8 编码

=== 背景说明 ===

历史上，Windows 终端（cmd.exe / PowerShell 5.x）默认使用系统 ANSI 代码页（简体中文 Windows
为 GBK），Python 的 sys.stdout 也继承该编码，导致 emoji 等非 GBK 字符无法正常输出。

但从 Python 3.6+ 开始，以下改进使得这个问题在大多数现代场景下不再需要手动修复：

  1. PEP 528 / PEP 529 (Python 3.6+)
     Windows 上 Python 不再简单使用 ANSI 代码页，而是直接调用 Windows Console API
     （WriteConsoleW）写入 Unicode 文本，绕过了 GBK 限制。

  2. PEP 540 (Python 3.7+)
     进一步引入 UTF-8 模式，当检测到终端支持时，自动使用 UTF-8 编码处理标准流。

  3. 终端层面的进化
     - VSCode / Cursor 等 IDE 内置终端 → 原生 UTF-8
     - Windows Terminal (wt.exe) → 原生 UTF-8（Win11 默认终端）
     - 传统 cmd.exe 中 chcp 65001 → 切换到 UTF-8 代码页

因此，在 现代 Windows + 现代 Python + 现代终端 的组合下，以下代码已属于 **防御性编程**：
- 对已经 UTF-8 的 stdout 再做一次 reconfigure(encoding="utf-8") 是无害的 no-op
- 但保留它可以在旧环境（老 Python / 老 cmd.exe）中避免崩溃
- errors="replace" 确保在任何畸形环境下不至于因为一个字符就脚本挂掉

=== 演示 ===

以下代码分三个阶段对比展示，建议在不同的终端环境中分别观察差异：
  第 1 段 — 不做任何设置（现代环境通常直接正常）
  第 2 段 — 强制设为 GBK（模拟旧环境的乱码效果）
  第 3 段 — 显式设为 UTF-8（防御性写法）
"""

import sys

TERMINAL_TYPES = {
    "vscode": "VSCode/IDE 内置终端",
    "windows_terminal": "Windows Terminal",
    "cmd_legacy": "传统 cmd.exe（非 Windows Terminal）",
}


# ================================================================================
# 第 1 段：不做任何设置
# 现代 Python 3.6+ 在 VSCode / Windows Terminal 中通常直接正常输出
# ================================================================================
print("=" * 60)
print(f"  sys.stdout.encoding = {sys.stdout.encoding}")
print("  ✅ 中文正常输出")
print("  🎯 Emoji 正常输出")
print("  🌟 特殊字符: — – … ' \"")
print()


# ================================================================================
# 第 2 段：强制设为 GBK（模拟旧环境的乱码效果）
# 在 GBK 编码下，emoji 等非 GBK 字符会被 errors="replace" 替换为 ?
# ================================================================================
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="gbk", errors="replace")

print("=" * 60)
print(f"  sys.stdout.encoding = {sys.stdout.encoding}")
print("  ✅ 中文正常输出（GBK 包含中文字符集）")
print("  🎯 Emoji 正常输出（GBK 不含 emoji，替换为 ?）")
print("  🌟 特殊字符: — – … ' \"（部分特殊符号也会被替换）")
print()


# ================================================================================
# 第 3 段：显式设为 UTF-8（防御性写法）
# 在现代环境中，这通常是一个无害的 no-op；在旧环境中，这是关键的修复
# ================================================================================
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 60)
print("第 3 段：显式设为 UTF-8（防御性写法）")
print(f"  sys.stdout.encoding = {sys.stdout.encoding}")
print("  ✅ 中文正常输出")
print("  🎯 Emoji 正常输出")
print("  🌟 特殊字符: — – … ' \"")
print()


# ================================================================================
# 快速自检：运行下面的代码，查看你当前环境的编码状态
# ================================================================================
print("=" * 60)
print("环境自检")
print(f"  sys.platform            = {sys.platform}")  # win32
print(f"  sys.getdefaultencoding()= {sys.getdefaultencoding()}")  # utf-8
print(f"  sys.stdout.encoding     = {sys.stdout.encoding}")  # utf-8
if sys.platform == "win32":
    import subprocess

    try:
        cp = subprocess.run(
            ["chcp"], shell=True, capture_output=True, text=True, timeout=5
        )
        print(f"  终端代码页(chcp)        = {cp.stdout.strip()}")  # 936
    except Exception:
        print("  终端代码页(chcp)        = 无法获取")
print()
