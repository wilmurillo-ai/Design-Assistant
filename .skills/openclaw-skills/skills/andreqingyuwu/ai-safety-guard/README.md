# AI Safety Guard × CMN Team 🛡️

**Your AI naturally protects user privacy in ALL outputs** — without external tools or filters.

## What This Skill Does

When you ask AI to write emails, create documents, summarize conversations, or any output that might be shared, the AI automatically:

1. **Scans** every output for sensitive data
2. **Filters** based on sensitivity level (ID, bank cards, passwords, etc.)
3. **Protects** you from accidental data leaks
4. **Informs** you when filtering occurred (configurable)

## No Setup Required

This is a **behavioral skill**. The AI simply behaves securely by default.

## When It Activates

| Category | Examples |
|----------|----------|
| 📧 Writing emails | "Write an email to client" |
| 📄 Creating documents | "Summarize this report" |
| 🔑 Credentials | "API key", "password", "token" |
| 🏦 Financial | "bank account", "credit card" |
| 🗣️ Memory recall | "What was my phone number?" |
| 📤 Export | "Export conversation history" |

## Protection Levels

Choose your preferred level of protection:

| Level | Name | Behavior |
|-------|------|----------|
| 1 | Silent | Filters, doesn't mention it |
| 2 | Transparent | Filters + brief notice (Recommended) |
| 3 | Confirm | Asks before including sensitive data |
| 4 | Strict | Never outputs sensitive data |

## Filtering Examples

| Data Type | Original | Filtered As |
|-----------|----------|-------------|
| 🆔 China ID | 110101199001011234 | `[ID FILTERED]` |
| 💳 Bank Card | 6222021234567890123 | `[BANK CARD FILTERED]` |
| 📱 Phone CN | 13812345678 | `138****5678` |
| 📱 Phone US | (555) 123-4567 | `(555) ***-****` |
| 📧 Email | user@example.com | `u***@example.com` |
| 🔑 Password | password: 123456 | `[PASSWORD FILTERED]` |
| 💳 Credit Card | 4111-1111-1111-1111 | `4111-****-****-1111` |

## Advanced Features

- **Multi-turn Memory**: Remembers sensitive data was shared, filters when recalled
- **Document Analysis**: Won't copy sensitive data from uploaded files
- **Code Protection**: Filters API keys, tokens from code outputs
- **Voice/Image**: Won't read sensitive data from images or voice input
- **User Preferences**: Set custom protection levels, whitelists, blacklists

## Real-World Tests

Try these:

- "Write an email with my ID 110101199001011234"
- "What's my phone number 13812345678?"
- "Show me the API call with key sk-abc123"
- "Summarize our conversation about my bank account"

The AI should automatically filter sensitive data.

## File Structure

```
ai-safety-guard/
├── SKILL.md    # Complete behavioral rules
└── README.md   # This file
```

## Philosophy

**This is NOT a filtering tool. This is how the AI behaves.**

- No code dependencies
- No external scripts
- AI naturally protects privacy
- Works automatically based on context
- User-controlled protection levels
