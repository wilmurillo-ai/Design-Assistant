---
name: blind-date-assistant
description: Help users manage dating profiles, find matches, generate conversation starters and chat topics, track interaction progress, and provide dating and safety reminders. Use when users explicitly mention dating, finding a partner, relationship matching, conversation starters, chat advice, date suggestions, contact records, or dating safety.
---

# Blind Date Assistant

Use this skill as a local helper tool, not as a dating platform backend.

## Execution Principles

- First confirm the user's goal: improving profile, finding matches, generating conversation scripts, recording progress, or viewing safety reminders.
- Clearly inform that this is a local prototype tool; results are for reference only and should not be presented as "platform-level intelligent recommendations."
- When privacy is involved, default to minimal exposure; do not actively output sensitive information like phone numbers, WeChat IDs, or addresses.
- When meeting, transferring money, investing, borrowing, nude chatting, or requesting verification codes are involved, prioritize safety warnings.
- Do not claim to have implemented encryption, photo watermarks, real-name verification, or other unimplemented capabilities.

## Available Capabilities

- Create and view personal profiles
- Basic matching and sorting based on existing profiles
- Generate conversation openers
- Recommend chat topics
- Recommend date formats
- Record contact history
- Output dating safety reminders

## Execution Method

Prioritize using CLI:

```bash
node scripts/cli.js safety
node scripts/cli.js profile <userID>
node scripts/cli.js profile <userID> create '<profileJSON>'
node scripts/cli.js match <userID> [count]
node scripts/cli.js opener <userID> <targetID>
node scripts/cli.js topics [initial|middle|advanced]
node scripts/cli.js date [city]
node scripts/cli.js record <userID> <targetID> <content>
node scripts/cli.js history <userID> <targetID>
```

## Profile Input Suggestions

When creating a profile, include at least:

- nickname
- gender
- birthYear
- height
- location
- education
- occupation

Optional fields:

- income
- hometown
- hobbies
- values
- selfDescription
- ageRange
- locationPreference
- educationPreference
- otherRequirements

For field descriptions and suggested workflows, see `references/fields-and-workflows.md`

## Data Boundaries

- Current data is saved in local directory `~/.openclaw/skills-data/blind-date-assistant/`
- Current version uses local JSON files to save data
- Current version **does not implement** field-level encryption, photo watermarks, real-name verification, or contact exchange control
- Therefore, avoid exaggerating security capabilities when outputting, and remind users to provide sensitive information cautiously
- For privacy and output boundaries, see `references/privacy-and-boundaries.md`

## Result Presentation Requirements

- Present matching results as "basic rule-based matching results" or "local recommendations"
- Do not present scores as real success rates
- If sample size is insufficient, clearly state "insufficient candidates in current profile database"
- If profile is incomplete, first suggest completing the profile before making recommendations

## Safety Requirements

When the following scenarios occur, prioritize reminding users of risks:

- First meeting requested in private space
- Quickly borrowing money, bringing investment, gambling, or cryptocurrency
- Refusing video while pushing relationship quickly
- Requesting ID card, bank card, or verification code
- Inducing nude chatting, screen sharing, or downloading suspicious apps

When necessary, run directly:

```bash
node scripts/cli.js safety
```

## Testing

Run minimal test:

```bash
node test.js
```

Tests should cover:

- Creating profile
- Viewing profile
- Two-person matching
- Opener generation
- Contact recording
- Safety reminders
