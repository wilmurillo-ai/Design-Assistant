#!/bin/bash
# Token审计监控技能安装脚本

set -e

echo "🚀 安装 Token审计监控技能..."
echo ""

# 创建安装目录
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# 创建数据目录
DATA_DIR="$HOME/.token-auditor"
mkdir -p "$DATA_DIR"

# 复制可执行文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/auditor.py" "$INSTALL_DIR/token-auditor"
chmod +x "$INSTALL_DIR/token-auditor"

echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  token-auditor monitor --project myapp --budget 1000"
echo "  token-auditor status"
echo "  token-auditor check --sensitivity high"
echo "  token-auditor report --period week"
echo "  token-auditor alert --budget 500 --thresholds 50,80,100"
echo ""
echo "数据存储: $DATA_DIR"
echo ""
echo "💡 访问完整平台: http://token-master.cn/shop/"
echo ""

# 检查PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "⚠️  请将 $INSTALL_DIR 添加到PATH:"
    echo "   echo 'export PATH=\"$INSTALL_DIR:\$PATH\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
fi
