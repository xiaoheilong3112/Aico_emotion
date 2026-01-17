#!/bin/bash
# 下载 MediaPipe Gesture Recognizer 模型

set -e

MODELS_DIR="models"
MODEL_URL="https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/latest/gesture_recognizer.task"
MODEL_FILE="gesture_recognizer.task"

echo "📦 下载 MediaPipe Gesture Recognizer 模型..."
echo "URL: $MODEL_URL"
echo ""

cd "$MODELS_DIR"

if [ -f "$MODEL_FILE" ]; then
    echo "✓ 模型文件已存在: $MODEL_FILE"
    ls -lh "$MODEL_FILE"
    exit 0
fi

echo "⬇️  正在下载..."
wget -O "$MODEL_FILE" "$MODEL_URL"

if [ -f "$MODEL_FILE" ]; then
    echo ""
    echo "✅ 下载成功！"
    ls -lh "$MODEL_FILE"
else
    echo ""
    echo "❌ 下载失败"
    exit 1
fi
