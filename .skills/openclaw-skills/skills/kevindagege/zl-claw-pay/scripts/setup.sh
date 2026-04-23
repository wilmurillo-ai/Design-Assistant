#!/bin/bash
# -*- coding: utf-8 -*-
# ZLPay Skill 安装脚本 (Linux/Mac)
# 
# 功能：
# 1. 检查 Python 版本（3.6+）
# 2. 创建虚拟环境
# 3. 安装依赖（Python 3.6 自动使用 requirements-py36.txt）
# 4. 验证安装
#
# 说明：
# - Python 3.6 使用 requirements-py36.txt（兼容版本）
# - Python 3.7+ 使用 requirements.txt（最新版本）

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}ZLPay Skill 安装程序${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 检查 Python 版本
echo -e "${YELLOW}[1/4] 检查 Python 版本...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ 错误: 未找到 Python 3${NC}"
    echo "请安装 Python 3.6 或更高版本"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ 找到 Python $PYTHON_VERSION${NC}"

# 检查版本号是否 >= 3.6
PYTHON_MAJOR=$(echo $PYTHON_VERSION | awk -F. '{print $1}')
PYTHON_MINOR=$(echo $PYTHON_VERSION | awk -F. '{print $2}')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 6 ]); then
    echo -e "${RED}❌ 错误: Python 版本过低 (需要 3.6+)${NC}"
    exit 1
fi

echo ""

# 2. 创建虚拟环境
echo -e "${YELLOW}[2/4] 创建虚拟环境...${NC}"
VENV_PATH="$PROJECT_ROOT/venv"

if [ -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠ 虚拟环境已存在，跳过创建${NC}"
else
    python3 -m venv "$VENV_PATH"
    echo -e "${GREEN}✓ 虚拟环境创建成功${NC}"
fi

echo ""

# 3. 安装依赖（使用虚拟环境 Python）
echo -e "${YELLOW}[3/4] 安装依赖...${NC}"
VENV_PYTHON="$VENV_PATH/bin/python"
VENV_PIP="$VENV_PATH/bin/pip"

# 跨平台兼容的 Python 路径
if [ -f "$VENV_PATH/Scripts/python.exe" ]; then
    # Windows
    VENV_PYTHON="$VENV_PATH/Scripts/python.exe"
    VENV_PIP="$VENV_PATH/Scripts/pip.exe"
fi

# 升级 pip
$VENV_PIP install --upgrade pip setuptools wheel > /dev/null 2>&1

# 安装依赖 - 根据Python版本选择对应的requirements文件
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -eq 6 ]; then
    REQUIREMENTS_FILE="$PROJECT_ROOT/scripts/requirements-py36.txt"
    echo -e "${YELLOW}检测到 Python 3.6，使用兼容版本依赖${NC}"
else
    REQUIREMENTS_FILE="$PROJECT_ROOT/scripts/requirements.txt"
fi

if [ -f "$REQUIREMENTS_FILE" ]; then
    $VENV_PIP install -r "$REQUIREMENTS_FILE"
    echo -e "${GREEN}✓ 依赖安装成功${NC}"
else
    echo -e "${RED}❌ 错误: 找不到 $REQUIREMENTS_FILE${NC}"
    exit 1
fi

echo ""

# 4. 验证安装
echo -e "${YELLOW}[4/4] 验证安装...${NC}"
# 使用虚拟环境的 Python 路径
VENV_PYTHON="$VENV_PATH/bin/python"
if [ -f "$VENV_PYTHON" ]; then
    "$VENV_PYTHON" -c "import requests; import dotenv; import qrcode; import cryptography; import sm_crypto"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 所有依赖验证成功${NC}"
    else
        echo -e "${RED}❌ 错误: 依赖验证失败${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ 错误: 找不到虚拟环境 Python: $VENV_PYTHON${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "请手动激活虚拟环境："
echo ""
echo "  Linux/Mac:  source venv/bin/activate"
echo "  Windows:    venv\\Scripts\\activate"
echo ""
echo "激活后，可以运行："
echo "  python scripts/skill_cli.py query_balance --sub_wallet_id=test_wallet"
echo ""
