---
name: midasheng-audio-denoise
description: |
  Voice enhancement and noise reduction service. Accepts a noisy audio file and returns a clean,
  denoised version. Use when user needs to remove background noise from audio files, clean up
  recordings, or preprocess audio for speech recognition.
requirements:
  - curl
---

# midasheng-audio-denoise

Voice enhancement and noise reduction service powered by advanced backend algorithms.

## 1. Trigger

Use this skill when the user wants to:
- Remove background noise from an audio file
- Clean up a noisy recording
- Enhance voice clarity
- Preprocess audio for speech recognition

## 2. API Details

**Endpoint:** `POST https://llmplus.ai.xiaomi.com/dasheng/audio/denoise` (multipart/form-data)

**Parameters:**
- `file`: The audio file to denoise

**Response:** Binary audio stream (WAV format)

## 3. Usage

### Basic denoising
```bash
curl -X POST "https://llmplus.ai.xiaomi.com/dasheng/audio/denoise" \
  -F "file=@noisy_recording.mp3" \
  -o clean_recording.wav
```

### Script usage
```bash
python3 scripts/denoise.py noisy_audio.mp3 -o clean_audio.wav
python3 scripts/denoise.py --queue   # Check queue status
```

## 4. Queue Status（排队情况）

### 查询命令
```bash
python3 scripts/denoise.py --queue
# 或直接调 API：
curl -X POST "https://llmplus.ai.xiaomi.com/metrics?path=/dasheng/audio/denoise"
```


### 返回字段
- `active`: 当前活跃请求数
- `avg_latency_ms`: 平均处理耗时（毫秒）
- 预估等待时长 = active × avg_latency_ms

### 何时调用
1. **IM 即将超时但 denoise 服务还未返回结果时**：查排队情况告知用户，请用户稍后来问。
2. **用户稍后询问任务进度但服务仍未返回时**：查最新排队情况返回给用户。

### 状态分级
- 🟢 active=0 或预估等待 <5s → 服务空闲
- 🟡 预估等待 5-30s → 轻微排队
- 🔴 预估等待 >30s → 排队较长，建议稍后重试

## 5. Supported Audio Formats

Input: mp3, wav, flac, ogg, m4a. Output: WAV.

## 6. Troubleshooting

- **Empty output**: Input file may be too short
- **API request failed**: Verify network connectivity
- **Poor results**: Works best on speech with background noise
