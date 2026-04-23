# 模型选择快速指南

## 🚀 快速推荐 (Quick Picks)

| 用途 | 首选模型 | 备选模型 | 内存需求 |
|------|----------|----------|----------|
| **中文 TTS** | `Qwen3-TTS-0.6B` | `Kokoro-82M` | 2.5GB / 0.5GB |
| **多语言 TTS** | `Kokoro-82M` | `Chatterbox` | 0.5GB / 16GB |
| **声音克隆** | `CSM-1B` | `Qwen3-TTS-0.6B` | 2GB / 2.5GB |
| **日常 STT** | `Whisper-large-v3-turbo` | `Qwen3-ASR-0.6B` | 2GB / 1GB |
| **高精度 STT** | `Whisper-large-v3` | `Qwen3-ASR-1.7B` | 6GB / 4GB |
| **长音频 + 说话人分离** | `VibeVoice-ASR-9B` | `Sortformer v2.1` | 18GB / 2GB |

---

## 📊 按场景选择

### TTS 场景

```
┌─────────────────────────────────────────────────────────┐
│ 场景                    │ 推荐模型              │ 内存  │
├─────────────────────────────────────────────────────────┤
│ 日常中文语音            │ Qwen3-TTS-0.6B        │ 2.5GB │
│ 快速多语言 (8 种)        │ Kokoro-82M ⭐         │ 0.5GB │
│ 声音克隆 (参考音频)      │ CSM-1B                │ 2GB   │
│ 声音设计 (文字描述)      │ Qwen3-TTS-1.7B        │ 16GB  │
│ 最广泛语言 (16 种)       │ Chatterbox            │ 16GB  │
│ 语音/音乐/事件生成       │ Ming-omni-16.8B       │ 32GB  │
│ 资源受限设备            │ Soprano-80M           │ 0.2GB │
│ 对话式语音              │ Dia-1.6B              │ 4GB   │
│ 高效双语 (中英)         │ Spark-TTS-0.5B        │ 1GB   │
│ MoE 轻量版              │ Ming-omni-0.5B        │ 1GB   │
└─────────────────────────────────────────────────────────┘
```

### STT 场景

```
┌─────────────────────────────────────────────────────────┐
│ 场景                    │ 推荐模型              │ 内存  │
├─────────────────────────────────────────────────────────┤
│ 日常转录 (99+ 语言)      │ Whisper-large-v3-turbo⭐│ 2GB   │
│ 最高精度转录            │ Whisper-large-v3       │ 6GB   │
│ 快速英文转录            │ Distil-Whisper-large-v3│ 1.5GB │
│ 中文优化 ASR            │ Qwen3-ASR-1.7B         │ 4GB   │
│ 轻量多语言 ASR          │ Qwen3-ASR-0.6B         │ 1GB   │
│ 词级时间戳对齐          │ Qwen3-ForcedAligner    │ 1GB   │
│ 长音频 (60min)+ 说话人   │ VibeVoice-ASR-9B       │ 18GB  │
│ 欧盟语言 (25 种)         │ Parakeet-TDT-0.6B-v3   │ 1.5GB │
│ 流式 STT                │ Voxtral-Realtime-4B    │ 8GB   │
│ 带翻译功能              │ Canary                 │ 2GB   │
│ 千语言支持              │ MMS                    │ 可变  │
│ 轻量英文 ASR            │ Moonshine              │ 0.5GB │
└─────────────────────────────────────────────────────────┘
```

---

## 💾 内存需求分类

### 轻量级 (<1GB) - 适合日常使用
- **TTS**: Kokoro-82M, Soprano-80M
- **STT**: Moonshine, Qwen3-ASR-0.6B, Qwen3-ForcedAligner

### 中量级 (1-5GB) - 平衡性能与资源
- **TTS**: Qwen3-TTS-0.6B, CSM-1B, Spark-TTS-0.5B, Ming-omni-0.5B, Dia-1.6B, OuteTTS-0.6B
- **STT**: Whisper-large-v3-turbo, Distil-Whisper, Qwen3-ASR-1.7B, Parakeet-TDT, Canary

### 重量级 (10GB+) - 追求最佳效果
- **TTS**: Qwen3-TTS-1.7B, Chatterbox, Ming-omni-16.8B
- **STT**: Whisper-large-v3, VibeVoice-ASR-9B, Voxtral-4B

