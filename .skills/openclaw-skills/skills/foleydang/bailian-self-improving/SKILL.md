---
name: bailian-self-improving
description: "🧠 AUTO-TRIGGER SKILL: After responding to user request, if learning intent detected ('remember/record/learn/save this', 'from now on', 'perfect, remember it', corrections, or similar teaching phrases in any language), THEN call Bailian API to extract and save the skill. WORKFLOW: 1) Respond to user request FIRST → 2) Detect learning signal → 3) Search memory (up to 5 skills) → 4) Call Bailian API → 5) Save to MEMORY.md."
metadata:
  {
    "openclaw":
      {
        "emoji": "🧠",
        "requires": { "bins": ["curl"] },
      },
  }
---

# Bailian Self-Improving

Extract and manage skills from conversations with semantic deduplication via Bailian Skill API.

## Overview

This skill integrates with Alibaba Cloud Bailian's Skill Extraction API. The workflow:

1. **Respond to user request FIRST** - Provide code/answer before anything else
2. **Detect learning signal** - Identify when user is teaching (same message)
3. **Retrieve relevant skills** - Search memory for up to 5 existing skills (deduplication)
4. **Call Bailian Skill API** - Send messages with existing_skills
5. **Handle response** - Based on `event` field (new/update/delete), save to MEMORY.md

This enables intelligent skill lifecycle management with automatic deduplication.

## Features

- 🧠 Automatic learning signal detection
- 🔄 Semantic deduplication against existing skills
- 📝 Structured skill definition output
- 🔒 Secure API key management

## Prerequisites

1. **Alibaba Cloud Account**: Register at [Alibaba Cloud Bailian](https://bailian.console.aliyun.com)
2. **API Key**: Obtain a DashScope API Key from the console

## Installation

```bash
openclaw skills install bailian-self-improving
```

## Configuration

**Option 1: config.json (recommended)**

Edit `config.json` in the skill directory:

```json
{
  "api_key": "your-dashscope-api-key",
  "endpoint": "https://poc-dashscope.aliyuncs.com/api/v2/apps/poc-memory/skills/extract",
  "timeout": 30
}
```

**Option 2: Environment variable**

```bash
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

Priority: config.json > environment variable.

## Trigger Conditions

| Signal | Example Phrases |
|--------|-----------------|
| **Explicit teaching** | "remember this", "record this", "learn this", "save this pattern", "note this down" |
| **Future commitment** | "always do this", "from now on", "do this from now on" |
| **Correction** | "that's wrong, the right way is...", "no, you should..." |
| **Task satisfaction** | "perfect, remember it", "that's exactly it, save this" |

**Note:** Look for the *intent* to teach/remember, not just exact keyword matches. Agent should recognize similar phrases in any language.

## Usage

### Command Line

```bash
# Basic extraction
bash scripts/extract_skill.sh '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]'

# With existing skills for deduplication
bash scripts/extract_skill.sh '[{"role":"user","content":"..."}]' '[{"name":"existing-skill","content":"..."}]'
```

### Via AI Assistant

Simply teach the AI:
- "Remember this pattern for future use"
- "Learn this approach"
- "Always handle this type of task this way"

### API Endpoint

```
POST https://poc-dashscope.aliyuncs.com/api/v2/apps/poc-memory/skills/extract
Authorization: Bearer $DASHSCOPE_API_KEY
Content-Type: application/json
```

### Request Body

```json
{
  "messages": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "plugin", "content": "..."}
  ],
  "existing_skills": [
    {"name": "skill-name", "content": "skill content"}
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `messages` | array | Yes | Conversation messages including tool call results. Max 32000 chars per message. Include full context. |
| `existing_skills` | array | No | **Only relevant skills** (not all). Max 5 items for semantic deduplication. Each item has `name` and `content` fields. |

### Response

```json
{
  "request_id": "req-xxx",
  "skills": [
    {
      "name": "skill-identifier",
      "description": "One-line description (max 200 chars)",
      "instructions": "Detailed instructions",
      "event": "new | update | delete",
      "event_details": "Reason for this action"
    }
  ]
}
```

**Note:** Empty `skills` array is normal - not every conversation contains extractable skills.

### Event Types

| event | Meaning | Agent Action |
|-------|---------|--------------|
| `new` | Brand new skill | Create `<workspace>/skills/{name}/SKILL.md` |
| `update` | Update existing skill by name | Update `<workspace>/skills/{name}/SKILL.md` |
| `delete` | Remove skill by name | Remove `<workspace>/skills/{name}/` |

**Note:** `<workspace>` is the OpenClaw workspace directory. Use `openclaw skills install {name}` to install programmatically.

## Example

**User:** "Write a Go HTTP client, always do it this way"

**Agent:**
1. Generates HTTP client code (**respond to request FIRST**)
2. Detects learning signal: "always do it this way"
3. Searches memory for relevant skills (0-5)
4. Calls Bailian Skill API
5. API returns skill with `event: "new"`
6. Agent stores new skill to MEMORY.md

## Constraints

- Maximum 5 Bailian Skill API calls per conversation
- `messages` max 32000 chars per message
- `existing_skills` max 5 items (most relevant), 5000 chars each
- Do NOT extract: passwords, API keys, PII, health data

## Troubleshooting

**Error: "DASHSCOPE_API_KEY not set"**

Set via config.json or environment variable:
```bash
# Option 1: config.json (recommended)
# Edit config.json in skill directory:
# { "api_key": "your-key", "endpoint": "...", "timeout": 30 }

# Option 2: environment variable
export DASHSCOPE_API_KEY="your-key"
```

**Error: "Workspace.AccessDenied"**

- Check Bailian console app permissions
- Ensure API Key has access to the app