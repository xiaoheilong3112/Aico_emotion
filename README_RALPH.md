# AICO 情感系统 - Ralph Wiggum 工作流

这是基于 [how-to-ralph-wiggum](https://github.com/ghuntley/how-to-ralph-wiggum) 的 AI 代理工作流，适配 AICO 情感系统开发。

## 项目概述

AICO 情感系统是一个基于 VAD 模型的双轮足机器人情感计算系统，采用 MediaPipe + Blendshapes 进行实时情感识别。

## 文件结构

```
XGO/Aico_emotion/
├── AGENTS.md              # 操作指南（构建/测试命令）
├── IMPLEMENTATION_PLAN.md # 实现计划（由 AI 维护）
├── PROMPT_plan.md         # 规划模式提示词
├── PROMPT_build.md        # 构建模式提示词
├── loop.sh                # 循环执行脚本
├── specs/                 # 规格说明文件夹
│   ├── human_face.md     # 人脸情感识别规格
│   ├── hand_gesture.md   # 手势识别规格
│   └── affect_state.md   # 情感状态模型规格
├── src/
│   ├── perception/       # 感知模块
│   ├── affect/          # 情感模块
│   └── lib/             # 共享工具
├── tests/               # 测试脚本
└── docs/                # 文档
```

## 三阶段工作流

### 阶段 1: 定义需求 (Copilot 对话)

在 VS Code Copilot 聊天中讨论功能需求，识别 JTBD (Jobs to Be Done)，将每个 JTBD 分解为关注点主题，为每个主题编写 `specs/FILENAME.md`。

**已有需求**:
- 人脸情感识别 (基于 Blendshapes)
- 手势识别 (MediaPipe Gesture Recognizer)
- VAD 情感空间映射
- 实时视频流处理

### 阶段 2: 规划模式

1. 运行辅助脚本:
```bash
./loop.sh plan
```

2. 复制输出到 VS Code Copilot
3. Copilot 分析 specs 和现有代码，生成/更新 IMPLEMENTATION_PLAN.md
4. 检查生成的计划，必要时重复

### 阶段 3: 构建模式

1. 运行辅助脚本:
```bash
./loop.sh build
```

2. 复制输出到 VS Code Copilot
3. Copilot 实现功能、运行测试、提交代码
4. 检查结果，重复循环直到完成

## 工作流程图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 编写规格说明 (specs/*.md)                                 │
│    - 人脸识别、手势识别、情感状态等                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 配置项目命令 (AGENTS.md)                                  │
│    - pytest, python scripts, benchmark                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 生成实现计划 (规划模式)                                    │
│    ./loop.sh plan → 复制到 Copilot                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 实现功能 (构建模式) - 循环执行                            │
│    ./loop.sh → 复制到 Copilot → git push → 重复              │
└─────────────────────────────────────────────────────────────┘
```

## 核心优势

- **迭代执行**: 通过多次迭代逐步完成任务
- **上下文隔离**: 每次迭代关注一个任务
- **状态持久化**: 通过 IMPLEMENTATION_PLAN.md 保持状态
- **反压机制**: 通过 pytest/类型检查提供质量保障
- **性能追踪**: 基准测试确保优化目标达成

## 快速开始

```bash
# 1. 进入项目目录
cd /media/liuyajun/Work1/code/XGO/Aico_emotion

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 查看当前计划
cat IMPLEMENTATION_PLAN.md

# 4. 运行规划模式（首次或需要重新规划时）
./loop.sh plan

# 5. 运行构建模式（日常开发）
./loop.sh build
```

## 项目目标

我们想要实现一个高性能、实时的情感计算系统，用于双轮足机器人交互：

1. **实时性能**: 60+ FPS 视频流处理
2. **准确性**: 基于 FACS 标准的情感识别
3. **多模态**: 人脸表情 + 手势 + 语音（未来）
4. **轻量化**: 适合嵌入式设备部署
5. **可扩展**: 易于添加新的感知模块

## 参考资料

- [How to Ralph Wiggum](https://github.com/ghuntley/how-to-ralph-wiggum)
- [MediaPipe Documentation](https://ai.google.dev/edge/mediapipe)
- [Russell's Circumplex Model](https://en.wikipedia.org/wiki/Emotion_classification#Circumplex_model)
