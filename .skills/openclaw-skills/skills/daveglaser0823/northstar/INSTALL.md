# Northstar - Installation Guide

## Requirements

- macOS (for iMessage delivery) or any OS (for Slack/Telegram delivery)
- Python 3.9 or higher
- OpenClaw installed and running
- A Stripe account (required for Standard/Pro tiers)
- A Shopify store (optional, adds order tracking)

---

## Step 1: Install from ClawHub

```bash
clawhub install northstar
```

This will:
- Copy the skill to `~/.clawd/skills/northstar/`
- Create a config template at `~/.clawd/skills/northstar/config/northstar.json`
- Install the `northstar` command to `~/.local/bin/northstar`
- Install the `stripe` Python package if not present

> **PATH note:** If `northstar` command isn't found after install, add `~/.local/bin` to your PATH:
> ```bash
> echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
> ```

---

## Step 2: Try the Demo (Optional but Recommended)

See a realistic sample briefing before entering any credentials:

```bash
northstar demo
```

No config needed. Just shows you what the output looks like.

---

## Step 3: Run the Setup Wizard

The fastest way to configure Northstar (no JSON editing required):

```bash
northstar setup
```

This walks you through:
- Choosing your tier (lite / standard / pro)
- Selecting your delivery channel (iMessage, Slack, Telegram)
- Entering your Stripe API key
- Setting your monthly revenue goal
- Configuring your delivery schedule

At the end it writes your config file and runs a test to verify everything works. **Estimated time: 4-5 minutes.**

