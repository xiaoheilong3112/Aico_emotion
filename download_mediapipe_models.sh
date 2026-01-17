#!/bin/bash
# 下载MediaPipe官方人脸检测模型

MODEL_DIR="$(dirname "$0")/models"
cd "$MODEL_DIR" || exit 1

echo "下载MediaPipe官方人脸检测模型..."

# 下载blaze_face_short_range.tflite (官方推荐的轻量级模型)
if [ ! -f "blaze_face_short_range.tflite" ]; then
    echo "正在下载 blaze_face_short_range.tflite..."
    wget -q --show-progress \
        "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/latest/blaze_face_short_range.tflite" \
        -O blaze_face_short_range.tflite
    
    if [ $? -eq 0 ]; then
        echo "✓ 下载成功: blaze_face_short_range.tflite"
    else
        echo "✗ 下载失败"
    fi
else
    echo "✓ 模型已存在: blaze_face_short_range.tflite"
fi

echo ""
echo "可用的人脸检测模型:"
ls -lh *.tflite 2>/dev/null | grep -i "face\|blaze" || echo "  未找到tflite模型"

echo ""
echo "使用方法:"
echo "  VisionPerceptor(use_mediapipe=True)  # 将自动使用下载的模型"
