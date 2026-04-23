---
name: senseaudio-elderly-voice-assistant
description: 银发族语音助手——老年人对着手机说话就能发消息、查天气、设闹钟、听戏曲，无需学任何操作。
metadata:
  openclaw:
    emoji: "👴"
    homepage: https://senseaudio.cn/docs
    requires:
      env:
        - SENSEAUDIO_API_KEY
      bins:
        - python3
    primaryEnv: SENSEAUDIO_API_KEY
    install:
      - kind: uv
        package: requests
compatibility:
  required_credentials:
    - name: SENSEAUDIO_API_KEY
      description: API key from https://senseaudio.cn/platform/api-key
      env_var: SENSEAUDIO_API_KEY
---

# 银发族语音助手 / Elderly Voice Assistant

老年人对着手机说话就能完成发消息、查天气、设闹钟、听新闻、听戏曲，不用学任何操作。

## 设计理念

- 零门槛：界面只有一个超大麦克风按钮，没有文字菜单，所有功能语音触发
- 口语容错：老年人说话啰嗦、重复、方言混杂、停顿长，LLM 做强容错意图理解
- 语音反馈：所有执行结果用清晰、慢速、大音量的 TTS 播报，不依赖屏幕
- 主动关怀：定时提醒吃药喝水、每天播报天气穿着、无交互时通知子女
- 内容陪伴：根据偏好播放戏曲评书老歌，也可与 AI 聊天解闷

## 工作流程

```
[按住大按钮说话] → ASR识别(容错) → LLM意图理解 → 执行动作 → TTS语音播报结果
```

## 核心 API

### 语音识别（ASR）

```bash
curl https://api.senseaudio.cn/v1/audio/transcriptions \
  -H "Authorization: Bearer $SENSEAUDIO_API_KEY" \
  -F file="@recording.wav" \
  -F model="sense-asr" \
  -F language="zh" \
  -F response_format="text"
# 返回：那个就是跟我那个大儿子说一下明天那个不用来了
```

### 语音合成（TTS）— 适老化参数

```bash
curl -X POST https://api.senseaudio.cn/v1/t2a_v2 \
  -H "Authorization: Bearer $SENSEAUDIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "SenseAudio-TTS-1.0",
    "text": "好的，已经帮您给大儿子发了消息，内容是：明天不用来了。",
    "stream": false,
    "voice_setting": {
      "voice_id": "female_0001_a",
      "speed": 0.8,
      "vol": 3.0,
      "pitch": 0
    },
    "audio_setting": {
      "format": "mp3",
      "sample_rate": 32000
    }
  }'
```

适老化 TTS 参数说明：

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| speed | 0.8 | 慢速播报，老人听得清 |
| vol | 3.0 | 大音量，适合听力下降 |
| voice_id | female_0001_a | 温暖女声，亲切感强 |

## 口语容错与意图理解

ASR 转写后，LLM 对老年人口语做强容错意图提取。

### 容错示例

| 老人原话（ASR 转写） | LLM 提取意图 | 执行动作 |
|---------------------|-------------|---------|
| 那个……就是……跟我那个大儿子说一下……明天那个不用来了 | send_message(to="大儿子", content="明天不用来了") | 发消息 |
| 今天外头冷不冷啊，要不要穿厚点 | get_weather(query="今天气温") | 查天气 |
| 帮我定个……就是下午三点……三点钟吃药的那个闹钟 | set_alarm(time="15:00", label="吃药") | 设闹钟 |
| 给我放段那个……黄梅戏……就是天仙配 | play_content(type="戏曲", query="黄梅戏天仙配") | 播放内容 |
| 没意思，给我放点东西听听 | play_content(type="推荐", based_on="历史偏好") | 智能推荐 |
| 跟我聊聊天吧，一个人怪无聊的 | chat(mode="陪伴") | AI 聊天 |

### LLM 意图提取 Prompt

```python
INTENT_SYSTEM_PROMPT = """你是一个专为老年人设计的语音助手的意图理解模块。
老年人说话有以下特点，你需要容错处理：
1. 大量口头禅和填充词：那个、就是、嗯、啊、这个
2. 重复表达：同一个意思说两三遍
3. 方言混杂：可能夹杂方言词汇
4. 长停顿：句子中间可能有很长的停顿导致断句不完整
5. 间接表达：不会直接说功能名，而是描述需求

请从用户的话中提取意图，返回 JSON：
{
  "intent": "send_message|get_weather|set_alarm|play_content|chat|unknown",
  "params": { ... },
  "confidence": 0.0-1.0
}

如果置信度低于 0.6，intent 设为 "confirm"，并生成一句确认话术。
确认话术要亲切、简短、用老人听得懂的话，比如：
"您是想让我帮您给大儿子发消息吗？"
"""
```

