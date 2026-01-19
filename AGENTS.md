# Aico Emotion System - Operations

该文件定义了项目的核心操作命令，供 AI 代理执行任务时参考。

## 构建与运行命令

### 环境激活
```bash
# 激活 Python 虚拟环境
source .venv/bin/activate
```

### 运行测试脚本
```bash
# 人脸情感识别测试 (Blendshapes)
python tests/test_human_face.py

# 手势识别测试
python tests/test_hand_gesture.py

# RPS数据集测试
python tests/test_rps_dataset.py

# Blendshapes性能基准测试
python tests/benchmark_blendshapes.py --mode comparison
```

### 运行示例程序
```bash
# 单人脸检测示例 (单张图像)
python examples/single_face_detection.py

# 视频流处理示例 (摄像头)
python examples/video_stream.py

# 多人脸检测示例
python examples/multi_face_detection.py
```

## 验证命令

### 测试
```bash
# 运行所有单元测试
pytest tests/ -v

# 运行特定测试模块
pytest tests/test_affect_state.py -v
pytest tests/test_perception_manager.py -v

# 运行覆盖率测试
pytest tests/ --cov=src --cov-report=html
pytest tests/ --cov=src --cov-report=term-missing
```

### 类型检查
```bash
# 如果使用 mypy
mypy src/ --check-untyped-defs
```

### 代码风格检查
```bash
# 如果使用 flake8
flake8 src/ tests/ --max-line-length=120

# 如果使用 black
black src/ tests/ --check
black src/ tests/  # 自动格式化
```

## 操作注意事项

### Python 环境
- **Python 版本**: 3.10.12
- **虚拟环境**: /media/liuyajun/Work1/code/XGO/Aico_emotion/.venv
- **主要依赖**: MediaPipe 0.10.31, OpenCV 4.8+, SQLite3, numpy, Pillow

### 依赖管理
```bash
# 安装依赖
pip install -r requirements.txt

# 查看已安装包
pip list

# 冻结当前环境
pip freeze > requirements.txt
```

### MediaPipe 模型文件

**重要**: AI 代理需要自行研究并下载所需模型！

模型存放目录: `models/`

当前已有模型:
- `face_landmarker.task` (人脸关键点检测)
- `gesture_recognizer.task` (手势识别)

**AI 代理工作流程**:
1. **研究阶段**: 使用 `fetch_webpage` 工具搜索最新模型版本和下载链接
2. **选择阶段**: 评估模型大小、性能、兼容性，选择最合适的版本
3. **下载阶段**: 使用 `run_in_terminal` 下载模型到 `models/` 目录
4. **验证阶段**: 测试模型是否可用

参考资源:
- MediaPipe Models: https://developers.google.com/mediapipe/solutions/vision/
- Hugging Face: https://huggingface.co/models
- Model Zoo: https://modelzoo.co/

### 数据库
- **位置**: `emotion_detection.db`
- **用途**: 存储检测历史记录
- **管理**: 使用 SQLite 命令行工具或 Python sqlite3 模块

### 测试数据集管理

**重要**: AI 代理需要自行研究并下载测试数据集！

数据集存放目录: `datasets/`

**AI 代理工作流程**:
1. **搜索阶段**: 使用 `fetch_webpage` 搜索相关数据集（Kaggle、Hugging Face、GitHub）
2. **评估阶段**: 评估数据集的规模、质量、许可证
3. **下载阶段**: 使用 `run_in_terminal` 下载（wget、curl、git clone、kaggle API）
4. **验证阶段**: 检查数据集完整性和格式

推荐数据集来源:
- **Kaggle**: https://www.kaggle.com/datasets
- **Hugging Face Datasets**: https://huggingface.co/datasets
- **Papers with Code**: https://paperswithcode.com/datasets
- **GitHub**: 搜索相关开源数据集

下载工具:
```bash
# wget 下载
wget -O datasets/dataset.zip https://example.com/dataset.zip

# Kaggle API
kaggle datasets download -d username/dataset-name -p datasets/

# Git clone
git clone https://github.com/user/dataset.git datasets/dataset-name

# 解压
unzip datasets/dataset.zip -d datasets/
```

### Git 工作流

**重要**: 所有提交信息必须使用中文！

