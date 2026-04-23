# Audio Announcement Skill 🦊

让 OpenClaw 开口说话，实时播报 AI 的一举一动！

## 概述

这是一个语音播报技能，可以让你的 AI 代理通过语音实时告诉你它在做什么。就像一只爱说话的龙虾，让你更清楚、更安心地知道 AI 的当前状态。

**版本**: 1.7.4  
**状态**: ✅ 生产就绪  
**安装**: `clawhub install audio-announcement`

### 🎯 最新更新 (v1.5.0)
- ✅ **Windows 默认使用 pygame** - `announce.sh` 在 Windows 平台自动调用 `announce_pygame.py`
- ✅ **简化 Windows 使用** - 无需手动选择脚本，统一使用 `announce.sh`
- ✅ **清理无用测试脚本** - 移除 `test-integration.sh` 和备份文件

### 📜 历史更新
- **v1.4.0**: Windows 11 完整支持，新增 `announce_pygame.py`，修复新会话语音、macOS 兼容性、跨平台哈希计算
- **v1.3.0**: 新增 workflow-helper.sh，支持自动包装命令
- **v1.2.0**: 新增离线模式支持
- **v1.1.0**: 支持多语言（9种语言）
- **v1.0.0**: 初始版本，支持 macOS/Linux

### 特性

- 🎯 **透明度**：清楚知道 AI 正在执行什么操作
- 🔒 **安全感**：实时听到操作，不用盯着日志看
- 💬 **人性化**：友好的声音，不是冷冰冰的文字
- ⚡ **效率**：专注你的工作，让 AI 用声音告诉你进度
- 🌍 **9种语言**：中文、英文、日文、韩文、西班牙语、法语、德语等
- 🔄 **队列机制**：消息永不丢失，自动重试

### 🦊 语音播报（强制执行）

**每次交互都必须语音播报！**

#### 播报时机与内容
| 时机 | 类型 | 内容要求 | 示例 |
|------|------|----------|------|
| 收到消息 | `receive` | 收到的指令信息 | "收到上传指令" |
| 开始工作 | `task` | 工作规划 | "准备上传到GitHub" |
| 执行中 | `task` | 下一步要处理的内容 | "正在生成文档" |
| 任务完成 | `complete` | 工作总结 | "上传完成" |
| **发送回复** | `complete` | 回复内容的简短总结 | "已发送项目地址" |

#### 内容原则
- **信息丰富**：包含指令/规划/进度/总结
- **简洁**：不超过 20 个字
- **不带名称**：不说用户名、不说"我"
- **口语化**：像朋友随口说一句

#### 强制播报场景
- 每次收到用户消息 → 先播报指令内容
- 开始执行任务 → 播报工作规划
- 执行过程中 → 播报下一步要做什么
- 任务完成/失败 → 播报工作总结
- **发送文字回复前 → 播报回复内容的简短总结（1句话）**
- **API/网络异常时 → 播报告警信息**
  - Token 用完 → "额度不足"
  - 网络超时 → "连接超时"
  - 接口异常 → "服务异常"
  - 模型不可用 → "模型繁忙"

#### 安装后配置

安装此技能后，需要将以下内容添加到 OpenClaw 工作区的 `AGENTS.md` 文件中，以确保 AI 代理强制执行语音播报：

```markdown
## 🦊 语音播报（强制执行）

**每次交互都必须语音播报！**

### 播报时机与内容
| 时机 | 类型 | 内容要求 | 示例 |
|------|------|----------|------|
| 收到消息 | `receive` | 收到的指令信息 | "收到上传指令" |
| 开始工作 | `task` | 工作规划 | "准备上传到GitHub" |
| 执行中 | `task` | 下一步要处理的内容 | "正在生成文档" |
| 任务完成 | `complete` | 工作总结 | "上传完成" |
| **发送回复** | `complete` | 回复内容的简短总结 | "已发送项目地址" |

### 内容原则
- **信息丰富**：包含指令/规划/进度/总结
- **简洁**：不超过 20 个字
- **不带名称**：不说用户名、不说"我"
- **口语化**：像朋友随口说一句

### 播报脚本
\`\`\`bash
~/.openclaw/skills/audio-announcement/scripts/announce.sh <type> "<message>" [lang]
\`\`\`

### 示例
\`\`\`bash
# 收到消息 - 说出指令
./announce.sh receive "收到上传指令"

# 开始工作 - 说出规划
./announce.sh task "准备上传文件"

# 执行中 - 说出进度
./announce.sh task "正在生成文档"

# 完成 - 说出总结
./announce.sh complete "上传完成"
\`\`\`

### 强制播报场景
- 每次收到用户消息 → 先播报指令内容
- 开始执行任务 → 播报工作规划
- 执行过程中 → 播报下一步要做什么
- 任务完成/失败 → 播报工作总结
- **发送文字回复前 → 播报回复内容的简短总结（1句话）**
- **API/网络异常时 → 播报告警信息**
  - Token 用完 → "额度不足"
  - 网络超时 → "连接超时"
  - 接口异常 → "服务异常"
  - 模型不可用 → "模型繁忙"
```

