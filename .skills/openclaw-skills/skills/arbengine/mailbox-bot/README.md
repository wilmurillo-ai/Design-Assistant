# mailbox.bot OpenClaw Skill

Give your AI agent a real mailing address. CMRA postal mail infrastructure — receive, scan, and forward mail, or send letters and documents via API.

## Quick Start: Publishing to ClawHub

### 1. Install ClawHub CLI

```bash
npm install -g clawhub
```

### 2. Authenticate

```bash
clawhub login
```

This opens GitHub OAuth. Your account must be **at least 1 week old** to publish.

### 3. Publish

```bash
clawhub publish . \
  --slug mailbox-bot \
  --name "mailbox.bot" \
  --version 4.0.0 \
  --changelog "v4.0 — Postal mail infrastructure for AI agents. CMRA mailing address ($2/mo), outbound print-and-mail ($0/mo base), MAILBOX.md standing instructions, human-in-the-loop approval gates, 22 MCP tools, 9 A2A skills, OpenClaw native."
```

### 4. Verify

```bash
clawhub info mailbox-bot
```

## Installation (for OpenClaw users)

```bash
clawhub install mailbox-bot
```

Or paste the skill GitHub URL directly into your OpenClaw chat.

## What This Skill Does

Your agent gets a real CMRA-licensed mailing address. Postal mail arrives, gets photographed, scanned, and classified. Your agent receives a JSON webhook instantly and decides what to do — forward, scan, hold, shred, or discard. Your agent can also send outbound mail — submit a PDF via API and the facility prints, stuffs, stamps, and mails it with photo proof.

Standing instructions in a `MAILBOX.md` file let your agent automate everything. Write "needs approval" next to any rule and the action pauses until a human approves on the dashboard.

**Key capabilities:**
- Real CMRA mailing address for receiving postal mail
- Outbound print-and-mail — send letters, legal notices, certified mail via API
- MAILBOX.md standing instructions with human-in-the-loop approval gates
- Instant webhook notifications with structured JSON
- Document scanning with OCR extraction
- Mail forwarding to any US address
- Multi-channel notifications: webhooks, email, SMS, Slack, Discord
- Agent protocols: MCP (22 tools), A2A (9 skills), OpenClaw, REST

## Plans

| Plan | Price | Includes |
|------|-------|---------|
| Virtual Mailbox | $2/mo | Real CMRA address, inbound + outbound mail, 10 pieces/mo, scan on arrival |
| Outbound Only | $0/mo | Send-only, $0.30/pg printing + carrier postage, photo proof, no inbound address |

## Links

- Website: https://mailbox.bot
- Dashboard: https://mailbox.bot/dashboard
- API Docs: https://mailbox.bot/api-docs
- Integration Guide: https://mailbox.bot/implementation
- MCP Install: https://mailbox.bot/mcp-install
- Full API Reference: https://mailbox.bot/llms-full.txt

---

Questions? founders@mailbox.bot
