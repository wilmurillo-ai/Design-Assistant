# bailian-studio

Bailian Studio skill: OCR text extraction + TTS speak.

## 功能一览

1) OCR 文本识别
- 支持本地图片与 URL
- 本地图片会先上传至 OSS，再调用百炼 OCR

2) TTS 语音播报（文本 → 语音播放）
- 百炼 TTS 生成 WAV
- 使用 ffplay 播放（依赖 ffmpeg）

## 安装依赖

```bash
pip install dashscope oss2
brew install ffmpeg
```

## 配置（secrets/bailian.env）

```env
DASHSCOPE_API_KEY=sk-xxx

# TTS 可选配置（留空走默认）
BAILIAN_TTS_MODEL=qwen3-tts-flash
BAILIAN_TTS_VOICE=
BAILIAN_TTS_SAMPLE_RATE=16000

OSS_ACCESS_KEY=ak-xxx
OSS_SECRET_KEY=sk-xxx
OSS_BUCKET=your-bucket
OSS_ENDPOINT=oss-cn-beijing.aliyuncs.com
OSS_REGION=cn-beijing
```

## 使用方法

### OCR

```bash
python3 {baseDir}/scripts/ocr_text.py --image /path/to.png
python3 {baseDir}/scripts/ocr_text.py --url https://example.com/image.png
```

### TTS

```bash
python3 {baseDir}/scripts/tts_speak.py --text "你好"
```