## 支持的功能

### 1. 发消息

```python
def handle_send_message(params: dict) -> str:
    """发消息给联系人"""
    to = params["to"]       # 联系人称呼：大儿子、老伴、小孙女
    content = params["content"]
    # 查找联系人映射 → 发送消息
    # ...
    return f"好的，已经帮您给{to}发了消息，内容是：{content}。要不要我再加点什么？"
```

### 2. 查天气

```python
import requests

def handle_get_weather(params: dict) -> str:
    """查天气并生成适老播报"""
    city = params.get("city", "默认城市")
    weather = requests.get(f"https://wttr.in/{city}?format=%c+%t+%h&lang=zh", timeout=10).text.strip()
    # 生成适老播报：加穿衣建议
    return f"今天{city}的天气是{weather}。建议您今天出门多穿一件外套，注意保暖。"
```

### 3. 设闹钟

```python
def handle_set_alarm(params: dict) -> str:
    """设置提醒闹钟"""
    time_str = params["time"]   # "15:00"
    label = params["label"]     # "吃药"
    # 调用系统闹钟 API
    # ...
    return f"好的，已经帮您设好了下午{time_str}的闹钟，到时候提醒您{label}。"
```

### 4. 播放内容

```python
CONTENT_CATEGORIES = {
    "戏曲": ["黄梅戏", "京剧", "越剧", "豫剧", "评剧"],
    "评书": ["三国演义", "水浒传", "岳飞传", "隋唐演义"],
    "老歌": ["邓丽君", "刘德华", "费玉清", "蔡琴"],
    "养生": ["养生堂", "健康之路", "中医养生"],
    "新闻": ["今日新闻", "国内要闻", "本地新闻"],
}

def handle_play_content(params: dict) -> str:
    content_type = params.get("type", "推荐")
    query = params.get("query", "")
    if content_type == "推荐":
        # 根据历史偏好推荐
        pass
    return f"好的，这就给您放{query}，您听着，想换就跟我说。"
```

### 5. AI 陪伴聊天

```python
CHAT_SYSTEM_PROMPT = """你是一位耐心、亲切的语音助手，正在陪一位老人聊天。
说话风格要求：
- 语速慢，句子短，每句不超过20个字
- 用"您"称呼，语气温暖像晚辈
- 多倾听，适当回应，不要长篇大论
- 聊家常话题：天气、吃饭、身体、往事
- 如果老人情绪低落，温柔安慰，必要时建议联系家人
"""
```

## 完整 Python 实现

