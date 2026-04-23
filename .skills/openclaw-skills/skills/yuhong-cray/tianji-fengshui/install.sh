#!/bin/bash

# ⚠️ 重要：在运行此脚本前请仔细审查
# 本脚本将：
# 1. 检查Python依赖
# 2. 测试核心功能
# 3. 可能调用外部API（如果配置了API密钥）
#
# 审查要点：
# - 检查所有命令，特别是exec/subprocess调用
# - 确认无远程代码下载和执行
# - 确认文件权限修改合理
#
# 建议先在沙盒环境中测试

echo "🔍 开始安装玄机子技能..."
echo "⚠️  请确保已阅读SKILL.md中的隐私警告"
echo ""

# 天机·玄机子技能安装脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🧭 安装天机·玄机子技能..."

# 检查Python依赖
echo "📦 检查Python依赖..."
python3 -c "import PIL" 2>/dev/null || {
    echo "⚠️  PIL (Pillow) 未安装，尝试安装..."
    pip install --quiet pillow 2>/dev/null || {
        echo "❌ 无法安装Pillow，请手动安装: pip install pillow"
        exit 1
    }
    echo "✅ Pillow 安装成功"
}

# 检查图片分析技能（可选依赖）
VIDEO_SKILL_NAME="video-image-file-analysis"
if command -v skillhub >/dev/null 2>&1; then
    if skillhub list | grep -q "$VIDEO_SKILL_NAME"; then
        echo "✅ 图片分析技能已安装"
    else
        echo "ℹ️  图片分析技能未安装，建议安装 $VIDEO_SKILL_NAME 技能"
        echo "   运行: skillhub install $VIDEO_SKILL_NAME"
    fi
else
    echo "ℹ️  skillhub 命令不可用，跳过技能依赖检查"
fi

# 检查OpenClaw配置
echo "🔧 检查OpenClaw配置..."
if command -v openclaw >/dev/null 2>&1; then
    # 检查豆包模型配置
    if openclaw config get models.providers.volcengine 2>/dev/null | grep -q "doubao-seed-2-0-pro-260215"; then
        echo "✅ 豆包视觉模型已配置"
    else
        echo "⚠️  豆包视觉模型未配置，需要配置豆包API密钥"
    fi
    
    # 检查DeepSeek模型配置
    if openclaw config get models.providers.deepseek 2>/dev/null | grep -q "deepseek"; then
        echo "✅ DeepSeek模型已配置"
    else
        echo "⚠️  DeepSeek模型未配置，需要配置DeepSeek API密钥"
    fi
else
    echo "ℹ️  openclaw 命令不可用，跳过配置检查"
    echo "   请确保已配置 volcengine 和 deepseek 提供商"
fi

# 设置执行权限
chmod +x "$SCRIPT_DIR/tianji_core.py"

# 创建测试
echo "🧪 运行简单测试..."
if python3 "$SCRIPT_DIR/tianji_core.py" "测试" >/dev/null 2>&1; then
    echo "✅ 天机·玄机子技能安装成功！"
    echo ""
    echo "📋 技能信息:"
    echo "   名称: 天机·玄机子"
    echo "   版本: 1.8.0"
    echo "   作者: 玄机子"
    echo "   功能: 风水命理分析 + 智能模型路由 + Subagent集成"
    echo ""
    echo "🚀 使用示例:"
    echo "   1. 图像分析: python3 tianji_core.py \"分析 /tmp/掌纹.jpg\""
    echo "   2. 八字分析: python3 tianji_core.py \"八字分析 姓名:张三 性别:男 出生:1990-01-01\""
    echo "   3. 聊天对话: python3 tianji_core.py \"你好，玄机子\""
    echo ""
    echo "🧭 玄机子已就位，随时为您提供风水智慧服务！"
else
    echo "❌ 测试失败，请检查Python环境"
    exit 1
fi