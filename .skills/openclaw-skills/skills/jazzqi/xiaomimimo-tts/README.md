# MiMo TTS Skill

小米 MiMo TTS 语音合成 OpenClaw Skill。

## 安装

```bash
clawhub install mimo-tts-v2
```

## 配置

设置环境变量：

```bash
export MIMO_API_KEY=your-api-key
```

获取 API Key: https://platform.xiaomimimo.com/

## 使用

### 命令行

```bash
# 生成语音
~/.openclaw/skills/mimo-tts/scripts/mimo-tts.sh "你好世界"

# 指定输出文件
~/.openclaw/skills/mimo-tts/scripts/mimo-tts.sh "你好世界" output.ogg

# 自定义语音
MIMO_VOICE=zh-CN-YunyangNeural ~/.openclaw/skills/mimo-tts/scripts/mimo-tts.sh "你好"
```

### 测试

```bash
~/.openclaw/skills/mimo-tts/scripts/test.sh
```

## 可用语音

- `zh-CN-XiaoxiaoNeural` - 中文女声（默认）
- `zh-CN-YunyangNeural` - 中文男声
- `zh-CN-XiaoyiNeural` - 中文女声（活泼）

## 依赖

- curl
- python3
- ffmpeg

## License

MIT
