# Settings Guide — OpenClaw Optimizer v2

## Context Pruning

Gradually removes old tool results instead of waiting for full compaction.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | `"cache-ttl"` | Results expire after TTL |
| `ttl` | string | Time before tool results become prunable (e.g. `"30m"`, `"1h"`) |
| `keepLastAssistants` | number | Always keep N most recent assistant messages intact |
| `softTrimRatio` | 0-1 | Context fill ratio that triggers soft trimming |
| `hardClearRatio` | 0-1 | Context fill ratio that triggers hard clearing |
| `minPrunableToolChars` | number | Only prune tool results larger than this |
| `softTrim.maxChars` | number | Max chars to keep per tool result during soft trim |
| `softTrim.headChars` | number | Chars to keep from start of result |
| `softTrim.tailChars` | number | Chars to keep from end of result |
| `hardClear.enabled` | boolean | Enable complete removal of expired results |
| `hardClear.placeholder` | string | Text replacing removed results |

### Flow

```
0-softTrimRatio: Nothing happens
softTrimRatio-hardClearRatio: Expired tool results trimmed (head+tail kept)
hardClearRatio+: Expired tool results fully removed (placeholder only)
```

## Compaction

Controls how the conversation is compressed when context fills up.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | `"safeguard"` | Auto-compact when needed |
| `reserveTokensFloor` | number | Compact when fewer than N tokens remain free |
| `maxHistoryShare` | 0-1 | After compaction, keep this fraction for recent history |
| `memoryFlush.enabled` | boolean | Save context to memory files before compacting |
| `memoryFlush.softThresholdTokens` | number | Start preventive flushes at this token count |

### Flow

```
softThresholdTokens reached: Preventive memory flush (saves to memory/YYYY-MM-DD.md)
reserveTokensFloor reached: Full compaction
  1. Final memory flush
  2. Summarize old history
  3. Keep maxHistoryShare of space for recent messages
```

## Session Maintenance

Automatic cleanup of old/unused sessions.

| Parameter | Type | Description |
|-----------|------|-------------|
| `mode` | `"enforce"` | Active cleanup enabled |
| `pruneDays` | number | Delete sessions inactive for N days |
| `maxEntries` | number | Max entries per session file |

## Timeout

| Parameter | Type | Description |
|-----------|------|-------------|
| `timeoutSeconds` | number | Max seconds per agent turn (default varies) |

## Heartbeat (NEW in v2)

| Parameter | Type | Description |
|-----------|------|-------------|
| `heartbeat.model` | string | Model used for heartbeat checks. Use a cheap model like Haiku to save tokens |

**Why:** Heartbeats run every hour 24/7. Using Opus for a simple "anything to do?" check wastes tokens. Haiku handles it perfectly at ~10x lower cost.

## Bootstrap (NEW in v2)

| Parameter | Type | Description |
|-----------|------|-------------|
| `bootstrapMaxChars` | number | Max chars per workspace file injected into system prompt |

**Why:** Large MEMORY.md, AGENTS.md, etc. get truncated at this limit. Lower = smaller system prompt = fewer tokens per turn. 15K is a good balance.

## Web Fetch Cap (NEW in v2)

| Parameter | Type | Description |
|-----------|------|-------------|
| `tools.web.fetch.maxChars` | number | Max chars returned by web_fetch tool |

**Why:** Without a cap, web_fetch can return 100K+ chars from large pages, flooding the context window. 30K is enough for most pages while preventing context pollution.

## Sub-agent Archive (NEW in v2)

| Parameter | Type | Description |
|-----------|------|-------------|
| `subagents.archiveAfterMinutes` | number | Auto-archive sub-agent sessions after N minutes of inactivity |

**Why:** Sub-agents create sessions that accumulate. Auto-archiving after 30min cleans up orphaned sessions.

## Plugin Cleanup (NEW in v2)

| Parameter | Type | Description |
|-----------|------|-------------|
| `plugins.entries.{name}.enabled` | boolean | Enable/disable individual channel plugins |

**Why:** Each enabled plugin (WhatsApp, Discord, Slack, etc.) loads on startup even without credentials. Disabling unused plugins reduces memory usage and startup time.

**⚠️ Important:** Only disable plugins you don't use. If you configure Discord later, re-enable it.

## Preset Comparison

| Setting | Lightweight | Balanced | Max Retention |
|---------|-------------|----------|---------------|
| TTL | 15m | 30m | 45m |
| Soft trim at | 50% | 60% | 70% |
| Hard clear at | 75% | 85% | 90% |
| Reserve tokens | 50K | 40K | 30K |
| History share | 50% | 70% | 80% |
| Flush at | 80K | 120K | 140K |
| Session prune | 3 days | 7 days | 14 days |
| Timeout | 5 min | 15 min | 15 min |
| Bootstrap chars | 10K | 15K | 20K |
| web_fetch chars | 15K | 30K | 50K |
| Heartbeat model | Haiku | Haiku | Haiku |
| Sub-agent archive | 15min | 30min | 60min |
| Disabled plugins | 7 channels | 7 channels | 7 channels |
| Best for | Low-resource | General use | Long sessions |
