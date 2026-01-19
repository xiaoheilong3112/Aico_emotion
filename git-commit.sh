#!/bin/bash
# AICO 情感系统 - Git 快速提交脚本
# 使用中文提交消息，自动推送到 GitHub

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  AICO 情感系统 - Git 快速提交工具                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查是否有未提交的更改
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}没有需要提交的更改${NC}"
    exit 0
fi

# 显示状态
echo -e "${BLUE}当前状态：${NC}"
git status --short
echo ""

# 提交类型选择
echo -e "${YELLOW}请选择提交类型：${NC}"
echo "1) 功能 (新功能)"
echo "2) 修复 (Bug 修复)"
echo "3) 性能 (性能优化)"
echo "4) 重构 (代码重构)"
echo "5) 测试 (测试相关)"
echo "6) 文档 (文档更新)"
echo "7) 构建 (构建/工具/依赖)"
echo ""
read -p "选择 (1-7): " type_choice

case $type_choice in
    1) commit_type="功能" ;;
    2) commit_type="修复" ;;
    3) commit_type="性能" ;;
    4) commit_type="重构" ;;
    5) commit_type="测试" ;;
    6) commit_type="文档" ;;
    7) commit_type="构建" ;;
    *) echo -e "${RED}无效选择${NC}"; exit 1 ;;
esac

# 输入提交消息
echo ""
echo -e "${YELLOW}请输入提交描述（中文）：${NC}"
read -p "> " commit_message

if [ -z "$commit_message" ]; then
    echo -e "${RED}提交消息不能为空${NC}"
    exit 1
fi

# 完整的提交消息
full_message="${commit_type}: ${commit_message}"

# 确认
echo ""
echo -e "${BLUE}将要提交：${NC}"
echo -e "${GREEN}${full_message}${NC}"
echo ""
read -p "确认提交？(y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}已取消${NC}"
    exit 0
fi

# 添加所有更改
echo ""
echo -e "${BLUE}添加文件...${NC}"
git add .

# 提交
echo -e "${BLUE}提交...${NC}"
git commit -m "$full_message"

# 推送到 GitHub
echo ""
echo -e "${BLUE}推送到 GitHub...${NC}"
git push github master

echo ""
echo -e "${GREEN}✓ 成功提交并推送到 GitHub！${NC}"
echo ""
echo -e "${BLUE}查看提交：${NC}"
git log --oneline -1
echo ""

# 询问是否也推送到阿里云
echo -e "${YELLOW}是否也推送到阿里云 Codeup？(y/n):${NC}"
read -p "> " push_codeup

if [ "$push_codeup" == "y" ] || [ "$push_codeup" == "Y" ]; then
    echo -e "${BLUE}推送到阿里云...${NC}"
    git push origin master
    echo -e "${GREEN}✓ 已推送到阿里云 Codeup${NC}"
fi

echo ""
echo -e "${GREEN}全部完成！${NC}"
