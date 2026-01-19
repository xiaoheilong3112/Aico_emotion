# AICO 情感系统 - Ralph Wiggum 快速入门

欢迎使用基于 Ralph Wiggum 工作流的 AICO 情感系统开发环境！

## 什么是 Ralph Wiggum?

Ralph Wiggum 是一种 AI 代理驱动的开发工作流，通过迭代执行、上下文隔离和状态持久化来高效完成复杂软件任务。

## 5 分钟快速开始

### 1. 查看当前项目状态

```bash
cd /media/liuyajun/Work1/code/XGO/Aico_emotion
cat IMPLEMENTATION_PLAN.md
```

这会显示:
- ✅ 已完成的任务
- 📋 待办任务列表
- 🐛 发现的问题
- 📝 开发笔记

### 2. 生成规划模式提示 (首次或需要重新规划时)

```bash
./loop.sh plan > /tmp/prompt_plan.txt
```

然后:
1. 打开 `/tmp/prompt_plan.txt`
2. 复制全部内容
3. 粘贴到 **VS Code Copilot 聊天窗口**
4. AI 会分析项目并更新 `IMPLEMENTATION_PLAN.md`
5. 检查更新后的计划

### 3. 生成构建模式提示 (日常开发)

```bash
./loop.sh build > /tmp/prompt_build.txt
# 或直接 ./loop.sh (默认是 build 模式)
```

然后:
1. 打开 `/tmp/prompt_build.txt`
2. 复制全部内容
3. 粘贴到 **VS Code Copilot 聊天窗口**
4. AI 会:
   - 选择一个高优先级任务
   - 实现功能
   - 运行测试
   - 更新计划
   - 提交代码
   - 推送到 Git

### 4. 重复构建循环

继续运行 `./loop.sh` 直到所有任务完成:

```bash
./loop.sh > /tmp/prompt_build.txt
# 复制 → 粘贴到 Copilot → 等待完成
# 重复...
```

## 工作流程图

```
┌─────────────────────────────────────────┐
│  编写/更新 specs/*.md (需求规格)        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────┐
│  ./loop.sh plan                         │
│  复制输出 → VS Code Copilot            │
│  AI 生成任务计划                        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
      ┌────────────────────────────┐
      │  ./loop.sh build           │ ←─────┐
      │  复制输出 → VS Code Copilot│      │
      │  AI 实现 1 个任务          │      │
      └─────────┬──────────────────┘      │
                │                         │
                ▼                         │
      ┌────────────────────────────┐      │
      │  检查代码 & 测试结果        │      │
      └─────────┬──────────────────┘      │
                │                         │
                ├─ 还有任务? ─────────────┘
                │
                ▼
      ┌────────────────────────────┐
      │  所有任务完成！ ✅          │
      └────────────────────────────┘
```

## 项目文件说明

| 文件 | 用途 | 谁维护 |
|------|------|--------|
| `AGENTS.md` | 操作命令指南 | 人工 |
| `IMPLEMENTATION_PLAN.md` | 任务列表和进度 | AI 自动 |
| `PROMPT_plan.md` | 规划模式提示词 | 人工 |
| `PROMPT_build.md` | 构建模式提示词 | 人工 |
| `loop.sh` | 上下文生成脚本 | 人工 |
| `specs/*.md` | 功能规格说明 | 人工 |
| `README_RALPH.md` | Ralph 工作流文档 | 人工 |

## 何时使用规划模式 vs 构建模式?

### 使用规划模式 (plan) 当:
- 📝 添加了新的 `specs/*.md` 文件
- 🎯 需要重新评估任务优先级
- 🤔 不确定下一步该做什么
- 🔄 项目方向有重大变化

### 使用构建模式 (build) 当:
- ✅ 有明确的任务列表
- 🔨 日常开发和实现功能
- 🐛 修复已知问题
- 🚀 持续迭代开发

## 典型开发会话

