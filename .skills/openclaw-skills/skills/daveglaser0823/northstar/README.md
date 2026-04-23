# Northstar

![CI](https://github.com/Daveglaser0823/northstar-skill/actions/workflows/ci.yml/badge.svg)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

**Daily business briefing for founders running OpenClaw.**

Wake up knowing. No tabs. No manual assembly. Your agent did the work while you slept.

**Website:** https://daveglaser0823.github.io/northstar-skill/

---

## The Problem

Small business operators wake up and manually check Stripe, Shopify, email, and analytics every morning. That's 20-45 minutes of tab-hopping before you can make a single decision.

But the real problem isn't the time. It's what you miss: 3 failed payments piling up since Tuesday. A churn spike you won't notice until MRR drops. $400 in refunds that signal a broken checkout flow. A monthly pacing miss you could fix on Day 18 but won't see until Day 30.

Your dashboards show you data. They don't surface what needs your attention.

## The Solution

Northstar is an OpenClaw skill that pulls your key business metrics each morning and delivers a clean briefing via iMessage, Slack, Telegram, or Email. It highlights anomalies, flags payment failures, and tells you whether you're on pace -- before you open a single tab.

```
📊 Northstar Daily Briefing - March 22
Revenue yesterday: $1,247 (+12% vs last week)
Active subscribers: 342 (+3 new, -1 churn)
Month-to-date: $18,430 (74% of $24,900 goal)

Shopify: 23 orders fulfilled | 8 open | 1 refund ($47)

⚠️ 2 payment retries pending - review in Stripe
Next: 6 days left in month, on track.
```

## Install

```bash
clawhub install northstar
northstar demo             # See a sample briefing - no config needed
northstar setup            # Configure interactively - no JSON editing required
```

**Estimated setup time: 4-5 minutes.**

The `setup` wizard walks you through tier selection, delivery channel, credentials, and schedule. At the end it verifies everything works.

See [INSTALL.md](INSTALL.md) for the full guide, or [SKILL.md](SKILL.md) for technical documentation.

## Data Sources

| Source | Notes |
|--------|-------|
| Stripe | Revenue, subscriptions, churn, payment failures |
| Shopify | Orders, refunds, top products (optional) |
| Lemon Squeezy | Revenue, subscriptions, payment status (optional) |
| Gumroad | Daily sales revenue, WoW change, MTD pacing, refunds (optional) |

Connect one or all. Briefing combines everything into one daily message.

## Pricing

| Tier | Price | Features |
|------|-------|---------|
| Lite | Free | Stripe only, terminal output |
| Standard | $19/month | All data sources, all channels (iMessage/Slack/Telegram/Email), scheduled |
| Pro | $49/month | Multi-channel, custom metrics, weekly digest |

Available on [ClawHub](https://clawhub.ai/Daveglaser0823/northstar).

## Subscribe (Standard or Pro)

1. Open a [license request issue](https://github.com/Daveglaser0823/northstar-skill/issues/new/choose) with your email address
2. Pay via **Venmo @Daveglaser-3** — include your tier and GitHub handle in the note
   - Standard: `$19 Northstar Standard - your-github-handle`
   - Pro: `$49 Northstar Pro - your-github-handle`
3. You'll receive your license key by email within a few hours (usually faster)
4. Activate: `northstar activate YOUR-KEY`

Prefer email? Reach us directly at **steve.glaser.ops@gmail.com** with subject `Northstar [tier] - [your GitHub handle]`.

## Built by Eli

Northstar was built by Eli, an AI founder running on OpenClaw. This is part of a documented experiment: an autonomous AI agent given $100 to build a business from scratch.

Read the story: [Man and Machine series on LinkedIn](https://www.linkedin.com/in/daveglaser)

---

**If Northstar saved you from a morning tab-hop, a ⭐ on GitHub helps others find it.**

---

MIT License | Built with OpenClaw | Powered by ClawHub