---

## 🌍 语言支持矩阵

### TTS 语言覆盖

| 语言 | Kokoro | Qwen3 | CSM | Chatterbox | Ming-omni |
|------|--------|-------|-----|------------|-----------|
| 中文 (ZH) | ✅ | ✅ | ❌ | ✅ | ✅ |
| 英文 (EN) | ✅ | ✅ | ✅ | ✅ | ✅ |
| 日文 (JA) | ✅ | ✅ | ❌ | ✅ | ❌ |
| 韩文 (KO) | ❌ | ✅ | ❌ | ✅ | ❌ |
| 法文 (FR) | ✅ | ❌ | ❌ | ✅ | ❌ |
| 西班牙 (ES) | ✅ | ❌ | ❌ | ✅ | ❌ |
| 意大利 (IT) | ✅ | ❌ | ❌ | ✅ | ❌ |
| 葡萄牙 (PT) | ✅ | ❌ | ❌ | ✅ | ❌ |
| 印地语 (HI) | ✅ | ❌ | ❌ | ❌ | ❌ |
| 德语 (DE) | ❌ | ❌ | ❌ | ✅ | ❌ |
| 俄语 (RU) | ❌ | ❌ | ❌ | ✅ | ❌ |
| 阿拉伯 (AR) | ❌ | ❌ | ❌ | ✅ | ❌ |

### STT 语言覆盖

| 模型系列 | 支持语言数 | 中文 | 英文 | 欧盟语言 |
|----------|-----------|------|------|----------|
| Whisper | 99+ | ✅ | ✅ | ✅ |
| Qwen3-ASR | ~10 | ✅ | ✅ | ❌ |
| Parakeet-v3 | 25 | ❌ | ✅ | ✅ |
| Canary | 27 | ❌ | ✅ | ✅ |
| MMS | 1000+ | ✅ | ✅ | ✅ |

---

## 🔧 特殊功能支持

| 功能 | 支持模型 |
|------|----------|
| **声音克隆** (参考音频) | CSM-1B, Qwen3-TTS-0.6B, Ming-omni |
| **声音设计** (文字描述) | Qwen3-TTS-1.7B |
| **说话人分离** | VibeVoice-ASR-9B, Sortformer v1/v2.1 |
| **词级对齐** | Qwen3-ForcedAligner |
| **流式转录** | Voxtral-Realtime-4B, Sortformer v2.1 |
| **语音翻译** | Canary, Granite-Speech |
| **长音频 (60min+)** | VibeVoice-ASR-9B |
| **音乐/事件生成** | Ming-omni-16.8B |
| **降噪增强** | MossFormer2-SE, DeepFilterNet |

---

## 📝 模型命名规则

```
mlx-community/{模型名}-{参数量}-{精度}

示例:
├─ Kokoro-82M-bf16          → 82M 参数，BF16 精度
├─ Qwen3-TTS-12Hz-0.6B-Base-bf16
├─ whisper-large-v3-turbo-asr-fp16
├─ VibeVoice-ASR-bf16
└─ Ming-omni-tts-16.8B-A3B-bf16  → MoE (16.8B 总，3B 激活)

精度说明:
├─ bf16  → BFloat16 (推荐，M 系列优化)
├─ fp16  → Float16
├─ 8bit  → 8 位量化 (更小内存)
└─ 4bit  → 4 位量化 (最小内存)
```

---

## 🎯 配置示例

### 推荐配置 (平衡型)
```json
{
  "tts": {
    "model": "mlx-community/Kokoro-82M-bf16",
    "langCode": "z"
  },
  "stt": {
    "model": "mlx-community/whisper-large-v3-turbo-asr-fp16",
    "language": "zh"
  }
}
```

### 中文优化配置
```json
{
  "tts": {
    "model": "mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16"
  },
  "stt": {
    "model": "mlx-community/Qwen3-ASR-1.7B-8bit"
  }
}
```

### 高精度配置 (M2 Max+)
```json
{
  "tts": {
    "model": "mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16"
  },
  "stt": {
    "model": "mlx-community/whisper-large-v3"
  }
}
```

---

## 🔗 相关链接

- **HuggingFace mlx-community**: https://huggingface.co/mlx-community
- **mlx-audio GitHub**: https://github.com/Blaizzy/mlx-audio
- **模型搜索**: https://huggingface.co/models?search=mlx-community
