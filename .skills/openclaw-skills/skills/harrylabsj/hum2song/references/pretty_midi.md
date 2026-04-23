# Pretty MIDI 参考资料

用于创建、操作和写入 MIDI 文件的 Python 库。

## 简介

Pretty MIDI 是一个用于处理 MIDI 文件的 Python 库，提供了简洁的 API 来创建和操作 MIDI 数据。

## 安装

```bash
pip install pretty_midi
```

## 基本用法

### 创建 MIDI 文件

```python
import pretty_midi

# 创建 MIDI 对象
pm = pretty_midi.PrettyMIDI()

# 创建乐器轨道
instrument = pretty_midi.Instrument(program=0)  # 钢琴

# 添加音符
note = pretty_midi.Note(
    velocity=100,
    pitch=60,  # C4
    start=0.0,
    end=0.5
)
instrument.notes.append(note)

# 添加轨道
pm.instruments.append(instrument)

# 保存
pm.write("output.mid")
```

### 读取 MIDI 文件

```python
# 加载 MIDI
pm = pretty_midi.PrettyMIDI("input.mid")

# 获取信息
print(f"时长: {pm.get_end_time()}秒")
print(f"BPM: {pm.estimate_tempo()}")

# 遍历音符
for instrument in pm.instruments:
    for note in instrument.notes:
        print(f"音高: {note.pitch}, 开始: {note.start}, 结束: {note.end}")
```

## 参考资料

- GitHub: https://github.com/craffel/pretty-midi
- 文档: https://craffel.github.io/pretty-midi/
