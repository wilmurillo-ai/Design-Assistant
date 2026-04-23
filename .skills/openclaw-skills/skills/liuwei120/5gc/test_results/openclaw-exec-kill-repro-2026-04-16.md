# OpenClaw exec 长任务异常复现报告

日期：2026-04-16
环境：Ubuntu 24.04 / OpenClaw 2026.4.14 / control-ui(webchat)
历史对比：旧版本 3.23-2 未出现该问题

## 结论

当前版本通过 control-ui / webchat 发起的 `exec` 长任务存在异常终止问题，表现为任务在约 5-10 秒或稍后被 `SIGTERM` / `SIGKILL`，与文档中 `tools.exec.timeoutSec` 默认 1800 秒的预期不符。

该问题已通过最小复现证明与业务脚本无关：纯 shell / 纯 Python 长任务同样会被提前终止。

## 排查结论

已排除：
- OOM / 内存不足
- cgroup memory 限制
- systemd MemoryMax/CPUQuota 限制
- 5GC 业务脚本本身导致
- Playwright 特有问题
- 站点可达性问题

已确认：
- 当前 `exec` 任务作为 `openclaw-gateway` 子进程运行，位于同一 control-group
- 当前版本这条 control-ui/webchat → gateway → exec 的执行链路，对中长任务存在异常回收/终止行为

## 最小复现

### 复现 1：纯 shell 长任务
```bash
#!/usr/bin/env bash
set -euo pipefail
for i in $(seq 1 24); do
  echo "tick:$i $(date '+%F %T')"
  sleep 5
done
echo done
```

实际结果：
- 输出 `tick:1 ...`
- 随后被 `SIGTERM`

### 复现 2：纯 Python 长任务
```bash
python3 - <<'PY'
import time
for i in range(1,61):
    print(f'pytick:{i}', flush=True)
    time.sleep(1)
print('done', flush=True)
PY
```

实际结果：
- 输出到 `pytick:9/10`
- 随后被 `SIGKILL`

## 关联公开 issue

- openclaw/openclaw#66359
  - 标题：`[Bug] exec commands receive SIGKILL frequently (every conversation turn)`
  - 版本：2026.4.12
  - 症状与本地现象高度相似

- openclaw/openclaw#66748 / #66749
  - 与 subagent background exec / heartbeat wake 相关
  - 说明 2026.4.x 期间 background exec 链路存在活跃改动

## 当前可行绕过方案

对于长任务（例如 Playwright 批量回归、批量编辑、长时间自动化）：
- 不要继续通过当前聊天 exec 路径运行
- 改用 detached 执行方式（nohup / setsid / systemd-run / 独立 shell）
- 或等待上游修复后再回归 chat exec 路径

## 建议

1. 短期：用 detached runner 恢复长任务可用性
2. 中期：结合 #66359 向上游补充 Linux/control-ui 的最小复现
3. 如需稳定生产使用，可考虑临时回退到 3.23-2 或避开当前 exec 链路
