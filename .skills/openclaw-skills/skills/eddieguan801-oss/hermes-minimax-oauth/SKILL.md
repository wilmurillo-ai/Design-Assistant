---
name: hermes-minimax-oauth
description: Add MiniMax OAuth authentication support to Hermes Agent. Use when integrating MiniMax OAuth into Hermes, fixing MiniMax auth issues, or adding new OAuth providers to Hermes. Covers hermes-cli/auth.py and hermes-cli/auth_commands.py modifications, correct MiniMax OAuth endpoints, PKCE flow, and ProviderConfig setup.
---

# Hermes MiniMax OAuth Integration

## Overview

This skill documents how to add MiniMax OAuth support to Hermes Agent using the PKCE + user_code flow (matching OpenClaw's implementation).

## Files Modified

1. `hermes_cli/auth.py` - OAuth flow functions, constants, ProviderConfig
2. `hermes_cli/auth_commands.py` - CLI command handlers
3. `hermes_cli/models.py` - Provider catalog entries

## MiniMax OAuth Configuration

### Correct Endpoints (from OpenClaw reference)

```
Base URL (Global): https://api.minimax.io
Base URL (China):  https://api.minimaxi.com

OAuth Code:  {base}/oauth/code
OAuth Token: {base}/oauth/token
```

### OAuth Parameters

```
Client ID:  78257093-7e40-4613-99e0-527b14b39113
Scope:      group_id profile model.completion
Grant Type: urn:ietf:params:oauth:grant-type:user_code
```

### PKCE Requirements

- Method: S256
- Generate 32-byte random verifier, base64url encode
- SHA256 hash of verifier = challenge

## Step-by-Step Implementation

### 1. Add Constants to auth.py

```python
DEFAULT_MINIMAX_PORTAL_URL = "https://api.minimax.io"
DEFAULT_MINIMAX_INFERENCE_URL = "https://api.minimax.io/anthropic"
MINIMAX_OAUTH_CLIENT_ID = "78257093-7e40-4613-99e0-527b14b39113"
MINIMAX_OAUTH_CODE_URL = "https://api.minimax.io/oauth/code"
MINIMAX_OAUTH_TOKEN_URL = "https://api.minimax.io/oauth/token"
MINIMAX_OAUTH_SCOPE = "group_id profile model.completion"
MINIMAX_ACCESS_TOKEN_REFRESH_SKEW_SECONDS = 120

# China variant uses api.minimaxi.com
```

### 2. Add ProviderConfig Entries

In `auth.py`, add to `PROVIDER_REGISTRY`:

```python
"minimax-oauth": ProviderConfig(
    id="minimax-oauth",
    name="MiniMax OAuth",
    auth_type="oauth_device_code",
    portal_base_url=DEFAULT_MINIMAX_PORTAL_URL,
    inference_base_url=DEFAULT_MINIMAX_INFERENCE_URL,
    client_id=MINIMAX_OAUTH_CLIENT_ID,
    scope=MINIMAX_OAUTH_SCOPE,
),
"minimax-cn-oauth": ProviderConfig(
    id="minimax-cn-oauth",
    name="MiniMax OAuth (China)",
    auth_type="oauth_device_code",
    portal_base_url="https://api.minimaxi.com",
    inference_base_url="https://api.minimaxi.com/anthropic",
    client_id=MINIMAX_OAUTH_CLIENT_ID,
    scope=MINIMAX_OAUTH_SCOPE,
),
```

### 3. Add Alias Mappings

In `_PROVIDER_ALIASES`:

```python
"minimax-global-oauth": "minimax-oauth",
"minimax_global_oauth": "minimax-oauth",
"minimax-china-oauth": "minimax-cn-oauth",
"minimax_china_oauth": "minimax-cn-oauth",
```

### 4. Implement OAuth Flow Functions

Key functions needed in `auth.py`:

- `_generate_pkce()` - Generate verifier/challenge/state
- `_minimax_oauth_request_code()` - POST to /oauth/code
- `_minimax_oauth_poll_token()` - Poll /oauth/token until approved
- `_minimax_device_code_login()` - Main login orchestrator
- `resolve_minimax_runtime_credentials()` - Token refresh logic
- `get_minimax_auth_status()` - Auth status check

### 5. Update auth_commands.py

Add to `_OAUTH_CAPABLE_PROVIDERS`:
```python
_OAUTH_CAPABLE_PROVIDERS = {
    "anthropic", "nous", "openai-codex", "qwen-oauth",
    "google-gemini-cli", "minimax-oauth", "minimax-cn-oauth"
}
```

Add login handler:
```python
if provider in ("minimax-oauth", "minimax-cn-oauth"):
    is_cn = provider == "minimax-cn-oauth"
    portal_url = auth_mod.DEFAULT_MINIMAX_CN_PORTAL_URL if is_cn else auth_mod.DEFAULT_MINIMAX_PORTAL_URL
    client_id = auth_mod.MINIMAX_CN_OAUTH_CLIENT_ID if is_cn else auth_mod.MINIMAX_OAUTH_CLIENT_ID
    scope = "group_id profile model.completion"
    creds = auth_mod._minimax_device_code_login(portal_base_url=portal_url, client_id=client_id, scope=scope)
    # ... create PooledCredential and add to pool
```

### 6. Add to models.py

In `CANONICAL_PROVIDERS`:
```python
ProviderEntry("minimax-oauth",  "MiniMax OAuth (Global)",   "MiniMax (global) via OAuth"),
ProviderEntry("minimax-cn-oauth","MiniMax OAuth (China)",   "MiniMax (China) via OAuth"),
```

In model lists:
```python
"minimax-oauth": ["MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M2.1", "MiniMax-M2"],
"minimax-cn-oauth": ["MiniMax-M2.7", "MiniMax-M2.5", "MiniMax-M2.1", "MiniMax-M2"],
```

### 7. Fix httpx Compatibility

httpx 0.28.x uses `response.is_success` not `response.ok`:
```python
# Wrong
if not response.ok:
# Correct
if not response.is_success:
```

## Testing

```bash
# Restart Hermes
pkill -f hermes_cli.main
cd ~/.hermes/hermes-agent && nohup venv/bin/python -m hermes_cli.main gateway run &

# Test OAuth flow
hermes auth add minimax-oauth

# Verify syntax
python3 -m py_compile hermes_cli/auth.py
python3 -m py_compile hermes_cli/auth_commands.py
python3 -m py_compile hermes_cli/models.py
```

## Common Errors

| Error | Fix |
|-------|-----|
| `Response object has no attribute 'ok'` | Change to `response.is_success` |
| `404` on OAuth endpoints | Use `/oauth/code` not `/api/oauth/device/code` |
| `invalid_api_key` | Set `MINIMAX_API_KEY` in `~/.hermes/.env` |

## Reference

See `references/openclaw-oauth-implementation.md` for the complete OpenClaw reference that this was based on.
