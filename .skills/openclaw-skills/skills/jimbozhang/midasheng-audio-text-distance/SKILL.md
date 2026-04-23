---
name: midasheng-audio-text-distance
description: |
  Multilingual audio-text retrieval and classification using GLAP (General Language Audio Pretraining).
  Use when user needs to search/match audio files against text descriptions, classify audio content
  by text queries, or perform cross-lingual audio understanding tasks.
  Supports sound events, speech, music across 50+ languages.
requirements:
  - curl
---

# midasheng-audio-text-distance

Contrastive Language-Audio Pretraining (GLAP) based service for multilingual audio-text retrieval and classification.

## 1. Trigger

Use this skill when the user wants to:
- Match audio files against text descriptions
- Classify audio content using natural language queries
- Perform zero-shot audio event detection
- Search audio by text in any language (supports 50+ languages)

## 2. API Details

**Endpoint:** `POST https://llmplus.ai.xiaomi.com/dasheng/audio/search` (multipart form-data)

**Parameters:**
- `files`: One or more audio files — can specify multiple times
- `text`: Comma-separated text descriptions/labels to match against

## 3. Usage

### Basic: Match audio against text labels
```bash
curl -X POST "https://llmplus.ai.xiaomi.com/dasheng/audio/search" \
  -F "files=@audio1.mp3" \
  -F "text=Noise,Speech,A person is speaking"
```

### Script usage
```bash
python3 scripts/audiosearch.py audio1.mp3 --text "Speech,Music,Noise"
python3 scripts/audiosearch.py --queue   # Check queue status
```

## 4. Queue Status（排队情况）

### 查询命令
```bash
python3 scripts/audiosearch.py --queue
# 或直接调 API：
curl -X POST "https://llmplus.ai.xiaomi.com/metrics?path=/dasheng/audio/search"
```

### 返回字段
- `active`: 当前活跃请求数
- `avg_latency_ms`: 平均处理耗时（毫秒）
- 预估等待时长 = active × avg_latency_ms

### 何时调用
1. **IM 即将超时但 search 服务还未返回结果时**：查排队情况告知用户，请用户稍后来问。
2. **用户稍后询问任务进度但服务仍未返回时**：查最新排队情况返回给用户。

### 状态分级
- 🟢 active=0 或预估等待 <5s → 服务空闲
- 🟡 预估等待 5-30s → 轻微排队
- 🔴 预估等待 >30s → 排队较长，建议稍后重试

## 5. Supported Audio Formats

Common formats: mp3, wav, flac, ogg, m4a.

## 6. Troubleshooting

- **Low scores across all labels**: Try broader descriptions
- **API request failed**: Verify network connectivity
- **Unsupported format**: Convert to mp3 or wav first
