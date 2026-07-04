# Windows 终端 UTF-8 编码

## 问题

Windows 终端（特指**传统 cmd.exe** 和**旧版 PowerShell 5.x**）默认使用系统 ANSI 代码页——简体中文 Windows 下为 **GBK**（代码页 936）。在以下场景中，Python 脚本输出 emoji 或特殊字符会出现乱码或 `UnicodeEncodeError`：

| 场景 | 终端 | Python 版本 | 是否受影响 |
|------|------|-------------|-----------|
| 现代 IDE（VSCode / Cursor / PyCharm） | 内置终端（UTF-8） | 3.6+ | ✅ 不受影响 |
| Windows Terminal (wt.exe) | 原生 UTF-8 | 3.6+ | ✅ 不受影响 |
| 传统 cmd.exe | ANSI 代码页（GBK） | < 3.6 | ❌ 乱码 |
| 传统 cmd.exe | ANSI 代码页（GBK） | 3.6+ | ⚠️ 取决于终端能力 |
| 旧版 PowerShell 5.x (ISE) | ANSI 代码页（GBK） | < 3.6 | ❌ 乱码 |

## 为什么现代环境通常不需要修复

Python 社区在 2016–2018 年间通过三个 PEP 从根源上解决了这个问题：

### PEP 528 / 529 — 让 Python 直接写 Unicode（Python 3.6+）

Python 3.6 之前，Windows 上的 Python 通过 ANSI API（`WriteConsoleA`）向控制台写入文本——这套 API 受系统代码页限制，GBK 字符集之外的内容（emoji、特殊符号）无法通过。

从 Python 3.6 开始，Windows 上的 Python 改用 Unicode Console API（`WriteConsoleW`），**直接向控制台写入 UTF-16LE（Windows 内部编码），完全绕过代码页限制**。这是最关键的一步。

### PEP 540 — UTF-8 模式（Python 3.7+）

Python 3.7 进一步引入了 UTF-8 模式：当检测到终端支持 Unicode 输出时，自动将 `sys.stdout.encoding` 设为 `utf-8`。这意味着你打印 `sys.stdout.encoding` 时看到的是 `utf-8`，而不是 `gbk`。

### 终端的进化

| 终端产品 | 推出时间 | UTF-8 支持 |
|----------|----------|-----------|
| VSCode 内置终端 | 2015（xterm.js） | ✅ 从第一天起就是 UTF-8 |
| Windows Terminal (wt.exe) | 2019 | ✅ 原生 UTF-8，Windows 11 默认终端 |
| Windows 10 1903+ "Beta: UTF-8" | 2019 | ✅ 系统级 UTF-8 代码页（需手动开启） |

**一句话总结**：在 现代 Windows + 现代 Python 3.6+ + 现代终端（VSCode / Windows Terminal）的组合下，你不需要手动设置任何东西——emoji 和特殊字符直接就能正常输出。

## 方案（防御性写法）

虽然现代环境通常不需要，但为了**兼容旧环境**或在**不确定运行环境**时确保健壮性，以下是防御性写法：

```python
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
```

| 参数 | 说明 |
|------|------|
| `encoding="utf-8"` | 将标准输出编码设为 UTF-8 |
| `errors="replace"` | 无法编码的字符用 `?` 替换，避免 `UnicodeEncodeError` |

> **注意**：在现代 Python 3.6+ + UTF-8 终端中，`reconfigure(encoding="utf-8")` 对已经是 UTF-8 的 stdout 再做一次设置，属于**无害的 no-op**——不会影响功能，只是多余调用。

## 要点

- Python 3.6+ 在 Windows 上**默认已能输出 Unicode**，无需手动设置
- 以下情况**仍建议保留**防御性代码：
  - 脚本需要在**不确定的旧 Windows 环境**中运行
  - 目标环境可能是**传统 cmd.exe** 且 Python < 3.6
  - 你希望**明确表达编码意图**，让代码更具可读性
- `sys.platform == "win32"` 确保只在 Windows 下执行，跨平台安全
- `errors="replace"` 是**兜底策略**——即使最坏情况也不会因为一个字符让脚本崩溃
- 替代方案：终端执行 `chcp 65001` 切换到 UTF-8 代码页（临时方案，每次需手动设置）

## 环境自检

运行以下代码快速了解当前环境的编码状态：

```python
import sys

print(f"sys.platform            = {sys.platform}")
print(f"sys.getdefaultencoding()= {sys.getdefaultencoding()}")
print(f"sys.stdout.encoding     = {sys.stdout.encoding}")

# Windows 下查看终端代码页
if sys.platform == "win32":
    import subprocess
    cp = subprocess.run(
        ["chcp"], shell=True, capture_output=True, text=True
    )
    print(f"终端代码页(chcp)        = {cp.stdout.strip()}")
```

---

## 真实历史小故事：为什么 Windows 的代码页是 936，而 Web 世界选择了 UTF-8？

