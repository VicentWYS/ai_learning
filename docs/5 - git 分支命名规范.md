
分支名不是随便起的。  
在公司里，**分支名本身就是“任务说明书”**。


## 一、公司里通用的分支命名结构
标准结构：

```
类型/简短描述
```

例如：

```
feature/prompt-template
fix/prompt-bug
refactor/prompt-structure
docs/readme-update
```

看到分支名，就知道你在干嘛。


## 二、最常用的“类型”只有这 6 个

|类型|含义|什么时候用|示例|
|:---:|:---:|:---:|---|
|feature|新功能 / 新模块|学一个新知识点|feature/langchain-prompt-template|
|fix|修 bug|代码有问题|fix/prompt-variable-error|
|refactor|重构|不加功能，只改结构|refactor/prompt-code-structure|
|docs|文档|改 README、注释|docs/add-usage-guide|
|test|测试相关|加测试代码|test/prompt-template-test|
|chore|杂事|配置、依赖、环境|chore/add-gitignore|

你现在学习阶段，**90% 用 feature**。


## 三、描述部分怎么写
规则只有三条：
1. 全小写
2. 单词用 `-` 连接
3. 一眼能看懂在干嘛

❌ 错误示例：

```
feature/test1
feature/newcode
feature/学习prompt
```

✅ 正确示例：

```
feature/langchain-prompt-template
feature/langchain-output-parser
feature/langchain-rag-pipeline
```

你以后回头看，**这是你的学习路线图**。


## 四、进阶：如果是公司，还会加任务号

例如：

```
feature/1234-prompt-template
fix/2345-variable-error
```

任务号来自 Jira / 禅道。

你现在不用，但知道这是**企业味道**。


## 五、非常关键的一点

> **分支名 = commit 的“上级语义”**

commit 是步骤：

```
feat: add basic example
feat: add partial variables
feat: add error handling
```

分支是目标：

```
feature/langchain-prompt-template
```

组合起来，历史会极其清晰。


## 六、给你量身定做一套

你后续可以这样命名：

```
feature/langchain-prompt-template
feature/langchain-model-invoke
feature/langchain-output-parser
feature/langchain-rag
feature/langchain-agent
```

将来你看 `git branch`，会非常震撼：

> 这不是分支列表，这是你的 LangChain 知识体系。


## 七、一句话记住规范

> **类型 + / + 做什么**

就够了。


## 八、再给你一个“工程味”小技巧

创建分支时直接这样：

```bash
git checkout -b feature/langchain-prompt-template
```

不要先起名再改，**一步到位**。

