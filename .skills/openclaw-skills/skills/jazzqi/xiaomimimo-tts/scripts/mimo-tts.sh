#!/bin/bash
# MiMo TTS - 使用小米米萌 API 生成语音

TEXT="$1"
API_KEY="${MIMO_API_KEY}"
VOICE="${MIMO_VOICE:-zh-CN-XiaoxiaoNeural}"
OUTPUT="${2:-/tmp/mimo-tts-$(date +%s).ogg}"

if [ -z "$TEXT" ]; then
    echo "用法: mimo-tts.sh \"文本\" [输出文件]"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo "错误: 请设置 MIMO_API_KEY 环境变量"
    exit 1
fi

# 调用 API
RESPONSE=$(curl -s -X POST "https://api.xiaomimimo.com/v1/chat/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"mimo-v2-tts\",
        \"messages\": [
            {\"role\": \"user\", \"content\": \"请朗读：$TEXT\"},
            {\"role\": \"assistant\", \"content\": \"$TEXT\"}
        ],
        \"voice\": \"$VOICE\"
    }")

# 使用 Python 提取音频数据（替代 jq）
AUDIO_DATA=$(echo "$RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
try:
    print(data['choices'][0]['message']['audio']['data'])
except (KeyError, IndexError, TypeError):
    print('null')
")

if [ -z "$AUDIO_DATA" ] || [ "$AUDIO_DATA" = "null" ]; then
    echo "错误: API 调用失败"
    echo "$RESPONSE"
    exit 1
fi

# 解码并保存
echo "$AUDIO_DATA" | base64 -d > "$OUTPUT.wav"

# 转换为 OGG
ffmpeg -y -i "$OUTPUT.wav" -acodec libopus -b:a 128k "$OUTPUT" 2>/dev/null
rm -f "$OUTPUT.wav"

echo "$OUTPUT"
