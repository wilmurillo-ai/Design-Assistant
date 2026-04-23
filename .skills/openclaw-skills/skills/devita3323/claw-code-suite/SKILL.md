---
name: claw-code-suite
version: 1.0.0
description: Complete integration of Claw Code harness engineering project with OpenClaw. Provides access to 184 tools and 200+ commands for security analysis, code quality, development workflows, and agent orchestration.
homepage: https://github.com/instructkr/claw-code
metadata:
  {
    "openclaw":
      {
        "emoji": "🦞",
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "verify-python",
              "kind": "exec",
              "command": "python3 --version",
              "label": "Verify Python 3 is available",
            },
          ],
      },
  }
---

# Claw Code Suite

Complete integration of the Claw Code harness engineering project with OpenClaw. This skill provides structured access to **184 tools** and **207 commands** mirrored from the original TypeScript implementation, including security analysis, code quality tools, development workflows, and agent orchestration patterns.

## Quick Start

Once installed, the skill exposes several high-level commands:

```bash
# Get system overview
./run.sh summary

# List available tools (first 10)
./run.sh tools --limit 10

# List available commands (first 10)
./run.sh commands --limit 10

# Route a prompt to find matching tools/commands
./run.sh route --prompt "analyze bash script for security issues" --limit 5

# Execute a specific tool (e.g., bashSecurity)
./run.sh exec-tool --name bashSecurity --payload "#!/bin/bash\necho test"

# Execute a specific command
./run.sh exec-command --name advisor --prompt "review this code"
```

## Available Capabilities

### Tool Categories

- **Security Analysis**: `bashSecurity`, `powershellSecurity`, etc.
- **Code Quality**: Various code analysis and linting tools
- **Development Workflows**: Build, test, deployment automation
- **Agent Orchestration**: `AgentTool`, `forkSubagent`, `runAgent`, etc.
- **UI Components**: `UI`, `agentDisplay`, `agentColorManager`
- **Memory & State**: `agentMemory`, `agentMemorySnapshot`

### Command Categories

- **Execution Commands**: `exec-command`, `exec-tool`
- **Routing & Discovery**: `route`, `show-command`, `show-tool`
- **Session Management**: `load-session`, `flush-transcript`
- **Runtime Modes**: `remote-mode`, `ssh-mode`, `teleport-mode`
- **Analysis & Reporting**: `summary`, `manifest`, `parity-audit`

## How It Works

1. **Harness Wrapper**: The `claw_harness.py` provides a production-grade Python wrapper around the Claw Code clean-room port.
2. **Enhanced Harness**: `claw_harness_enhanced.py` supports expanded command set with positional arguments.
3. **Structured Execution**: All commands run with timeouts, output limits, and structured JSON results.
4. **Event Logging**: All invocations are logged for audit and Nexus integration.
5. **Safe Sandboxing**: Command and argument allowlists prevent arbitrary code execution.

## Security Model

**This skill does NOT hijack or remotely control AI agents.** It is a **local utility library** with strict security controls:

