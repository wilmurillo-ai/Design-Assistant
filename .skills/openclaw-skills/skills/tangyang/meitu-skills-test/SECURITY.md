# Security Model

This document describes the security implications of using `meitu-skills`.

## Credential Requirements

This skill requires Meitu OpenAPI credentials to function. Credentials can be provided via:

| Method | Location | Priority |
|--------|----------|----------|
| Environment variables | `MEITU_OPENAPI_ACCESS_KEY`, `MEITU_OPENAPI_SECRET_KEY` | Highest |
| Credentials file | `~/.meitu/credentials.json` | Fallback |
| Legacy file | `~/.openapi/credentials.json` | Lowest |

### Credentials File Format

```json
{
  "accessKey": "your-access-key",
  "secretKey": "your-secret-key"
}
```

**Security note:** Credential files should have restricted permissions (`chmod 600`). Never commit credentials to version control.

## Permissions

### File System Access

| Path | Access | Purpose |
|------|--------|---------|
| `~/.meitu/credentials.json` | Read | Load API credentials |
| `~/.openapi/credentials.json` | Read | Load API credentials (legacy) |
| `~/.meitu/runtime-update-state.json` | Read/Write | Persist runtime version state |

### Command Execution

| Command | Purpose | When Used |
|---------|---------|-----------|
| `meitu` | CLI tool execution | Every tool invocation |
| `npm view` | Check latest version | Version checks (when not `off`) |
| `npm install -g` | Install/update runtime | Only when `MEITU_RUNTIME_UPDATE_MODE=apply` |

## Runtime Update Modes

The skill supports three runtime update modes controlled by `MEITU_RUNTIME_UPDATE_MODE`:

| Mode | Behavior | Security Implication |
|------|----------|---------------------|
| `check` (default) | Checks npm for updates, reports availability, **does not install** | Safe: Read-only operations |
| `off` | No version checks or installs | Safest: No external network calls for updates |
| `apply` | Checks and **auto-installs** when outdated | Requires consent: Modifies global npm packages |

### Recommendation

- Use `check` (default) for normal operation
- Use `off` in locked-down environments
- Use `apply` only when you explicitly consent to automatic global package installation

### Manual Update (Recommended)

Instead of `apply` mode, prefer manual updates:

```bash
npm install -g meitu-cli@latest
meitu --version
```

## Data Flow

```
User Request
    │
    ▼
run_command.js
    │
    ├── Read credentials (env or file)
    │
    ├── Check runtime version (if not 'off')
    │   └── npm view meitu-cli@latest version
    │
    ├── Execute meitu CLI
    │   └── spawnSync('meitu', [...args])
    │
    └── Return result
```

## What This Skill Does NOT Do

- Does not send credentials to any third-party services
- Does not modify files outside `~/.meitu/` directory
- Does not execute arbitrary commands (only `meitu` and `npm`)
- Does not auto-install packages in default mode (`check`)

## Audit Checklist

Before using this skill in production:

- [ ] Credentials stored securely (env vars or restricted file)
- [ ] `MEITU_RUNTIME_UPDATE_MODE` set appropriately for your environment
- [ ] Reviewed `npm` package source (`meitu-cli` on npm registry)
- [ ] Understand that `apply` mode enables global npm installs

## Vulnerability Reporting

If you discover a security vulnerability, please report it privately to the maintainers. Do not open a public issue.

## Version History

| Version | Changes |
|---------|---------|
| 2025-03-21 | Initial security documentation |