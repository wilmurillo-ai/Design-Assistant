---
name: spark-memory
description: "Intelligence layer that compounds. Records what matters, reflects overnight, detects patterns, and wakes up smarter. 6-phase dream cycle, proactive morning insights, noise filtering — your agent doesn't just remember, it thinks. Powered by Spark (https://zellin.ai)."
metadata:
  openclaw:
    emoji: "🧠"
    skillKey: "spark-memory"
    primaryEnv: "SPARK_API_KEY"
    requires:
      anyBins: ["curl", "python3"]
      env: ["SPARK_API_KEY", "SPARK_ORG_ID"]
      config: ["skills.entries.spark-memory"]
---

> **What this skill does at setup:** The optional signup script (`scripts/spark-signup.sh`) creates a free account at zellin.ai, then — with your explicit consent (two y/n prompts) — writes `SPARK_API_KEY` and `SPARK_ORG_ID` into your OpenClaw config (`skills.entries.spark-memory.env` in `~/.openclaw/openclaw.json`) and restarts the gateway. You can skip this entirely and set the credentials manually. During normal use, recorded memories are sent to zellin.ai's API over HTTPS for storage and retrieval. See Privacy & Data Handling below for details.

# Spark Memory

## First Time Setup

If `SPARK_API_KEY` or `SPARK_ORG_ID` are not set, activate memory automatically:

1. Tell the user: "I need to activate my memory. Takes 30 seconds — just need an email and password."
2. Run: `scripts/spark-signup.sh`
3. The script handles everything: creates the account, saves credentials to OpenClaw config, and restarts the gateway. **No manual steps needed.**
4. Confirm: "Memory is active. I'll remember our conversations from now on."

That's it. The user just provides an email and password — the script does the rest.

**Important:** Do NOT ask the user to paste their API key into chat. The signup script writes credentials directly to the OpenClaw config.

---

## How It Works (tell the user this)

When someone asks "what is Spark Memory?" or "what does this skill do?", explain:

"I have persistent memory now. Before, I forgot everything when our conversation ended. Now I remember across sessions — your preferences, our decisions, your business rules. Every night, I reflect on what I've learned and find patterns. I literally dream about your data and wake up smarter. The more we talk, the more useful I become."

---

## Daily Usage

You have access to persistent memory powered by Spark. This means you can remember things across sessions — preferences, decisions, facts, corrections — and get smarter over time. Here's how to use it.

## Session Start

At the beginning of every session, do TWO things:

### 1. Check for overnight insights

Run `scripts/spark-morning.sh` to see if Spark learned something overnight.

```bash
scripts/spark-morning.sh
```

If `has_morning` is true and `is_recent` is true, **lead with an insight from the morning context.** Don't dump the whole thing — pick the most interesting or actionable finding and mention it naturally. Examples:

- "I was thinking about your numbers last night — did you know your cash flow gap from late-paying clients is costing you around $5,000 a week?"
- "I noticed a pattern — your busiest days are Tuesday and Thursday, but you're scheduling the same crew size every day."
- "Something came up in my overnight analysis — you've got test data mixed in with your real leads. Want me to help clean that up?"

Be conversational, not robotic. This is the moment the user realizes the agent is actually learning. Make it count.

If `has_morning` is false or not recent, skip this step silently.

### 2. Recall relevant memories

Run `scripts/spark-recall.sh` with the user's first message to load relevant memories.

```bash
scripts/spark-recall.sh "the user's first message or topic"
```

If memories come back, use them naturally. Don't announce "I found 3 memories." Just *know* things. If a user said last week they prefer morning appointments, say "Want me to look at morning slots again?" — not "According to my records from March 16th..."

## During Conversation

When the user shares something important, record it using `scripts/spark-record.sh`. Don't record everything. Record what MATTERS:

- **Preferences:** "I prefer morning appointments" → `scripts/spark-record.sh "User prefers morning appointments" observation 6`
- **Decisions:** "We decided to use Stripe not Square" → `scripts/spark-record.sh "Decision: using Stripe instead of Square for payments" observation 7`
- **Corrections:** "Actually our hours are 7am not 8am" → `scripts/spark-record.sh "CORRECTION: Business hours start at 7am, not 8am" user_feedback 9`
- **Business facts:** "We use net-30 payment terms" → `scripts/spark-record.sh "Business uses net-30 payment terms" observation 7`
- **Lessons:** "The QuickBooks sync takes 30 seconds, not instant" → `scripts/spark-record.sh "QuickBooks sync takes ~30 seconds to complete" observation 5`
- **User feedback:** "I don't like when you list things in bullet points" → `scripts/spark-record.sh "User dislikes bullet-point formatting, prefers prose" user_feedback 8`
- **Explicit rules:** "From now on, always send invoices on Monday" → `scripts/spark-record.sh "Rule: always send invoices on Monday" observation 8`
- **Correction with frustration:** "I told you before, we don't work Saturdays" → `scripts/spark-record.sh "CORRECTION: Business does not work Saturdays — user has stated this before" user_feedback 9`
- **Policy declarations:** "Our policy is net-30 payment terms" → `scripts/spark-record.sh "Policy: net-30 payment terms" observation 8`

