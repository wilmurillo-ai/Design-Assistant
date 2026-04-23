---
name: server-doctor
description: 诊断并修复 AI Agent 服务器的 CPU/内存/进程异常问题。适用场景：服务器突然变慢、CPU占用100%、内存爆满、进程堆积、SSH卡顿、AI服务无响应。触发条件：提到服务器卡、CPU高、内存满、进程异常、服务器生病了、需要诊断、需要优化、需要急救。
---

# Server Doctor 🩺

> 服务器体检 + 问题修复 Skill。专治：CPU爆、内存漏、进程堆、响应慢。

---

## 一步体检（3秒出结果）

```bash
echo "=== 负载 ===" && uptime && echo "=== 内存 ===" && free -m && echo "=== 磁盘 ===" && df -h / && echo "=== 进程TOP5 ===" && ps aux --sort=-%cpu | head -6
```

## 常见病 + 处方

| 症状 | 原因 | 处方 |
|------|------|------|
| 大量 `curl-smart` 进程 | 外部脚本重试无上限 | 杀进程 + 修复调用方式 |
| 大量 `python3` 残留 | subprocess 超时没杀 | 找超时脚本，修复超时 |
| 内存逐渐升高 | 内存泄漏 | 定位泄漏进程并重启 |
| CPU 100% 但进程不明 | 挖矿/异常计算 | 检查 cron 和可疑任务 |
| SSH 卡顿 | 带宽跑满 | `iftop` 看流量 |

## 快速杀进程三板斧

```bash
# 1. 按名字杀（谨慎）
pkill -9 -f "进程名关键字"

# 2. 找 PID 杀
kill -9 $(pgrep -f "关键字")

# 3. 批量安全杀（先看再杀）
ps aux | grep "可疑关键字" | grep -v grep
kill -9 PID列表
```

## curl-smart 进程爆炸修复

**症状**：数百个 `curl-smart` 进程堆积，CPU 100%，服务器卡死

**修复方案**：

```bash
# 1. 立即止血
pkill -9 -f curl-smart

# 2. Python 脚本中替换 curl 调用为 urllib（永远不超过5秒）
import urllib.request
with urllib.request.urlopen("https://example.com", timeout=5) as resp:
    data = resp.read()
```

## 预防规范

1. **所有外部网络调用必须设超时**
   - `curl` → `--connect-timeout 3 --max-time 6`
   - Python urllib → `timeout=5`

2. **subprocess 永远加 timeout 参数**
   ```python
   subprocess.run(cmd, timeout=10)
   ```

3. **有重试逻辑的脚本必须加进程锁**
   ```bash
   LOCKFILE="/tmp/your-script.lock"
   if [ -f "$LOCKFILE" ]; then exit 0; fi
   trap "rm -f $LOCKFILE" EXIT
   touch "$LOCKFILE"
   ```

4. **cron 任务加进程数上限检查**
   ```bash
   count=$(pgrep -f "your-script" | wc -l)
   if [ "$count" -gt 3 ]; then echo "already running, skip"; exit 0; fi
   ```