## 平台支持

| 平台 | 状态 | 推荐方案 | 说明 |
|------|------|----------|------|
| **macOS** | ✅ 稳定 | `announce.sh` | 原生 `afplay` 播放，无需额外依赖 |
| **Linux** | ✅ 稳定 | `announce.sh` | 需安装 `mpg123` 或 `ffmpeg` |
| **Windows** | ✅ 稳定 | `announce.sh` | 自动调用 pygame，无需 WMP |
| **Android** | ⚠️ 实验性 | `announce.sh` | 需要 Termux 环境 |

### Windows 特别说明 (v1.5.0 更新)

Windows 11 默认禁用了 Windows Media Player。从 v1.5.0 开始，`announce.sh` 在 Windows 平台会自动检测并调用 `announce_pygame.py`，无需手动选择脚本：

```powershell
# 安装依赖
pip install edge-tts pygame

# 统一使用 announce.sh（Windows 自动调用 pygame 版本）
./announce.sh complete "任务完成" zh
```

**Windows 方案对比：**

| 方案 | 依赖 | 适用场景 |
|------|------|----------|
| `announce.sh` | `pygame` | ✅ **推荐**，自动检测平台，统一接口 |
| `announce_pygame.py` | `pygame` | 直接调用，高级用户可选 |
| `announce.bat` | VLC/WMP | 备用方案，需安装 VLC |
| `announce.ps1` | PowerShell + WMP | 旧方案，Win11 可能不兼容 |

## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install edge-tts
```

注意：edge-tts 需要 Python 3.7+。如果遇到安装问题，请确保网络通畅或使用国内镜像源。

### 2. 平台特定依赖

#### macOS
- 系统自带音频播放支持，无需额外安装

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install mpg123

# CentOS/RHEL/Fedora
sudo yum install mpg123
```

#### Windows

**推荐方案 - 使用 pygame（无需 VLC/WMP）：**
```powershell
pip install edge-tts pygame
```

