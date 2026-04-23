---
name: feishu-mini-voice-assistant
description: "飞书语音助手 - Whisper.cpp + Edge-TTS，极简无Hook，直接调用"
---

# Feishu Mini Voice Assistant

为 OpenClaw 提供的飞书语音交互完整解决方案，支持语音识别（ASR）和语音合成（TTS）。

## ✨ 特性

- **语音识别**：Whisper.cpp，支持 5 种模型（150MB ~ 3GB）
- **语音合成**：Edge-TTS，8 种女声音色可选
- **极简架构**：无 Hook，无轮询，两个脚本直接调用
- **原生集成**：使用 `message.send(filePath=...)` 发送本地 OGG 文件
- **自包含**：不依赖系统 Python 环境（可选 `lib/` 目录）
- **完整文档**：SKILL.md + install.sh 检查脚本

## 📦 文件结构

```
voice-assistant/
├── asr.py          # 语音识别 CLI
├── tts.py          # 语音合成 CLI
├── converter.py    # 格式转换工具
├── install.sh      # 依赖检查脚本
└── SKILL.md        # 完整文档（本文件）
```

## 🔧 依赖要求

| 依赖 | 说明 | 安装方法 |
|------|------|----------|
| ffmpeg ≥ 4.0 | 音频格式转换 | `sudo apt install -y ffmpeg` |
| Python 3.8+ | 运行脚本 | 系统自带或 `sudo apt install python3` |
| whisper.cpp | Whisper 推理引擎 | 编译见下文 |
| Whisper 模型 | 识别模型文件 | 下载见下文 |
| edge-tts | 微软 TTS 引擎 | `pip install edge-tts` |

### 编译 whisper.cpp

```bash
cd ~/.openclaw/workspace
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
mkdir -p build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)
```

编译完成后，二进制文件位于：
- `~/openclaw/workspace/whisper.cpp/build/bin/whisper-cli`（推荐）
- 或 `~/openclaw/workspace/whisper.cpp/build/bin/main`

### 下载 Whisper 模型

模型文件应放置在 `skills/voice-assistant/models/whisper/` 目录。

#### 支持的模型

| 模型 | 大小 | 精度 | 推荐场景 |
|------|------|------|----------|
| `ggml-large-v3-turbo.bin` | 3GB | ⭐⭐⭐⭐⭐ | 专业级，嘈杂环境 |
| `ggml-large-v3.bin` | 3GB | ⭐⭐⭐⭐ | 通用场景，中文優化 |
| `ggml-medium.bin` | 1.5GB | ⭐⭐⭐ | 平衡性能与质量 |
| `ggml-small.bin` | 500MB | ⭐⭐ | 快速响应，资源有限 |
| `ggml-base.bin` | 150MB | ⭐ | 最小体积，简单语音 |

**下载地址：** https://huggingface.co/ggerganov/whisper.cpp

```bash
# 创建目录
mkdir -p ~/.openclaw/workspace/skills/voice-assistant/models/whisper
cd ~/.openclaw/workspace/skills/voice-assistant/models/whisper

# 下载中等模型（推荐）
curl -L -o ggml-medium.bin \
  "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin?download=true"
```

## 🚀 快速使用

### 命令行使用

```bash
# 1. 语音识别（ASR）
python3 asr.py input.ogg \
  --model models/whisper/ggml-medium.bin \
  --bin ~/.openclaw/workspace/whisper.cpp/build/bin/whisper-cli

# 2. 语音合成（TTS）
python3 tts.py \
  --text "你好，世界" \
  --output reply.ogg \
  --voice xiaoxiao
```

### 在 OpenClaw Agent 中集成

```python
import subprocess
import asyncio

async def handle_voice_message(ogg_path, chat_id):
    """处理语音消息的完整流程"""

    # 路径配置（可通过环境变量覆盖）
    SKILL_DIR = "~/.openclaw/workspace/skills/voice-assistant"
    WHISPER_BIN = os.getenv("WHISPER_BIN", "~/.openclaw/workspace/whisper.cpp/build/bin/whisper-cli")
    MODEL_PATH = os.getenv("WHISPER_MODEL", f"{SKILL_DIR}/models/whisper/ggml-medium.bin")
    OUTPUT_OGG = "/home/itian/.openclaw/workspace/tmp/reply.ogg"

    # 1. 识别语音
    text = subprocess.run([
        "python3", f"{SKILL_DIR}/asr.py", ogg_path,
        "--model", MODEL_PATH,
        "--bin", WHISPER_BIN
    ], capture_output=True, text=True).stdout.strip()

    # 2. 生成回复（你的业务逻辑）
    reply = generate_reply(text)  # 替换为实际逻辑

    # 3. 合成语音
    subprocess.run([
        "python3", f"{SKILL_DIR}/tts.py",
        "--text", reply,
        "--output", OUTPUT_OGG,
        "--voice", "xiaoxiao"
    ], capture_output=True, text=True)

    # 4. 发送回复
    await message.send(
        target=f"user:{chat_id}",
        filePath=OUTPUT_OGG,
        message=reply
    )
```

