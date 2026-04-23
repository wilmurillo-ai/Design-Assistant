---
name: stock-announcement
version: 1.1.0
description: 每日股票投资组合公告工具，集成Gmail邮件报告和Sonos语音播报功能。
tags: ['stocks', 'finance', 'gmail', 'sonos', 'automation']
author: OpenClaw Assistant
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires": { "bins": ["sonos", "python3"], "pip": ["yfinance", "pandas", "python-dotenv", "google-api-python-client"] },
        "install":
          [
            {
              "id": "python-deps",
              "kind": "pip",
              "packages": ["yfinance", "pandas", "python-dotenv", "google-api-python-client", "google-auth-httplib2", "google-auth-oauthlib"],
              "label": "Install Python dependencies"
            },
            {
              "id": "sonoscli",
              "kind": "go",
              "module": "github.com/steipete/sonoscli/cmd/sonos@latest",
              "bins": ["sonos"],
              "label": "Install sonoscli"
            }
          ],
      },
  }
---

# Stock Announcement Skill v1.1.0

## 功能说明

每日自动股票投资组合公告工具，包含市场分析、邮件报告和Sonos语音播报功能。

## 主要功能

- 📊 投资组合实时绩效分析（基于yfinance）
- 📧 通过Gmail API发送HTML格式邮件报告
- 🔊 Sonos音箱语音播报当日收益
- 📈 显示总市值、当日盈亏、最佳/最差表现股票

## v1.1.0 更新日志

### 🔧 修复内容

1. **邮件发送异常修复**
   - 解决Gmail凭证路径解析问题
   - 添加多路径凭证自动扫描机制
   - 内置3次重试机制（指数退避算法）

2. **Sonos播报异常修复**
   - 修复TTS命令行参数格式
   - 添加音箱发现预检查
   - 3次自动重试 + 超时保护（30秒）
   - 优化播报文本格式，去除多余空白

3. **稳定性增强**
   - 新增结构化日志系统
   - 所有外部调用添加超时保护
   - 改进工作区路径自动检测
   - 完善异常捕获和错误信息输出

## 使用方法

```bash
# 运行公告脚本
python3 daily_stock_announcement.py
```

## 配置说明

1. 将Gmail OAuth token存放于 `config/token.json`
2. 设置环境变量：
   - `SONOS_SPEAKER`: Sonos音箱名称 (默认: "Living Room")
   - `RECIPIENT_EMAIL`: 报告接收邮箱
