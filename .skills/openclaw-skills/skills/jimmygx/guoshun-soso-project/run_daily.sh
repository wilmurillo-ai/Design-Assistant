#!/bin/bash
# 招标监控 - 每日自动运行
cd /root/.openclaw/skills/bid-monitor
python3 monitor.py >> /var/log/bid-monitor.log 2>&1
