#!/bin/bash
# Token消费优选技能安装脚本

set -e

echo "🚀 安装 Token消费优选技能..."
echo ""

# 创建安装目录
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# 复制可执行文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp "$SCRIPT_DIR/optimizer.py" "$INSTALL_DIR/token-consumer-optimizer"
cp "$SCRIPT_DIR/models.json" "$INSTALL_DIR/token-models.json"
chmod +x "$INSTALL_DIR/token-consumer-optimizer"

echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  token-consumer-optimizer recommend --task \"代码生成\""
echo "  token-consumer-optimizer compare --input 1000 --output 500"
echo "  token-consumer-optimizer estimate --model gpt-4o --input 10000"
echo "  token-consumer-optimizer budget --monthly 500"
echo ""
echo "💡 访问完整平台: http://token-master.cn/shop/"
echo ""

# 检查PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "⚠️  请将 $INSTALL_DIR 添加到PATH:"
    echo "   echo 'export PATH=\"$INSTALL_DIR:\$PATH\"' >> ~/.bashrc"
    echo "   source ~/.bashrc"
fi
