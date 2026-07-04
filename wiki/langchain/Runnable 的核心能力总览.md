| 能力    | 方法                     | 解决的问题            |       |
| ----- | ---------------------- | ---------------- | ----- |
| 单次调用  | invoke                 | 普通调用             |       |
| 批量调用  | batch                  | 并行优化             |       |
| 流式输出  | stream                 | 实时输出             |       |
| 自动重试  | with_retry             | 网络不稳定            |       |
| 失败降级  | with_fallbacks         | 模型宕机             |       |
| 结构化输出 | with_structured_output | JSON解析           |       |
| 绑定参数  | bind                   | 固定部分参数           |       |
| 类型约束  | with_types             | 类型安全             |       |
| 链式组合  | pipe / `               | `                |        |
| 配置注入  | with_config            | tracing/metadata |       |


可以从代码中一直查看 model 的父类，会一直往上追溯到 Runnable 类，查看 Runnable 类的方法，就可以知道 Runnable 类有哪些能力。

Runnable 类是所有可运行对象的基类，所以所有可运行对象都有这些能力。

这些能力包括：
- 单次调用 （invoke）
- 批量调用 （batch）
- 流式输出 （stream）
- 自动重试 （with_retry）
- 失败降级 （with_fallbacks）
- 结构化输出 （with_structured_output）
- 绑定参数 （bind）
- 类型约束 （with_types）
- 链式组合 （pipe / `）
- 配置注入 （with_config）

查看 langchain_core/runnables/base.py 文件，可以看到 Runnable 类的方法。

