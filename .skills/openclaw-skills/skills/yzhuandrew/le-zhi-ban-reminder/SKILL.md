# 乐知班温馨提醒

自动生成班级温馨提醒图片并通过飞书发送给用户。

## 功能

根据用户请求生成指定日期的班级温馨提醒图片，支持自定义提醒内容和主题颜色，生成后自动通过飞书发送。

## 使用场景

当用户说类似以下内容时激活：
- "下载明天的温馨提醒"
- "生成后天的班级提醒"
- "下载2026-03-20的温馨提醒，记得带水杯，用蓝色主题"
- "温馨提醒，明天穿校服，绿色主题"

## 参数说明

网站URL：`https://lezhiban.yzhu.host/`

支持的参数：
- `date` (必需): 日期，格式 `YYYY-MM-DD`
  - 相对日期：今天、明天、后天
- `notes` (可选): 特别通知内容，例如 "明天请穿校服，带好跳绳"
- `theme` (可选): 主题颜色，支持 `pink`, `blue`, `green`, `orange`, `purple`
- `autoDownload=true` (必需): 开启自动下载

## 实现流程

1. **解析用户请求**
   - 识别日期：今天、明天、后天，或具体日期
   - 识别 notes 参数：提醒内容
   - 识别 theme 参数：主题颜色

2. **构造 URL**
   - 基础URL：`https://lezhiban.yzhu.host/`
   - 添加参数：`?autoDownload=true&date=YYYY-MM-DD`
   - 可选参数：`&notes=xxx&theme=xxx`

3. **生成图片**
   - 使用 `open` 命令打开URL
   - 等待3秒让图片生成和下载完成
   - 检查下载文件夹：`~/Downloads/乐知班温馨提醒_YYYY-MM-DD*.png`
   - 找到最新下载的图片文件
   - **重要**：确认图片下载后，关闭浏览器窗口：
     ```bash
     osascript -e 'tell application "Safari" to close front window' 2>/dev/null || \
     osascript -e 'tell application "Google Chrome" to close front window' 2>/dev/null
     ```

4. **复制图片到 workspace（重要！）**
   - 图片下载到 `~/Downloads/` 后，需要先复制到 workspace
   - 命令：`cp ~/Downloads/乐知班温馨提醒_YYYY-MM-DD.png ~/.openclaw/workspace/remind.png`
   - 或重命名：`mv ~/Downloads/乐知班温馨提醒_YYYY-MM-DD.png ~/.openclaw/workspace/remind_YYYY_MM_DD.png`
   - **原因**：飞书 message 工具无法直接从 ~/Downloads/ 读取文件

5. **发送到飞书**
   - 使用 `message` 工具发送图片
   - 参数：
     - `action`: "send"
     - `channel`: "feishu"
     - `message`: 描述文字（如"已生成X天的班级温馨提醒📝"）
     - `media`: workspace 中的图片路径（如 `~/.openclaw/workspace/remind.png`）
   - **重要**：发送后回复 `NO_REPLY`，避免重复回复

6. **清理旧图片（可选）**
   - 每次生成新图片后，检查是否有7天前的旧图片需要清理
   - 清理命令：`find ~/Downloads -name "乐知班温馨提醒_*.png" -mtime +7 -delete`
   - 清理命令：`find ~/.openclaw/workspace -name "remind*.png" -mtime +7 -delete`
   - 目的：避免图片堆积占用空间
   - 也可以手动执行清理脚本：`/Users/yzhu/.openclaw/workspace/cleanup_reminders.sh`

7. **确认发送**
   - 检查 message 工具的返回结果
   - 如果发送失败，记录错误信息

## 注意事项

