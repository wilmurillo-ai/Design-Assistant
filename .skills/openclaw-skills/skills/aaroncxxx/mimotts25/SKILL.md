---
name: mimotts25
description: 小米大模型 MiMo TTS 2.5 语音合成。支持多种预设音色（中文/英文/默认）、风格控制（情感、方言、角色扮演、语速）、音频标签精细控制。Use when the user asks to convert text to speech, generate audio, read text aloud with a specific style/emotion/dialect, or create voice files.
metadata: {"openclaw":{"requires":{"env":["MIMO_API_KEY"]},"primaryEnv":"MIMO_API_KEY","emoji":"🎙️"}}
---

# MiMo TTS 2.5 — 语音合成

小米大模型 MiMo TTS 2.5 版本，高质量中文/英文语音合成。

## 首次配置

⚠️ **TTS 的 API Key 独立于模型推理 Key。** 即使 `mimo-v2-pro` 能正常调用，TTS 仍需单独配置 Key。

1. 前往小米 MiMo 开放平台获取 TTS API Key：https://api.xiaomimimo.com
2. 通过 OpenClaw 配置：

```
openclaw config set skills.entries.mimotts25.apiKey "your-tts-api-key-here"
```

或直接设置环境变量 `MIMO_API_KEY`。
配置后需重启会话。

### 故障排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `401 Invalid API Key` | API Key 未传入或格式不对 | 确认已用 `config set` 配置 TTS 专用 Key，重启会话 |
| 工具调用被 abort | 上下文过长或系统繁忙 | 等几秒后重试 |

## 生成语音

使用 `scripts/tts.py` 合成语音：

```bash
python3 "{baseDir}/scripts/tts.py" "要合成的文本" -o output.wav
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-o` | `output.wav` | 输出文件路径 |
| `-v` | `mimo_default` | 音色：`mimo_default`、`default_zh`、`default_en` |
| `-s` | 无 | 风格标签，如 `开心`、`东北话`、`悄悄话`、`孙悟空` |
| `-f` | `wav` | 音频格式 |
| `--user-msg` | 无 | 可选的用户角色上下文，用于调整语气 |
| `--api-key` | 环境变量 `MIMO_API_KEY` | API Key 覆盖 |

### 使用示例

```bash
# 基础合成
python3 "{baseDir}/scripts/tts.py" "你好，今天天气真好" -o hello.wav

# 方言风格
python3 "{baseDir}/scripts/tts.py" "哎呀妈呀，这天儿也忒冷了吧" -s "东北话" -o dongbei.wav

# 英文音色
python3 "{baseDir}/scripts/tts.py" "Hello, how are you today?" -v default_en -o hello_en.wav

# 情感 + 语速
python3 "{baseDir}/scripts/tts.py" "明天就是周五了，真开心！" -s "开心 变快" -o happy.wav

# 唱歌
python3 "{baseDir}/scripts/tts.py" "一闪一闪亮晶晶" -s "唱歌" -o sing.wav
```

## 风格与音频标签

- 在文本开头使用 `<style>风格</style>` 设置整体风格
- 行内音频标签精细控制：`(紧张)`、`(小声)`、`(语速加快)`、`(深呼吸)`、`(苦笑)`、`(沉默片刻)`
- 多风格组合：`<style>开心 变快</style>文本内容`

## 音色列表

| 名称 | voice 参数 |
|------|-----------|
| MiMo-默认 | `mimo_default` |
| MiMo-中文女声 | `default_zh` |
| MiMo-英文女声 | `default_en` |

## 参考风格

| 风格 | 适用场景 |
|------|---------|
| `可爱` | 撒娇、软萌 |
| `开心` | 欢快、兴奋 |
| `东北话` | 方言、搞笑 |
| `悄悄话` | 神秘、低语 |
| `孙悟空` | 角色扮演 |
| `唱歌` | 儿歌、旋律 |
| `变快` / `变慢` | 语速控制 |
| 可自由组合 | `开心 变快`、`可爱 悄悄话` |

## 交付

生成音频后，用 `MEDIA:` 指令交付给用户：

```
MEDIA:output.wav
```
