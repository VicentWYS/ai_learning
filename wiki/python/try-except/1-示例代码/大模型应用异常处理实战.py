"""
大模型应用异常处理实战 —— 一个 AI 知识问答助手

场景说明：
  用户上传一篇技术文档，向 AI 提问。系统需要完成以下步骤：
    步骤 1：加载文档
    步骤 2：调用 Embedding API，把文档转成向量
    步骤 3：在向量库中检索相关内容
    步骤 4：调用 Chat API，生成最终回答

  每一步都可能失败，且失败策略各不相同。
  本文件演示如何用"ABCD 分类法"设计完整的异常处理体系。
"""

import os
import time
import logging
from dataclasses import dataclass
from typing import Optional

# ── 日志配置 ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ai_qa")


# ============================================================
# 第一部分：自定义异常体系
# ============================================================
# 目的：让上层调用者不需要关心底层是 openai 的错误还是 langchain 的错误，
#       只需要按"策略分类"来捕获即可。

class AIQASystemError(Exception):
    """AI 问答系统所有异常的基类"""
    pass


# ── B 类异常：用户修正即可 ────────────────────────────────
class ConfigError(AIQASystemError):
    """配置错误——API Key 没配、Base URL 写错等"""
    pass


class DocumentLoadError(AIQASystemError):
    """文档加载失败——文件不存在、格式不支持等"""
    pass


# ── D 类异常：致命错误，程序无法继续 ──────────────────────
class EmbeddingFatalError(AIQASystemError):
    """向量化致命错误——反复重试后仍然失败"""
    pass


class ChatFatalError(AIQASystemError):
    """对话生成致命错误"""
    pass


# ============================================================
# 第二部分：模拟外部依赖（实际开发中这些是真实的 API 调用）
# ============================================================

class SimulatedEmbeddingAPI:
    """
    模拟 Embedding API。
    实际开发中，这里是对 openai.Embedding.create() 或类似接口的调用。
    """

    def __init__(self, fail_mode: Optional[str] = None):
        """
        fail_mode:
          None        → 正常
          "timeout"   → 模拟超时
          "auth"      → 模拟认证失败
          "rate_limit"→ 模拟限流
        """
        self.fail_mode = fail_mode

    def embed(self, text: str) -> list[float]:
        if self.fail_mode == "timeout":
            raise TimeoutError("Embedding API 响应超时")
        if self.fail_mode == "auth":
            raise RuntimeError("AuthenticationError: Invalid API key")  # 模拟 SDK 抛出的认证异常
        if self.fail_mode == "rate_limit":
            raise RuntimeError("RateLimitError: Too many requests")
        # 正常返回
        return [0.1, 0.2, 0.3]  # 假的向量


class SimulatedChatAPI:
    """模拟 Chat API。"""

    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode

    def chat(self, prompt: str) -> str:
        if self.fail_mode == "timeout":
            raise TimeoutError("Chat API 响应超时")
        if self.fail_mode == "connection":
            raise ConnectionError("Chat API 连接失败")
        return f"这是对 '{prompt[:30]}...' 的回答"


class SimulatedVectorDB:
    """模拟向量数据库检索。"""

    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode

    def search(self, query_vector: list[float], top_k: int = 3) -> list[str]:
        if self.fail_mode == "empty":
            return []  # 不是异常，但业务上需要考虑
        if self.fail_mode == "corrupt":
            raise RuntimeError("向量库索引损坏")
        return ["相关片段1", "相关片段2", "相关片段3"]


# ============================================================
# 第三部分：各子步骤——各自内建异常处理
# ============================================================

# ── 步骤 1：加载文档 ──────────────────────────────────────
# 策略：B 类——失败了用户换个文件就好，不需要重试

def load_document(file_path: str) -> str:
    """加载文档内容。失败时抛出 DocumentLoadError（B 类）。"""
    if not os.path.exists(file_path):
        raise DocumentLoadError(
            f"文件不存在：{file_path}\n"
            f"请确认文件路径是否正确，文件是否已被移动或删除。"
        )

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError as e:
        raise DocumentLoadError(
            f"文件编码不支持：{e}\n"
            f"请将文件保存为 UTF-8 编码格式后重试。"
        ) from e
    except PermissionError as e:
        raise DocumentLoadError(
            f"没有权限读取文件：{e}\n"
            f"请检查文件权限设置。"
        ) from e

    if not content.strip():
        raise DocumentLoadError("文档内容为空，请提供有效的文档。")

    logger.info(f"文档加载成功，共 {len(content)} 字符")
    return content


