#!/bin/bash
# piper_speak.sh — Oblio TTS via Piper
# Usage: bash piper_speak.sh "Hello, I am Oblio."
# Or pipe: echo "Hello" | bash piper_speak.sh

VOICE="/home/oblio/piper-voices/en_US-lessac-medium.onnx"
OUTPUT_DIR="/home/oblio/.openclaw/workspace/logs"

if [ -n "$1" ]; then
    TEXT="$1"
else
    TEXT=$(cat)
fi

if [ -z "$TEXT" ]; then
    echo "Usage: piper_speak.sh \"text to speak\"" >&2
    exit 1
fi

# Generate WAV file (more compatible than raw audio)
OUTFILE="${OUTPUT_DIR}/tts_output_$(date +%s).wav"
echo "$TEXT" | piper --model "$VOICE" --output_file "$OUTFILE" 2>/dev/null

if [ -f "$OUTFILE" ]; then
    echo "Audio saved: $OUTFILE"
    # Try to play (aplay for ALSA, paplay for PulseAudio)
    if command -v aplay &>/dev/null; then
        aplay "$OUTFILE" 2>/dev/null &
    elif command -v paplay &>/dev/null; then
        paplay "$OUTFILE" 2>/dev/null &
    fi
else
    echo "TTS generation failed" >&2
    exit 1
fi
