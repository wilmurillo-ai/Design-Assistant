---
name: voice-output
description: Use when Tony says voice reply or speaks. Speaks response aloud via Doubao TTS afplay to MOMAX BS6.
---

# voice-output skill

## 触发条件

**以下任一条件满足时，触发语音输出：**
- 消息包含「语音回复」「用话说」「voice reply」「语音」
- Tony 明确要求"说给我听"
- 任何明确要求语音输出的自然语言表达

**Tony 说"不要语音""纯文字"时：即使满足触发条件也不播放。**

## 执行步骤（每次收到 Tony 消息时必须执行）

```
1. 检查消息是否包含触发词
2. 如果是：
   a. 生成完整文字回复（详细、完整）
   b. 生成语音播报内容（口语化描述这个文字版本）
   c. 调用 voice_speak.py 播放语音
   d. 等待语音播放完成
3. 回复 Tony（文字 + 语音同时存在）
```

## 文字内容 vs 语音内容

| 类型 | 要求 |
|------|------|
| **文字回复** | 详细、完整，详细输出所有内容 |
| **语音播报** | 口语化描述，口头表达这个完整版本的内容 |

**原则**：语音不是逐字朗读文字，而是对这个版本的**口头描述**——保留核心要点，用自然口语表达。

## 语音内容规则

- **口语化**：「我发现了...」「这是...」
- **要点突出**：核心信息优先
- **去掉格式符号**：不用 Markdown 格式，用口头语言
- **长度适中**：比详细文字短，但核心内容不遗漏

## 调用方式

```bash
python3 /Users/tony/.openclaw/workspace/skills/voice-output/scripts/voice_speak.py "要说的内容"
```

参数（可选）：
```bash
# 指定音色和情绪
python3 voice_speak.py "内容" zh_female_xiaohe_uranus_bigtts happy 1.0 1.0
```

## 架构

- **TTS API**：豆包语音合成 2.0（非流式 HTTP）
- **默认音色**：`zh_female_xiaohe_uranus_bigtts`（小何，清晰自然）
- **播放器**：`afplay`（macOS 内置，自动路由到 MOMAX BS6）
- **无后台进程**：每次触发直接调用 API

## 依赖

- Python3（自带 urllib、base64）
- `afplay`（macOS 内置）
- 豆包 TTS 2.0 凭证（APPID: 8982709936）

## 详细 API 文档

参见 `references/doubao_tts_api.md`