# ── 步骤 2：文档向量化（含重试逻辑） ──────────────────────
# 策略：A 类异常（超时、限流）→ 自动重试
#       B 类异常（认证失败）→ 立即失败，提示用户

def embed_document(
    text: str,
    embedding_api: SimulatedEmbeddingAPI,
    max_retries: int = 3,
) -> list[float]:
    """
    将文档转换为向量。内建完整的异常分类处理。

    返回：向量列表；失败时抛出 ConfigError（B 类）或 EmbeddingFatalError（D 类）
    """

    # ═══════════════════════════════════════════════════════
    # 关键设计：用 try-except 的嵌套结构实现"先重试，重试耗尽后再分类"
    # ═══════════════════════════════════════════════════════

    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Embedding 调用：第 {attempt}/{max_retries} 次")
            result = embedding_api.embed(text)
            logger.info(f"Embedding 成功，向量维度：{len(result)}")
            return result

        except TimeoutError as e:
            # ── A 类：超时 → 指数退避重试 ──────────────
            last_error = e
            wait = 2 ** attempt
            logger.warning(
                f"Embedding 超时 (第 {attempt}/{max_retries} 次)，{wait}s 后重试..."
            )
            if attempt < max_retries:
                print(f"⏳ Embedding 服务响应慢，正在第 {attempt} 次重试...")
                time.sleep(wait)
            # 最后一次也失败，落到下面的"重试耗尽"处理

        except RuntimeError as e:
            # ── 模拟 SDK 异常：需要按消息内容细分 ──────
            msg = str(e).lower()
            last_error = e

            if "authentication" in msg:
                # B 类：认证失败，重试没用
                raise ConfigError(
                    "Embedding API Key 无效。\n"
                    "请检查 .env 文件中的 API Key 是否正确，是否已过期。"
                ) from e

            if "rate_limit" in msg:
                # A 类：限流，指数退避重试
                wait = 2 ** attempt
                logger.warning(f"触发限流，{wait}s 后重试...")
                if attempt < max_retries:
                    print(f"⏳ Embedding 请求太频繁，{wait}s 后重试...")
                    time.sleep(wait)
                continue

            # 无法识别的 RuntimeError，不重试，直接抛
            raise EmbeddingFatalError(
                f"Embedding API 返回未知错误：{e}"
            ) from e

        except Exception as e:
            # 兜底：从未见过的异常，不重试
            raise EmbeddingFatalError(
                f"Embedding 过程发生未预期的错误：{type(e).__name__}: {e}"
            ) from e

    # ── 重试耗尽 ──────────────────────────────────────────
    raise EmbeddingFatalError(
        f"Embedding 在 {max_retries} 次重试后仍然失败。\n"
        f"最后错误：{type(last_error).__name__}: {last_error}\n"
        f"请稍后再试，或联系服务商检查服务状态。"
    )


# ── 步骤 3：向量检索（含降级策略） ────────────────────────
# 策略：如果检索本身抛异常 → C 类降级（用空结果继续，不影响主流程）
#       如果返回空结果 → 不是异常，但需要在生成回答时处理

def retrieve_context(
    query_vector: list[float],
    vector_db: SimulatedVectorDB,
) -> tuple[list[str], bool]:
    """
    检索相关内容。
    返回：(结果列表, 是否来自降级)
    """
    try:
        results = vector_db.search(query_vector, top_k=3)
    except Exception as e:
        # C 类：检索失败，降级为"无上下文"
        logger.warning(f"向量检索失败，降级为空上下文：{e}")
        print("⚠️ 知识库检索暂时不可用，将基于模型自身知识回答。")
        return [], True  # True 表示这是降级结果

    if not results:
        logger.info("检索完成但无匹配结果")
        print("ℹ️ 未在文档中找到相关内容，将基于模型自身知识回答。")
    else:
        logger.info(f"检索到 {len(results)} 条相关内容")

    return results, False


# ── 步骤 4：调用 Chat API 生成回答（含重试 + 降级）──────
# 策略：A 类异常 → 重试
#       重试耗尽 → 降级返回，而不是直接崩溃

