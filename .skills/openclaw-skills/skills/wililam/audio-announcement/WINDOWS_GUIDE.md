# Windows 使用指南 | Windows Guide

## 🪟 Windows 11 完全支持

audio-announcement 现已完整支持 Windows 10/11，无需安装 VLC 或 Windows Media Player！

---

## 快速开始 (Quick Start)

### 1. 安装依赖

```powershell
# 安装 edge-tts（语音生成）
pip install edge-tts

# 安装 pygame（音频播放，推荐）
pip install pygame
```

### 2. 测试播报

```powershell
# 中文播报
python scripts/announce_pygame.py complete "任务完成" zh

# 英文播报
python scripts/announce_pygame.py task "Processing..." en

# 日文播报
python scripts/announce_pygame.py error "エラー" ja
```

---

## 方案对比 | Solution Comparison

| 方案 | 命令 | 依赖 | 适用场景 |
|------|------|------|----------|
| **PyGame (推荐)** | `python announce_pygame.py` | `pygame` | ✅ Windows 11 首选，无需 WMP |
| Batch | `announce.bat` | VLC | 备用方案，需安装 VLC |
| PowerShell | `announce.ps1` | WMP | 旧方案，Win11 可能不兼容 |

---

## 详细说明

### 为什么选择 PyGame？

**Windows 11 的变化：**
- Windows 11 默认禁用 Windows Media Player 可选功能
- 原版 `announce.bat` 和 `announce.ps1` 依赖 WMP COM 组件
- 导致无声或播放失败

**PyGame 的优势：**
- ✅ 无需 Windows Media Player
- ✅ 无需 VLC 或 ffmpeg
- ✅ 直接播放 MP3，低延迟
- ✅ 支持音量控制
- ✅ 跨平台兼容（Windows/macOS/Linux）

---

## 参数说明

```powershell
python announce_pygame.py <type> <message> [language]

# type: 消息类型
#   - task      : 任务开始/处理中
#   - complete  : 任务完成
#   - error     : 错误/警告
#   - custom    : 自定义消息

# message: 要播报的文字

# language: 语言代码（可选，默认 zh）
#   - zh: 中文
#   - en: 英文
#   - ja: 日文
#   - ko: 韩文
#   - es: 西班牙语
#   - fr: 法语
#   - de: 德语
```

---

## 故障排除 | Troubleshooting

### 问题：pygame 安装失败

```powershell
# 确保 Python 3.7+ 已安装
python --version

# 升级 pip
python -m pip install --upgrade pip

# 安装 pygame
pip install pygame --upgrade

# 如果仍然失败，下载预编译 wheel
# 访问: https://pypi.org/project/pygame/#files
```

### 问题：没有声音

1. **检查系统音量**
   - 确认系统未静音
   - 确认音量不是 0%

2. **检查 Python 输出**
   ```powershell
   python scripts/announce_pygame.py complete "测试" zh
   ```
   查看是否有错误信息

3. **测试 pygame 单独播放**
   ```python
   import pygame
   pygame.mixer.init()
   pygame.mixer.music.load("test.mp3")
   pygame.mixer.music.play()
   ```

### 问题：edge-tts 生成失败

- 检查网络连接（需要访问微软 TTS 服务）
- 首次使用需要下载语音包，可能较慢
- 检查是否被防火墙阻止

---

## 高级配置

### 修改音量

编辑 `announce_pygame.py`，修改配置：

```python
VOLUME = 0.8  # 音量 0.0 - 1.0 (默认 1.0)
```

### 保留临时文件（调试）

```python
KEEP_TEMP_FILES = True  # 保留生成的 MP3 文件
```

---

## 在 OpenClaw 中使用

### 配置 OpenClaw 使用 PyGame 版本

编辑你的 OpenClaw 配置，将播报命令改为：

```python
# 原来 (macOS/Linux)
"~/.openclaw/skills/audio-announcement/scripts/announce.sh"

# Windows 改为
"python ~/.openclaw/skills/audio-announcement/scripts/announce_pygame.py"
```

### 示例：在 Python 脚本中调用

```python
import subprocess

def announce(type_, message, lang="zh"):
    script_path = r"C:\Users\YourName\.openclaw\skills\audio-announcement\scripts\announce_pygame.py"
    subprocess.run(["python", script_path, type_, message, lang])

# 使用
announce("task", "开始处理数据")
# ... 执行任务 ...
announce("complete", "数据处理完成")
```

---

## 技术细节

- **语音生成**: Microsoft Edge TTS (在线)
- **音频播放**: PyGame Mixer
- **缓存目录**: `%USERPROFILE%\.cache\audio-announcement\`
- **临时文件**: `%TEMP%\audio-announcement\`

---

## 兼容性

| 系统 | 状态 | 备注 |
|------|------|------|
| Windows 11 | ✅ 完全支持 | 推荐 PyGame 方案 |
| Windows 10 | ✅ 完全支持 | 推荐 PyGame 方案 |
| Windows 8/7 | ⚠️ 可能可用 | 未测试 |

---

## 作者

**miaoweilin** (wililam)  
https://github.com/wililam/audio-announcement-skills

---

<div align="center">

**🦊 让你的 AI 在 Windows 上也能开口说话！**

⭐ 如果对你有帮助，请给个 Star！⭐

</div>
