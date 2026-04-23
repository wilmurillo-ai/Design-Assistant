# Multi-language Integration

Use this reference when the user wants Telegram moderation integration examples beyond PHP.

## Goal

Provide small, readable webhook/action examples in common backend languages so teams can adapt the Telegram integration layer without being forced into PHP.

## Included languages

- Python
- Go
- Java

## Shared design rules

All example scripts should:
- treat this skill as a Telegram integration layer, not a full moderation engine
- validate Telegram webhook secret before processing
- normalize Telegram message updates into a small internal payload
- call an external moderation core endpoint
- map moderation result into Telegram actions such as delete, warn, mute, ban, or review notification
- use environment variables for all secrets and endpoints
- use explicit timeout values
- stay intentionally small and adaptation-friendly

## Important limitation

These examples are integration demos, not production-complete frameworks.

They do not automatically provide:
- offense count persistence
- queue-based retries
- OCR / QR / ASR media inspection
- full admin dashboard
- distributed rate limiting

## Suggested use

- read the language example that matches your stack
- adapt the normalization and action mapping to your business rules
- keep the moderation policy in `post-content-moderation` or your own moderation core
- do not duplicate policy logic across all languages unless required
