# LangChain 中 Middleware、State、Checkpointer 的含义与联系

基于 `main.py` 中的程序整理。

## 一、三者的含义与作用

### 1. Middleware（中间件）

- **含义**：在 Agent 图执行过程中、**模型调用前后**插入的钩子逻辑，用于横切关注点（日志、计数、修剪消息、校验输出等）。
- **约束**：必须继承 `AgentMiddleware`，并实现固定方法名：
  - `before_model(state, runtime)`：在调用模型**之前**执行；
  - `after_model(state, runtime)`：在模型**响应之后**执行；
  - 可选 `before_agent(state, runtime)`：在整次 Agent 调用更早阶段执行。
- **与 State 的关系**：两个参数里都会收到当前 `state`（及 `runtime`）。可**只读** state，也可通过**返回一个 dict** 将部分更新合并进 state（如修剪 `messages`、不做修改则返回 `None`）。
- **执行顺序**：多个中间件时，`before_model` 按配置顺序正序执行（M1→M2→M3），`after_model` 按逆序执行（M3→M2→M1），类似洋葱模型。

### 2. State（图状态）

- **含义**：LangGraph 图在执行过程中的**当前状态**，通常包含 `messages` 等键，在节点与中间件之间传递。
- **作用**：
  - 作为一次 `invoke` 的**输入**：若没有 checkpointer，则直接使用用户传入的 `input`；若有 checkpointer，会先按 `thread_id` 恢复上一轮 state，再与本次 `input` 合并得到“当前 state”。
  - 在**图执行**中：各节点和中间件读取、修改 state；中间件通过 `before_model`/`after_model` 的返回值对 state 做部分更新。
  - 作为一次 `invoke` 的**输出**：图执行结束后的 state 即为返回的 `response`；若有 checkpointer，该 state 会被保存，供下次同 `thread_id` 的 invoke 恢复。

### 3. Checkpointer（检查点存储器）

- **含义**：LangGraph 用来**持久化/恢复图状态**的组件，与一次“会话”通过 `config.configurable.thread_id` 绑定。
- **作用**：
  - **invoke 前**：若提供了 checkpointer 和 `thread_id`，LangGraph 会调用 `checkpointer.get(thread_id)`（或等价接口）恢复该会话上一轮的 state，再与本次 `input` 合并。
  - **invoke 后**：将本次执行得到的**新 state** 通过 `checkpointer.put(thread_id, state)`（或等价接口）写回，供下次同线程调用使用。
- **常见实现**：`InMemorySaver()`（内存，进程内、重启即丢）、`SqliteSaver`（SQLite 持久化，可跨重启、跨进程）。
- **与 State 的关系**：Checkpointer 只负责 state 的“存”和“取”，不参与图内逻辑；恢复出来的 state 与 input 合并后，就与无 checkpointer 时一样在图和中间件中流转。

## 二、在 LangChain 运行中的联系

1. **入口**：`agent.invoke(input, config)`。`config` 中若有 `configurable.thread_id`，且 agent 带有 checkpointer，则会先按 thread_id 恢复 state，再与 input 合并得到当前 state。
2. **图执行**：当前 state 进入图；在“调用模型”这一环节前后，会依次经过所有中间件的 `before_model` 和 `after_model`，它们可以读取并可选地更新 state。
3. **模型调用**：在中间件 before/after 之间发生，使用当时的 state（如 `messages`）作为上下文。
4. **结束**：图执行完成后得到新的 state，作为 `invoke` 的返回值；若配置了 checkpointer，该 state 会按 thread_id 写回 checkpointer。

因此：**State** 是图执行与中间件共同操作的数据对象；**Middleware** 在模型调用前后读写 state；**Checkpointer** 在 invoke 边界对 state 做跨次调用的持久化与恢复。三者通过 state 和 invoke 生命周期串联在一起。

## 三、图示

关系与单次 invoke 流程见同目录下的 **`langchain_middleware_state_checkpointer.drawio`**，可用 draw.io 或 VS Code 的 Draw.io 插件打开编辑。