- **自动发送**：每次生成图片后自动通过飞书发送，不需要用户提醒
- **图片路径**：图片下载到 `~/Downloads/`，文件名格式为 `乐知班温馨提醒_YYYY-MM-DD (N).png`
- **时间处理**：当前时区为 Asia/Shanghai (GMT+8)
- **关闭浏览器**：**每次下载完图片后必须关闭浏览器窗口**，避免窗口堆积
- **错误处理**：如果飞书发送失败，告诉用户并建议检查网络或飞书配置

## 飞书发送已知问题和解决方案

### ✅ 成功方案（已验证）
会话中确认飞书图片发送的正确方法：
- 先复制图片到 workspace：`cp ~/Downloads/xxx.png ~/.openclaw/workspace/remind.png`
- 然后发送 workspace 中的文件
- **原因**：message 工具无法直接从 ~/Downloads/ 读取文件

### ❌ 之前的问题
会话 7d69186c 和后续测试中发现：
- message 工具返回成功但只能看到文件路径，看不到图片
- 尝试直接使用 ~/Downloads/ 路径失败
- base64 编码方式文件太大（3MB+）不适合通过 buffer 发送

## 示例对话

**用户：** 下载明天的温馨提醒

**流程：**
1. 解析：明天 = 今天 + 1天
2. 构造URL：`https://lezhiban.yzhu.host/?autoDownload=true&date=2026-03-15`
3. 执行：`open "https://lezhiban.yzhu.host/?autoDownload=true&date=2026-03-15"`
4. 等待：`sleep 3`
5. 查找：`ls -lt ~/Downloads/乐知班温馨提醒_2026-03-15*.png`
6. 关闭：`osascript -e 'tell application "Safari" to close front window'`
7. 复制：`cp ~/Downloads/乐知班温馨提醒_2026-03-15.png ~/.openclaw/workspace/remind.png`
8. 发送：`message(action="send", channel="feishu", message="已生成明天的班级温馨提醒📝", media="~/.openclaw/workspace/remind.png")`
9. 清理：`find ~/Downloads -name "乐知班温馨提醒_*.png" -mtime +7 -delete`
10. 回复：`NO_REPLY`

**用户：** 下载后天的温馨提醒，记得带水杯，用蓝色主题

**流程：**
1. 解析：后天 = 今天 + 2天，notes="记得带水杯"，theme="blue"
2. 构造URL：`https://lezhiban.yzhu.host/?autoDownload=true&date=2026-03-16&notes=记得带水杯&theme=blue`
3. 后续步骤同上

## 日期解析规则

- "今天" / "今日"：当天日期
- "明天" / "明日"：当天 + 1天
- "后天"：当天 + 2天
- 具体日期：直接使用（如 "2026-03-20" 或 "3月20日"）
- "下周二"：计算下周二的日期

## 关键命令

```bash
# 打开URL生成图片
open "https://lezhiban.yzhu.host/?autoDownload=true&date=2026-03-15&notes=xxx&theme=xxx"

# 等待并查找最新下载的图片
sleep 3 && ls -lt ~/Downloads/乐知班温馨提醒_2026-03-15*.png | head -1

# 检查图片文件
file ~/Downloads/乐知班温馨提醒_2026-03-15.png

# 关闭浏览器窗口（重要！）
osascript -e 'tell application "Safari" to close front window' 2>/dev/null || \
osascript -e 'tell application "Google Chrome" to close front window' 2>/dev/null
```

## 技能文件结构

```
le-zhi-ban-reminder/
├── SKILL.md          # 本文件
└── references/       # 可选：相关文档或示例
```

## 相关会话

- 会话ID: 7d69186c
- 创建时间: 2026-03-14 14:50-14:58
- 主题: 配置班级温馨提醒自动生成和飞书发送功能

## 清理脚本

- 位置：`/Users/yzhu/.openclaw/workspace/cleanup_reminders.sh`
- 功能：删除7天前的温馨提醒图片
- 手动执行：`bash /Users/yzhu/.openclaw/workspace/cleanup_reminders.sh`
- 自动执行：已添加到 `HEARTBEAT.md`，每次心跳检查并清理
