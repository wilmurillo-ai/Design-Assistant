# OpenClaw mlx-audio 插件

🎙️ **mlx-audio 的 OpenClaw 集成 - Apple Silicon 本地 TTS & STT**

无需 API 密钥，无需云服务。基于 [Blaizzy/mlx-audio](https://github.com/Blaizzy/mlx-audio)。

---

## 项目定位

本插件将 **mlx-audio** 集成到 OpenClaw，提供：

- 🗣️ **TTS 工具** - 文本转语音 (`mlx_tts` 工具 + `/mlx-tts` 命令)
- 🎧 **STT 工具** - 语音转文本 (`mlx_stt` 工具 + `/mlx-stt` 命令)
- 📚 **Skills 文档** - 教会 OpenClaw Agent 如何使用这些工具

**不是重新实现** - 这是封装官方 mlx-audio 库的集成层。

---

## 架构

```
OpenClaw Agent
     │
     │ (通过 skills/mlx-tts/SKILL.md 学习)
     ▼
工具调用：mlx_tts
     │
     ▼
插件 (src/index.ts)
     │
     ▼
HTTP API → Python 服务器 (python-runtime/)
     │
     ▼
mlx-audio 库 (Blaizzy/mlx-audio)
     │
     ▼
生成音频
```

---

## 前置要求

### 1. 安装 mlx-audio (必需)

```bash
# 使用 uv (推荐)
uv tool install mlx-audio --prerelease=allow

# 或使用 pip
pip install mlx-audio
```

### 2. 验证安装

```bash
# 测试 TTS
mlx_audio.tts.generate --model mlx-community/Kokoro-82M-bf16 --text "你好" --lang_code z

# 测试 STT
mlx_audio.stt.transcribe --model mlx-community/whisper-large-v3-turbo-asr-fp16 --audio test.wav
```

---

## 安装

### 构建插件

```bash
cd ~/.openclaw/workspace/projects/openclaw-mlx-audio
bun install
bun run build
```

### 在 OpenClaw 中启用

在 `openclaw.json` 中添加：

```json
{
  "plugins": {
    "entries": {
      "openclaw-mlx-audio": {
        "enabled": true,
        "config": {
          "tts": {
            "enabled": true,
            "model": "mlx-community/Kokoro-82M-bf16",
            "port": 19280,
            "langCode": "z"
          },
          "stt": {
            "enabled": true,
            "model": "mlx-community/whisper-large-v3-turbo-asr-fp16",
            "port": 19290,
            "language": "zh"
          }
        }
      }
    }
  }
}
```

### 重启 OpenClaw

```bash
openclaw gateway restart
```

---

## 使用方法

### 工具调用 (Agent)

Agent 会通过 Skills 文档自动学习使用这些工具。

**TTS 示例:**
```json
{
  "tool": "mlx_tts",
  "parameters": {
    "action": "generate",
    "text": "你好，OpenClaw!",
    "outputPath": "/tmp/speech.mp3"
  }
}
```

**STT 示例:**
```json
{
  "tool": "mlx_stt",
  "parameters": {
    "action": "transcribe",
    "audioPath": "/tmp/recording.m4a",
    "language": "zh"
  }
}
```

### 命令调用 (用户)

```bash
# TTS 命令
/mlx-tts status
/mlx-tts test "你好世界"
/mlx-tts models
/mlx-tts reload

# STT 命令
/mlx-stt status
/mlx-stt transcribe /tmp/audio.mp3
/mlx-stt models
/mlx-stt reload
```

---

## 支持的模型

### TTS 模型

| 模型 | 语言 | 描述 |
|------|------|------|
| **Kokoro-82M** ⭐ | 8 种 | 快速，54 种预设声音 |
| **Qwen3-TTS-0.6B** | ZH, EN, JA, KO | 中文质量优秀 |
| **Qwen3-TTS-1.7B** | ZH, EN, JA, KO | 文字描述生成声音 |
| **CSM-1B** | EN | 对话式，声音克隆 |
| **Chatterbox** | 16 种 | 最广泛语言覆盖 |

### STT 模型

| 模型 | 语言 | 描述 |
|------|------|------|
| **Whisper-large-v3-turbo** ⭐ | 99+ | 快速准确 |
| **Whisper-large-v3** | 99+ | 最高精度 |
| **Qwen3-ASR** | ZH, EN, JA, KO | 阿里多语言 |
| **VibeVoice-ASR-9B** | 多语言 | 说话人分离，长音频 |

完整列表见 [MODELS.md](./MODELS.md)。

---

## 项目结构

```
openclaw-mlx-audio/
├── src/                        # TypeScript 插件代码
│   ├── index.ts                # 主入口
│   ├── tts-server.ts           # TTS 服务器管理
│   └── stt-server.ts           # STT 服务器管理
│
├── python-runtime/             # Python 封装层 (mlx-audio)
│   ├── tts_server.py           # TTS HTTP 服务器
│   └── stt_server.py           # STT HTTP 服务器
│
├── skills/                     # OpenClaw Skills
│   ├── mlx-tts/SKILL.md        # TTS 使用指南
│   └── mlx-stt/SKILL.md        # STT 使用指南
│
├── README.md                   # 本文件
├── README.zh-CN.md             # 中文文档
├── PROJECT_STRUCTURE.md        # 架构详情
├── MODELS.md                   # 支持的模型列表
└── QUICK_REFERENCE.md          # 模型选择快速指南
```

---

## 开发

```bash
# 安装依赖
bun install

# 构建
bun run build

# 监听模式
bun run dev

# 测试
bun test
```

---

## 配置说明

### TTS 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `true` | 启用 TTS |
| `model` | string | `Kokoro-82M` | 使用的模型 |
| `port` | number | `19280` | 服务器端口 |
| `langCode` | string | `"z"` | 语言代码 (Kokoro) |
| `pythonEnvMode` | string | `"managed"` | `managed` 或 `external` |

### STT 配置

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | `true` | 启用 STT |
| `model` | string | `whisper-large-v3-turbo` | 使用的模型 |
| `port` | number | `19290` | 服务器端口 |
| `language` | string | `"zh"` | 语言代码 |
| `pythonEnvMode` | string | `"managed"` | `managed` 或 `external` |

---

## 故障排除

### 服务器无法启动

```bash
# 检查 mlx-audio 是否安装
which mlx_audio

# 直接测试 mlx-audio
mlx_audio.tts.generate --text "测试" --lang_code z
```

### 模型下载问题

模型缓存在 `~/.cache/huggingface/hub/`。清空缓存重试：

```bash
rm -rf ~/.cache/huggingface/hub/models--mlx-community--*
```

### 检查状态

```bash
/mlx-tts status
/mlx-stt status
```

---

## 许可证

MIT

## 致谢

- **[mlx-audio](https://github.com/Blaizzy/mlx-audio)** by Blaizzy - 核心 TTS/STT 引擎
- **[OpenClaw](https://github.com/openclaw/openclaw)** - 插件框架

---

## 链接

- GitHub: https://github.com/openclaw/openclaw-mlx-audio
- mlx-audio: https://github.com/Blaizzy/mlx-audio
- 文档：[MODELS.md](./MODELS.md), [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