def generate_answer(
    prompt: str,
    chat_api: SimulatedChatAPI,
    max_retries: int = 2,
) -> str:
    """
    调用 Chat API 生成回答。
    重试失败后降级，而不是抛异常让整个程序崩溃。
    """

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Chat API 调用：第 {attempt}/{max_retries} 次")
            answer = chat_api.chat(prompt)
            logger.info("Chat API 调用成功")
            return answer

        except TimeoutError as e:
            # A 类：超时重试
            wait = 2 ** attempt
            logger.warning(f"Chat API 超时，{wait}s 后重试...")
            if attempt < max_retries:
                print(f"⏳ AI 响应较慢，正在重试...")
                time.sleep(wait)
                continue
            # 重试耗尽 → 降级
            logger.error(f"Chat API 重试 {max_retries} 次后仍超时")
            return (
                "抱歉，AI 服务当前响应较慢，暂时无法生成完整回答。\n"
                "请稍后重试，或简化您的问题。"
            )

        except ConnectionError as e:
            # A 类：连接失败重试
            wait = 2 ** attempt
            logger.warning(f"Chat API 连接失败，{wait}s 后重试...")
            if attempt < max_retries:
                print(f"⏳ 连接 AI 服务失败，正在重试...")
                time.sleep(wait)
                continue
            # 重试耗尽 → 降级
            logger.error(f"Chat API 连接重试 {max_retries} 次后仍失败")
            return (
                "抱歉，当前无法连接到 AI 服务。\n"
                "请检查网络连接后重试。"
            )

        except Exception as e:
            # 未知异常 → 直接降级，不重试
            logger.exception("Chat API 发生未预期异常")
            return f"抱歉，生成回答时出现错误。详情已记录日志，请稍后重试。"

    # 理论上不会到这里，但作为防御性编程的兜底
    return "抱歉，AI 服务暂时不可用。"


# ============================================================
# 第四部分：主流程——编排所有步骤，集中的异常分发
# ============================================================

@dataclass
class QAResult:
    """问答结果，统一的数据结构"""
    success: bool
    answer: str
    error_message: str = ""
    degraded: bool = False  # 是否经过了降级处理


def ai_qa_pipeline(
    file_path: str,
    question: str,
    embedding_api: SimulatedEmbeddingAPI,
    chat_api: SimulatedChatAPI,
    vector_db: SimulatedVectorDB,
) -> QAResult:
    """
    AI 问答主流程。
    按顺序执行：加载文档 → 向量化 → 检索 → 生成回答。

    每一层的异常要么被内部处理，要么上升到这一层统一处理。
    这一层只做"最终决策"：是提示用户、还是降级返回、还是致命退出。
    """

    # ── 步骤 1：加载文档 ──────────────────────────────────
    # B 类异常直接向上抛到 main()，因为没文档后面的步骤没有意义
    try:
        document = load_document(file_path)
    except DocumentLoadError as e:
        return QAResult(
            success=False,
            answer="",
            error_message=str(e),
        )

    # ── 步骤 2：文档向量化 ────────────────────────────────
    try:
        doc_vector = embed_document(document, embedding_api)
    except ConfigError as e:
        # B 类：配置问题，告诉用户
        return QAResult(
            success=False,
            answer="",
            error_message=str(e),
        )
    except EmbeddingFatalError as e:
        # D 类：致命错误
        logger.exception("文档向量化致命失败")
        return QAResult(
            success=False,
            answer="",
            error_message=(
                f"文档处理失败：{e}\n"
                f"建议：稍后重试，或检查 Embedding 服务状态。"
            ),
        )

    # ── 步骤 3：检索相关内容 ──────────────────────────────
    # 注意：C 类降级已经在 retrieve_context 内部处理，
    #       这里只需要处理降级后的结果
    retrieved_docs, is_degraded = retrieve_context(doc_vector, vector_db)

    # ── 步骤 4：构建 prompt + 生成回答 ────────────────────
    # A 类重试 + 降级已在 generate_answer 内部处理

    if retrieved_docs:
        context = "\n".join(retrieved_docs)
        prompt = f"根据以下参考资料回答问题。\n\n参考资料：\n{context}\n\n问题：{question}"
    else:
        prompt = f"请根据你的知识回答问题。\n\n问题：{question}"

    answer = generate_answer(prompt, chat_api)

    # 判断回答是否是降级结果
    is_answer_degraded = "抱歉" in answer and ("重试" in answer or "稍后" in answer)

    return QAResult(
        success=True,
        answer=answer,
        degraded=is_degraded or is_answer_degraded,
    )


# ============================================================
# 第五部分：程序入口——最外层的"终极兜底"
# ============================================================

