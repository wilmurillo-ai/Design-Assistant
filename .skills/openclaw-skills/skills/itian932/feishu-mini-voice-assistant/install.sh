#!/bin/bash
# Voice Assistant 极简安装脚本
# 只做依赖检查，不配置 Hook（Hook 方案已废弃）

set -e

echo "========================================"
echo "  语音助手安装检查"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

WORKSPACE="$HOME/.openclaw/workspace"
SKILL_DIR="$WORKSPACE/skills/voice-assistant"
WHISPER_DIR="$WORKSPACE/whisper.cpp"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查函数
check_ffmpeg() {
    log_info "1. 检查 ffmpeg..."
    if command -v ffmpeg &>/dev/null; then
        FFMPEG_VER=$(ffmpeg -version | head -1)
        log_info "✅ ffmpeg 已安装: $FFMPEG_VER"
        return 0
    else
        log_error "❌ ffmpeg 未安装"
        echo "   安装命令: sudo apt update && sudo apt install -y ffmpeg"
        return 1
    fi
}

check_edge_tts() {
    log_info "2. 检查 edge-tts Python 包..."
    # 优先检查 skill 自带的 lib 目录
    if python3 -c "import sys; sys.path.insert(0, '$SKILL_DIR/lib'); import edge_tts" 2>/dev/null; then
        log_info "✅ edge-tts 已安装到 skill lib 目录"
        return 0
    fi
    # 其次检查全局环境
    if python3 -c "import edge_tts" 2>/dev/null; then
        log_info "✅ edge-tts 已安装到全局 Python 环境"
        return 0
    fi
    log_warn "⚠️  edge-tts 未安装"
    echo "   安装方法（任选其一）："
    echo "   a) 安装到 skill lib（推荐，自包含）:"
    echo "      pip install --target='$SKILL_DIR/lib' edge-tts"
    echo "   b) 安装到全局环境:"
    echo "      pip install edge-tts"
    return 1
}

check_whisper_binary() {
    log_info "3. 检查 whisper.cpp 编译二进制..."
    # 检查标准路径
    local BIN_CANDIDATES=(
        "$WHISPER_DIR/build/bin/whisper-cli"
        "$WHISPER_DIR/build/bin/main"
        "$WHISPER_DIR/main"
        "$WHISPER_DIR/build/main"
    )

    for bin in "${BIN_CANDIDATES[@]}"; do
        if [[ -f "$bin" ]]; then
            log_info "✅ 找到 whisper 二进制: $bin"
            return 0
        fi
    done

    log_warn "⚠️  whisper.cpp 二进制未找到"
    echo "   编译方法："
    echo "   1) 克隆仓库（如果尚未克隆）:"
    echo "      cd $WORKSPACE && git clone https://github.com/ggerganov/whisper.cpp"
    echo "   2) 编译:"
    echo "      cd $WHISPER_DIR && mkdir -p build && cd build"
    echo "      cmake .. && make -j\$(nproc)"
    echo "   3) 编译完成后，二进制将位于:"
    echo "      $WHISPER_DIR/build/bin/whisper-cli"
    return 1
}

check_whisper_model() {
    log_info "4. 检查 Whisper 模型文件..."
    local MODEL_DIR="$SKILL_DIR/models/whisper"
    local FOUND_MODELS=()

    # 检查常见模型文件
    local MODELS=(
        "ggml-large-v3-turbo.bin:大模型（3GB）- 最高精度"
        "ggml-large-v3.bin:大模型（3GB）- 高精度"
        "ggml-medium.bin:中模型（1.5GB）- 平衡"
        "ggml-small.bin:小模型（500MB）- 快速"
        "ggml-base.bin:基础模型（150MB）- 最小体积"
    )

    for entry in "${MODELS[@]}"; do
        IFS=':' read -r filename desc <<< "$entry"
        local model_path="$MODEL_DIR/$filename"
        if [[ -f "$model_path" ]]; then
            local size=$(du -h "$model_path" | cut -f1)
            log_info "✅ 找到模型: $filename ($size) - $desc"
            FOUND_MODELS+=("$filename")
        fi
    done

    if [[ ${#FOUND_MODELS[@]} -eq 0 ]]; then
        log_warn "⚠️  未找到任何 Whisper 模型"
        echo "   下载模型（选择一个）："
        echo "   a) 大模型（3GB，推荐）:"
        echo "      mkdir -p '$MODEL_DIR' && cd '$MODEL_DIR'"
        echo "      curl -L -o ggml-large-v3-turbo.bin \\"
        echo "        'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo.bin?download=true'"
        echo ""
        echo "   b) 中等模型（1.5GB）:"
        echo "      curl -L -o ggml-medium.bin \\"
        echo "        'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin?download=true'"
        echo ""
        echo "   c) 小模型（150MB）:"
        echo "      curl -L -o ggml-base.bin \\"
        echo "        'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin?download=true'"
        echo ""
        echo "   所有模型下载地址: https://huggingface.co/ggerganov/whisper.cpp"
        return 1
    fi

    log_info "📊 找到 ${#FOUND_MODELS[@]} 个模型，可使用 --model 参数指定"
    return 0
}

# 执行检查
FAIL_COUNT=0

check_ffmpeg || ((FAIL_COUNT++))
echo ""

check_edge_tts || ((FAIL_COUNT++))
echo ""

check_whisper_binary || ((FAIL_COUNT++))
echo ""

check_whisper_model || ((FAIL_COUNT++))
echo ""

# 总结
echo "========================================"
if [[ $FAIL_COUNT -eq 0 ]]; then
    echo "  ✅ 所有检查通过！"
    echo "========================================"
    echo ""
    echo "📝 使用示例："
    echo "  识别语音:"
    echo "    python3 $SKILL_DIR/asr.py input.ogg \\"
    echo "      --model $SKILL_DIR/models/whisper/ggml-medium.bin \\"
    echo "      --bin $WHISPER_DIR/build/bin/whisper-cli"
    echo ""
    echo "  合成语音:"
    echo "    python3 $SKILL_DIR/tts.py \\"
    echo "      --text '你好' \\"
    echo "      --output $WORKSPACE/tmp/reply.ogg \\"
    echo "      --voice xiaoxiao"
    echo ""
    echo "  在 Agent 中集成:"
    echo "    使用 message.send(filePath='...', message='...')"
    echo ""
    echo "  详细文档: $SKILL_DIR/SKILL.md"
    echo ""
    log_info "✅ 安装检查完成"
    exit 0
else
    echo "  ⚠️  有 $FAIL_COUNT 项检查未通过"
    echo "========================================"
    echo ""
    echo "💡 完成上述检查后，重新运行本脚本验证"
    echo ""
    log_warn "⚠️  依赖未完全就绪，但可以继续开发测试"
    exit 1
fi
