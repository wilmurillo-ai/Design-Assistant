---
name: monitor-alert
description: System health monitoring and alerting for Automaton. Checks cron execution, heartbeat rhythm, disk space, API limits, and memory health. Auto-alerts on anomalies.
author: Automaton
metadata:
  openclaw:
    emoji: 🚨
    tags:
      - monitoring
      - alerting
      - health-check
      - automation
---

# 🚨 Monitor & Alert System

System health monitoring and automated alerting for Automaton.

## Core Functions

### 1. Cron Execution Monitor
- Verify all cron jobs executed on schedule
- Detect missed or failed executions
- Alert if >2 consecutive failures

### 2. Heartbeat Rhythm Check
- Verify heartbeats running every 20 minutes
- Detect gaps in execution
- Alert if >40 minutes between heartbeats

### 3. Disk Space Monitor
- Check workspace disk usage
- Alert if >80% full
- Auto-cleanup suggestions

### 4. API Limit Tracker
- Monitor token usage vs budget
- Alert at 70%, 90%, 100% thresholds
- Suggest optimization strategies

### 5. Memory Health Check
- Verify memory files accessible
- Check for corruption
- Alert if daily log missing

## Usage

```bash
# Manual health check
node skills/monitor-alert/health-monitor.js

# Check specific component
node skills/monitor-alert/health-monitor.js --cron
node skills/monitor-alert/health-monitor.js --heartbeat
node skills/monitor-alert/health-monitor.js --disk
node skills/monitor-alert/health-monitor.js --token
node skills/monitor-alert/health-monitor.js --memory
```

## Alert Channels

| Severity | Channel | Response Time |
|----------|---------|---------------|
| Low | Log only | Next review |
| Medium | Daily summary | <24h |
| High | Immediate message | <1h |
| Critical | Immediate + loud alert | <5min |

## Configuration

Edit `skills/monitor-alert/config.json`:

```json
{
  "thresholds": {
    "disk": {
      "warn": 80,
      "critical": 95
    },
    "token": {
      "warn": 70,
      "critical": 90
    },
    "heartbeat": {
      "maxGap": 40
    },
    "cron": {
      "maxFailures": 2
    }
  },
  "alerts": {
    "channel": "webchat",
    "quietHours": {
      "start": "23:00",
      "end": "07:00"
    }
  }
}
```

## Files

```
monitor-alert/
├── SKILL.md              # This file
├── health-monitor.js     # Main monitoring script
├── config.json           # Configuration
├── alert-history.md      # Alert log
└── tests/
    └── health-check.js   # Integration tests
```

---

**Author**: Automaton  
**License**: MIT  
**Last updated**: 2026-03-20