这个故事要从 **1993 年**讲起。

当时，Windows 刚刚发布中文版（Windows 3.1 中文版），微软需要一种方式让中国用户能在电脑上输入和显示汉字。那时 Unicode 标准刚刚诞生（1991 年发布 1.0 版），远远没有普及。微软的选择是沿用中国国家标准 **GB 2312**，并将其扩展为 **GBK**（"扩展国标"），分配了代码页编号 **936**。

这个决定在当时是**完全合理的**——1993 年的硬盘只有几百 MB，GBK 用 2 字节编码一个汉字，而 Unicode 需要 2-4 字节；1993 年的内存只有几 MB，GBK 只需要维护 21886 个字符的映射表，远小于 Unicode 的野心。在那个年代，"兼容本国标准"比"全球统一编码"更重要——用户能用中文就已经是巨大的进步了。

时间快进到 **2000 年代初**，Web 开始爆发。

一个日本工程师在 2002 年写了一篇博客，抱怨他搭建的日文 BBS 系统在处理用户提交的中文、韩文、阿拉伯文混合帖子时，数据库中产生了大量无从修复的乱码。他尝试了 Shift_JIS（日文代码页 932）、EUC-JP、GBK，甚至自己写了一个混合编码方案——统统失败。同一条帖子里如果混入了跨代码页的文字，那就是一场灾难：Shift_JIS 的「表示」和 GBK 的「表示」占用的字节序列完全不同，它们在数据库里互相覆盖，最终谁也还原不回去。

这个问题有一个名字——**代码页冲突（Code Page Collision）**。在 90 年代末到 2000 年代初，这是多语言 Web 应用的头号噩梦。每个国家有自己的代码页，每个代码页对同一个字节有不同的解释，数据一旦跨代码页存储，就再也无法无损还原。

而在这个时候，一个叫 **Ken Thompson**（对，就是那个 Ken Thompson——Unix 之父、Go 语言联合发明人）和 **Rob Pike** 在贝尔实验室设计了一个东西：**UTF-8**。

UTF-8 的设计理念堪称天才：
- 它**完全兼容 ASCII**——所有 ASCII 字符在 UTF-8 中保持单字节不变，这意味着所有已有的英文系统、英文协议（HTTP、SMTP、JSON）无需任何修改就能直接处理 UTF-8
- 它是**自同步的**——即使从中间截断一个多字节序列，你也能从下一个字符的起始字节重新对齐
- 它用一个编码空间容纳了**全人类所有书写系统**——中文、日文、韩文、阿拉伯文、希伯来文、盲文、emoji……全部在同一个表里

到了 **2008 年**，谷歌做了一个影响深远的决定：**将所有产品内部处理的默认编码从各自代码页统一为 UTF-8**。同一时期，Python 3（2008 年发布）做了一个痛苦但正确的选择：将所有字符串的内部表示统一为 Unicode，默认源文件编码为 UTF-8。Ruby 1.9、PHP 6（后改为 PHP 5.4+）纷纷跟进。

到 **2010 年代中后期**，UTF-8 已经成为事实上的标准——超过 **95% 的网页**使用 UTF-8 编码。整个互联网是 UTF-8 的，所有的 JSON API 是 UTF-8 的，所有的现代编程语言默认源文件编码都是 UTF-8 的。

**但**——Windows 的 cmd.exe 没有跟上。直到 Windows 10 时代，cmd.exe 的默认代码页依然是 936（简体中文）/ 932（日文）/ 949（韩文）……这就像一个矗立在 UTF-8 海洋中的孤岛。

为什么不改？因为**向后兼容**是微软的信仰。数以百万计的企业内部系统、批处理脚本、遗留应用依赖于代码页假设。如果微软在某次 Windows 更新中把 cmd.exe 的默认代码页从 936 改成 UTF-8，可能会无声地破坏那些依赖 GBK 输出的系统——这些系统连报错都不会有，只是悄悄地输出乱码。

所以直到 **2019 年**，微软才用了一个迂回策略：推出全新产品 **Windows Terminal**，从一开始就是 UTF-8 原生的，旧 cmd.exe 保持不变。同时，Windows 10 1903 在区域设置中增加了一个 **Beta 选项**，允许用户手动切换到系统级 UTF-8。

而 Python 社区没有等微软——他们用 PEP 528 / 529（Python 3.6, 2016 年）从**应用层**直接绕过代码页限制，调用 Unicode Console API。这是一个漂亮的"你不改我绕过去"方案。

所以，你今天在 VSCode 的终端里打印 emoji 时一切正常，背后是三十年的编码演进史：
- 1993 年，GBK 是一个务实的选择
- 2002 年，多语言冲突让 UTF-8 成为必然
- 2008 年，谷歌和 Python 3 押注 UTF-8
- 2016 年，Python 绕过 Windows 代码页
- 2019 年，微软用新终端告别旧代码页

你看到的每一个正常显示的 emoji，都是这些决策的余晖。
