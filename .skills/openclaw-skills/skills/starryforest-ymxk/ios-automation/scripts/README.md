# StarryForest Agent SKILL

封装了 StarryForest Agent Mail API v1 的七种自动化操作，通过邮件发送到 iOS 快捷指令自动化。

## ⚠️ 重要说明

### 触发自动化流程的要求

要成功触发 iOS 自动化流程，必须满足以下条件：

1. **发送方**：必须使用 `starryforest_ymxk@126.com`（account="126"）
2. **接收方**：必须发送到 `starryforest_ymxk@hotmail.com`
3. **邮件主题**：必须包含"自动化推送"短语
4. **Token**：固定为 "starryforest_agent"（自动生成，无需配置）

### 邮件主题要求

- 默认邮件标题为"自动化推送"
- 如果自定义标题，请确保包含"自动化推送"短语
- SKILL 会自动验证标题，如果不包含会发出警告

## 安装

将 `/home/wudi/skills/` 目录添加到 Python 路径：

```bash
export PYTHONPATH=/home/wudi:$PYTHONPATH
```

或在使用时导入：

```python
import sys
sys.path.append('/home/wudi')
from skills import StarryForestAgent
```

## 七种操作

| 操作 | 函数 | 说明 |
|------|------|------|
| 创建闹钟 | `create_alarm()` | 设置闹钟时间和重复规则 |
| 创建提醒事项 | `create_reminder()` | 创建提醒事项，支持优先级 |
| 创建备忘录 | `create_memo()` | 创建备忘录（标题+内容） |
| 创建日历日程 | `create_calendar_event()` | 创建日历事件，支持地点和备注 |
| 专注模式 | `focus_mode()` | 开启/关闭专注模式 |
| 播放音乐 | `play_music()` | 播放/暂停音乐，选择播放列表 |
| 写日记 | `write_journal()` | 写日记（标题+日期+内容） |

## 使用方式

### 方式一：类式 API（推荐，支持批量操作）

```python
from skills import StarryForestAgent

# 初始化 Agent（使用 126 邮箱）
agent = StarryForestAgent(account="126")

# 添加多个操作
agent.create_reminder(
    title="测试提醒",
    due="2026-02-07 15:00",
    notes="来自 Python SKILL",
    priority="中"
)

agent.create_memo(
    title="测试备忘录",
    content="这是通过 SKILL 创建的备忘录"
)

agent.create_alarm(
    time="07:30",
    label="晨练",
    repeat=["Monday", "Wednesday", "Friday"]
)

# 一次性发送所有操作到 Hotmail
agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送")
```

### 方式二：便捷函数（单次操作）

```python
from skills import send_reminder, send_memo, send_alarm

# 快捷发送单个提醒事项
send_reminder(
    title="测试提醒",
    to_email="starryforest_ymxk@hotmail.com",
    due="2026-02-07 15:00",
    notes="来自便捷函数"
)

# 快捷发送单个备忘录
send_memo(
    title="测试备忘录",
    content="这是通过便捷函数创建的",
    to_email="starryforest_ymxk@hotmail.com"
)

# 快捷发送闹钟
send_alarm(
    time="07:30",
    to_email="starryforest_ymxk@hotmail.com",
    label="晨练"
)
```

## 时间格式规范

| 字段类型 | 格式 | 示例 | 适用操作 |
|---------|------|------|---------|
| 时间点 | `YYYY-MM-DD HH:mm` | `2026-02-07 15:00` | 提醒事项、日历、专注模式 |
| 闹钟时间 | `HH:mm` | `07:30` | 创建闹钟 |
| 仅日期 | `YYYY-MM-DD` | `2026-02-07` | 写日记 |

## 完整示例

### 示例 1：创建提醒事项

```python
from skills import StarryForestAgent

agent = StarryForestAgent()
agent.create_reminder(
    title="测试提醒：喝水",
    due="2026-02-07 15:00",
    notes="来自 Python SKILL",
    priority="中"
)
agent.send_all("starryforest_ymxk@hotmail.com")
```

### 示例 2：创建日历日程

```python
from skills import StarryForestAgent

agent = StarryForestAgent()
agent.create_calendar_event(
    title="OpenClaw 测试日程",
    start="2026-02-07 10:00",
    end="2026-02-07 10:30",
    location="Home",
    notes="测试：创建日历事件",
    all_day=False
)
agent.send_all("starryforest_ymxk@hotmail.com")
```