def main():
    """
    程序入口。
    这里的 try-except 是最后一道防线：
    - 捕获所有在 ai_qa_pipeline 中没处理到的异常
    - 打印清晰友好的错误信息
    - 确保程序不会"裸崩"
    """

    print("=" * 60)
    print("  AI 知识问答助手")
    print("=" * 60)
    print()

    # ── 初始化外部依赖 ────────────────────────────────────
    # 实际开发中替换为真实的 API 对象
    embedding_api = SimulatedEmbeddingAPI(fail_mode=None)  # None="timeout"/"auth"/"rate_limit"
    chat_api = SimulatedChatAPI(fail_mode=None)            # None="timeout"/"connection"
    vector_db = SimulatedVectorDB(fail_mode=None)          # None="empty"/"corrupt"

    # ── 执行问答 ──────────────────────────────────────────
    try:
        result = ai_qa_pipeline(
            file_path="knowledge_base/技术文档.txt",  # 请替换为实际文件路径
            question="什么是异常处理的 ABCD 分类法？",
            embedding_api=embedding_api,
            chat_api=chat_api,
            vector_db=vector_db,
        )

        if result.success:
            print(f"\n{'─' * 40}")
            print(f"📝 AI 回答{' (降级模式)' if result.degraded else ''}：")
            print(f"{'─' * 40}")
            print(result.answer)
            print(f"{'─' * 40}")
        else:
            print(f"\n❌ 问答失败：\n{result.error_message}")

    except DocumentLoadError as e:
        # B 类：还没被 ai_qa_pipeline catch，可能是 load_document 里没覆盖到的
        print(f"❌ 文档加载失败：{e}")

    except ConfigError as e:
        # B 类
        print(f"❌ 配置错误：{e}")

    except AIQASystemError as e:
        # 我们自定义的所有异常的兜底
        print(f"❌ 系统错误：{e}")

    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作。")

    except Exception as e:
        # D 类：终极兜底——我们完全没预料到的问题
        print(f"\n❌ 程序遇到未预期的错误：{type(e).__name__}: {e}")
        print("详细错误信息已记录到日志。")
        logger.exception("主程序未捕获的异常")


# ============================================================
# 第六部分：测试不同故障模式
# ============================================================

def test_failure_modes():
    """
    演示不同故障模式下系统的行为。
    逐个测试：认证失败 → 超时 → 连接失败 → 检索故障。
    """
    print("\n\n")
    print("=" * 60)
    print("  故障模式测试")
    print("=" * 60)

    test_cases = [
        {
            "name": "场景1：正常流程",
            "embedding_mode": None,
            "chat_mode": None,
            "vector_db_mode": None,
        },
        {
            "name": "场景2：Embedding 认证失败（B 类——立即失败）",
            "embedding_mode": "auth",
            "chat_mode": None,
            "vector_db_mode": None,
        },
        {
            "name": "场景3：Embedding 超时（A 类——自动重试）",
            "embedding_mode": "timeout",
            "chat_mode": None,
            "vector_db_mode": None,
        },
        {
            "name": "场景4：Chat 连接失败（A 类——重试后降级）",
            "embedding_mode": None,
            "chat_mode": "connection",
            "vector_db_mode": None,
        },
        {
            "name": "场景5：向量库损坏（C 类——降级空上下文）",
            "embedding_mode": None,
            "chat_mode": None,
            "vector_db_mode": "corrupt",
        },
    ]

    for case in test_cases:
        print(f"\n{'─' * 60}")
        print(f"🔬 {case['name']}")
        print(f"{'─' * 60}")

        embedding_api = SimulatedEmbeddingAPI(fail_mode=case["embedding_mode"])
        chat_api = SimulatedChatAPI(fail_mode=case["chat_mode"])
        vector_db = SimulatedVectorDB(fail_mode=case["vector_db_mode"])

        result = ai_qa_pipeline(
            file_path=__file__,  # 用这个文件本身当输入，保证文件存在
            question="什么是 ABCD 分类法？",
            embedding_api=embedding_api,
            chat_api=chat_api,
            vector_db=vector_db,
        )

        if result.success:
            status = "⚠️ 降级" if result.degraded else "✅ 正常"
            print(f"结果：{status}")
            print(f"回答：{result.answer[:80]}...")
        else:
            print(f"结果：❌ 失败")
            print(f"原因：{result.error_message[:100]}")


if __name__ == "__main__":
    # main()
    test_failure_modes()
