# Tozil for OpenClaw 🦞

**Production-ready cost tracking** — Track every AI dollar your OpenClaw agent spends. Per-model cost breakdown, daily budgets, and alerts — all in a secure web dashboard at [agents.tozil.dev](https://agents.tozil.dev).

> **🔒 Privacy First**: Tozil **never** accesses your conversations, prompts, or responses. Only cost metadata (model names, token counts, pricing) is collected. [Full privacy details below](#️-security--privacy-guarantees).

## ✨ What's New in v3.1.0

- **🔒 Enterprise Security**: TLS 1.2 enforcement, input validation, injection protection
- **⚡ Memory Optimized**: Batched processing prevents memory overflow on large logs
- **🎯 Zero Duplicates**: Byte offset tracking eliminates duplicate events
- **📊 Comprehensive Logging**: Detailed error tracking and performance monitoring
- **🛠️ Production Ready**: Retry logic, graceful failures, robust error handling
- **📦 Easy Install**: One-command setup with `install.sh`

## How It Works

OpenClaw records every AI call in session logs (`~/.openclaw/agents/main/sessions/*.jsonl`). This hook:

1. **Reads logs incrementally** using byte offset tracking (no file modification time issues)
2. **Processes in batches** to prevent memory overflow (configurable batch size)
3. **Validates and secures** all data before transmission
4. **Sends to Tozil API** with retry logic and comprehensive error handling

Works with **every provider** — Anthropic, OpenAI, Google, Mistral, DeepSeek, OpenRouter, and more. No SDK patching or npm dependencies needed.

## 🚀 Quick Install

```bash
# Clone the repo
git clone https://github.com/tozil-dev/tozil-openclaw.git
cd tozil-openclaw

# Run the installer
./install.sh

# Set your API key (get one at https://agents.tozil.dev)
export TOZIL_API_KEY=tz_xxxxxxxxxxxxx

# Enable the hook
openclaw hooks enable tozil
openclaw gateway restart
```

> **📌 Important**: This installs as an OpenClaw **hook** (in `~/.openclaw/hooks/tozil/`), not a **skill** (in `~/.openclaw/workspace/skills/`). Hooks run automatically in the background, while skills are manually invoked. This is the correct approach for cost tracking.

## Manual Install

```bash
# Create hook directory
mkdir -p ~/.openclaw/hooks/tozil

# Copy files
cp handler.js sync_costs.js ~/.openclaw/hooks/tozil/

# Set API key
export TOZIL_API_KEY=tz_xxxxxxxxxxxxx

# Enable
openclaw hooks enable tozil
openclaw gateway restart
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `TOZIL_API_KEY` | (required) | Your Tozil API key (get at agents.tozil.dev) |
| `TOZIL_BASE_URL` | `https://agents.tozil.dev` | API base URL (HTTPS only) |
| `TOZIL_SYNC_INTERVAL_MS` | `3600000` (1 hour) | How often to sync |
| `TOZIL_BATCH_SIZE` | `100` | Events per batch (memory optimization) |
| `OPENCLAW_SESSIONS_DIR` | `~/.openclaw/agents/main/sessions` | Session logs directory ⚠️ **Note**: Only tracks main agent by default. For sub-agents, set this to `~/.openclaw/agents/*/sessions` or specific agent directory. |
| `TOZIL_DEBUG` | (unset) | Set to `1` for verbose logging |

## What It Captures

From each AI call in the session logs:

| Field | Description | Privacy |
|-------|-------------|---------|
| `model` | Which model was used | ✅ Safe |
| `provider` | anthropic, openai, google, etc. | ✅ Safe |
| `input_tokens`, `output_tokens` | Token counts | ✅ Safe |
| `cache_read_tokens`, `cache_write_tokens` | Cache usage | ✅ Safe |
| `total_cost_usd` | Provider-calculated cost | ✅ Safe |
| `timestamp` | When the call was made | ✅ Safe |
| `session_id` | Session identifier | ✅ Safe |

**🔒 Privacy**: Does **not** capture prompts, responses, or any content. Only metadata and costs.

## 🛡️ Security & Privacy Guarantees

### ✅ What We NEVER Collect
- **❌ No prompts or inputs** - Your conversations stay private
- **❌ No AI responses** - What AI says to you stays between you
- **❌ No message content** - Zero access to actual conversation data  
- **❌ No file contents** - We don't read files you work with
- **❌ No personal data** - Names, emails, or user info from conversations
- **❌ No sensitive data** - API keys, passwords, or credentials are never touched

### ✅ What We Collect (Metadata Only)
- **✓ Model name** - Which AI model was used (e.g., "claude-3-sonnet")
- **✓ Token counts** - How many tokens were processed (input/output/cache)
- **✓ Costs** - What the provider charged (public pricing data)
- **✓ Timestamps** - When calls were made  
- **✓ Provider** - Which service (anthropic, openai, google, etc.)
- **✓ Session ID** - Anonymous session identifier (no personal info)

### 🔒 How We Protect Your Data
- **End-to-End HTTPS** - All data transmission uses TLS 1.2+
- **No Content Parsing** - Script only reads cost/usage fields from logs
- **Local Processing** - Data filtering happens on your machine, not ours
- **Minimal Surface** - Only essential cost metadata leaves your system
- **Open Source** - You can audit exactly what data is collected

**🔍 Want to verify?** Check the source code - the `extractEvents()` function in `sync_costs.js` shows exactly what fields are extracted.

## Manual Sync

```bash
# Test the sync manually
cd ~/.openclaw/hooks/tozil && TOZIL_API_KEY=tz_xxx node sync_costs.js

# With debug output  
cd ~/.openclaw/hooks/tozil && TOZIL_DEBUG=1 TOZIL_API_KEY=tz_xxx node sync_costs.js
```

## Troubleshooting

### Check Logs

```bash
# Handler logs (JavaScript errors)
tail -f ~/.openclaw/logs/tozil-handler.log

# Sync logs (JavaScript sync errors)
tail -f ~/.openclaw/logs/tozil-sync.log

# OpenClaw gateway logs
openclaw logs --limit 50 | grep tozil
```

### Common Issues

**"Invalid TOZIL_API_KEY format"**
- API key must start with `tz_` and be at least 16 characters
- Get a valid key at https://agents.tozil.dev

**"TOZIL_BASE_URL must use HTTPS"**
- Only HTTPS URLs are allowed for security
- Default: `https://agents.tozil.dev`

**"Sessions dir not found"**
- Check that OpenClaw is installed and has run at least once
- Verify path: `ls ~/.openclaw/agents/main/sessions/`

**"Module not found"**
- Ensure Node.js 16+ is installed: `node --version`

### Performance Monitoring

The hook logs sync performance:
```
[2026-03-16 21:45:30] Sync completed successfully in 1247ms
[2026-03-16 21:45:30] Synced: 142 accepted, 0 skipped
```

### Limitations & Scope

- **Main Agent Only**: Default configuration tracks only the main OpenClaw agent (`~/.openclaw/agents/main/sessions`). Sub-agents or isolated sessions in other directories require custom `OPENCLAW_SESSIONS_DIR` configuration.
- **Log-Based Approach**: Requires OpenClaw session logs to exist. If logs are disabled or corrupted, tracking won't work.
- **Network Dependency**: Requires internet access to sync with Tozil API. Offline periods will queue data for next sync.

## Architecture

### Security Features
- **TLS 1.2+ only** - Rejects insecure connections
- **Input validation** - Regex validation on API keys and URLs
- **Injection protection** - Native JSON parsing prevents code injection
- **Path traversal protection** - Validates session IDs

### Reliability Features
- **Byte offset tracking** - Never misses or duplicates events
- **Atomic updates** - Offset files updated only after successful sync
- **Retry logic** - 2 retries with 3-second delays
- **Graceful degradation** - Never breaks OpenClaw on errors
- **Memory bounded** - Configurable batch processing

### Monitoring
- **Structured logging** - Timestamps, levels, detailed error messages
- **Performance tracking** - Sync timing and event counts
- **Debug mode** - Verbose output for troubleshooting

## Pricing

- **Free**: $0/month — tracks up to $50/month in AI spend
  - **What happens when you exceed $50?** Tracking continues normally, dashboard shows "Upgrade Suggested" banner. All data and features remain available. No interruption to service.
- **Pro**: $9/month — unlimited tracking + budget alerts + advanced analytics

**Need higher limits?** Enterprise plans available at [agents.tozil.dev/pricing](https://agents.tozil.dev/pricing)

Get started at **https://agents.tozil.dev**

## License

MIT — See [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Test with `TOZIL_DEBUG=1 node sync_costs.js`
5. Submit a pull request

## Support

- **Documentation**: https://docs.tozil.dev
- **Issues**: https://github.com/tozil-dev/tozil-openclaw/issues
- **Email**: hello@tozil.dev