# Librosa 参考资料

Python 音频分析库，用于音乐和音频分析。

## 简介

Librosa 是一个用于音乐和音频分析的 Python 库，提供音频特征提取、节拍检测、音高分析等功能。

## 安装

```bash
pip install librosa
```

## 核心功能

### 音频加载

```python
import librosa

# 加载音频
y, sr = librosa.load("audio.wav", sr=44100)
```

### 节拍检测

```python
# 检测 BPM
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
beat_times = librosa.frames_to_time(beat_frames, sr=sr)
```

### 音高检测

```python
# 使用 piptrack 检测音高
pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
```

### 频谱特征

```python
# 短时傅里叶变换
D = librosa.stft(y)

# 梅尔频谱
mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)

# 色度特征
chroma = librosa.feature.chroma_stft(y=y, sr=sr)
```

## 参考资料

- 官网: https://librosa.org/
- 文档: https://librosa.org/doc/latest/
- GitHub: https://github.com/librosa/librosa
