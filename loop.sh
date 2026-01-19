#!/bin/bash
# AICO Emotion System - Ralph Wiggum Workflow Loop Script
# 用于生成 AI 代理工作所需的完整上下文

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认模式是 build
MODE="${1:-build}"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AICO 情感系统 - Ralph Wiggum Workflow Generator          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查必要文件
check_file() {
    if [ ! -f "$1" ]; then
        echo -e "${RED}错误: 未找到文件 $1${NC}"
        exit 1
    fi
}

check_file "AGENTS.md"
check_file "IMPLEMENTATION_PLAN.md"

if [ "$MODE" = "plan" ]; then
    check_file "PROMPT_plan.md"
    PROMPT_FILE="PROMPT_plan.md"
    echo -e "${YELLOW}模式: 规划模式 (Planning Mode)${NC}"
elif [ "$MODE" = "build" ]; then
    check_file "PROMPT_build.md"
    PROMPT_FILE="PROMPT_build.md"
    echo -e "${GREEN}模式: 构建模式 (Build Mode)${NC}"
else
    echo -e "${RED}错误: 无效的模式 '$MODE'。使用 'plan' 或 'build'${NC}"
    echo "用法: ./loop.sh [plan|build]"
    exit 1
fi

echo ""
echo -e "${BLUE}正在生成上下文...${NC}"
echo ""

# 生成分隔符
print_separator() {
    echo "════════════════════════════════════════════════════════════"
}

# 生成文件内容块
print_file() {
    local file=$1
    local title=$2
    
    print_separator
    echo "FILE: $file"
    if [ -n "$title" ]; then
        echo "TITLE: $title"
    fi
    print_separator
    cat "$file"
    echo ""
    echo ""
}

# 输出组装好的提示
{
    print_file "$PROMPT_FILE" "主提示词"
    print_file "AGENTS.md" "操作指南"
    print_file "IMPLEMENTATION_PLAN.md" "实现计划"
    
    # 如果存在 specs 目录，列出所有规格文件
    if [ -d "specs" ]; then
        echo "════════════════════════════════════════════════════════════"
        echo "SPECS 目录内容:"
        echo "════════════════════════════════════════════════════════════"
        
        if [ "$(ls -A specs/*.md 2>/dev/null)" ]; then
            for spec_file in specs/*.md; do
                print_file "$spec_file"
            done
        else
            echo "（specs 目录为空）"
            echo ""
        fi
    fi
    
    # 显示项目结构摘要
    echo "════════════════════════════════════════════════════════════"
    echo "项目结构摘要:"
    echo "════════════════════════════════════════════════════════════"
    tree -L 3 -I '__pycache__|*.pyc|.venv|.git|*.db|models' --charset ascii || {
        echo "注意: 未安装 tree 命令，使用 ls 替代"
        ls -R --ignore='__pycache__|*.pyc|.venv|.git|*.db'
    }
    echo ""
    
    # 显示最近的 git 提交
    if [ -d ".git" ]; then
        echo "════════════════════════════════════════════════════════════"
        echo "最近的 Git 提交 (最近 5 条):"
        echo "════════════════════════════════════════════════════════════"
        git log --oneline --graph --decorate -5 || echo "无法读取 git 历史"
        echo ""
    fi
    
    # 显示当前 git 状态
    if [ -d ".git" ]; then
        echo "════════════════════════════════════════════════════════════"
        echo "当前 Git 状态:"
        echo "════════════════════════════════════════════════════════════"
        git status --short || echo "无法读取 git 状态"
        echo ""
    fi
}

echo ""
echo -e "${GREEN}✓ 上下文生成完成！${NC}"
echo ""
echo -e "${YELLOW}使用方法:${NC}"
echo "1. 将上述输出复制到剪贴板"
echo "2. 粘贴到 VS Code Copilot 聊天窗口"
echo "3. 等待 AI 代理完成任务"

if [ "$MODE" = "plan" ]; then
    echo "4. 检查更新后的 IMPLEMENTATION_PLAN.md"
    echo "5. 如需修改，重复运行 ./loop.sh plan"
elif [ "$MODE" = "build" ]; then
    echo "4. AI 将实现功能、运行测试、并提交代码"
    echo "5. 检查结果，重复运行 ./loop.sh build 直到完成"
fi

echo ""
echo -e "${BLUE}提示: 使用 './loop.sh plan' 进入规划模式${NC}"
echo -e "${BLUE}      使用 './loop.sh build' 进入构建模式（默认）${NC}"
echo ""
