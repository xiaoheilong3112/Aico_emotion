# Git 配置指南 - AICO 情感系统

## 当前配置状态

### 远程仓库
✅ **GitHub**: https://github.com/xiaoheilong3112/Aico_emotion.git (远程名: `github`)
✅ **阿里云 Codeup**: git@codeup.aliyun.com:694b798cba2d7df023d98815/robotics/Aico_emotion.git (远程名: `origin`)

### 用户信息
- **用户名**: AICO Dev Team
- **邮箱**: dev@aico.local

---

## 日常使用

### 提交代码（使用中文！）

```bash
# 1. 查看修改
git status

# 2. 添加文件
git add .

# 3. 提交（必须使用中文提交消息）
git commit -m "功能: 添加音频感知模块"

# 4. 推送到 GitHub
git push github master

# 5. （可选）同时推送到阿里云
git push origin main
```

### 提交类型（中文）

| 类型 | 说明 | 英文对应 |
|------|------|----------|
| 功能 | 新功能 | feat |
| 修复 | Bug 修复 | fix |
| 性能 | 性能优化 | perf |
| 重构 | 代码重构 | refactor |
| 测试 | 测试相关 | test |
| 文档 | 文档更新 | docs |
| 构建 | 构建/工具/依赖 | chore |

### 提交示例

```bash
# 新功能
git commit -m "功能: 添加音频感知模块与 VAD 映射"
git commit -m "功能: 实现多模态情感融合"

# Bug 修复
git commit -m "修复: 解决 blendshapes 计算溢出问题"
git commit -m "修复: 修复手势识别在低光照下的误检"

# 性能优化
git commit -m "性能: 优化人脸检测速度提升 30%"
git commit -m "性能: 减少内存占用 50MB"

# 重构
git commit -m "重构: 提取公共感知基类"
git commit -m "重构: 统一 VAD 映射接口"

# 测试
git commit -m "测试: 添加音频模块单元测试"
git commit -m "测试: 添加 FER2013 数据集测试"

# 文档
git commit -m "文档: 更新 API 使用文档"
git commit -m "文档: 添加性能优化指南"

# 构建
git commit -m "构建: 更新 MediaPipe 到 0.10.31"
git commit -m "构建: 添加 requirements.txt 依赖"
```

---

## 首次推送到 GitHub

如果是首次推送，需要设置上游分支：

```bash
# 首次推送到 GitHub
git push -u github main

# 之后就可以简写
git push github master
```

---

## 同时推送到两个远程仓库

### 方法 1: 分别推送
```bash
git push github master
git push origin main
```

### 方法 2: 配置 push 到两个远程
```bash
# 添加第二个 push URL
git remote set-url --add --push origin https://github.com/xiaoheilong3112/Aico_emotion.git

# 之后 git push origin main 会同时推送到两个仓库
```

---

## 拉取更新

### 从 GitHub 拉取
```bash
git pull github main
```

### 从阿里云拉取
```bash
git pull origin main
```

---

## 分支管理

### 创建功能分支
```bash
# 创建并切换到新分支
git checkout -b feature/audio-perception

# 开发...

# 提交
git commit -m "功能: 添加音频感知模块"

# 推送分支到 GitHub
git push github feature/audio-perception

# 合并回主分支
git checkout main
git merge feature/audio-perception
git push github master
```

### 查看分支
```bash
# 本地分支
git branch

# 远程分支
git branch -r

# 所有分支
git branch -a
```

---

## 查看历史

```bash
# 查看提交历史
git log --oneline --graph --decorate -10

# 查看某个文件的历史
git log --follow src/perception/human_face.py

# 查看最近的修改
git diff HEAD~1
```

---

## 撤销操作

### 撤销未提交的修改
```bash
# 撤销工作区的修改
git checkout -- file.py

# 撤销暂存区的修改
git reset HEAD file.py

# 放弃所有本地修改
git reset --hard HEAD
```

### 修改最后一次提交
```bash
# 修改提交消息
git commit --amend -m "功能: 修正后的提交消息"

# 添加遗漏的文件
git add forgotten_file.py
git commit --amend --no-edit
```

---

## 常见问题

### Q: 如何切换默认推送的远程仓库？

**A**: 修改 `.git/config` 或使用命令：
```bash
# 设置 github 为默认 push 目标
git config branch.main.remote github
```

### Q: 忘记使用中文提交了怎么办？

**A**: 修改最后一次提交：
```bash
git commit --amend -m "功能: 新的中文提交消息"
git push github master --force  # 如果已经推送，需要强制推送
```

### Q: 推送失败怎么办？

**A**: 可能的原因和解决方法：

1. **需要认证**:
```bash
# 使用 HTTPS 时需要 GitHub Token
# 设置 credential helper
git config --global credential.helper cache
```

2. **分支冲突**:
```bash
# 先拉取再推送
git pull github main --rebase
git push github master
```

3. **权限问题**:
   - 确保你有仓库的写权限
   - 检查 GitHub Token 或 SSH Key

### Q: 如何配置 SSH 方式推送？

**A**: 修改为 SSH URL：
```bash
git remote set-url github git@github.com:xiaoheilong3112/Aico_emotion.git
```

确保已配置 SSH Key：
```bash
# 生成 SSH Key（如果没有）
ssh-keygen -t ed25519 -C "dev@aico.local"

# 添加到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥到 GitHub
cat ~/.ssh/id_ed25519.pub
# 在 GitHub Settings > SSH Keys 中添加
```

---

## Ralph Wiggum 工作流中的 Git

在 Ralph Wiggum 工作流中，AI 代理会自动：

1. ✅ 实现功能
2. ✅ 运行测试
3. ✅ 更新 `IMPLEMENTATION_PLAN.md`
4. ✅ `git add .`
5. ✅ `git commit -m "类型: 描述"` （中文）
6. ✅ `git push github master`

你只需要：
- 运行 `./loop.sh` 生成提示
- 复制到 VS Code Copilot
- AI 会处理其余的一切！

---

## 快速参考

```bash
# 日常工作流
git status                          # 查看状态
git add .                           # 添加所有修改
git commit -m "功能: 描述"         # 提交（中文）
git push github master                # 推送到 GitHub

# 查看历史
git log --oneline -10               # 最近 10 条提交
git diff                            # 查看未暂存的修改

# 分支管理
git branch                          # 查看分支
git checkout -b feature/xxx         # 创建新分支
git merge feature/xxx               # 合并分支

# 撤销操作
git reset HEAD~1                    # 撤销最后一次提交（保留修改）
git reset --hard HEAD~1             # 撤销最后一次提交（删除修改）
```

---

## 相关文档

- [AGENTS.md](AGENTS.md) - 操作命令指南
- [PROMPT_build.md](PROMPT_build.md) - 构建模式提示词
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - 实现计划
- [QUICK_START.md](QUICK_START.md) - 快速入门

**记住：所有提交消息必须使用中文！** 🇨🇳
