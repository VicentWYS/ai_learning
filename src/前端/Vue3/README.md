## 简介
Vue是一款用于构建用户界面的 JavaScript 框架。它基于标准 HTML、CSS 和 JavaScript 构建，并提供了一套声明式的、组件化的编程模型，帮助你高效地开发用户界面。无论是简单还是复杂的界面，Vue 都可以胜任。

## 学习目标
- 官网：https://cn.vuejs.org/
- 官方教程：https://cn.vuejs.org/guide/introduction.html

| 天数   | 学习内容                    | 输出         |
| ---- | ----------------------- | ---------- |
| Day1 | Vue 基础、项目创建、SFC、模板语法    | 能显示动态数据    |
| Day2 | ref、reactive、事件、v-model | 能做输入框和按钮   |
| Day3 | v-for、组件、props、emit     | 能拆分聊天页面    |
| Day4 | axios/fetch、FastAPI 对接  | 能发送消息并显示回复 |
| Day5 | 生命周期、computed、watch     | 完善聊天逻辑     |
| Day6 | Vue Router、简单页面         | 能做多页面      |
| Day7 | 完成一个 ChatGPT 简易版页面      | 整体串联       |


可以把这一周的目标直接设为：

- 第 1 天：搭建 Vue 项目，显示一个输入框和按钮。
- 第 2 天：实现聊天消息列表（v-for、组件、v-model）。
- 第 3 天：接入 FastAPI /chat 接口，实现一次完整请求。
- 第 4 天：支持消息历史、加载状态、错误提示。
- 第 5 天：支持 Enter 发送、自动滚动、Markdown 渲染。
- 第 6 天：加入侧边栏、模型选择、设置页面。
- 第 7 天：整体重构，整理项目结构。

这样，一周结束时，你不仅学会了 Vue3 的核心能力，还拥有了一个真正可运行的 AI 对话前端。之后继续学习 RAG、Agent 或多轮对话时，可以直接在这个项目上迭代，而不用重新搭建前端框架。

## 配置环境
- 电脑上安装 vscode, 安装 vue(official) 插件。
- 电脑上安装 Node.js（推荐使用最新的 LTS 版本）。
- 验证：在终端中输入 `node -v`，如果显示版本号，则表示安装成功。
- 进入前端目录：`cd 前端项目目录`
- 创建vue项目: `npm create vue@latest`
- 进入vue项目：`cd 项目名称`
- 安装依赖：`npm install`
- 运行项目：`npm run dev`
- 发布到生产环境：`npm run build`