**备用方案 - 使用 VLC：**
- 安装 [VLC](https://www.videolan.org/vlc/) 媒体播放器
- 或确保系统已安装能播放 MP3 的音频软件

## 安装方法

### 🚀 方法一：使用 ClawHub（推荐）

```bash
# 安装最新版
clawhub install audio-announcement

# 或安装特定版本
clawhub install audio-announcement@1.4.0
```

**优点**：
- 自动处理依赖和配置
- 一键安装，无需手动复制文件
- 自动版本管理
- 社区支持

### 方法二：手动安装（备用）

1. 克隆此技能仓库：
```bash
git clone https://github.com/wililam/audio-announcement-skills.git
```

2. 复制技能到 OpenClaw skills 目录：
```bash
# macOS/Linux
cp -r audio-announcement-skills/skills/audio-announcement ~/.openclaw/skills/

# Windows (PowerShell)
Copy-Item -Recurse -Force audio-announcement-skills\skills\audio-announcement $env:USERPROFILE\.openclaw\skills\
```

### 方法三：从网络直接下载（如果克隆失败）

如果 git clone 失败，可以手动下载：
1. 访问 https://github.com/wililam/audio-announcement-skills
2. 点击 "Code" → "Download ZIP"
3. 解压后复制 `skills/audio-announcement` 文件夹到 `~/.openclaw/skills/`

## 使用方法

### 测试播报

使用 `announce.sh` 脚本测试语音功能：

```bash
# 中文播报（任务完成）
./announce.sh complete "任务完成" zh

# 英文播报（任务完成）
./announce.sh complete "Task finished" en

# 日文播报（处理中）
./announce.sh task "処理中です" ja
```

### 在 OpenClaw 中使用

技能安装后，OpenClaw 会自动加载。你可以通过以下方式触发播报：

1. **在技能配置中启用**：确保 audio-announcement 技能已启用
2. **自定义事件**：在你的工作流中添加播报动作
3. **使用 Skill API**：调用 `announce.sh` 脚本

### 使用方法

#### macOS / Linux

使用 `announce.sh` 脚本：

```bash
# 收到消息 - 说出指令
./announce.sh receive "收到上传指令" zh

# 开始工作 - 说出规划
./announce.sh task "准备上传到GitHub" zh

# 执行中 - 说出进度
./announce.sh task "正在生成文档" zh

# 任务完成 - 工作总结
./announce.sh complete "任务完成" zh

# 发送回复 - 回复内容总结
./announce.sh complete "已发送项目地址" zh

# 英文播报（任务完成）
./announce.sh complete "Task finished" en

# 日文播报（处理中）
./announce.sh task "処理中です" ja
```

#### Windows

使用 `announce_pygame.py` 脚本（推荐）：

```powershell
# 中文播报
python scripts/announce_pygame.py complete "任务完成" zh

# 英文播报
python scripts/announce_pygame.py task "Processing..." en

# 日文播报
python scripts/announce_pygame.py error "エラーが発生しました" ja
```

**Windows 批处理脚本（备用）：**

```cmd
# 使用批处理脚本（需安装 VLC）
scripts\announce.bat complete "任务完成" zh
```

### 脚本参数

所有脚本支持以下参数：

```bash
./announce.sh <type> "<message>" <language>

# type: 消息类型
#   - receive: 收到消息/指令
#   - task: 任务开始/处理中
#   - complete: 任务完成
#   - error: 错误/警告
#   - custom: 自定义消息

# message: 要播报的文字内容

# language: 语言代码
#   - zh: 中文
#   - en: 英文
#   - ja: 日文
#   - ko: 韩文
#   - es: 西班牙语
#   - fr: 法语
#   - de: 德语
```

## 故障排除

### edge-tts 安装失败
- 检查 Python 版本（需要 3.7+）
- 使用 `--trusted-host` 参数或更换镜像源
- 升级 pip: `python -m pip install --upgrade pip`

### Windows 特定问题

**问题：Windows 11 没有声音**
- ✅ 解决方案：使用 `announce_pygame.py` 替代 `announce.bat`
- 安装 pygame: `pip install pygame`
- 原因：Windows 11 默认禁用 Windows Media Player

**问题：pygame 安装失败**
- 确保 Python 3.7+ 已安装
- 尝试: `pip install pygame --upgrade`
- 或下载预编译 wheel: https://pypi.org/project/pygame/#files

### 没有声音
- **macOS**: 检查系统音量，确认 `afplay` 可用
- **Linux**: 确认 `mpg123` 或 `ffmpeg` 已安装
- **Windows**: 确认 `pygame` 已安装，或使用 VLC 方案
- 测试播放: `mpg123 test.mp3` (Linux) 或系统音频播放器

### 播报延迟
- 首次使用会有缓存延迟（首次下载语音包）
- 网络不佳时可能影响语音获取速度
- 考虑使用本地语音合成引擎替代

## 技术说明

- 使用 Microsoft Edge 的 TTS 在线服务
- 语音队列系统确保消息按顺序播放
- 支持中断和优先级管理
- 自动重试失败的播报

## 贡献

欢迎提交 Issue 和 PR！

## License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 作者

miaoweilin - [GitHub](https://github.com/wililam)

## 🚀 工作流程集成

### 快速集成
```bash
# 加载助手函数
source ~/.openclaw/skills/audio-announcement/scripts/workflow-helper.sh

# 使用示例
announce_task "开始任务"
announce_complete "任务完成"
announce_error "发生错误"
```

### 自动包装命令
```bash
# 自动播报任务开始和完成
announce_wrap "文件备份" backup_script.sh
```

### 带进度播报
```bash
announce_with_progress "系统更新" 3 \
    "sudo apt update" \
    "sudo apt upgrade -y" \
    "sudo apt autoremove -y"
```

🦊 让你的工作流程会说话，提高透明度和工作效率！
Make your workflow talk, increase transparency and productivity!

⭐ 如果这个技能对你有帮助，请给它一个 star！⭐
