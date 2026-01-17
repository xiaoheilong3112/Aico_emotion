#!/bin/bash
# AICO 情感系统项目初始化脚本

set -e

echo "🚀 AICO 情感系统项目初始化"
echo "================================"

PROJECT_ROOT=$(pwd)

# 1. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p src/{affect,perception,policy,expression,utils}
mkdir -p tests
mkdir -p config
mkdir -p models
mkdir -p logs
mkdir -p scripts

# 1.5. 检查并安装系统依赖
echo "🔍 检查系统依赖..."
MISSING_DEPS=()

# 检查 portaudio19-dev
if ! dpkg -l | grep -q portaudio19-dev; then
    MISSING_DEPS+=("portaudio19-dev")
fi

# 检查 python3.10-dev
if ! dpkg -l | grep -q python3.10-dev; then
    MISSING_DEPS+=("python3.10-dev")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "⚠️  缺少系统依赖: ${MISSING_DEPS[*]}"
    echo "正在尝试安装..."
    
    if sudo apt-get update && sudo apt-get install -y "${MISSING_DEPS[@]}"; then
        echo "✅ 系统依赖已安装"
    else
        echo "❌ 自动安装失败，请手动运行："
        echo "sudo apt-get install -y portaudio19-dev python3.10-dev libopencv-dev ffmpeg"
        exit 1
    fi
else
    echo "✅ 系统依赖已满足"
fi

# 2. 创建 Python 虚拟环境
echo "🐍 创建 Python 虚拟环境..."
if [ ! -d ".venv" ]; then
    python3.10 -m venv .venv
    echo "✅ 虚拟环境已创建"
else
    echo "⚠️  虚拟环境已存在"
fi

# 3. 激活虚拟环境
echo "⚡ 激活虚拟环境..."
source .venv/bin/activate

# 4. 升级 pip 和安装 uv
echo "📦 升级包管理工具..."
pip install --upgrade pip
pip install uv

# 5. 创建 pyproject.toml（如果不存在）
if [ ! -f "pyproject.toml" ]; then
    echo "📝 创建 pyproject.toml..."
    cat > pyproject.toml << 'EOF'
[project]
name = "aico-emotion"
version = "0.1.0"
description = "AICO 双轮足机器人情感系统"
requires-python = ">=3.10"
authors = [
    {name = "AICO Team"}
]

dependencies = [
    "opencv-python>=4.8.0",
    "mediapipe>=0.10.0",
    "fer>=22.5.0",
    "SpeechRecognition>=3.10.0",
    "PyAudio>=0.2.13",
    "transformers>=4.35.0",
    "torch>=2.0.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "pyyaml>=6.0",
    "sqlalchemy>=2.0.0",
    "pyserial>=3.5",
    "psutil>=5.9.0",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]

[project.optional-dependencies]
dev = [
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
EOF
else
    echo "⚠️  pyproject.toml 已存在，跳过创建"
fi

# 6. 安装依赖
echo "📦 安装依赖（这可能需要几分钟）..."
echo "提示：PyAudio 安装可能较慢，请耐心等待..."

# 先安装不依赖编译的包
uv pip install numpy pyyaml pytest pytest-cov psutil pyserial sqlalchemy pandas

# 再安装需要编译的包
uv pip install opencv-python mediapipe

# 最后尝试安装 PyAudio（如果失败会给出提示）
if ! uv pip install PyAudio; then
    echo "⚠️  PyAudio 安装失败，跳过（语音功能将不可用）"
    echo "如需语音功能，请确保安装了 portaudio19-dev："
    echo "sudo apt-get install portaudio19-dev"
fi

# 安装 AI 相关库
uv pip install fer transformers torch --no-deps
uv pip install SpeechRecognition

echo ""
echo "✅ 项目初始化完成！"
echo ""
echo "📋 下一步操作："
echo "  1. 激活虚拟环境: source .venv/bin/activate"
echo "  2. 查看开发方案: cat AICO_情感系统开发方案_执行版.md"
echo "  3. 运行初始测试: bash run_tests.sh"
echo ""
echo "🎯 开始开发吧！"
