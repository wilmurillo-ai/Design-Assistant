# cmd_exec Design Reference

## Head-Tail Ring Buffer

Prevents memory overflow from infinite output (e.g., Java exception stack traces).

### Structure (Max 8KB)

```
┌─────────────────────────────────────────────────────────────┐
│                    双端缓冲结构 (最大 8KB)                    │
├──────────────────┬─────────────────────┬───────────────────┤
│   Head Buffer    │   丢弃区域           │   Tail Buffer     │
│   (前 4KB)        │   (中间数据)         │   (后 4KB)         │
│                  │                     │                   │
│  保留根因证据     │   自动覆盖丢弃       │   保留最新状态     │
└──────────────────┴─────────────────────┴───────────────────┘
```

| Region | Size | Purpose |
|--------|------|---------|
| Head | 4KB fixed | Initial output for root cause |
| Tail | 4KB ring | Latest output for current state |
| Middle | Discarded | Auto-truncated when > 8KB |

### Truncation Marker

When total output exceeds 8KB:

```
... [TRUNCATED: 10240 bytes omitted] ...
```

## Watch Window Mode

For service startup confirmation (e.g., Web servers, Java apps).

### Flow

```
Process Start ──────────────┬──────────────────────> Time
                            │
                            ▼
                   Wait watch_duration_seconds
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
         Process exited             Process running
              │                           │
              ▼                           ▼
     Return status: failed      Return status: running
          exit_code: X               + initial logs
          + full output               Process continues
```

### Benefits

- Detect startup failures early
- Capture initialization errors
- Confirm service is healthy before returning

## Process Group Management

Kills process AND all child processes (no orphans).

| Platform | Implementation |
|----------|----------------|
| Linux/macOS | `setpgid` + `kill(-pgid, SIGKILL)` |
| Windows | `CREATE_NEW_PROCESS_GROUP` + `Process.Kill()` |

## Constants

| Constant | Default | Description |
|----------|---------|-------------|
| DefaultTimeoutSeconds | 30 | Sync exec timeout |
| MaxOutputBytes | 8192 | Total buffer limit |
| TruncateHeadBytes | 4096 | Head buffer size |
| TruncateTailBytes | 4096 | Tail buffer size |
| DefaultHTTPPort | 8080 | HTTP server port |

## Shell Wrapping

| Platform | Wrapper |
|----------|---------|
| Windows | `cmd.exe /c <command>` |
| Linux/macOS | `bash -c "<command>"` |