**GitHub 仓库**: https://github.com/xiaoheilong3112/Aico_emotion

```bash
# 查看状态
git status

# 添加更改
git add .

# 提交 (使用中文语义化提交消息)
git commit -m "功能: 添加音频感知模块"
git commit -m "修复: 解决 blendshapes 计算错误"
git commit -m "性能: 优化人脸检测速度"
git commit -m "文档: 更新 API 文档"
git commit -m "测试: 添加集成测试用例"
git commit -m "重构: 提取公共感知基类"

# 推送到 GitHub
git push github main
```

**提交类型（中文）**:
- `功能`: 新功能 (feat)
- `修复`: Bug 修复 (fix)
- `性能`: 性能优化 (perf)
- `重构`: 代码重构 (refactor)
- `测试`: 测试相关 (test)
- `文档`: 文档更新 (docs)
- `构建`: 构建/工具/依赖更新 (chore)

**Git 远程仓库配置**:
```bash
# 添加 GitHub 远程仓库
git remote add github https://github.com/xiaoheilong3112/Aico_emotion.git

# 查看远程仓库
git remote -v

# 首次推送
git push -u github main
```

### 性能监控
```bash
# CPU/内存占用监控 (运行测试时)
python -m memory_profiler tests/test_human_face.py

# 帧率监控 (内置于测试脚本)
python tests/benchmark_blendshapes.py --mode video
```

## 代码库模式

### 项目结构
```
src/
├── perception/           # 感知模块 (输入层)
│   ├── human_face.py    # 人脸检测与情感识别
│   ├── hand_gesture.py  # 手势识别
│   └── perception_manager.py  # 多模态管理器
├── affect/              # 情感计算模块
│   ├── affect_state.py  # VAD情感状态
│   └── affect_space.py  # 情感空间映射
└── lib/                 # 共享工具
    └── db_manager.py    # 数据库管理
```

### 设计模式
1. **感知-情感分离**: 
   - `perception/` 负责原始数据处理（人脸、手势）
   - `affect/` 负责情感状态计算（VAD模型）

2. **MediaPipe 封装**:
   - 所有 MediaPipe 调用封装在 perception 模块
   - 统一的错误处理和资源管理

3. **VAD 模型**:
   - Valence (-1 到 +1): 情感效价
   - Arousal (0 到 1): 情感唤醒度
   - Dominance (-1 到 +1): 情感支配性

4. **Blendshapes 映射**:
   - 52 个 MediaPipe blendshapes → 7 种情感
   - 基于 FACS (Facial Action Coding System)
   - 权重配置位于 `human_face.py` 的 BLENDSHAPE_EMOTION_WEIGHTS

### 命名约定
- **模块**: 小写蛇形 `human_face.py`
- **类**: 大驼峰 `AffectState`, `HumanFacePerception`
- **函数**: 小写蛇形 `perceive()`, `calculate_vad()`
- **私有方法**: 前缀下划线 `_analyze_emotion_from_blendshapes()`
- **常量**: 大写蛇形 `BLENDSHAPE_EMOTION_WEIGHTS`

### 测试策略
- **单元测试**: `tests/test_*.py`
- **集成测试**: `tests/test_perception_manager.py`
- **基准测试**: `tests/benchmark_*.py`
- **数据集测试**: `tests/test_*_dataset.py`

### 关键性能指标
- **处理时间**: < 40ms/帧 (目标 60+ FPS)
- **CPU 占用**: < 20% (单核)
- **内存占用**: < 200MB (不含模型)
- **准确率**: > 80% (基于标准数据集)

### 已知优化
1. **FER 移除** (2025-01-19):
   - 移除 TensorFlow 依赖
   - 使用 Blendshapes 替代 CNN
   - 性能提升: 95ms → 39.6ms (2.4x)
   - CPU 降低: 80%

2. **MediaPipe 优化**:
   - max_num_faces=5 (平衡性能和功能)
   - running_mode=VIDEO (视频流模式)
   - min_detection_confidence=0.5

### 未来扩展点
- 音频感知模块 (`src/perception/audio.py`)
- 情感推理引擎 (`src/affect/affect_inference.py`)
- 策略模块 (`src/policy/`)
- ROS2 集成 (`src/ros2_bridge/`)