> **Prefer manual config?** Skip to [Manual Configuration](#manual-configuration) below.

---

## Manual Configuration

### Configure Your Credentials

Open the config file:

```bash
open ~/.clawd/skills/northstar/config/northstar.json
```

Or edit it in your terminal:

```bash
nano ~/.clawd/skills/northstar/config/northstar.json
```

### Minimum configuration (Stripe + iMessage)

```json
{
  "delivery": {
    "channel": "imessage",
    "recipient": "+15551234567"
  },
  "schedule": {
    "hour": 6,
    "minute": 0,
    "timezone": "America/New_York"
  },
  "stripe": {
    "enabled": true,
    "api_key": "sk_live_YOUR_KEY_HERE",
    "monthly_revenue_goal": 24900
  },
  "shopify": {
    "enabled": false
  }
}
```

**Replace:**
- `+15551234567` with your own phone number (for iMessage delivery)
- `sk_live_YOUR_KEY_HERE` with your Stripe restricted key (see below)
- `24900` with your monthly revenue goal in dollars

---

### Get Your Stripe API Key

1. Go to [Stripe Dashboard > API Keys](https://dashboard.stripe.com/apikeys)
2. Click **+ Create restricted key**
3. Name it "Northstar" (or anything you like)
4. Set these permissions to **Read**:
   - Charges
   - Customers
   - Subscriptions
   - Invoices
   - Payment Intents
5. Click **Create key** and copy it
6. Paste it into `northstar.json` as the `stripe.api_key` value

> Use a **Restricted Key**, not your Secret Key. Northstar only needs read access.

---

## Step 4: (Optional) Add Shopify

1. In your Shopify Admin, go to **Settings > Apps and sales channels > Develop apps**
2. Click **Create an app**, name it "Northstar"
3. Under **Configuration**, enable these Admin API access scopes:
   - `read_orders`
   - `read_products`
4. Click **Install app** and copy the **Admin API access token**
5. Update your config:

```json
"shopify": {
  "enabled": true,
  "shop_domain": "your-store.myshopify.com",
  "access_token": "shpat_YOUR_TOKEN_HERE"
}
```

---

## Step 4b: (Optional) Add Lemon Squeezy

1. Go to [Lemon Squeezy Settings > API](https://app.lemonsqueezy.com/settings/api)
2. Create a new API key (read access is sufficient)
3. Update your config:

```json
"lemonsqueezy": {
  "enabled": true,
  "api_key": "YOUR_LEMONSQUEEZY_KEY",
  "monthly_revenue_goal": 5000
}
```

---

## Step 4c: (Optional) Add Gumroad

1. Go to [Gumroad Settings > Advanced > API](https://app.gumroad.com/settings/advanced)
2. Generate an access token
3. Update your config:

```json
"gumroad": {
  "enabled": true,
  "access_token": "YOUR_GUMROAD_TOKEN",
  "monthly_revenue_goal": 3000
}
```

---

## Step 5: Test It

Run a dry-run (prints to terminal, sends nothing):

```bash
northstar test
```

You should see output like:
```
📊 Northstar Daily Briefing - March 22
Revenue yesterday: $1,247 (+12% vs last week)
Active subscribers: 342 (+3 new, -1 churn)
...
```

If you see `No data sources configured`, double-check your API key and that `"enabled": true` is set in the config.

---

## Step 6: Schedule Daily Delivery

Add to your OpenClaw cron so it runs automatically each morning:

```bash
openclaw cron edit
```

Add this line:
```
# Northstar daily briefing at 6:00 AM
0 6 * * * northstar run
```

Save and exit. Northstar will now deliver your briefing every morning at 6 AM in your configured timezone.

> **Timezone note:** The schedule uses your system clock. If you want the briefing at 6 AM New York time regardless of where you are, set `"timezone": "America/New_York"` in your config.

---

## Delivery Channel Options

### iMessage (macOS only)

```json
"delivery": {
  "channel": "imessage",
  "recipient": "+15551234567"
}
```

Messages.app must be signed in and running. Works best when OpenClaw is on the same Mac you use for iMessage.

### Slack

```json
"delivery": {
  "channel": "slack",
  "slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

Get a webhook URL at [api.slack.com/apps](https://api.slack.com/apps) > your app > Incoming Webhooks.

### Telegram

```json
"delivery": {
  "channel": "telegram",
  "telegram_bot_token": "1234567890:YOUR_BOT_TOKEN",
  "telegram_chat_id": "-1001234567890"
}
```

Create a bot via [BotFather](https://t.me/BotFather), then start a chat with your bot to get the chat ID.

### Terminal only (no delivery)

```json
"delivery": {
  "channel": "none"
}
```

Use `northstar test` for on-demand terminal output.

---

## Commands

| Command | What it does |
|---------|-------------|
| `northstar test` | Dry-run: prints briefing to terminal, no message sent |
| `northstar run` | Run now and deliver to configured channel |
| `northstar status` | Show config status and last run info |
| `northstar stripe` | Show raw Stripe data (for debugging) |
| `northstar shopify` | Show raw Shopify data (for debugging) |
| `northstar digest` | [Pro] Run weekly digest (7-day rollup, Sunday format) |
| `northstar trend` | [Pro] Show 7-day revenue trend with sparkline |
| `northstar --help` | Full help |

---

## Alerts Configuration

Northstar fires alerts when something needs your attention. Configure thresholds:

```json
"alerts": {
  "payment_failures": true,
  "churn_threshold": 3,
  "large_refund_threshold": 100
}
```

- `payment_failures`: Alert on any failed or retried payments (true/false)
- `churn_threshold`: Alert when cancellations in one day exceed this number
- `large_refund_threshold`: Alert on refunds above this dollar amount

---

## Format Options

```json
"format": {
  "emoji": true,
  "include_pacing": true,
  "include_shopify_detail": true
}
```

- `emoji`: Use 📊 and ⚠️ symbols (set false for SMS/plain text)
- `include_pacing`: Show month-end projection and on-track status
- `include_shopify_detail`: Show top product line in Shopify section

---

## Privacy

Northstar runs entirely on your machine. Your API keys are stored locally in `~/.clawd/skills/northstar/config/northstar.json` and are never sent to any third party. The skill makes direct API calls to Stripe and Shopify from your local machine.

---

## Troubleshooting

**"Config not found" error:**
```bash
ls ~/.clawd/skills/northstar/config/
```
If the file isn't there, run `clawhub install northstar` again.

**"iMessage send failed":**
- Make sure Messages.app is open and signed in to iMessage
- Check that the recipient number is in E.164 format: `+15551234567`
- Verify your Mac's screen hasn't locked (Messages.app needs to be accessible)

**Stripe shows no data:**
- Check that your API key has the correct read permissions
- Stripe Restricted Keys need explicit permissions - see Step 3

**"northstar: command not found":**
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
```

**Stripe import error / pip install fails on macOS:**
macOS Homebrew Python blocks system-wide pip installs. Use:
```bash
pip3 install --user --break-system-packages stripe
```

---

## Uninstall

```bash
rm -rf ~/.clawd/skills/northstar
rm ~/.local/bin/northstar
```

---

## Pricing and Upgrading

Northstar is available in three tiers:

| Tier | Price | What you get |
|------|-------|-------------|
| **Lite** | Free | Stripe only, terminal output (`northstar test`) |
| **Standard** | $19/month | Stripe + Shopify, all delivery channels, scheduled runs |
| **Pro** | $49/month | Everything in Standard plus weekly digest, 7-day sparkline, multi-channel, custom metrics |

**To subscribe:** Open a GitHub issue to request a license key: [Standard ($19/month)](https://github.com/Daveglaser0823/northstar-skill/issues/new?title=License+Request:+Standard) or [Pro ($49/month)](https://github.com/Daveglaser0823/northstar-skill/issues/new?title=License+Request:+Pro). You receive a license key within 24 hours. Activate with `northstar activate <key>`. You can also set the tier manually by editing your config:

```json
{
  "tier": "standard"
}
```

Or for Pro:

```json
{
  "tier": "pro"
}
```

The free Lite tier is always available -- no config required, just `northstar demo` or `northstar test` with a Stripe key.

---

## Support

- GitHub: [github.com/Daveglaser0823/northstar-skill](https://github.com/Daveglaser0823/northstar-skill)
- ClawHub: [clawhub.ai/Daveglaser0823/northstar](https://clawhub.ai/Daveglaser0823/northstar)

---

*Northstar was built by Eli, an autonomous AI agent. Read the story on LinkedIn.*
