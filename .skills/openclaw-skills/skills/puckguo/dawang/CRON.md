# Cron 任务配置

## 心跳脚本
脚本位置: `/Users/godspeed/.openclaw/agents/dawang/cron/heartbeat.sh`

## 添加定时任务

运行 `crontab -e` 并添加:

```bash
# 大汪心跳 - 每30分钟检查一次
*/30 * * * * /Users/godspeed/.openclaw/agents/dawang/cron/heartbeat.sh

# 大汪每日汇报 - 每天9点、15点、21点
0 9,15,21 * * * /Users/godspeed/.openclaw/agents/dawang/cron/daily-report.sh
```

## 手动测试
```bash
/Users/godspeed/.openclaw/agents/dawang/cron/heartbeat.sh
```

## 日志查看
```bash
tail -f /Users/godspeed/.openclaw/agents/dawang/cron/heartbeat.log
```
