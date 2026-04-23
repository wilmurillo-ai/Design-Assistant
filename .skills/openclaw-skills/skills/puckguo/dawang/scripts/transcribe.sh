#!/bin/bash
# YouTube to Whisper Transcription Script
# Usage: ./transcribe.sh "https://www.youtube.com/watch?v=VIDEO_ID" [output.txt]

set -e

VIDEO_URL="${1}"
OUTPUT_FILE="${2:-transcript.txt}"
MODEL_PATH="/Users/godspeed/.openclaw/workspaces/dawang/scripts/models/ggml-tiny.bin"
AUDIO_DIR="/Users/godspeed/.openclaw/workspaces/dawang/scripts/temp"
AUDIO_FILE="$AUDIO_DIR/youtube_audio.mp3"
WHISPER_CLI="/usr/local/Cellar/whisper-cpp/1.8.4/bin/whisper-cli"

# Create temp dir
mkdir -p "$AUDIO_DIR"

if [ -z "$VIDEO_URL" ]; then
    echo "Usage: $0 \"YouTube_URL\" [output.txt]"
    exit 1
fi

# Cleanup any existing files
rm -f "$AUDIO_DIR"/*.mp3 "$AUDIO_DIR"/*.webm "$AUDIO_DIR"/*.part 2>/dev/null

echo "📥 Step 1: Downloading audio from YouTube..."
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "$AUDIO_FILE.%(ext)s" "$VIDEO_URL" || \
yt-dlp -x --audio-format mp3 --audio-quality 0 --output "$AUDIO_FILE.%(ext)s" "$VIDEO_URL"

# Find the actual downloaded file
AUDIO_DOWNLOADED=$(ls "$AUDIO_DIR"/youtube_audio.* 2>/dev/null | head -1)
if [ -z "$AUDIO_DOWNLOADED" ]; then
    echo "Error: Audio download failed"
    exit 1
fi

# If it's not .mp3, convert
if [[ "$AUDIO_DOWNLOADED" != *.mp3 ]]; then
    echo "🎵 Converting to MP3..."
    ffmpeg -i "$AUDIO_DOWNLOADED" -vn -acodec libmp3lame -q:a 2 "$AUDIO_FILE" -y
    rm -f "$AUDIO_DOWNLOADED"
else
    mv "$AUDIO_DOWNLOADED" "$AUDIO_FILE"
fi

echo "🎤 Step 2: Transcribing with Whisper (tiny model)..."
"$WHISPER_CLI" \
    -m "$MODEL_PATH" \
    -f "$AUDIO_FILE" \
    -otxt \
    -of "${OUTPUT_FILE%.txt}" \
    --no-timestamps

echo "✅ Done! Transcript saved to: $OUTPUT_FILE"
echo ""
echo "📝 Preview (first 500 chars):"
head -c 500 "$OUTPUT_FILE"
echo "..."

# Cleanup
rm -f "$AUDIO_FILE"
echo ""
echo "🧹 Cleaned up temporary files"