### ✅ What It Can Do
- Execute **allowlisted commands only** (20+ predefined commands like `summary`, `tools`, `route`, `exec-tool`)
- Run Python subprocesses **locally** with timeouts (default 120s) and output limits (25k chars)
- Perform **static analysis** (e.g., `bashSecurity`, `powershellSecurity` inspect code, don't execute it)
- Route prompts to find relevant tools/commands
- Log all invocations locally for audit

### ❌ What It Cannot Do
- **No arbitrary code execution** – only commands in `COMMAND_DEFS` are allowed
- **No network calls** (unless the underlying Claw Code tools make them – most are analysis tools)
- **No persistence** – results are returned via JSON, no background daemons
- **No privilege escalation** – runs with the same permissions as the OpenClaw agent
- **No auto‑execution** – the skill must be explicitly enabled and called by an agent

### 🔐 Security Features
- **Command allowlist**: Only 20+ specific commands are exposed (see `COMMAND_DEFS` in harness)
- **Argument validation**: All flags are validated against per‑command allowlists
- **Timeout enforcement**: Default 120‑second timeout per command
- **Output truncation**: Output limited to 25,000 characters to prevent memory exhaustion
- **No shell=True**: All subprocesses use `shell=False` with explicit argument lists
- **Structured errors**: All failures return structured JSON, no raw tracebacks

### 🛡️ User Control
- The skill **must be explicitly installed and enabled** by the user
- The OpenClaw agent **must have `exec` permission** to use it
- Users can inspect the entire source code (Python, not compiled)
- All invocations are logged to `claw_harness_events.jsonl` for review

### 🔍 Transparency
- **Source available**: All Python code is in the skill directory
- **No obfuscation**: No minified/compiled code
- **No telemetry**: Event logging is local-only (optional)
- **No dependencies**: Only requires Python 3 (no external packages)

Think of this as installing a **local library of code analysis utilities** – similar to installing `shellcheck` or `bandit` but with a unified OpenClaw interface.

## Integration Examples

### Security Analysis
```bash
# Analyze a bash script
./run.sh exec-tool --name bashSecurity --payload "$(cat script.sh)"

# Analyze PowerShell
./run.sh exec-tool --name powershellSecurity --payload "$(cat script.ps1)"
```

### Code Review
```bash
# Route a code review request
./run.sh route --prompt "review this Python function for bugs" --limit 5

# Use the advisor command
./run.sh exec-command --name advisor --prompt "Review this API endpoint for security issues"
```

### Agent Orchestration
```bash
# Start an agent session
./run.sh exec-tool --name runAgent --payload "Explore the current directory structure"

# Fork a subagent for specific task
./run.sh exec-tool --name forkSubagent --payload "Write unit tests for module X"
```

## Configuration

Environment variables (optional):

- `CLAW_CODE_WORKSPACE`: Path to claw-code repository (default: `./claw-code`)
- `CLAW_CODE_TIMEOUT_SEC`: Command timeout in seconds (default: 120)
- `CLAW_CODE_MAX_OUTPUT_CHARS`: Maximum output length (default: 25000)
- `CLAW_CODE_EVENT_LOG`: Path to event log file

## Skill Structure

```
claw-code-suite/
├── SKILL.md                    # This file
├── run.sh                      # Main entry point
├── claw_harness.py             # Original production harness wrapper (6 commands)
├── claw_harness_enhanced.py    # Enhanced harness with full command set
├── claw_wrapper.py             # Python adapter
├── scripts/
│   └── claw_wrapper.py         # Core Python wrapper
├── claw-code/                  # Claw Code Python port (full)
│   ├── src/                    # Python source code
│   ├── tests/                  # Test suite
│   └── telemetry/              # Event logging
├── capability_index.json       # Tool/command inventory
└── package.json                # Node.js metadata
```

## Advanced Usage

### Direct Python API
```python
import sys
sys.path.append(".")
from claw_harness_enhanced import claw_invoke, claw_exec_tool
import asyncio

async def main():
    result = await claw_exec_tool("bashSecurity", "#!/bin/bash\necho test")
    print(result)

asyncio.run(main())
```

### Using Enhanced Harness Directly
```bash
python3 -c "
import asyncio
from claw_harness_enhanced import claw_route
result = asyncio.run(claw_route('security audit', 3))
print(result)
"
```

## Development

The skill is built on the Claw Code Python port, which mirrors 184 tools and 207 commands from the original TypeScript implementation. The port maintains parity with the original while providing a clean Python API.

To extend or modify:
1. Edit `claw_harness_enhanced.py` to expose additional commands from `src/main.py`
2. Update `COMMAND_DEFS` in the harness
3. Test with `./run.sh --summary` to verify functionality

## License

Claw Code is licensed under its original terms. This integration skill is provided as-is for OpenClaw users.

## Support

- GitHub: https://github.com/instructkr/claw-code
- OpenClaw Discord: https://discord.com/invite/clawd
- ClawHub: https://clawhub.ai