### 示例 3：批量操作

```python
from skills import StarryForestAgent

agent = StarryForestAgent()

# 闹钟
agent.create_alarm(
    time="07:30",
    label="晨练",
    repeat=["Monday", "Wednesday", "Friday"]
)

# 提醒事项
agent.create_reminder(
    title="测试提醒",
    due="2026-02-07 15:00",
    priority="中"
)

# 备忘录
agent.create_memo(
    title="批量操作测试",
    content="一次发送多个操作"
)

# 日历日程
agent.create_calendar_event(
    title="工作会议",
    start="2026-02-07 09:00",
    end="2026-02-07 10:00"
)

# 专注模式
agent.focus_mode(
    name="工作",
    on=True,
    until="2026-02-07 12:00"
)

# 音乐控制
agent.play_music(
    play=True,
    playlist="每日推荐"
)

# 日记
agent.write_journal(
    title="日记",
    date="2026-02-07",
    content="今天完成了批量操作测试"
)

# 一次性发送所有操作
agent.send_all("starryforest_ymxk@hotmail.com", "批量自动化推送")
```

### 示例 4：验证自动化流程配置

```python
from skills import StarryForestAgent

# 使用 126 邮箱发送到 Hotmail，符合自动化流程要求
agent = StarryForestAgent("126")

agent.create_reminder(
    title="自动化流程验证",
    due="2026-02-07 23:00",
    notes="使用 126 邮箱发送到 Hotmail",
    priority="中"
)

# 发送配置：
# - 发送方：starryforest_ymxk@126.com
# - 接收方：starryforest_ymxk@hotmail.com
# - 标题：自动化推送
# - Token：starryforest_agent
agent.send_all("starryforest_ymxk@hotmail.com", "自动化推送")
```

## 邮箱配置

当前支持两个邮箱：

| 邮箱 | 账户参数 | IMAP | SMTP |
|------|---------|------|------|
| 126 | `account="126"` | ✅ | ✅ |
| QQ | `account="qq"` | ✅ | ✅ |

## API 参考

### StarryForestAgent 类

#### 初始化
```python
agent = StarryForestAgent(account="126")  # 或 "qq"
```

#### 方法

| 方法 | 说明 |
|------|------|
| `create_alarm(time, label, enabled, repeat)` | 创建闹钟 |
| `create_reminder(title, due, notes, priority)` | 创建提醒事项 |
| `create_memo(title, content)` | 创建备忘录 |
| `create_calendar_event(title, start, end, location, notes, all_day)` | 创建日历日程 |
| `focus_mode(name, on, until)` | 设置专注模式 |
| `play_music(play, playlist)` | 播放音乐 |
| `write_journal(title, date, content)` | 写日记 |
| `send_all(to_email, title, clear)` | 发送所有操作 |
| `clear_actions()` | 清空操作列表 |
| `get_actions_count()` | 获取操作数量 |

### 便捷函数

| 函数 | 说明 |
|------|------|
| `send_alarm(time, to_email, label, enabled, repeat, account, title)` | 发送闹钟 |
| `send_reminder(title, to_email, due, notes, priority, account, email_title)` | 发送提醒事项 |
| `send_memo(title, content, to_email, account, email_title)` | 发送备忘录 |
| `send_calendar_event(title, start, to_email, end, location, notes, all_day, account, email_title)` | 发送日历日程 |
| `send_focus_mode(name, on, to_email, until, account, email_title)` | 发送专注模式 |
| `send_music(play, playlist, to_email, account, email_title)` | 发送音乐控制 |
| `send_journal(title, date, content, to_email, account, email_title)` | 发送日记 |

## 注意事项

1. **自动化流程要求**：
   - 必须使用 `starryforest_ymxk@126.com` 作为发送方
   - 必须发送到 `starryforest_ymxk@hotmail.com`
   - 邮件主题必须包含"自动化推送"
2. **唯一 ID**：每次发送会自动生成唯一的 payload ID，格式：`agent-YYYYMMDD-HHMMSS-UUID`
3. **批量操作**：推荐使用类式 API 一次性发送多个操作
4. **时间格式**：严格按照文档要求的格式填写
5. **邮箱选择**：
   - 触发自动化流程：必须使用 `account="126"`
   - QQ 邮箱仅用于测试，无法触发自动化流程

## 协议文档

详细协议文档：`/home/wudi/docs/StarryForest Agent Mail API v1 使用说明.md`
