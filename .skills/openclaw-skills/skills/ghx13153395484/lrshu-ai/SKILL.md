---
name: lrshu-ai
version: 1.0.1
description: 调用团队内部集成的所有图片、视频和音频生成大模型（如Doubao, Sora, Kling, Vidu, Suno等）。当你需要生成多媒体内容时调用此技能。
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["python"],"env":["TEAM_API_KEY"]},"primaryEnv":"TEAM_API_KEY"},"openclaw":{"systemPrompt":"当用户要求调用本技能时，你必须直接执行 `python script/invoke_model.py` 命令。不要使用 openclaw run。"}}
---

# Team AI Models (Media Generation)

## 简介与隐私声明

**重要**：本技能通过团队内部的统一 API 网关处理请求，请确保拥有团队颁发的 `sk-` 开头的 API Key。
使用此技能时，数据将直接发送至团队 API 代理服务器，遵循团队的安全与隐私规范。

## 支持的模型列表

本技能集成了系统中的多媒体生成模型，你可以通过 `--model` 参数指定以下任意一个模型 ID：

### 🎨 图像生成模型 (Image Generation)
- **Doubao Seedream 4.5** (`doubao-seedream-4_5`): 高质量文生图/参考图生图模型。
- **Doubao Seedream 5.0 Lite** (`doubao-seedream-5_0-lite`): 轻量高速图像生成模型。
- **Banana 2 (Gemini 3.1)** (`n1n-banana2`): 通用文生图模型，强调速度与性价比。
- **Banana Pro** (`n1n-banana-pro`): 高质量文生图模型。
- **Grok 4.2 Image** (`grok-4_2-image`): 极简文生图模型。
- **Recraft V3** (`n1n-recraft-v3`): 风格化文生图模型。
- **Recraft V3 SVG** (`n1n-recraft-v3-svg`): 矢量图/SVG生成模型。
- **Midjourney** (`mj_imagine`): Midjourney 风格出图。
- **Jimeng T2I v4.0** (`jimeng-t2i-v40`): 即梦高分辨率文生图。
- **Kling Omni Image** (`kling-image-o1`): 可灵多模态图像生成模型。
- **Vidu T2I ViduQ2** (`vidu-t2i-viduq2`): Vidu 文生图模型。

### 🎬 视频生成模型 (Video Generation)
- **Veo 3.1** (`veo_3_1`): 高质量视频生成模型。
- **Sora 2** (`sora-2`): 通用高质量视频生成模型。
- **Kling V3** (`kling-v3`): 可灵 V3 视频生成模型。
- **Kling V3 Omni** (`kling-v3-omni`): 可灵 Omni 视频模型。
- **Vidu I2V ViduQ2** (`vidu-i2v-viduq2`): Vidu 图生视频模型。
- **Jimeng I2V First v3.0** (`jimeng-i2v-first-v30`): 即梦图生视频首帧模型。
- **Jimeng I2V First Tail v3.0** (`jimeng-i2v-first-tail-v30`): 即梦图生视频首尾帧模型。
- **Jimeng Dream Actor M1** (`jimeng-dream-actor-m1-gen-video-cv`): 即梦梦幻演员视频生成。
- **Jimeng OmniHuman 1.5** (`jimeng-omnihuman-1_5`): 即梦数字人视频生成。
- **Doubao Seedance 1.5 Pro** (`doubao-seedance-1_5-pro`): 豆包舞蹈视频生成。
- **Bailian Wan2 6 R2V** (`bailian-wan2_6-r2v`): 阿里百炼 Wan2 视频生成。
- **Bailian Wan2 6 R2V Flash** (`bailian-wan2_6-r2v-flash`): 阿里百炼 Wan2 视频生成（极速版）。

### 🎵 音频与音乐生成模型 (Audio/Music Generation)
- **Gemini 2.5 Pro TTS** (`n1n-gemini-2.5-pro-preview-tts`): 文本转语音模型。
- **Doubao TTS** (`doubao-tts`): 豆包文本转语音模型。
- **Keling TTS** (`keling-tts`): 可灵文本转语音模型。
- **Kling Audio Clone** (`kling-audio-clone`): 可灵音色克隆模型。
- **Vidu Audio Clone** (`vidu-audio-clone`): Vidu 音色克隆模型。
- **Keling SFX** (`keling-audio-sfx`): 音效生成模型。
- **Suno Music** (`suno_music`): 音乐生成模型。

*(注：如果需要特定的参数格式如参考图、时长等，请根据平台接口规范使用。)*

## 使用方法（给 AI Agent 的指令）

**CRITICAL INSTRUCTION FOR AGENT**: 
当用户要求调用 `lrshu-ai` 技能时，你**绝对不能**使用 `openclaw run`。本技能不提供可执行的二进制文件或 Node 包，而是提供了一个 Python 脚本。
你**必须**直接通过系统自带的 `python` 命令来运行 `script/invoke_model.py`。

### 前置检查

1. 检查当前是否有 `TEAM_API_KEY` 环境变量（通常以 `sk-` 开头）。平台网关默认配置为 `https://dlazy.com/api/ai/tool`，无需额外设置。
2. 确保已安装所需的依赖：

```bash
pip install requests
```

### 调用模型生成/分析

1. 根据用户意图，确定要调用的模型 ID，并编写高质量的 Prompt。
2. 调用本技能目录下的脚本：

- **纯文本/通用生成请求**：

  ```bash
  python script/invoke_model.py --model 'n1n-gemini-2.5-pro-preview-tts' --prompt '生成一段介绍产品的语音'
  ```

- **带参考图/视频请求（多模态）**：

  ```bash
  python script/invoke_model.py --model 'doubao-seedream-4_5' --prompt '根据图片生成赛博朋克风格的海报' --image 'absolute/path/to/image.jpg'
  ```

- **处理远程多模态链接**：

  ```bash
  python script/invoke_model.py --model 'sora-2' --prompt '让图片中的人物动起来' --image 'https://example.com/ref.jpg' --remote
  ```

等待命令执行结束，并获取返回结果作为该任务的输出。

### 错误处理与特殊参数说明

- **图生视频模型强制要求参考图**：当你调用图生视频（I2V）模型（如 `vidu-i2v-viduq2`, `jimeng-i2v-first-v30`）时，**必须**使用 `--image` 参数提供参考图，否则服务端会拒绝请求。
- **首尾帧模型**：如 `jimeng-i2v-first-tail-v30`，默认需要提供首帧和尾帧，当前脚本的 `--image` 仅映射为首帧，若因缺失尾帧报错，请根据需要调整或使用基础的 `jimeng-i2v-first-v30` 模型。
- **参数自适应**：脚本会自动将 `--image` 映射为服务端需要的 `images` 或 `firstFrame` 字段，你只需统一使用 `--image` 即可。
- 如果遇到远程资源（图片/视频）下载或访问超时，可尝试先将资源下载至工作区，再使用本地路径作为参数调用。
- 如果提示 `Unauthorized`，请提醒用户检查团队 API Key 的有效性或余额。