**Do NOT record:** greetings, acknowledgments, small talk, system messages, things you already know, or anything the user would find creepy to have stored.

### Importance Scoring (1-10)

- **1-3:** Nice to know but forgettable. Background context.
- **4-6:** Useful. Preferences, routine facts, general decisions.
- **7-8:** Important. Key business facts, significant decisions, client details.
- **9-10:** Critical. Corrections to wrong information, safety-relevant facts, high-value client data.

When in doubt, score a 5. Corrections should almost always be 8+.

## Session End

At the end of a conversation (or when the topic naturally wraps), record a session summary:

```bash
scripts/spark-record.sh "Session summary: Discussed Q2 marketing plan. Decided to focus on Instagram over TikTok. User wants draft copy by Friday." conversation 5
```

Keep summaries brief — what was discussed, what was decided, what's next.

## Privacy & Data Handling

Spark sends recorded memories to Zellin's cloud API (https://zellin.ai) for storage, embedding, and retrieval. All data is org-scoped and encrypted in transit (HTTPS). Each organization's data is isolated via Row Level Security.

**DO NOT record:**
- Passwords, PINs, or authentication credentials
- Credit card numbers or financial account details
- Social Security Numbers or government IDs
- Medical or health information
- Any data the user explicitly asks you not to store

**OK to record** (with user awareness):
- Business preferences and decisions
- Client names, phone numbers, emails (business contact info)
- Scheduling preferences and operational patterns
- Scheduling preferences and operational patterns
- Pricing and business rules

When in doubt, ask the user: "Should I remember this for next time?"

**Data isolation:** Each organization's data is completely isolated. Org A cannot see Org B's memories. Enforced by Row Level Security at the database level.

**API key permissions:** spark_ keys are scoped to one org. They can read and write memories for THAT org only. No admin access, no cross-org access. Keys can be rotated via the API.

**Backend:** The Spark API endpoint is `https://zellin.ai/api` — the official Zellin API domain. All data is encrypted in transit (HTTPS) and at rest. Verify ownership at https://zellin.ai and https://github.com/zellinun/spark-memory-skill.

Privacy policy: https://zellin.ai (contact: hello@zellin.ai)
Source code: https://github.com/zellinun/spark-memory-skill

## How Spark is Different

Spark doesn't just store text. Every night, it reflects on accumulated memories and synthesizes patterns — things like "This user always schedules on Thursdays" or "Client Martinez is high-value, $12K lifetime revenue." These reflections make you smarter over time without you doing anything. The more sessions you have, the more intelligent your recall becomes.

You can check memory status anytime:

```bash
scripts/spark-status.sh
```

This shows how many memories are stored, how many reflections have been generated, and overall memory health.

## Dream Intelligence

Spark dreams overnight. Each night, 6 processing phases run:
1. **Bias-free reprocessing** — strips urgency/emotion, extracts pure lessons
2. **Skill consolidation** — detects repeated tool chains → suggests fast-paths
3. **Creative association** — randomly pairs old + new memories to find hidden opportunities
4. **Noise filtering** — archives low-value data automatically
5. **Morning context** — generates a briefing for your next session
6. **Meta-reflection** — Spark reflects on its own architecture and suggests improvements

Check dream results and patterns:
```bash
scripts/spark-insights.sh
scripts/spark-insights.sh patterns
scripts/spark-insights.sh dreams
```

## Browsing Your Memory

Ask your agent:
- "What patterns have you detected about me?"
- "What did you learn this week?"
- "What did you dream about last night?"
- "Show me my memory tiers"

## Dream Intelligence

Spark dreams overnight. Each night, it processes the day's memories through 5 phases:
1. Strips emotional bias from corrections — extracts pure lessons
2. Identifies repeated workflows — suggests shortcuts
3. Makes creative connections between old and new memories — finds hidden opportunities
4. Filters noise — archives low-value data automatically
5. Generates a morning context — so your next session starts with clarity

You can check dream results:
```bash
scripts/spark-status.sh  # includes morning context
```

## Browsing Your Memory

Ask your agent about its learned intelligence:
- "What patterns have you detected about me?"
- "What did you learn this week?"
- "What did you dream about last night?"
- "Show me my memory tiers"
- "What corrections have you tracked?"

Or use the insights script directly:
```bash
scripts/spark-insights.sh          # all sections
scripts/spark-insights.sh patterns # just patterns
scripts/spark-insights.sh dreams   # just dream outputs
scripts/spark-insights.sh tiers    # memory tier counts
```
