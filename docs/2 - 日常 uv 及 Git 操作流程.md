
## uv 操作流程
激活项目：

```bash
cd 本项目
```

```bash
.venv\Scripts\activate
```

安装新依赖：
```bash
uv add xxx
```


## 编程流程
1. 明确需求
2. 编写代码，测试验证
3. 编写文档，记录开发过程和总结
4. 提交 Git，开 PR，Merge


## Git 使用流程
### 新建项目，并提交远程仓库：

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/VicentWYS/ai_learning
git push -u origin main
```

### 代码更新，与版本控制：
```bash
git checkout main
git pull origin main
git checkout -b feature/xxx

# 开发中反复
git add .
git commit -m "feat: xxx"

git push -u origin feature/xxx
# 去 GitHub 开 PR 并 Merge

git checkout main
git pull origin main
git branch -d feature/xxx
git push origin --delete feature/xxx
git fetch -p
```

### commit 与 push

- `commit`：记录开发过程中的一个个里程碑，建议小步提交、频繁提交，每次提交都对应一个清晰、独立的改动。
- `push`：将已经准备好共享的提交同步到远程仓库，通常在阶段性完成、需要备份、需要协作或准备发起代码评审时进行。

实际团队开发中，一个开发者一天可能会有 10～30 次 commit，但通常只会 2～10 次 push。也就是说，commit 的频率通常高于 push，这是比较推荐的工作习惯。

```
开始开发
↓
修改代码
↓
git add .
↓
git commit -m "完成登录接口"
↓
继续开发
↓
git commit -m "增加验证码"
↓
继续开发
↓
git commit -m "优化异常处理"
↓
所有功能完成
↓
本地测试通过
↓
git push origin feature/login
↓
创建 Pull Request / Merge Request
```