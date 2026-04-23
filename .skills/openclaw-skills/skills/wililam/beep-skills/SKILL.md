# beep-skills Skill 🔔

让 OpenClaw 开口说话，实时播报 AI 的一举一动！

## 概述

这是一个语音播报技能，可以让你的 AI 代理通过语音实时告诉你它在做什么。就像一个小喇叭，让你更清楚、更安心地知道 AI 的当前状态。

**版本**: 2.1.0-dev  
**状态**: ✅ 生产就绪  
**安装**: `clawhub install beep` 或 `pip install beep-announcement`

---

## 🎯 品牌说明

### 为什么叫 "Beep · 小喇叭"？
- **Beep**：4个字母，小学生都会读，电脑提示音的代名词
- **小喇叭**：童年记忆中的通知工具，一说就懂
- **组合**：既有科技感（Beep），又有亲切感（小喇叭）
- **Slogan**：让电脑会说话

### 命令行工具
```bash
# 新命令（推荐）
beep test                    # 测试所有类型播报
beep config                  # 查看/设置配置
beep verify-integration      # 一键验证集成（新增！）
beep stats                   # 查看统计信息

# 旧命令（兼容）
audio-announce test         # 仍可用（向后兼容）
audio-announce config
```

---

## 🆕 最新更新 (v2.1.0 - 2026-04-19)

### 🎉 新增：一键集成验证
- ✅ **`beep verify-integration`** - 完整验证命令
  - 依赖检查（pygame, edge-tts, Python 版本）
  - 配置验证（音量、语言、异步设置）
  - 环境自检（7项系统检查）
  - **播放4种测试语音**（receive, task, complete, error）
  - 输出结构化报告 + 返回码（0=成功，1=失败）
  - 安装后首次运行，一键确认集成成功

### 🔧 稳定性增强
- ✅ **重试机制**：网络调用 3 次重试 + 指数退避（1s→2s→4s）
- ✅ **播放降级**：pygame → 系统播放器 → 仅日志（保证核心功能）
- ✅ **配置热重载**：`beep config reload` 无需重启应用
- ✅ **LRU 缓存**：自动清理旧文件，默认保留最新100个
- ✅ **结构化日志**：时间戳 + 级别 + 消息，支持 DEBUG/INFO/WARNING/ERROR
- ✅ **运行时统计**：缓存大小、成功率、运行时间
- ✅ **异常堆栈**：`exc_info=True`，调试更清晰
- ✅ **路径容错**：中文/空格路径安全处理

### 🐛 问题修复
- ✅ 修复配置读取 bug（配置文件路径错误）
- ✅ 修复方法缺失问题（AnnouncementHelper 类同步）
- ✅ 修复函数名错误（`cleanup_old_cache` → `cleanup_temp_files`）
- ✅ 修复重��定义（移除重复的 `clear_cache` 和 `reload_config`）
- ✅ 删除多余文件（误创建的 `core.py`）

### 📊 测试数据（v2.1.0）
- **平台**：Windows 11 (win32)
- **Python**：3.13.12
- **pygame**：2.6.1 (SDL 2.28.4)
- **edge-tts**：7.2.8
- **测试结果**：6/6 成功（100%）
- **缓存文件**：140 个（2.87 MB）
- **运行时间**：~20 秒

---

## 🎤 语音播报（强制执行）

**每次交互都必须语音播报！**

### 播报时机与内容

| 时机 | 类型 | 内容要求 | 示例 |
|------|------|----------|------|
| 收到消息 | `receive` | 收到的指令信息 | "收到上传指令" |
| 开始工作 | `task` | 工作规划 | "准备上传到GitHub" |
| 执行中 | `task` | 下一步要处理的内容 | "正在生成文档" |
| 任务完成 | `complete` | 工作总结 | "上传完成" |
| **发送回复** | `complete` | 回复内容的简短总结 | "已发送项目地址" |
| 遇到异常 | `error` | 错误描述 | "网络连接失败" |

### 内容原则
- **信息丰富**：包含指令/规划/进度/总结
- **简洁**：不超过 20 个字
- **不带名称**：不说用户名、不说"我"
- **口语化**：像朋友随口说一句

---

## 🛠️ 快速集成

### Python Agent（推荐）

```python
# 方式1: 使用 beep 包（新名称）
from beep import receive, task, complete, error

# 一行调用，默认异步不阻塞
receive("用户查询天气")
task("正在获取数据")
complete("已发送天气预报")
error("网络超时")

# 方式2: 使用 AnnouncementHelper（更多控制）
from beep import AnnouncementHelper
helper = AnnouncementHelper()
helper.config.async_default = True  # 默认异步
helper.config.volume = 0.8           # 调整音量
```

### 配置管理

```bash
# 查看当前配置
beep config

# 设置配置
beep config async_default=true volume=0.8

# 测试所有类型
beep test

# 一键验证集成（推荐！）
beep verify-integration

# 查看统计
beep stats

# 启用/禁用
beep enable
beep disable
```

