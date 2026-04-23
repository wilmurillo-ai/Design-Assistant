#!/bin/bash
# 金融分析师团队 - 环境安装脚本
# 自动检测环境，给客户选择权

set -e

echo "============================================================"
echo "📊 金融分析师团队 - 环境配置向导"
echo "============================================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测函数
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✅ Python $PYTHON_VERSION 已安装${NC}"
        return 0
    else
        echo -e "${RED}❌ Python 未安装${NC}"
        return 1
    fi
}

check_pip() {
    if command -v pip3 &> /dev/null || command -v pip &> /dev/null; then
        echo -e "${GREEN}✅ pip 已安装${NC}"
        return 0
    else
        echo -e "${RED}❌ pip 未安装${NC}"
        return 1
    fi
}

check_akshare() {
    if python3 -c "import akshare" 2>/dev/null; then
        AKSHARE_VERSION=$(python3 -c "import akshare; print(akshare.__version__)" 2>/dev/null || echo "未知")
        echo -e "${GREEN}✅ akshare $AKSHARE_VERSION 已安装${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ akshare 未安装${NC}"
        return 1
    fi
}

check_browserless() {
    BROWSERLESS_URL=${BROWSERLESS_URL:-""}
    if curl -s --connect-timeout 5 "$BROWSERLESS_URL/json/version" | grep -q "Browser"; then
        echo -e "${GREEN}✅ browserless 服务可用 ($BROWSERLESS_URL)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ browserless 服务不可用${NC}"
        return 1
    fi
}

# 环境检测
echo "📋 环境检测中..."
echo ""

PYTHON_OK=true
PIP_OK=true
AKSHARE_OK=true
BROWSERLESS_OK=true

check_python || PYTHON_OK=false
check_pip || PIP_OK=true
check_akshare || AKSHARE_OK=false
check_browserless || BROWSERLESS_OK=false

echo ""
echo "============================================================"
echo "📊 环境状态汇总"
echo "============================================================"

if $AKSHARE_OK && $BROWSERLESS_OK; then
    echo -e "运行模式: ${GREEN}完整模式${NC} (所有功能可用)"
elif $AKSHARE_OK; then
    echo -e "运行模式: ${YELLOW}标准模式${NC} (实时行情可用，PE/PB 功能受限)"
else
    echo -e "运行模式: ${YELLOW}纯 AI 模式${NC} (无实时数据，仅 AI 分析)"
fi

echo ""

# 给客户选择权
if ! $AKSHARE_OK || ! $BROWSERLESS_OK; then
    echo "============================================================"
    echo "🔧 环境优化建议"
    echo "============================================================"
    echo ""
    
    # akshare 安装选项
    if ! $AKSHARE_OK; then
        echo "1️⃣ akshare 数据获取库"
        echo "   功能: 获取股票实时行情、财务数据"
        echo "   大小: ~55MB (含依赖)"
        echo ""
        read -p "是否安装 akshare? (y/n) [默认: y]: " INSTALL_AKSHARE
        INSTALL_AKSHARE=${INSTALL_AKSHARE:-y}
        
        if [[ "$INSTALL_AKSHARE" =~ ^[Yy]$ ]]; then
            echo ""
            echo "正在安装 akshare..."
            pip3 install akshare --quiet
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ akshare 安装成功${NC}"
            else
                echo -e "${RED}❌ akshare 安装失败，请手动执行: pip3 install akshare${NC}"
            fi
        else
            echo "跳过 akshare 安装"
        fi
        echo ""
    fi
    
    # browserless 配置选项
    if ! $BROWSERLESS_OK; then
        echo "2️⃣ browserless 浏览器服务"
        echo "   功能: 获取 PE/PB 等财务数据"
        echo "   方式: Docker 容器 或 远程服务"
        echo ""
        echo "选项:"
        echo "  A) 使用本地 Docker (推荐)"
        echo "  B) 使用远程服务 (browserless.io)"
        echo "  C) 跳过配置"
        echo ""
        read -p "请选择 (A/B/C) [默认: C]: " BROWSERLESS_CHOICE
        BROWSERLESS_CHOICE=${BROWSERLESS_CHOICE:-C}
        
        case $BROWSERLESS_CHOICE in
            [Aa])
                echo ""
                echo "正在检查 Docker..."
                if command -v docker &> /dev/null; then
                    echo "Docker 已安装"
                    echo ""
                    read -p "是否启动 browserless 容器? (y/n) [默认: y]: " START_DOCKER
                    START_DOCKER=${START_DOCKER:-y}
                    
                    if [[ "$START_DOCKER" =~ ^[Yy]$ ]]; then
                        echo "正在启动 browserless 容器..."
                        docker run -d --name browserless -p 3000:3000 browserless/chrome:latest 2>/dev/null || \
                        docker start browserless 2>/dev/null
                        
                        if [ $? -eq 0 ]; then
                            echo -e "${GREEN}✅ browserless 容器已启动${NC}"
                            echo "访问地址: http://localhost:3000"
                        else
                            echo -e "${RED}❌ 容器启动失败，请手动执行:${NC}"
                            echo "  docker run -d --name browserless -p 3000:3000 browserless/chrome"
                        fi
                    fi
                else
                    echo -e "${YELLOW}⚠️ Docker 未安装${NC}"
                    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
                fi
                ;;
            [Bb])
                echo ""
                echo "使用远程 browserless 服务"
                echo "1. 注册 browserless.io 获取 API Key"
                echo "2. 设置环境变量:"
                echo "   export BROWSERLESS_URL=https://chrome.browserless.io"
                echo "   export BROWSERLESS_API_KEY=your_api_key"
                ;;
            [Cc]|*)
                echo "跳过 browserless 配置"
                ;;
        esac
    fi
fi

echo ""
echo "============================================================"
echo "✅ 环境配置完成"
echo "============================================================"
echo ""

# 最终状态检测
echo "最终环境状态:"
check_akshare && AKSHARE_OK=true || AKSHARE_OK=false
check_browserless && BROWSERLESS_OK=true || BROWSERLESS_OK=false

echo ""
if $AKSHARE_OK && $BROWSERLESS_OK; then
    echo -e "运行模式: ${GREEN}完整模式${NC} ✅"
    echo "所有功能可用！"
elif $AKSHARE_OK; then
    echo -e "运行模式: ${YELLOW}标准模式${NC}"
    echo "实时行情可用，PE/PB 功能需要配置 browserless"
else
    echo -e "运行模式: ${YELLOW}纯 AI 模式${NC}"
    echo "建议安装 akshare 获取实时数据"
fi

echo ""
echo "============================================================"
echo "🤓 金融分析师团队已就绪！"
echo "============================================================"