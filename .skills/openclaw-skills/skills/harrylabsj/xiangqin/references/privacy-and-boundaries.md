# Privacy and Boundaries

## Storage

- Current version stores data locally in JSON files under `~/.openclaw/skills-data/blind-date-assistant/`.
- Current version does not implement field-level encryption.
- Current version does not implement photo watermarking or identity verification.

## Output rules

- Do not expose exact home address, phone number, WeChat ID, ID number, bank information, or verification codes.
- When showing candidate profiles, prefer masked or coarse-grained location information.
- Present matching results as rule-based recommendations, not as guarantees or predictions.

## Safety escalation

When a conversation includes any of the following, prioritize warning the user:

- borrowing money
- investment or crypto guidance
- requests for verification codes
- pressure to move to private places quickly
- refusal to video verify while pushing intimacy quickly
- requests to install suspicious apps or use screen sharing
