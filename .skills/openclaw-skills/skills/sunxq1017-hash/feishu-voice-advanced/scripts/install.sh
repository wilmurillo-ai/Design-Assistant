#!/bin/bash
# 安装脚本

echo "🎙️ 安装 Feishu Voice Advanced Skill..."

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 需要安装 Python 3"
    exit 1
fi

# 检查 ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ 错误: 需要安装 ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: apt-get install ffmpeg"
    exit 1
fi

# 创建临时目录
mkdir -p /tmp/feishu_voice

echo "✅ 依赖检查通过"
echo ""
echo "📦 Skill 文件位置:"
echo "  $(pwd)/feishu_voice.py"
echo ""
echo "🚀 使用方法:"
echo "  from feishu_voice import FeishuVoice, recognize, send"
echo ""
echo "  # 识别语音"
echo "  text = recognize('/path/to/audio.ogg')"
echo ""
echo "  # 发送语音（自动情绪）"
echo "  send('你好，桥总！')"
echo ""
echo "  # 发送语音（指定情绪）"
echo "  send('任务完成了！', emotion='happy')"
echo ""
echo "🎭 支持的情绪:"
echo "  - neutral: 普通"
echo "  - happy: 开心"
echo "  - sad: 悲伤"
echo "  - angry: 严肃"
echo "  - excited: 激动"
echo "  - auto: 自动检测"
echo ""
