# Basic Pitch 参考资料

Spotify 开源的音高检测工具，用于从音频中提取 MIDI 音符。

## 简介

Basic Pitch 是 Spotify 开发的轻量级音高检测模型，能够将音频转换为 MIDI 格式。

## 安装

```bash
pip install basic-pitch
```

## 基本用法

```python
from basic_pitch import ICASSP_2022_MODEL_PATH
from basic_pitch.inference import predict

# 预测音频
model_output, midi_data, note_events = predict("audio_file.wav")

# 保存 MIDI
midi_data.write("output.mid")
```

## 输出说明

- `model_output`: 原始模型输出
- `midi_data`: PrettyMIDI 对象
- `note_events`: 音符事件列表

## 参考资料

- GitHub: https://github.com/spotify/basic-pitch
- 论文: https://arxiv.org/abs/2203.09893
