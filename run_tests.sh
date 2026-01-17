#!/bin/bash
# AICO 情感系统测试运行脚本

# 确保在项目根目录
cd "$(dirname "$0")"

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行: bash setup_project.sh"
    exit 1
fi

echo "🧪 AICO 情感系统测试套件"
echo "================================"

# 检查是否有测试文件
if [ ! -d "tests" ] || [ -z "$(ls -A tests/*.py 2>/dev/null)" ]; then
    echo "⚠️  测试目录为空，创建示例测试..."
    mkdir -p tests
    
    # 创建基础测试
    cat > tests/test_basic.py << 'EOF'
"""基础功能测试"""
def test_import():
    """测试基础导入"""
    import numpy
    import cv2
    assert True

def test_environment():
    """测试Python版本"""
    import sys
    assert sys.version_info >= (3, 10)
EOF
fi

echo ""
echo "运行测试..."

# 检查是否有源代码文件
if [ -n "$(find src -name '*.py' 2>/dev/null)" ]; then
    # 有源代码，运行带覆盖率的测试
    uv run pytest tests/ -v --cov=src --cov-report=term-missing
else
    # 没有源代码，仅运行测试
    echo "提示：src/ 目录为空，跳过覆盖率检查"
    uv run pytest tests/ -v
fi

echo ""
echo "✅ 测试完成"
