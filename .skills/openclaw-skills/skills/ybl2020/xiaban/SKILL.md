# 虾办 - xiaban

私人待办事项管理 Skill，支持文字/图片 AI 解析，定时提醒。

## 功能

- **文字解析**：发送文字，自动提取待办任务
- **图片解析**：发送图片，自动识别待办清单
- **查询**：查看所有待办（未完成/已完成分开展示）
- **完成/删除**：标记任务完成或删除
- **定时提醒**：每小时自动推送未完成事项

## 文件结构

```
xiaban/
├── SKILL.md
├── todos.json              # 数据存储
├── scripts/
│   ├── todo_add.py        # 添加待办
│   ├── todo_list.py       # 查询待办
│   ├── todo_done.py       # 标记完成/删除
│   └── todo_remind.py     # 定时提醒
└── README.md
```

## 环境配置

Gateway 需启用 OpenAI 兼容接口（默认已开启）：
```json
gateway.http.endpoints.chatCompletions.enabled: true
```

## 使用方式

### 添加待办（文字）
发送文字给老虾，自动解析并存入 `todos.json`

### 添加待办（图片）
发送图片给老虾，自动识别图内待办清单

### 查询
- `我的待办` — 查看所有待办
- `完成了xxx` — 标记完成
- `删除xxx` — 删除待办

### 定时提醒
每小时 cron 自动扫描 `todos.json` 并推送到 Telegram

## 版本

v0.0.1
