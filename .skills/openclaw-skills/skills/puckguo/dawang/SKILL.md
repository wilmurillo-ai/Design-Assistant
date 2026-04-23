---
name: dawang-workspace
description: Dawang Workspace配置和技能索引
---

# Dawang Workspace Skills

## Workspace概述

Dawang是执行Agent，负责代码编写、脚本开发、技术实现。

## 本Workspace Skills

### vtrain-food-analyzer
V-Train饮食数据分析器
- 位置: `~/.openclaw/workspaces/dawang/skills/vtrain-food-analyzer/`
- 功能: 获取用户饮食记录，生成可视化报告

## 全局Skills引用

以下Skills在dawang中常用：

| Skill | 描述 | 位置 |
|-------|------|------|
| `dianping-screenshot` | 大众点评截图 | global |
| `feishu-send-image` | 飞书发图 | global |
| `web-scraper` | 网页抓取 | global |

## Chrome调试模式

大众点评等网站截图需要Chrome调试模式：

```bash
# 启动调试模式
open -a "Google Chrome" --args --remote-debugging-port=9222
```

端口: 9222