```bash
# 早上开始工作
cd /media/liuyajun/Work1/code/XGO/Aico_emotion
source .venv/bin/activate

# 查看昨天的进度
cat IMPLEMENTATION_PLAN.md

# 运行构建模式 (继续昨天的任务)
./loop.sh > /tmp/prompt.txt

# 在 VS Code 中打开 /tmp/prompt.txt
# 复制 → Copilot → 等待 AI 完成一个任务

# 检查结果
git log -1
pytest tests/ -v

# 继续下一个任务
./loop.sh > /tmp/prompt.txt
# 重复...

# 中午休息前，查看进度
cat IMPLEMENTATION_PLAN.md
git log --oneline -5
```

## 常见问题

### Q: 如何添加新功能?

**A:** 
1. 在 `specs/` 目录创建新的 `.md` 规格文件
2. 运行 `./loop.sh plan` 生成新计划
3. 运行 `./loop.sh build` 开始实现

### Q: AI 选择的任务不对怎么办?

**A:** 
1. 在 `IMPLEMENTATION_PLAN.md` 中调整任务优先级
2. 或者直接在 Copilot 中告诉 AI: "请实现 XXX 任务"

### Q: 测试失败了怎么办?

**A:** 
AI 会自动修复并重新测试。如果反复失败:
1. 检查 `AGENTS.md` 中的测试命令是否正确
2. 手动运行 `pytest tests/ -v` 查看详细错误
3. 告诉 AI 具体的错误信息

### Q: 如何暂停工作?

**A:** 
随时可以停止! `IMPLEMENTATION_PLAN.md` 保存了所有状态:
- 已完成的任务 ✅
- 正在进行的任务 🚧
- 待办任务 📋

下次直接运行 `./loop.sh` 继续即可。

### Q: 我可以手动修改代码吗?

**A:** 
当然可以! Ralph 工作流只是辅助工具:
1. 手动修改代码
2. 运行测试确保通过
3. 手动更新 `IMPLEMENTATION_PLAN.md` (或让 AI 同步)
4. Git 提交

## 最佳实践

### ✅ DO (推荐做法)
- 📝 保持 `specs/` 文件更新和清晰
- 🔄 频繁运行 `./loop.sh` (小步迭代)
- ✅ 每次任务后检查测试结果
- 📊 定期查看 `IMPLEMENTATION_PLAN.md`
- 💬 给 AI 清晰的反馈

### ❌ DON'T (避免做法)
- ❌ 不要一次堆太多任务
- ❌ 不要跳过测试
- ❌ 不要忘记更新计划文件
- ❌ 不要在不理解的情况下盲目运行
- ❌ 不要忽略 AI 发现的问题

## 进阶技巧

### 自定义 loop.sh 输出

编辑 `loop.sh` 来:
- 过滤特定文件
- 添加更多上下文
- 调整输出格式

### 使用 Git 分支

```bash
# 为大功能创建分支
git checkout -b feature/audio-perception

# 使用 Ralph 工作流开发
./loop.sh > /tmp/prompt.txt

# 完成后合并
git checkout main
git merge feature/audio-perception
```

### 性能监控

```bash
# 在循环中添加性能检查
./loop.sh > /tmp/prompt.txt
# AI 实现功能...
pytest tests/ -v
python tests/benchmark_blendshapes.py --mode comparison
```

## 当前项目状态

### ✅ 已完成
- 人脸情感识别 (Blendshapes)
- 手势识别 (MediaPipe)
- VAD 情感模型
- 性能优化 (2.4x 提升)

### 🚧 进行中
- Ralph Wiggum 工作流设置

### 📋 待办
- 音频感知模块
- 多模态融合
- 策略模块
- ROS2 集成

## 获取帮助

- 📖 详细文档: [README_RALPH.md](README_RALPH.md)
- 📋 项目计划: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- ⚙️ 操作指南: [AGENTS.md](AGENTS.md)
- 📚 功能规格: `specs/*.md`

## 下一步

1. 运行 `./loop.sh plan` 生成初始计划
2. 复制输出到 VS Code Copilot
3. 查看生成的任务列表
4. 运行 `./loop.sh build` 开始第一个任务

**开始你的 Ralph Wiggum 之旅吧！** 🚀