```python
import os
import json
import requests
import tempfile
import subprocess
from datetime import datetime

API_KEY = os.environ["SENSEAUDIO_API_KEY"]
ASR_URL = "https://api.senseaudio.cn/v1/audio/transcriptions"
TTS_URL = "https://api.senseaudio.cn/v1/t2a_v2"

# 适老化 TTS 参数
ELDERLY_TTS_PARAMS = {
    "model": "SenseAudio-TTS-1.0",
    "stream": False,
    "voice_setting": {
        "voice_id": "female_0001_a",
        "speed": 0.8,   # 慢速
        "vol": 3.0,     # 大音量
        "pitch": 0,
    },
    "audio_setting": {"format": "mp3", "sample_rate": 32000},
}


def asr_recognize(audio_path: str) -> str:
    """语音识别，返回转写文本"""
    with open(audio_path, "rb") as f:
        resp = requests.post(
            ASR_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            files={"file": f},
            data={"model": "sense-asr", "language": "zh", "response_format": "text"},
            timeout=20,
        )
    resp.raise_for_status()
    return resp.text.strip()


def tts_speak(text: str) -> None:
    """TTS 合成并播放，适老化参数"""
    payload = {**ELDERLY_TTS_PARAMS, "text": text}
    resp = requests.post(
        TTS_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    resp.raise_for_status()
    audio_bytes = bytes.fromhex(resp.json()["data"]["audio"])
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_bytes)
        tmp = f.name
    for cmd in [["afplay", tmp], ["play", tmp], ["mpg123", tmp]]:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue


def extract_intent(text: str, llm_call) -> dict:
    """LLM 意图提取，容错老年人口语"""
    result = llm_call(
        system=INTENT_SYSTEM_PROMPT,
        user=text,
    )
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {"intent": "unknown", "params": {}, "confidence": 0.0}


def handle_intent(intent_result: dict) -> str:
    """根据意图执行动作，返回播报文本"""
    intent = intent_result.get("intent")
    params = intent_result.get("params", {})
    confidence = intent_result.get("confidence", 1.0)

    if confidence < 0.6 or intent == "confirm":
        return intent_result.get("confirm_text", "您刚才说的是什么意思，能再说一遍吗？")

    if intent == "send_message":
        to = params.get("to", "家人")
        content = params.get("content", "")
        # TODO: 调用消息发送接口
        return f"好的，已经帮您给{to}发了消息，内容是：{content}。"

    elif intent == "get_weather":
        city = params.get("city", "")
        weather = requests.get(
            f"https://wttr.in/{city or ''}?format=%c+%t+%h&lang=zh", timeout=10
        ).text.strip()
        return f"今天的天气是{weather}。出门记得看看冷不冷，注意保暖。"

    elif intent == "set_alarm":
        time_str = params.get("time", "")
        label = params.get("label", "提醒")
        # TODO: 调用系统闹钟接口
        return f"好的，已经帮您设好了{time_str}的闹钟，到时候提醒您{label}。"

    elif intent == "play_content":
        query = params.get("query", "")
        content_type = params.get("type", "内容")
        # TODO: 调用内容播放接口
        return f"好的，这就给您放{query or content_type}，您听着，想换就跟我说。"

    elif intent == "chat":
        # 返回空字符串，由上层进入聊天模式
        return ""

    else:
        return "对不起，我没听清楚您说的。能再说一遍吗？说慢一点也没关系。"


class ElderlyVoiceAssistant:
    def __init__(self, llm_call):
        self.llm_call = llm_call
        self.last_active = datetime.now()
        self.preferences = {}  # 历史偏好

    def process_voice(self, audio_path: str) -> None:
        """主流程：录音 → 识别 → 意图 → 执行 → 播报"""
        self.last_active = datetime.now()

        # 1. ASR
        text = asr_recognize(audio_path)
        print(f"[识别] {text}")

        # 2. 意图理解
        intent_result = extract_intent(text, self.llm_call)
        print(f"[意图] {intent_result}")

        # 3. 执行 + 播报
        if intent_result.get("intent") == "chat":
            reply = self.llm_call(system=CHAT_SYSTEM_PROMPT, user=text)
            tts_speak(reply)
        else:
            response_text = handle_intent(intent_result)
            if response_text:
                tts_speak(response_text)
```

## 主动关怀系统

```python
import threading
import time as time_module

class ProactiveCareScheduler:
    """主动关怀调度器"""

    def __init__(self, assistant: ElderlyVoiceAssistant, notify_family_callback):
        self.assistant = assistant
        self.notify_family = notify_family_callback
        self.reminders = []  # [(hour, minute, text), ...]

    def add_medication_reminder(self, hour: int, minute: int, medicine: str):
        self.reminders.append((hour, minute, f"该吃{medicine}了，记得喝水。"))

    def morning_briefing(self):
        """每天早上主动播报天气和穿着建议"""
        weather = requests.get("https://wttr.in/?format=%c+%t&lang=zh", timeout=10).text.strip()
        tts_speak(f"早上好！今天天气{weather}。记得吃早饭，注意身体。")

    def check_inactivity(self):
        """超过24小时无交互，通知子女"""
        delta = datetime.now() - self.assistant.last_active
        if delta.total_seconds() > 86400:
            self.notify_family("老人今天还没有使用语音助手，请关注一下。")

    def run(self):
        """后台运行调度循环"""
        def loop():
            while True:
                now = datetime.now()
                # 早上8点播报天气
                if now.hour == 8 and now.minute == 0:
                    self.morning_briefing()
                # 检查自定义提醒
                for h, m, text in self.reminders:
                    if now.hour == h and now.minute == m:
                        tts_speak(text)
                # 检查无交互
                self.check_inactivity()
                time_module.sleep(60)

        threading.Thread(target=loop, daemon=True).start()
```

## 错误处理与容错

```python
def safe_process_voice(assistant: ElderlyVoiceAssistant, audio_path: str):
    """带容错的语音处理"""
    try:
        assistant.process_voice(audio_path)
    except requests.exceptions.Timeout:
        tts_speak("网络有点慢，请稍等一下再试。")
    except requests.exceptions.ConnectionError:
        tts_speak("网络好像断了，请检查一下网络连接。")
    except Exception:
        tts_speak("出了点小问题，请再说一遍，或者让家人帮您看看。")
```

## 相关资源

- [SenseAudio ASR API](https://senseaudio.cn/docs/asr_api)
- [SenseAudio TTS API](https://senseaudio.cn/docs/text_to_speech_api)
- [SenseAudio 音色列表](https://senseaudio.cn/docs/voice_api)
