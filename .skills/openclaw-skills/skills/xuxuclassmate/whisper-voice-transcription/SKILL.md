---
name: whisper-voice-transcription
description: 语音消息转文字（STT）完整方案 — whisper.cpp（C++本地，首选）+ 云端API兜底。含安装、模型下载、使用流程和踩坑记录。
tags: [speech-to-text, stt, voice, transcription, whisper, audio, chinese]
---

# 语音转文字（Speech-to-Text）方案

## 🎯 主方案：whisper.cpp（本地离线转录）

> 纯 C++ 实现的 Whisper 语音识别，无需 Python 虚拟环境，支持离线使用。

### 前置依赖

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| `g++` / `gcc` / `make` | 编译 whisper.cpp | 系统包管理器 |
| `cmake` (≥3.14) | 构建系统 | [CMake 官网](https://cmake.org/download/) 或包管理器 |
| `ffmpeg` | 音频格式转换 | 系统包管理器 |
| `git` | 克隆源码 | 系统包管理器 |

### 安装步骤

#### Step 1: 克隆 whisper.cpp 源码

```bash
git clone --depth 1 https://github.com/ggerganov/whisper.cpp.git ~/whisper.cpp
cd ~/whisper.cpp
```

> 💡 如果 GitHub 访问慢，可使用 HuggingFace 镜像或 Git 代理。**请始终验证下载文件的完整性（SHA256 校验）。**

#### Step 2: 编译

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
make -C build -j$(nproc)
```

编译产物在 `~/whisper.cpp/build/bin/`：
- `whisper-cli` — 命令行转录工具 ✅ 主要用这个
- `whisper-server` — HTTP 服务端
- `whisper-quantize` — 模型量化工具

#### Step 3: 下载模型

从 [HuggingFace](https://huggingface.co/ggerganov/whisper.cpp/tree/main) 下载 ggml 格式模型到 `~/whisper.cpp/models/`：

| 模型 | 大小 | 准确度 | 速度 | 推荐场景 |
|------|------|--------|------|---------|
| **ggml-large-v3.bin** ⭐ | ~3GB | 最高 | 较慢 | **默认推荐，生产使用** |
| ggml-base.bin | ~142MB | 中等 | 最快 | 快速测试/调试 |
| ggml-small.bin | ~466MB | 较好 | 中等 | 平衡选择 |

> ⚠️ **安全提醒**：仅从官方 HuggingFace 仓库 (`ggerganov/whisper.cpp`) 下载模型文件。下载后建议校验 SHA256 哈希。

#### Step 4: 验证安装

```bash
~/whisper.cpp/build/bin/whisper-cli --help
# 应显示版本信息和用法
```

---

## 🔧 标准转录流程

### 两步走：预处理 + 转录

```bash
# Step 1: ffmpeg 预处理 — 任意音频格式 → 16kHz mono wav
ffmpeg -i <输入音频文件> -ar 16000 -ac 1 -f wav /tmp/voice.wav -y

# Step 2: whisper-cli 转录
~/whisper.cpp/build/bin/whisper-cli \
    -m ~/whisper.cpp/models/ggml-large-v3.bin \
    -f /tmp/voice.wav -l zh --no-timestamps
```

### 一键脚本封装

```bash
transcribe() {
    local input="$1"
    local wav="/tmp/whisper_$(date +%s).wav"
    ffmpeg -y -i "$input" -ar 16000 -ac 1 -f wav "$wav" 2>/dev/null || { echo "ffmpeg转换失败"; return 1; }
    ~/whisper.cpp/build/bin/whisper-cli \
        -m ~/whisper.cpp/models/ggml-large-v3.bin \
        -f "$wav" -l zh --no-timestamps 2>/dev/null
}
# 用法: transcribe your_audio.ogg
```

### 参数说明

| 参数 | 含义 | 推荐值 |
|------|------|--------|
| `-m` | 模型路径 | `ggml-large-v3.bin`（最准）/ `ggml-base.bin`（快速） |
| `-f` | 音频文件路径 | 必须是 wav 格式 |
| `-l` | 语言 | `zh`(中文), `en`(英文), `auto`(自动检测) |
| `--no-timestamps` | 不输出时间戳 | 推荐加上，输出更干净 |
| `-t` | 线程数 | 默认4，可根据 CPU 核心数调大加速 |

---

## 🔄 Hermes 内置转录失败时的回退流程

当 Hermes 内置语音转录报错时，可用此方案手动转录：

### Step 1: 定位语音文件

语音文件通常在 Hermes 的音频缓存目录中。查找最近的音频文件：

```bash
# 查找最近 5 分钟内修改的音频文件（路径因配置而异）
find ~ -type f -mmin -5 \( -name "*.ogg" -o -name "*.mp3" -o -name "*.wav" \) 2>/dev/null
```

> ⚠️ 请根据实际 Hermes 配置调整搜索路径。常见位置包括 `~/.hermes/cache/audio/` 或平台特定缓存目录。

### Step 2: 转录

```bash
# 将 <找到的音频文件路径> 替换为实际路径
ffmpeg -y -i <音频文件> -ar 16000 -ac 1 -f wav /tmp/voice.wav 2>/dev/null
~/whisper.cpp/build/bin/whisper-cli \
    -m ~/whisper.cpp/models/ggml-large-v3.bin \
    -f /tmp/voice.wav -l zh --no-timestamps 2>/dev/null
```

---

## ☁️ 备选方案：云端 API

当本地算力不足或需要更高准确度时，可使用云端 ASR 服务：

| 服务 | 模型 | 费用 | 特点 |
|------|------|------|------|
| [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text) | whisper-1 | 按量付费 | 准确度高，官方API |
| [Groq Whisper](https://console.groq.com/) | whisper-large-v3 | 免费额度 | 速度快，免费层可用 |
| [SiliconFlow SenseVoice](https://cloud.siliconflow.cn) | SenseVoiceSmall | 注册送额度 | 中文优化好 |
| [DeepSeek](https://platform.deepseek.com/) | - | 极低价格 | 性价比高 |

> 💡 使用云端 API 需要相应平台的 API Key，并确保网络可达。

---

## ⚠️ 注意事项与最佳实践

### 安全建议

1. **仅从官方源下载**：whisper.cpp 仅从 GitHub (`ggerganov/whisper.cpp`) 获取，模型仅从 HuggingFace 官方仓库获取
2. **校验下载完整性**：大文件下载后应验证 SHA256 哈希
3. **不要从未知镜像下载可执行文件**：非官方镜像可能篡改文件内容
4. **权限最小化**：whisper-cli 只需读权限访问模型文件和音频文件

### 性能优化

- 使用 `large-v3` 模型获得最佳中文准确度
- 增加 `-t` 线程数加速（不超过 CPU 核心数）
- 音频预处理固定为 16kHz mono 可获得最佳效果

### 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| 编译失败 | 缺少 cmake 或编译工具 | 安装 build-essential / cmake |
| 转录乱码/空白 | 音频格式不支持 | 先用 ffmpeg 转 wav |
| 速度太慢 | 模型太大/CPU太弱 | 换 base 模型或用云端 API |
| 中文准确度差 | 用了小模型 | 升级到 large-v3 模型 |

---

## 方案对比

| 维度 | whisper.cpp (本地) | 云端 API |
|------|-------------------|----------|
| 依赖 | gcc/cmake/ffmpeg | 网络 + API Key |
| 隐私 | ✅ 本地处理，数据不出机器 | ❌ 音频上传至第三方 |
| 费用 | 免费（自备算力） | 按 API 调用量计费 |
| 延迟 | 取决于本地算力 | 取决于网络 |
| 离线可用 | ✅ 是 | ❌ 否 |
| 中文准确度 | high (large-v3) | 通常最高 |
