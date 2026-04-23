---
name: mimo-tts
description: |
  使用小米米萌 TTS (mimo-v2-tts) 生成语音。
  支持中文语音合成，需要 MIMO_API_KEY。
---

# MiMo TTS Skill

## 快速开始

当用户请求 TTS 时：

```bash
~/.openclaw/skills/mimo-tts/scripts/mimo-tts.sh "要转换的文本"
```

## 配置

设置环境变量：
```bash
export MIMO_API_KEY=your-api-key
```

## 语音选项

默认使用 `zh-CN-XiaoxiaoNeural`（中文女声）
