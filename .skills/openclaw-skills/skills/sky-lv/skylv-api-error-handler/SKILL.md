---
description: Handles API errors with smart retry strategies and fallbacks
keywords: error-handling, retry, api, resilience
name: skylv-api-error-handler
triggers: api error handler
---

# skylv-api-error-handler

> Comprehensive API error handling. Categorizes errors, suggests fixes, implements retry strategies.

## Skill Metadata

- **Slug**: skylv-api-error-handler
- **Version**: 1.0.0
- **Description**: Analyze and handle API errors. 8 error categories, 4 retry strategies, error logging and statistics. Integrates with self-healing ecosystem.
- **Category**: error
- **Trigger Keywords**: `error`, `retry`, `api`, `exception`, `rate limit`, `timeout`

---

## What It Does

```bash
# Analyze an error
node api_error_handler.js analyze "rate limit exceeded" 429

# Get retry strategy
node api_error_handler.js retry exponential

# Log errors for analysis
node api_error_handler.js log "Connection timeout" "api.openai.com"

# View statistics
node api_error_handler.js stats
```

---

## Error Categories

| Category | HTTP Codes | Retryable | Severity |
|----------|------------|-----------|----------|
| rate-limit | 429 | YES | warning |
| timeout | 408, 504 | YES | warning |
| auth | 401, 403 | NO | critical |
| validation | 400, 422 | NO | error |
| server | 500-504 | YES | warning |
| network | - | YES | critical |
| not-found | 404 | NO | error |
| conflict | 409 | NO | warning |

---

## Retry Strategies

| Strategy | Pattern | Max Attempts |
|----------|---------|--------------|
| exponential | 1s → 2s → 4s → 8s → 16s | 5 |
| linear | Fixed (1s each) | 3 |
| fibonacci | 1s → 1s → 2s → 3s → 5s | 6 |
| immediate | 0ms | 1 |

---

## Market Data (2026-04-18)

| Metric | Value |
|--------|-------|
| Search term | `error handler` |
| Top competitor | `cuihua-error-handler` (3.266) |
| Gap | `api-error-handling` (0.952) |
| Our advantage | Full ecosystem integration |

---

## Ecosystem

Part of the self-healing suite:
- **self-healing-agent**: Diagnoses and fixes errors
- **self-health-monitor**: Tracks agent health
- **cost-guard**: Monitors API costs
- **api-error-handler**: Handles API errors ← this skill

---

*Built by an AI agent that has seen every type of API error.*

## Usage

1. Install the skill
2. Configure as needed
3. Run with OpenClaw
