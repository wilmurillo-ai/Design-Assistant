---
name: feishu-card
description: >
  Send rich interactive card messages to Feishu via Open API.
  Activate when: user wants to send a Feishu card, interactive message, rich notification,
  formatted alert, news digest card, data dashboard with charts, or any styled message
  beyond plain text in Feishu. Supports: markdown cards, raw card JSON, template-based cards
  (news_digest, report, alert, data_dashboard), and chart components (line/bar/pie).
  NOT for: plain text messages, reading messages, or managing Feishu docs/wiki.
---

# Feishu Card Message Skill

Send rich interactive card messages through Feishu Open API via `scripts/feishu_card.py`.

## Prerequisites

- `FEISHU_APP_ID` and `FEISHU_APP_SECRET` env vars (or `--app-id`/`--app-secret` flags)
- Feishu app must have `im:message:send_as_bot` permission
- Target user/chat must be reachable by the bot

## Quick Start

```bash
SKILL_DIR=~/.openclaw/skills/feishu-card

# Simple markdown card
python3 $SKILL_DIR/scripts/feishu_card.py \
  --to <receive_id> --type open_id \
  --markdown "**Hello!** This is a card." \
  --title "Greeting" --color blue

# Raw card JSON file
python3 $SKILL_DIR/scripts/feishu_card.py \
  --to <receive_id> --type chat_id \
  --card /path/to/card.json

# Template-based card
python3 $SKILL_DIR/scripts/feishu_card.py \
  --to <receive_id> --type open_id \
  --template news_digest --data /path/to/news.json
```

## Three Modes

### 1. Markdown Mode (`--markdown`)
Wrap markdown text into a card. Combine with `--title` and `--color`.

Colors: `blue` `wathet` `turquoise` `green` `yellow` `orange` `red` `carmine` `violet` `purple` `indigo` `grey` `default`

### 2. Raw Card Mode (`--card`)
Pass a pre-built card JSON file (schema 2.0). Full control over all components.

### 3. Template Mode (`--template` + `--data`)
Use bundled templates with a data JSON file.

| Template | Use Case | Key Data Fields |
|----------|----------|----------------|
| `news_digest` | Multi-item news | `title`, `footer`, `items[]` (title, summary, source, time, url) |
| `report` | Structured report | `title`, `summary`, `conclusion`, `footer`, `items[]` (title, content) |
| `alert` | Alert/notification | `title`, `level`, `time`, `detail`, `action`, `footer` |
| `data_dashboard` | Data dashboard with chart | `title`, `metric_1..3`, `chart_type`, `chart_title`, `chart_data`, `x_field`, `y_field`, `series_field`, `details`, `footer` |

## Chart Support

Feishu Schema 2.0 supports `chart` components (VChart-based). Three chart types: **line**, **bar**, **pie**.

## Image Support

Upload and embed images in cards. Supports local files and URLs.

```bash
# Append image to any card mode
python3 $SKILL_DIR/scripts/feishu_card.py \
  --to <id> --type open_id \
  --markdown "Check this out:" --title "Photo" \
  --image /path/to/photo.png

# URL also works (auto-downloads then uploads to Feishu)
python3 $SKILL_DIR/scripts/feishu_card.py \
  --to <id> --type open_id \
  --markdown "News image:" \
  --image "https://example.com/image.jpg"
```

### Programmatic image upload

```python
from feishu_card import get_tenant_token, upload_image, build_image_element

token = get_tenant_token(app_id, app_secret)

# From local file or URL
img_key = upload_image(token, "/path/to/image.png")
# or: img_key = upload_image(token, "https://example.com/photo.jpg")

# Build card element
img_el = build_image_element(img_key, alt_text="描述", mode="fit_horizontal")
# Insert img_el into card["body"]["elements"]
```

**Note:** Feishu only accepts real image files (PNG/JPG/GIF/BMP). SVG and HTML pages disguised as images will fail with error `234011`.

### Programmatic chart building

