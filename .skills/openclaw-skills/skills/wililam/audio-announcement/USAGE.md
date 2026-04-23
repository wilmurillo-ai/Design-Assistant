# Audio Announcement Skill - 使用指南

## 快速开始

### 1. 测试安装
```powershell
cd $env:USERPROFILE\.openclaw-autoclaw\skills\audio-announcement\scripts
.\announce.ps1 complete "测试成功！" zh
```

### 2. 基本用法
```powershell
.\announce.ps1 <类型> "<消息>" [语言]

# 示例：
.\announce.ps1 task "正在下载文件..." zh
.\announce.ps1 complete "任务完成" en
.\announce.ps1 error "发生错误，请检查" zh
.\announce.ps1 custom "自定义消息" ja
```

### 3. 支持的参数
- **类型**：`task`（进行中）, `complete`（完成）, `error`（错误）, `custom`（自定义）
- **语言**：`zh`（中文）, `en`（英文）, `ja`（日文）, `ko`（韩文）, `es`（西语）, `fr`（法语）, `de`（德语）
- **音量**：脚本自动根据时间段调整（正常 50%，午休/晚休 30%）

## 在 OpenClaw 中集成

### Bash 工作流（macOS/Linux）
```bash
#!/bin/bash
# 在你的技能或脚本中
~/.openclaw-autoclaw/skills/audio-announcement/scripts/announce.sh task "开始处理任务" zh
# 执行其他操作...
~/.openclaw-autoclaw/skills/audio-announcement/scripts/announce.sh complete "任务完成" zh
```

### PowerShell 工作流（Windows）
```powershell
# 在你的技能或脚本中
& "$env:USERPROFILE\.openclaw-autoclaw\skills\audio-announcement\scripts\announce.ps1" task "正在处理..." zh
# 执行其他操作...
& "$env:USERPROFILE\.openclaw-autoclaw\skills\audio-announcement\scripts\announce.ps1" complete "处理完成" zh
```

### Python 集成示例
```python
import subprocess
import os

def announce(message, type="complete", lang="zh"):
    script = os.path.expanduser("~/.openclaw-autoclaw/skills/audio-announcement/scripts/announce.ps1")
    subprocess.Popen(["powershell", "-File", script, type, message, lang], creationflags=subprocess.CREATE_NO_WINDOW)

# 使用
announce("开始下载", "task")
# ... 执行任务 ...
announce("下载完成", "complete")
```

## 高级功能

### 队列系统（Bash 版本）
原始脚本支持队列，但 PowerShell 版本采用直接异步播放。如果你需要队列功能（保证消息顺序），可以使用以下模式：

```powershell
# 将消息写入队列文件，由专门的队列管理器处理
$queueDir = "$env:USERPROFILE\.cache\audio-announcement-queue"
New-Item -ItemType Directory -Force -Path $queueDir | Out-Null
$queueFile = Join-Path $queueDir "$(Get-Date -Format 'yyyyMMdd_HHmmss_ffff').txt"
"complete|任务完成|zh" | Out-File $queueFile -Encoding UTF8
```

### 音量控制
脚本会根据时间段自动调整音量：
- **正常时间**（8:00-12:00, 14:00-22:00）：50%
- **午休**（12:00-14:00）：30%
- **晚休**（22:00-8:00）：30%

如需手动控制，修改脚本中的 `NORMAL_VOLUME` 和 `REST_VOLUME` 变量。

### 语音缓存
所有生成的语音会缓存在 `~/.cache/audio-announcement/`，相同内容不会重复生成，节省流量和时间。

## 故障排除

### 问题：没有声音
**检查：**
1. 系统音量是否开启
2. 是否安装了音频播放器（VLC / Windows Media Player）
3. 测试播放生成的 MP3 文件：
```powershell
# 手动测试
edge-tts --text "测试" --voice "zh-CN-XiaoxiaoNeural" --write-media "test.mp3"
# 然后双击 test.mp3 播放
```

### 问题：脚本执行被阻止
**解决：** PowerShell 可能需要更改执行策略：
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

### 问题：edge-tts 报错
**检查：**
- Python 版本 >= 3.7
- 网络连接（需要访问微软 TTS 服务）
- `edge-tts --version` 是否正常输出

## 技术细节

- **语音引擎**：Microsoft Edge TTS（免费在线服务）
- **音频格式**：MP3
- **播放方式**：异步非阻塞（不影响主流程）
- **缓存位置**：`~/.cache/audio-announcement/`
- **临时文件**：`%TEMP%\audio-announcement\`

## 版本

- **技能版本**：1.0.0
- **脚本版本**：1.2.1（适配 Windows PowerShell）
- **edge-tts**：7.2.8+

## 作者

原项目：miaoweilin (wililam)
适配：OpenClaw Agent
协议：MIT

🦊 让你的 AI 开口说话，让你更安心！
