---
name: bid-monitor
description: >
  招标监控：自动抓取招投标网站，按关键词过滤新项目，飞书/Telegram推送。
  支持智能化/EPC总承包/中标公告，可独立配置关键词、数据源、推送目标。
metadata:
  {
    "openclaw":
      {
        "version": "1.0.0",
        "requires": { "bins": ["python"], "pip": ["requests", "beautifulsoup4"] },
      },
  }
---

# 国顺搜项目 — 招标监控

自动抓取招投标网站，按关键词筛选，推送新项目通知。

## 快速开始

1. 编辑 `config.json`：改 `keywords` 和 `push.target`
2. 运行：`python monitor.py`
3. 注册定时任务：在 OpenClaw 中说 "注册招标监控定时任务"

## 配置

`config.json` 关键字段：
- `keywords.core`：核心关键词，如 `["智能化", "信息化"]`
- `keywords.extend`：扩展词，如 `["安防", "弱电", "无人机"]`
- `keywords.exclude`：排除词，如 `["农业"]`
- `push.target`：飞书 open_id 或群聊 ID
- `scoring.threshold`：最低分，建议 `5`

## 特点

- 总承包项目检查正文是否含智能化内容
- 招标+中标公告均推送
- 推送含命中原因
- 支持飞书/Telegram/Webhook

## 依赖

`pip install requests beautifulsoup4`
