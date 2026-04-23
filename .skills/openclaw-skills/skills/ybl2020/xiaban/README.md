# 私人待办事项系统 v0.0.1

一个简单的基于文件的待办事项管理系统，支持文字和图片两种输入方式，通过 AI 自动解析提取任务内容。

## 文件结构

```
~/.openclaw/workspace/
├── todos.json              # 数据存储文件（初始化为空数组）
├── scripts/
│   ├── todo_add.py         # 添加待办（支持文字/图片）
│   ├── todo_list.py        # 查询待办
│   ├── todo_done.py        # 标记完成/删除
│   └── todo_remind.py      # 定时提醒脚本
└── README.md               # 本文件
```

## 环境配置

### 1. 设置环境变量

在运行脚本前，需要配置以下环境变量：

```bash
# OpenAI 兼容 API 配置
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.minimaxi.com/anthropic/v1"  # 可选，默认即为此值
export MODEL_NAME="MiniMax-M2.7-highspeed"  # 可选，默认为此值
```

**配置方法：**

**临时生效（当前终端会话）：**
```bash
export OPENAI_API_KEY="your-api-key"
export MODEL_NAME="your-model-name"
```

**永久生效（推荐）：**
添加到 shell 配置文件：
```bash
echo 'export OPENAI_API_KEY="your-api-key"' >> ~/.zshrc   # 或 ~/.bash_profile
echo 'export MODEL_NAME="your-model-name"' >> ~/.zshrc
source ~/.zshrc
```

### 2. 安装依赖

```bash
pip install openai
```

## 基本使用

### 添加待办

**文字待办：**
```bash
python ~/.openclaw/workspace/scripts/todo_add.py --text "明天下午3点开会"
# AI 会自动提取任务内容，例如："明天下午3点开会"
```

**图片待办：**
```bash
python ~/.openclaw/workspace/scripts/todo_add.py --image /path/to/note.jpg
# AI 会分析图片提取待办事项
```

### 查看待办

```bash
python ~/.openclaw/workspace/scripts/todo_list.py
```

输出示例：
```
============================================================
📋 待办事项列表
============================================================

🔴 未完成 (2 项):
------------------------------------------------------------
⏳ [abc12345] 📝 明天下午3点开会
    📅 创建: 2026-03-21 20:30:00

⏳ [def67890] 🖼️  整理项目文档
    📅 创建: 2026-03-21 19:15:00
    🖼️  原图: /path/to/image.jpg

🟢 已完成 (1 项):
------------------------------------------------------------
✅ [ghi12345] 📝 购买 groceries
    📅 创建: 2026-03-20 10:00:00
    ✅ 完成: 2026-03-21 08:30:00
```

### 完成任务

```bash
python ~/.openclaw/workspace/scripts/todo_done.py --complete abc12345
```

### 删除待办

```bash
python ~/.openclaw/workspace/scripts/todo_done.py --delete abc12345
```

### 切换状态

```bash
python ~/.openclaw/workspace/scripts/todo_done.py --toggle abc12345
```

## 定时提醒

### 配置 Cron Job

编辑 crontab：
```bash
crontab -e
```

添加以下行（示例：每天 9:00、14:00、20:00 提醒）：

```bash
# 每天 9:00、14:00、20:00 发送待办提醒
0 9,14,20 * * * /usr/bin/python3 ~/.openclaw/workspace/scripts/todo_remind.py >> ~/.openclaw/workspace/todo_remind.log 2>&1
```

或每小时检查一次：
```bash
0 * * * * /usr/bin/python3 ~/.openclaw/workspace/scripts/todo_remind.py >> ~/.openclaw/workspace/todo_remind.log 2>&1
```

**注意：**
- `todo_remind.py` 会使用 OpenClaw 的 `message` 工具发送 Telegram 消息
- 确保 OpenClaw 环境已正确配置，且能访问 `message` 模块
- 如果不在 OpenClaw 环境中运行，脚本会输出到 stdout（模拟发送）

### 手动测试提醒

```bash
python ~/.openclaw/workspace/scripts/todo_remind.py
```

## 数据格式

`todos.json` 中的每条待办包含：

```json
{
  "id": "abc12345",           // 8位唯一标识
  "content": "任务内容",       // AI 提取后的任务文本
  "created_at": "2026-03-21 20:30:00",
  "status": "pending",        // pending | done
  "mode": "text"              // text | image
}
```

图片待办多一个字段：
```json
{
  "id": "xyz98765",
  "content": "整理会议记录",
  "created_at": "2026-03-21 19:15:00",
  "status": "pending",
  "mode": "image",
  "image_description": "原图路径: /path/to/note.jpg"
}
```

## AI 模型配置

系统通过环境变量 `MODEL_NAME` 控制使用的模型，无需修改代码。支持的模型取决于你的 OpenAI 兼容 API 服务。

常见配置示例：

```bash
# MiniMax
export MODEL_NAME="MiniMax-M2.7-highspeed"

# 其他提供商
export MODEL_NAME="gpt-4o-mini"
export MODEL_NAME="claude-3-haiku"
```

如果 `MODEL_NAME` 未设置，系统会默认使用 `MiniMax-M2.7-highspeed`。

## 故障排除

### 1. `ModuleNotFoundError: No module named 'openai'`
运行：`pip install openai`

### 2. AI 解析失败
检查 `OPENAI_API_KEY` 是否配置正确，以及 `OPENAI_BASE_URL` 是否可达。

### 3. message 工具不可用
确保 `todo_remind.py` 在 OpenClaw 环境中运行（直接通过 OpenClaw 调度）。如果独立运行，只会模拟输出。

### 4. 图片无法解析
确保图片路径正确，且格式为 jpg/png/gif/webp。图片大小不宜过大（建议 < 10MB）。

## 快速示例

```bash
# 1. 设置环境变量（示例）
export OPENAI_API_KEY="your-key"
export MODEL_NAME="MiniMax-M2.7-highspeed"

# 2. 添加几个待办
python ~/.openclaw/workspace/scripts/todo_add.py --text "周五前完成项目文档"
python ~/.openclaw/workspace/scripts/todo_add.py --text "预约牙医检查"
python ~/.openclaw/workspace/scripts/todo_add.py --image ~/Pictures/shopping-list.jpg

# 3. 查看所有待办
python ~/.openclaw/workspace/scripts/todo_list.py

# 4. 完成一个待办
python ~/.openclaw/workspace/scripts/todo_done.py --complete abc12345

# 5. 测试提醒
python ~/.openclaw/workspace/scripts/todo_remind.py
```

## 扩展建议

- 添加标签/分类功能
- 支持优先级（高/中/低）
- 支持截止日期和循环提醒
- Web 界面或 Telegram bot 前端
- 数据同步到云端

---

**开发完成于 2026-03-21**
