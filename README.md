# AICO 情感系统

> 基于 VAD 模型的双轮足机器人情感计算系统

## 🎉 最新进展

**📅 2026年1月15日 v1.4** - 简化面板 + SQLite数据库！
- ✅ **简化可视化**: 280px精简面板，只显示核心信息（情感、置信度、边界框）
- ✅ **数据库集成**: SQLite存储详细信息（VAD值、情感分布、技术参数）
- ✅ **数据查询**: 提供query_database.py工具查看统计和详情
- ✅ **文件管理**: 所有测试文件统一放在tests/目录
- ✅ **性能优化**: 图片体积减少15-25%（17-20KB vs 22-24KB）
- 📊 数据库: test_outputs/emotion_detection.db
- 📝 查询工具: tests/query_database.py

## 快速开始

### 1. 初始化项目

```bash
# 克隆或进入项目目录
cd Aico_emotion

# 运行初始化脚本（自动创建环境和安装依赖）
bash setup_project.sh
```

### 2. 下载MediaPipe模型（可选但推荐）

```bash
# 下载Google官方人脸检测模型
bash download_mediapipe_models.sh
```

### 3. 激活开发环境

```bash
source .venv/bin/activate
```

### 4. 运行测试

```bash
# 运行所有测试
bash run_tests.sh

# 或手动运行特定测试
uv run pytest tests/test_state.py -v
```

### 5. 视觉检测演示

```bash
# 实时摄像头检测
uv run python demo_vision.py realtime

# 图片文件检测
uv run python demo_vision.py image

# 对比不同检测器效果
uv run python demo_vision.py compare

# 可视化测试（AffectNet数据集，保存到数据库）
uv run python tests/test_real_images.py vis sad 3
```

### 6. 查询检测数据库

```bash
# 查看最近的检测记录
uv run python tests/query_database.py recent 10

# 查看统计信息
uv run python tests/query_database.py stats

# 查看特定情感统计
uv run python tests/query_database.py stats fear

# 查看检测详情（含VAD值和情感分布）
uv run python tests/query_database.py detail 1

# 导出数据到JSON
uv run python tests/query_database.py export output.json 100
```

### 7. 启动主程序

```bash
# 仅视觉感知（需要摄像头）
uv run python main.py --vision

# 多模态感知
uv run python main.py --vision --audio

# 查看所有选项
uv run python main.py --help
```

## 项目结构

```
Aico_emotion/
├── config/              # 人格配置文件
├── src/                 # 源代码
│   ├── affect/          # 情感核心 ✅
│   │   ├── state.py     # VAD状态、Percept数据结构
│   │   └── personality.py  # 人格配置加载器
│   ├── perception/      # 感知模块 ✅
│   │   └── vision.py    # 视觉情感识别 (MediaPipe + FER)
│   ├── policy/          # 策略引擎 ⏭️
│   ├── expression/      # 表达层 ⏭️
│   └── utils/           # 工具模块 ✅
│       └── database.py  # 情感检测结果数据库
├── tests/               # 测试代码 ✅
│   ├── test_state.py         # 状态模块测试
│   ├── test_personality.py   # 人格配置测试
│   ├── test_vision.py        # 视觉感知测试
│   ├── test_real_images.py   # 真实图像测试（含数据库集成）
│   └── query_database.py     # 数据库查询工具
├── test_outputs/        # 测试输出目录
│   ├── visualizations/       # 可视化标注图片（280px简化面板）
│   ├── reports/              # 测试报告
│   └── emotion_detection.db  # SQLite数据库（详细信息）
├── models/              # AI模型文件
│   ├── blaze_face_short_range.tflite  # MediaPipe人脸检测
│   ├── haarcascade_frontalface_default.xml
│   └── EmotionDetectionModel.h5       # FER情感模型
├── demo_vision.py       # 视觉检测演示脚本
├── test_real_images.py  # AffectNet真实图像测试脚本
├── main.py              # 主程序入口 ⏭️
└── pyproject.toml       # 项目配置

✅ 已完成  🚧 进行中  ⏭️ 待开发
```

## 🎯 使用示例

### 视觉情感识别

```python
from src.perception.vision import VisionPerceptor, detect_emotion_from_image

# 方式1: 从摄像头实时检测
with VisionPerceptor(camera_id=0) as vp:
    percept = vp.perceive()
    if percept:
        print(f"情感: {percept.metadata['dominant_emotion']}")
        print(f"VAD: V={percept.valence_hint:.2f}, A={percept.arousal_hint:.2f}")

# 方式2: 从图片文件检测
percept = detect_emotion_from_image("face.jpg")
if percept:
    print(f"检测到 {percept.confidence:.0%} 置信度的 {percept.metadata['dominant_emotion']} 情感")

# 方式3: 批量处理
vp = VisionPerceptor(camera_id=0)
frames = [...]  # 图像列表
results = vp.batch_perceive(frames)
```

### 测试真实图像（AffectNet数据集）

```bash
# 测试所有情感类别（每类5张样本）
uv run python test_real_images.py

# 测试单个类别（如happy，10张样本）
uv run python test_real_images.py single happy 10

# 可视化结果（生成标注图片）
uv run python test_real_images.py vis fear
```

## 核心概念

### VAD 情感空间

- **Valence（愉悦度）**：[-1, 1] 不愉快 → 愉快
- **Arousal（激活度）**：[0, 1] 平静 → 激动
- **Dominance（主导度）**：[-1, 1] 被动 → 主动

### 模块架构

```
感知层 → 推断层 → 状态层 → 策略层 → 表达层
```

## 开发指南

详细开发方案请参考：[AICO_情感系统开发方案_执行版.md](AICO_情感系统开发方案_执行版.md)

### 添加新的感知模态

1. 在 `src/perception/` 创建新模块
2. 实现 `perceive()` 方法，返回 `Percept` 对象
3. 在 `main.py` 中注册

### 自定义人格

编辑 `config/personality.yaml`：

```yaml
personality:
  emotional_gain: 0.7      # 调整情绪敏感度
  recovery_rate: 0.01      # 调整恢复速度
  expressiveness: 0.8      # 调整表达强度
```

### 运行性能测试

```bash
uv run python scripts/benchmark.py
```

## 部署到 RK3588

```bash
# 构建 Docker 镜像
docker build -t aico-emotion:v1 .

# 运行（带设备访问）
docker run --rm -it \
  --device /dev/video0 \
  --device /dev/snd \
  -v $(pwd)/config:/app/config \
  aico-emotion:v1
```

## 依赖说明

- **OpenCV**：图像处理
- **MediaPipe**：人脸检测
- **FER**：表情识别
- **SpeechRecognition**：语音识别
- **Transformers**：NLP 情感分析

## 故障排除

### 摄像头无法访问

```bash
# 检查设备
ls /dev/video*

# 测试摄像头
uv run python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### 麦克风无法识别

```bash
# 检查音频设备
arecord -l

# 测试录音
arecord -d 3 test.wav
```

### 依赖安装失败

```bash
# 安装系统依赖（Ubuntu）
sudo apt-get install -y \
  python3.10-dev \
  portaudio19-dev \
  libopencv-dev \
  ffmpeg

# 重新安装 Python 依赖
uv pip install --force-reinstall -e .
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目主页：待定
- 问题反馈：GitHub Issues