## 🎨 Edge-TTS 音色列表

| 音色ID | 语言 | 描述 |
|--------|------|------|
| `xiaoxiao` | 普通话 | 温暖女声（默认） |
| `xiaoxuan` | 普通话 | 温暖 |
| `xiaoyi` | 普通话 | 可爱 |
| `liaoning` | 辽宁话 | 幽默 |
| `shaanxi` | 陕西方言 | 明亮 |
| `hiugaai` | 粤语 | 友好 |
| `hiumaan` | 粤语 | - |
| `hsiaochen` | 台湾中文 | 友好 |

使用 `--voice` 参数指定音色，例如：`--voice liaoning`

## 📝 脚本参数说明

### asr.py

```
usage: asr.py [-h] [--model MODEL] [--bin WHISPER_BIN] [--verbose] audio_file

语音识别，将 OGG/WAV 转换为文本

positional arguments:
  audio_file            输入音频文件路径（OGG 或 WAV）

optional arguments:
  -h, --help            show this help message and exit
  --model MODEL         Whisper 模型文件路径（默认：models/whisper/ggml-medium.bin）
  --bin WHISPER_BIN     whisper-cli 二进制路径（默认：～/.openclaw/workspace/whisper.cpp/build/bin/whisper-cli）
  --verbose            输出详细日志
```

### tts.py

```
usage: tts.py [-h] --text TEXT --output OUTPUT [--voice VOICE]

语音合成，将文本转换为 OGG 音频

required arguments:
  --text TEXT       要合成的文本
  --output OUTPUT   输出 OGG 文件路径

optional arguments:
  -h, --help       show this help message and exit
  --voice VOICE    Edge-TTS 音色 ID（默认：xiaoxiao）
```

## 🔍 依赖检查

运行 `install.sh` 检查所有依赖是否就绪：

```bash
cd ~/.openclaw/workspace/skills/voice-assistant
./install.sh
```

脚本会检查：
1. ✅ ffmpeg
2. ✅ edge-tts（skill lib 目录或全局）
3. ✅ whisper.cpp 二进制
4. ✅ Whisper 模型文件

并给出详细的安装/下载指引。

## 📊 工作流程

```
用户发送 OGG 语音
    ↓
OpenClaw 接收并存到 inbound/ 目录
    ↓
Agent 调用 asr.py 识别（OGG → WAV → 文本）
    ↓
Agent 处理文本生成回复
    ↓
Agent 调用 tts.py 合成（文本 → OGG）
    ↓
Agent 使用 message.send(filePath=...) 发送回复
    ↓
用户收到语音消息
```

## ⚙️ 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `WHISPER_MODEL` | Whisper 模型路径 | `models/whisper/ggml-medium.bin` |
| `WHISPER_BIN` | whisper-cli 二进制路径 | `~/.openclaw/workspace/whisper.cpp/build/bin/whisper-cli` |
| `OPENCLAW_WORKSPACE` | OpenClaw 工作空间 | `~/.openclaw/workspace` |

这些环境变量可用于自定义路径，避免硬编码。

## 🚨 常见问题

### Q: `FileNotFoundError: Whisper model not found`
A: 下载模型到 `models/whisper/` 目录，或使用 `--model` 指定正确路径，或设置 `WHISPER_MODEL` 环境变量。

### Q: `ModuleNotFoundError: No module named 'edge_tts'`
A: 运行 `pip install edge-tts` 或 `pip install --target=lib edge-tts`。

### Q: 识别速度慢？
A: 使用较小的模型（如 `ggml-small.bin`），或确保 whisper-cli 已正确编译且使用 CPU 优化。

### Q: TTS 合成失败？
A: 检查网络连接（Edge-TTS 需要访问微软服务），或更换音色 ID。

## 📌 注意事项

- 本 skill **不包含**预编译的 whisper.cpp 二进制文件
- 本 skill **不包含** Whisper 模型文件（需单独下载）
- 所有输出 OGG 文件保存在 `workspace/tmp/`，可安全清理
- 无任何 Hook 或自动轮询配置，完全由 Agent 控制
- 建议在 Agent 中使用绝对路径以避免权限问题

## 🎯 版本历史

- **0.0.2** - 修复元数据，添加 requires 和 env 声明，完善环境变量支持
- **0.0.1** - 初始发布，极简架构，两个核心脚本

---

**最后更新：2026-03-29**
**维护者：添哥工作室**
