# 测试输出文件夹说明

本文件夹包含AICO情感系统视觉感知模块的测试输出结果。

## 📁 文件夹结构

```
test_outputs/
├── visualizations/      # 可视化标注图片
│   └── [emotion]_[detected]_[filename]_[timestamp].jpg
└── reports/            # 测试报告文本
    └── test_report_[timestamp].txt
```

## 🖼️ 可视化图片说明

### 文件命名格式
```
[预期情感]_[检测情感]_[原始文件名]_[时间戳].jpg
```

例如：`sad_sad_image0010114_20260114_165356.jpg`
- 预期情感：sad
- 检测情感：sad（正确✅）
- 原始文件：image0010114.jpg
- 时间戳：2026-01-14 16:53:56

### 可视化内容

每张图片包含：

**左侧原图区域**：
- ✅ 人脸检测框（颜色根据情感类型）
- ✅ 主导情感标签（带置信度）
- ✅ 颜色编码：
  - 绿色 = happy（愉快）
  - 蓝色 = sad（悲伤）
  - 红色 = angry（愤怒）
  - 灰色 = neutral（中性）
  - 黄色 = surprise（惊讶）
  - 紫色 = fear（恐惧）
  - 橙色 = disgust（厌恶）

**右侧信息面板**（400像素宽）：
1. **标题**: Emotion Analysis
2. **主导情感**: 检测到的主要情感（带颜色和置信度）
3. **VAD值**：
   - Valence（愉悦度）: -1到+1，绿色/红色显示
   - Arousal（激活度）: 0到1，黄色显示
   - Dominance（主导性）: -1到+1，紫色显示
4. **情感分布条形图**: 显示所有7种情感的概率分布
   - 按概率从高到低排序
   - 中文标签 + 百分比
   - 颜色编码
5. **元数据**：
   - 时间戳
   - 原始文件名

### 示例说明

成功识别的例子（sad_sad_image0010114.jpg）：
- 主导情感：悲伤（88%置信度）✅
- VAD：V=-0.70（负面），A=0.30（低激活），D=-0.30（被动）
- 情感分布：sad 88%, neutral 6%, angry 3%...
- 判断：正确 ✅

错误识别的例子（Anger_fear_image0016779.jpg）：
- 预期：anger
- 检测：fear（42%置信度）❌
- 说明：愤怒被误判为恐惧，两者都是负面高激活情感

## 📊 测试报告说明

### 文件命名格式
```
test_report_[YYYYMMDD_HHMMSS].txt
```

### 报告内容

1. **测试配置**
   - 每类样本数
   - 数据集路径
   - 输出目录

2. **详细结果**（每个情感类别）
   - 类别名称
   - 准确率统计
   - 样本详情：
     - ✅ 正确识别
     - ❌ 错误识别
     - 预期 vs 检测情感
     - 置信度

3. **总体统计**
   - 各类别准确率汇总
   - 总体准确率

### 报告示例

```
================================================================================
                    AffectNet 真实图像情感识别测试报告
                         测试时间: 2026-01-14 16:53:25
================================================================================

测试配置:
  - 每类样本数: 5
  - 数据集路径: /media/liuyajun/Work1/code/XGO/affectnet/archive (3)/Test
  - 输出目录: test_outputs

详细结果:
--------------------------------------------------------------------------------

类别: sad
  准确率: 1/5 = 20.0%
  样本详情:
    [✗] image0020777.jpg: 预期=sad, 检测=angry (置信度=0.60)
    [✗] image0002086.jpg: 预期=sad, 检测=neutral (置信度=0.72)
    ...
    [✓] image0020686.jpg: 预期=sad, 检测=sad (置信度=0.62)

总体准确率: 2/29 = 6.9%
```

## 🎯 使用建议

### 1. 查看可视化结果
```bash
# 在文件浏览器中打开
nautilus test_outputs/visualizations/

# 或使用图片查看器
eog test_outputs/visualizations/*.jpg
```

### 2. 分析测试报告
```bash
# 查看最新报告
cat test_outputs/reports/test_report_*.txt | tail -100

# 或使用文本编辑器
gedit test_outputs/reports/test_report_*.txt
```

### 3. 批量分析

按情感类别筛选：
```bash
# 查看所有sad类别的识别结果
ls test_outputs/visualizations/sad_*.jpg

# 查看所有识别正确的（文件名中预期和检测相同）
ls test_outputs/visualizations/ | grep -E "^([a-z]+)_\1_"
```

### 4. 清理旧测试
```bash
# 删除指定日期的测试结果
rm test_outputs/visualizations/*20260114*.jpg
rm test_outputs/reports/test_report_20260114*.txt

# 清空所有测试结果（慎用）
rm -rf test_outputs/visualizations/*
rm -rf test_outputs/reports/*
```

## 📈 性能分析

通过可视化和报告，您可以：

1. **识别模型弱点**：哪些情感最容易混淆
2. **评估置信度**：低置信度预测是否可靠
3. **VAD空间验证**：情感映射是否符合预期
4. **数据质量检查**：哪些图片人脸检测失败

## 🔄 持续改进

基于测试结果的改进方向：

1. **高混淆类别**：针对性收集训练数据
2. **低置信度场景**：优化预处理或阈值
3. **检测失败案例**：改用MTCNN或MediaPipe
4. **情感边界案例**：引入多模态信息辅助

---

**生成工具**: `test_real_images.py`  
**数据集**: AffectNet  
**更新日期**: 2026年1月14日
