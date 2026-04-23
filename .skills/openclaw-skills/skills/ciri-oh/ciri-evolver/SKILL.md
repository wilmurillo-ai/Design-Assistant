---
name: evolver
description: "Skill self-evolution engine for OpenClaw agents. Based on GEP (Genome Evolution Protocol), scans workspace memory/ logs to detect error signals, matches Gene templates to generate evolution suggestions. Supports 4 strategies (balanced/innovate/harden/repair-only), Loop daemon, Review mode, Lifecycle management. 技能自进化引擎."
---

# Evolver - 技能自进化引擎 v3.0.6

> **Version**: 3.0.6
> **License**: GNU General Public License v3.0 (GPL-3.0)
> **Copyright**: 2026

---

## Open Source Attribution | 开源许可与归属

1. **Inspired by GEP (Genome Evolution Protocol)**
   GEP protocol proposed by [EvoMap](https://evomap.ai), this skill uses its concepts and architecture.

2. **Independent OpenClaw Implementation**
   Core code (`bin/evolve.js`) is independently developed for OpenClaw.

---

## ⚠️ Security Notes | 安全说明

**Memory Directory Scanning**
This skill scans `.md` files in the `memory/` directory to detect error signals.

**Do NOT store sensitive information in `memory/` directory**, including:
- API keys, tokens, passwords
- Private conversations or personal data
- Financial or health information
- Any credentials or secrets

**Protected Files**
To exclude specific files from scanning, add this line at the top of any `.md` file:

```markdown
<!-- evolver-ignore -->
```

Files starting with `# evolver-ignore` or containing `<!-- evolver-ignore -->` will be skipped.

**No External Network Calls**
This skill generates a text-based GEP prompt only. It does NOT make any external API calls,
send data to external services, or transmit credentials over the network.

Full license text: see [LICENSE](LICENSE).

---

## Quick Start | 快速开始

### Install

```bash
clawhub install ciri-evolver
```

### Run

```bash
# Single evolution scan
node skills/evolver/bin/evolve.js

# Test mode (no file writes)
node skills/evolver/bin/evolve.js --dry-run
```

### Background Daemon

```bash
# Start daemon (auto-runs every 4 hours)
node skills/evolver/bin/evolve.js start

# Check status
node skills/evolver/bin/evolve.js status

# Stop
node skills/evolver/bin/evolve.js stop
```

---

## Core Features | 核心功能

| Feature | Description |
|---------|-------------|
| Signal Detection | Scans memory/ logs for 10+ error patterns |
| Gene Matching | Matches signals to reusable strategy templates |
| Capsule Management | Stores validated fixes with diff + confidence |
| 4 Evolution Strategies | balanced / innovate / harden / repair-only |
| Loop Mode | Continuous background daemon |
| Review Mode | Pause for human confirmation |
| Lifecycle | start / stop / status / check |
| Bootstrap | Auto-creates Gene library on first run |

---

## Supported Error Signals | 支持的错误信号

| Signal | Meaning |
|--------|---------|
| TimeoutError | Network timeout |
| ECONNREFUSED | Connection refused |
| RateLimitError | Rate limit exceeded |
| AuthError | Authentication failed |
| ContextOverflow | Context memory exceeded |
| ModelFallback | Model routing fallback |
| GatewayTimeout | Gateway timeout |
| ParseError | Parse/syntax error |
| FileNotFound | File not found |
| DeprecationWarning | Deprecated API warning |

---

## Commands | 命令

| Command | Description |
|---------|-------------|
| `evolve.js` | Single evolution cycle |
| `evolve.js --dry-run` | Test mode (no file writes) |
| `evolve.js --loop` | **Continuous daemon mode** (setInterval, no child process) |
| `evolve.js --review` | Review mode (pause + human confirm) |
| `evolve.js --strategy=<name>` | Set evolution strategy |
| `evolve.js start` | Start daemon (use fork/cron to background) |
| `evolve.js stop` | Graceful stop (SIGTERM) |
| `evolve.js status` | Show running state |
| `evolve.js check` | Health check + auto-restart if stagnant |

### Background Running Guide | 后台运行指南

`--loop` 使用 setInterval 单进程守护，不会调用 shell 或创建子进程，
因此需要用户自行选择以下方式将进程持久化：

#### 方式一：child_process.fork()（独立进程保护）

**作用**：通过 Node.js fork 创建独立子进程，OpenClaw 崩溃或重启后进程依然存活。

```javascript
// 创建一个 launcher.js:
const { fork } = require('child_process');
const child = fork('./bin/evolve.js', ['--loop'], {
  detached: true,
  stdio: 'ignore',
});
child.unref();
// 进程在后台独立运行
```

或直接终端运行：
```bash
node -e "const{fork}=require('child_process');const c=fork('./bin/evolve.js',['--loop'],{detached:true,stdio:'ignore'});c.unref();"
```

#### 方式二：OpenClaw Cron 定时任务

**作用**：由 OpenClaw 管理定时触发，每次跑完单次扫描就结束，
不占后台进程资源。OpenClaw 关闭时任务自动停止。

在 OpenClaw 面板或 `openclaw.json` 中配置：

```json
{
  "cron": {
    "evolver": {
      "command": "node /path/to/evolve.js",
      "schedule": "0 */4 * * *",
      "enabled": true,
      "description": "Evolver skill evolution scan every 4 hours"
    }
  }
}
```

或者在终端直接添加 crontab：

```bash
crontab -e
# 添加：0 */4 * * * node /path/to/evolve.js >> /var/log/evolver.log 2>&1

# 查看日志
tail -f /var/log/evolver.log
```

#### 两种方式对比

| | child_process.fork | OpenClaw Cron |
|---|---|---|
| OpenClaw 崩溃后 | 进程继续跑 ✅ | 任务停止 |
| 日志完整性 | 持续写入 ✅ | 每次单独记录 |
| 资源占用 | 持续占用内存 | 跑完释放 ✅ |
| 管理方式 | 手动 kill | OpenClaw 控制 ✅ |
| 配置复杂度 | 需写 JS | 中等 |

### Strategies | 策略

| Strategy | Innovate | Optimize | Repair |
|----------|----------|---------|--------|
| `balanced` | 50% | 30% | 20% |
| `innovate` | 80% | 15% | 5% |
| `harden` | 20% | 40% | 40% |
| `repair-only` | 0% | 20% | 80% |

---

## File Structure | 文件结构

```
skills/evolver/
├── SKILL.md              # This file
├── LICENSE              # GPL-3.0 license
├── bin/
│   └── evolve.js        # Core script
└── assets/
    ├── GENES.md         # Gene library (editable)
    ├── CAPSULES.md      # Validated fixes
    └── EVOLUTION_EVENTS.md  # Evolution logs
```

---

## Example Output | 示例输出

```
Evolver - Skill Self-Evolution Engine v3.0.6

   Strategy: balanced
   Mode: SINGLE

Signals detected: ModelFallback
Genes: 5 total, 1 matched

================================================================================
           GEP Evolution Prompt
================================================================================

> Evolution ID: EVT-YYYYMMDD-XXXX
> Strategy: balanced (innovate:0.5 optimize:0.3 repair:0.2)

## Detected Signals
  - ModelFallback

## Matched Genes
  ### [20260416-004] repair
  Signals: ModelFallback
  Strategy:
    Fix model routing issues...

## Suggested Actions
  1. [repair] Fix model routing + log fallback chain

## Evolution Event Record
{ "type": "EvolutionEvent", ... }

Evolution event recorded.
```

---

## Troubleshooting | 故障排除

**Q: "No such file or directory"?**  
A: Run from correct workspace directory or use absolute path.

**Q: Background process gone?**  
A: Check with `evolve.js status`, restart with `evolve.js check`.

**Q: No signals detected?**  
A: Check `memory/` directory for logs containing error keywords.

**Q: No gene match?**  
A: Edit `assets/GENES.md` to add new gene templates.

---

## Architecture | 架构说明

### Daemon Loop Mode
`--loop` uses Node.js `setInterval` in a single process — **no child_process.spawn, no exec, no fork**.
This avoids T1140 (Inline Python code execution) and shell command execution false positives.

Use `child_process.fork` or OpenClaw cron to persist the process externally.

### Process Lifecycle
```
node evolve.js --loop     → foreground daemon (setInterval, blocks terminal)
node evolve.js start      → foreground daemon (user backgrounds with fork/cron)
node evolve.js stop       → SIGTERM graceful shutdown (via PID file)
node evolve.js check      → health check + restart if stagnant (>8h no run)
```

## Changelog | 版本历史

- **v3.0.6**: Added `<!-- evolver-ignore -->` file protection. Added Security Notes section in SKILL.md. GENES.md rewritten to remove external API references (pure code-level fixes only).
- **v3.0.4**: Reset CAPSULES.md to empty. Cleared Evolution ID in Example Output.
- **v3.0.3**: Removed runtime data from published package (evolver-state.json, evolver.pid, EVOLUTION_EVENTS.md). Reset to clean initial state.
- **v3.0.2**: Replaced `child_process.spawn` daemon with `setInterval` + `nohup`. Eliminates T1140 sandbox false positive. `--loop` is now single-process. Fixed nohup PID capture bug.
- **v3.0.1**: Fixed header comments, usage docs, version string (v2.0 -> v3.0)
- **v3.0.0**: Removed fetchSkill and autoIssue functions. Cleaner, safer, no exec/fetch.
- v2.0.3: Code optimizations (regex pre-compilation, path traversal protection)
- v2.0.0: Full feature set (Loop, Review, Lifecycle)
- v1.0.0: Initial release (Signal Detection + Gene Matching)