```python
import sys; sys.path.insert(0, "~/.openclaw/skills/feishu-card/scripts")
from feishu_card import build_chart_element, get_tenant_token, send_card

chart = build_chart_element(
    chart_type="line",
    data_values=[
        {"date": "1月", "value": 100},
        {"date": "2月", "value": 150},
    ],
    title="月度趋势",
    x_field="date",
    y_field="value",
)

card = {
    "schema": "2.0",
    "config": {"wide_screen_mode": True},
    "header": {"title": {"tag": "plain_text", "content": "📊 报表"}, "template": "blue"},
    "body": {"elements": [chart]},
}

token = get_tenant_token(app_id, app_secret)
send_card(token, receive_id, "open_id", card)
```

For chart JSON structure details, see `references/card-components.md` → Chart 图表。

## Additional Options

- `--reply-to <message_id>` — Reply to an existing message
- `--type open_id|chat_id` — Receiver ID type

## Programmatic Use

```python
from feishu_card import get_tenant_token, build_card_from_markdown, send_card

token = get_tenant_token(app_id, app_secret)
card = build_card_from_markdown("**Hello**", title="Test", color="blue")
send_card(token, receive_id, "open_id", card)
```

### Building complex cards programmatically

```python
import json
from feishu_card import get_tenant_token, send_card, build_chart_element

token = get_tenant_token(app_id, app_secret)

card = {
    "schema": "2.0",
    "config": {"wide_screen_mode": True},
    "header": {
        "title": {"tag": "plain_text", "content": "周报"},
        "template": "purple",
    },
    "body": {
        "elements": [
            {"tag": "markdown", "content": "**本周总结**\n完成了 3 个里程碑"},
            {"tag": "hr"},
            {
                "tag": "column_set",
                "flex_mode": "none",
                "columns": [
                    {"tag": "column", "width": "weighted", "weight": 1,
                     "elements": [{"tag": "markdown", "content": "**完成率**\n<font color='green'>92%</font>"}]},
                    {"tag": "column", "width": "weighted", "weight": 1,
                     "elements": [{"tag": "markdown", "content": "**延期项**\n<font color='red'>2</font>"}]},
                ],
            },
            {"tag": "hr"},
            build_chart_element("bar", [
                {"task": "需求", "count": 15, "type": "完成"},
                {"task": "需求", "count": 3, "type": "进行中"},
                {"task": "Bug", "count": 8, "type": "完成"},
                {"task": "Bug", "count": 1, "type": "进行中"},
            ], title="任务统计", x_field="task", y_field="count", series_field="type", stack=True),
            {"tag": "hr"},
            {
                "tag": "collapsible_panel",
                "expanded": False,
                "header": {"title": {"tag": "plain_text", "content": "查看详情"}},
                "elements": [{"tag": "markdown", "content": "详细内容..."}],
            },
            {"tag": "hr"},
            {"tag": "markdown", "content": "<font color='grey'>自动生成 | 周报系统</font>"},
        ]
    },
}

send_card(token, receive_id, "open_id", card)
```

## ⚠️ Schema 2.0 陷阱（实测踩坑记录）

这些是实际发送卡片时遇到的兼容性问题，会导致 `200861 unsupported tag` 错误：

| 陷阱 | 说明 | 解决方案 |
|------|------|---------|
| `action` 标签已废弃 | 按钮容器在 Schema 2.0 中不可用 | 用 markdown `[文字](url)` 链接替代 |
| `note` 标签已废弃 | 底部备注标签不可用 | 用 `markdown` + `<font color='grey'>...</font>` |
| `collapsible_panel.vertical_spacing` | 不接受 `"default"` 字符串值 | **省略此属性**，或用 `"8px"` 等像素值 |

## 已实测可用组件

| 组件 | 状态 | 说明 |
|------|------|------|
| `markdown` | ✅ 已验证 | 支持粗体/链接/列表/font color |
| `hr` | ✅ 已验证 | 分割线 |
| `column_set` | ✅ 已验证 | 多列布局 |
| `collapsible_panel` | ✅ 已验证 | 折叠面板（注意 vertical_spacing 陷阱） |
| `img` | ✅ 已验证 | 图片（upload_image 上传后嵌入，支持本地文件和URL） |
| `chart` | ✅ 已验证 | VChart 图表（line/bar/pie） |

完整组件参考：`references/card-components.md`
