
# 1. 初始化项目
```bash
# 初始化项目
cd my-project
git init
git status

# 创建第一次提交
git add .
git commit -m "Initial commit"
git log --oneline

# 查看当前分支（应为 * main）
git branch

# 创建 develop 分支
git switch -c develop
```


# 2. 开发流程（多次重复）
## 2.1 创建功能分支并修改提交
```bash
# 创建功能分支
git switch develop
git switch -c feature/login

# 修改代码

# 提交
git status
git add .
git commit -m "Add login feature"
git log --oneline --graph --all
```

## 2.2 功能完成，合并回 develop
```bash
# 切换，合并
git switch develop
git merge feature/login

# 删除功能分支
git branch -d feature/login
git branch
```


# 3. 发布版本：develop → main
假设 develop 测试完成。

```bash
# 切换 main
git switch main
git merge develop
git log --oneline

# 创建版本标签
git tag -a v1.0 -m "Release version 1.0"
git tag
git show v1.0

# 发布后同步 develop
git switch develop
git merge main
```

# 4. 推送到远程 GitHub 仓库
本地提交、合并、打 tag 都只影响本地仓库，需要单独用 `git push` 推送到 GitHub。

## 4.1 关联远程仓库（只需一次）
先在 GitHub 上建一个空仓库，然后在本地执行：

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git remote -v   # 确认已关联
```

## 4.2 推送分支
本流程涉及 `main` 和 `develop` 两个分支，都要推上去：

```bash
# 首次推送 main，并让本地 main 跟踪远程
git push -u origin main

# 推送 develop
git push -u origin develop
```

`-u`（`--set-upstream`）只需第一次加，之后在对应分支上直接 `git push` 即可。

## 4.3 推送标签（tag）
tag 默认不会随分支推送，要单独推：

```bash
git push origin v1.0
# 或者一次性推送所有本地 tag
git push origin --tags
```

> 推送需要 GitHub 账号凭证。GitHub 从 2021 年起不再支持账号密码推送，需要用 **Personal Access Token (PAT)**，或配置 **SSH 密钥**。


# 5. 查看提交记录
切换到 main 分支。可通过以下指令，只关注打了tag的记录，从而快速得到一条 main 分支干净的版本线。

```bash
# main 分支上只查看包含tag的记录
git log --oneline --tags --simplify-by-decoration
```
