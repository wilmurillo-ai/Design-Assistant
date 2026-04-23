# mlx-audio 支持模型完整列表

基于 [Blaizzy/mlx-audio](https://github.com/Blaizzy/mlx-audio) 仓库整理。

---

## 🗣️ TTS (Text-to-Speech) 模型

### 轻量级模型 (<1GB)

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **Kokoro-82M** | `mlx-community/Kokoro-82M-bf16` | EN, JA, ZH, FR, ES, IT, PT, HI | ⭐ 推荐默认，54 种声音，快速 |
| **Soprano-1.1-80M** | `mlx-community/Soprano-1.1-80M-bf16` | EN | 超轻量高质量 |

### 中型模型 (1-5GB)

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **Qwen3-TTS-0.6B** | `mlx-community/Qwen3-TTS-12Hz-0.6B-Base-bf16` | ZH, EN, JA, KO | 中文优化，声音克隆 |
| **CSM-1B** | `mlx-community/csm-1b` | EN | 对话式，声音克隆 |
| **OuteTTS-0.6B** | `mlx-community/OuteTTS-1.0-0.6B-fp16` | EN | 高效 |
| **Spark-TTS-0.5B** | `mlx-community/Spark-TTS-0.5B-bf16` | EN, ZH | 高效 bilingual |
| **Ming-omni-0.5B** (Dense) | `mlx-community/Ming-omni-tts-0.5B-bf16` | EN, ZH | MoE 轻量版 |
| **Dia-1.6B** | `mlx-community/Dia-1.6B-fp16` | EN | 对话优化 |

### 大型模型 (10GB+)

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **Qwen3-TTS-1.7B** | `mlx-community/Qwen3-TTS-12Hz-1.7B-VoiceDesign-bf16` | ZH, EN, JA, KO | 声音设计 |
| **Chatterbox** | `mlx-community/chatterbox-fp16` | 16 种 | 最广泛语言覆盖 |
| **Ming-omni-16.8B** (BailingMM) | `mlx-community/Ming-omni-tts-16.8B-A3B-bf16` | EN, ZH | MoE 多模态，语音/音乐/事件 |

---

## 🎧 STT (Speech-to-Text) 模型

### Whisper 系列

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **whisper-large-v3-turbo** | `mlx-community/whisper-large-v3-turbo-asr-fp16` | 99+ | ⭐ 推荐默认，快速准确 |
| **whisper-large-v3** | `mlx-community/whisper-large-v3` | 99+ | 最高精度 |
| **distil-large-v3** | `distil-whisper/distil-large-v3` | EN | 蒸馏版，更快 |

### Qwen3 系列

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **Qwen3-ASR-0.6B** | `mlx-community/Qwen3-ASR-0.6B-8bit` | ZH, EN, JA, KO | 轻量多语言 |
| **Qwen3-ASR-1.7B** | `mlx-community/Qwen3-ASR-1.7B-8bit` | ZH, EN, JA, KO | 高精度 |
| **Qwen3-ForcedAligner-0.6B** | `mlx-community/Qwen3-ForcedAligner-0.6B-8bit` | ZH, EN, JA, KO | 词级时间戳对齐 |

### 其他大模型

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **VibeVoice-ASR-9B** | `mlx-community/VibeVoice-ASR-bf16` | 多语言 | 说话人分离，60min 长音频 |
| **Voxtral-Mini-3B** | `mlx-community/Voxtral-Mini-3B-2507-bf16` | 多语言 | Mistral 语音 |
| **Voxtral-Realtime-4B** | `mlx-community/Voxtral-Mini-4B-Realtime-2602-fp16` | 多语言 | 流式 STT |

### 专用模型

| 模型 | HuggingFace | 语言 | 特点 |
|------|-------------|------|------|
| **Parakeet-TDT-0.6B-v3** | `mlx-community/parakeet-tdt-0.6b-v3` | 25 EU | NVIDIA 高精度 |
| **Canary** | (see README) | 25 EU + RU | NVIDIA 带翻译 |
| **Moonshine** | (see README) | EN | 轻量 ASR |
| **MMS** | (see README) | 1000+ | Meta 千语言 |
| **Granite-Speech** | (see README) | EN, FR, DE, ES, PT, JA | IBM ASR+ 翻译 |

---

## 🎛️ VAD (Voice Activity Detection) 模型

| 模型 | HuggingFace | 特点 |
|------|-------------|------|
| **Sortformer v1** | `mlx-community/diar_sortformer_4spk-v1-fp32` | 最多 4 说话人 |
| **Sortformer v2.1** | `mlx-community/diar_streaming_sortformer_4spk-v2.1-fp32` | 流式，AOSC 压缩 |

---

## 🔊 STS (Speech-to-Speech) 模型

| 模型 | HuggingFace | 用途 |
|------|-------------|------|
| **SAM-Audio** | `mlx-community/sam-audio-large` | 文本引导声音分离 |
| **Liquid2.5-Audio** | `mlx-community/LFM2.5-Audio-1.5B-8bit` | STS/TTS/STT 多模态 |
| **MossFormer2 SE** | `starkdmi/MossFormer2_SE_48K_MLX` | 语音增强，降噪 |
| **DeepFilterNet 1/2/3** | `mlx-community/DeepFilterNet-mlx` | 语音增强，降噪 |

---

## 📝 模型选择建议

### TTS 场景

| 场景 | 推荐模型 |
|------|----------|
| 日常中文 TTS | **Qwen3-TTS-0.6B** |
| 多语言快速 TTS | **Kokoro-82M** |
| 声音克隆 | **CSM-1B** 或 **Qwen3-TTS-0.6B** |
| 声音设计 | **Qwen3-TTS-1.7B** |
| 最广泛语言 | **Chatterbox** |
| 资源受限 | **Soprano-80M** |

### STT 场景

| 场景 | 推荐模型 |
|------|----------|
| 日常转录 | **Whisper-large-v3-turbo** |
| 最高精度 | **Whisper-large-v3** |
| 中文优化 | **Qwen3-ASR-1.7B** |
| 长音频 + 说话人分离 | **VibeVoice-ASR-9B** |
| 欧盟语言 | **Parakeet-TDT-v3** |
| 需要翻译 | **Canary** |
| 资源受限 | **Moonshine** |

---

## 🔗 参考

- mlx-audio GitHub: https://github.com/Blaizzy/mlx-audio
- HuggingFace mlx-community: https://huggingface.co/mlx-community