配置文件位置：`~/.config/audio-announcement/config.json`（路径不变，保持兼容）

---

## 🔧 平台支持

| 平台 | 主方案 | 备选方案 | 安装命令 |
|------|--------|----------|----------|
| **Windows** | pygame | 无 | `pip install beep-announcement pygame` |
| **macOS** | pygame | afplay | `brew install edge-tts && pip install pygame beep-announcement` |
| **Linux** | pygame | mpg123 | `apt install edge-tts mpg123 && pip install pygame beep-announcement` |

**自动选择逻辑**：
- 如果 `pygame` 可用 → 所有平台统一使用 pygame 方案
- 如果 `pygame` 不可用 → macOS/Linux 使用系统播放器
- Windows 无 pygame 会报错（必须安装 pygame）

---

## 📦 安装方式

### 方式一：PyPI（推荐）
```bash
pip install beep-announcement pygame
```

### 方式二：ClawHub
```bash
clawhub install beep
```

### 方式三：GitHub 源码
```bash
git clone https://github.com/wililam/beep-announcement.git
cd beep-announcement
pip install -e .
```

---

## 🧪 测试与验证

### 一键验证集成（推荐！）
```bash
beep verify-integration
```

该命令会：
1. ✅ 检查依赖是否正确安装
2. ✅ 验证配置文件
3. ✅ 运行环境自检
4. ✅ **依次播放4种测试语音**
5. ✅ 输出完整报告

听到测试语音 + 看到 "🎉 所有检查通过！" 表示集成成功。

### 基础测试
```bash
beep test
```

测试所有4种播报类型（receive, task, complete, error）。

### 启动自检
```bash
# 自动运行（每次 /new 或 /reset）
python scripts/startup_check_announcement.py

# 手动运行
beep check
```

---

## ⚙️ 配置选项

配置文件：`~/.config/audio-announcement/config.json`

```json
{
  "enabled": true,             // 启用/禁用播报
  "default_lang": "zh",        // 默认语言
  "volume": 0.25,              // 音量 (0.0-1.0)
  "async_default": true,       // 默认异步播放
  "cache_enabled": true,       // 启用缓存
  "log_level": "WARNING",      // 日志级别
  "prefer_pygame": true,       // 优先使用 pygame
  "fallback_to_shell": true    // 失败时回退到 shell 脚本
}
```

运行时修改：
```python
from beep import set_config
set_config(async_default=False, volume=0.8)
```

---

## 🔍 故障排除

### 问题：没有声音

1. 检查系统音量
2. 确认 pygame 已安装：`python -c "import pygame; print(pygame.version.ver)"`
3. 测试 edge-tts：`edge-tts --text "测试" --voice zh-CN-XiaoxiaoNeural --write-media test.mp3`
4. 手动播放 test.mp3 确认音频输出正常

### 问题：播报延迟

- 首次使用会有缓存延迟（下载语音包）
- 考虑使用 `async_default=true` 异步播放
- 检查网络连接（edge-tts 需要联网）

### 问题：/RESET 后播报失效

- 确认 `startup_check_announcement.py` 已配置自动运行
- 手动运行自检：`python scripts/startup_check_announcement.py`
- 检查 IDENTITY.md 和 AGENTS.md 是否保留

---

## 📈 性能与优化

- **缓存机制**：首次生成 MP3 后缓存，后续播放直接复用（无需重复生成）
- **异步播放**：默认后台播放，不阻塞 Agent 响应（可配置为同步）
- **批量操作**：多文件处理时自动队列化
- **资源清理**：临时文件 24 小时自动清理

---

## 🤝 贡献

欢迎提交 Issue 和 PR！

如果你发现任何遗漏播报的场景，或需要更多集成示例，请告诉我们。

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🎉 总结

**Beep · 小喇叭** v2.1.0 提供了：

- ✅ **一键集成验证**：`beep verify-integration` 安装后立即确认
- ✅ **跨平台支持**（Windows/macOS/Linux）
- ✅ **PyPI 一键安装**：`pip install beep-announcement`
- ✅ **防遗忘机制**（启动自检 + 强制规则）
- ✅ **Session Hook 自动恢复**
- ✅ **异步非阻塞播放**
- ✅ **9种语言支持**
- ✅ **稳定性增强**（重试、降级、热重载、LRU 缓存）

**你的 OpenClaw Agent 现在可以"开口说话"了，而且永远不会忘记！** 🔔🗣️

---

**🚀 快速开始：**

```bash
# 1. 安装
pip install beep-announcement pygame

# 2. 一键验证（推荐！）
beep verify-integration

# 3. 配置
beep config async_default=true

# 4. 测试
beep test

# 5. 集成到你的 Agent
from beep import receive, task, complete, error
```

开始享受透明、有温度的声音体验吧！
