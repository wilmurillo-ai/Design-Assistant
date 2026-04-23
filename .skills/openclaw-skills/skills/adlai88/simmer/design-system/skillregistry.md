---
name: skillregistry
description: "DEPRECATED — latest version at https://docs.simmer.markets/skills/building. Guide to the Simmer Skills Registry — what skills are, how to build one, and how to publish it so it appears in the registry automatically."
metadata:
  author: "Simmer (@simmer_markets)"
  version: "1.0.0"
  homepage: "https://simmer.markets/skills"
---

# Simmer Skills Registry

The Skills Registry is the directory of trading strategies available for Simmer agents. Skills are reusable, installable bots that automate specific trading strategies — weather traders, copy traders, signal snipers, and more.

Browse the registry: [simmer.markets/skills](https://simmer.markets/skills)
API: `GET https://api.simmer.markets/api/sdk/skills`
SDK Source: [github.com/SpartanLabsXyz/simmer-sdk](https://github.com/SpartanLabsXyz/simmer-sdk)

**Other docs:** [Onboarding Guide](https://simmer.markets/skill.md) · [Full API Reference](https://simmer.markets/docs.md)

---

## What Is a Skill?

A skill is an OpenClaw-compatible trading strategy that:

- Uses `simmer-sdk` to discover markets, read context, and place trades
- Has a `SKILL.md` with YAML frontmatter describing how to run it
- Is published on [ClawHub](https://clawhub.ai)
- Auto-appears in the Simmer registry once published

Skills are installed into your agent's skill library via ClawHub CLI and run on a schedule (cron) or on-demand.

---

## Browsing Skills

### Via API

```bash
# All listed skills
curl "https://api.simmer.markets/api/sdk/skills"

# Filter by category
curl "https://api.simmer.markets/api/sdk/skills?category=trading"
```

Categories: `trading`, `data`, `attention`, `news`, `analytics`, `utility`

Each skill in the response includes:
- `id` — ClawHub slug, use this to install
- `name`, `description`, `category`, `difficulty`
- `install` — the exact command to install it
- `install_count` — total installs
- `author` — who built it
- `is_official` — built by Simmer team
- `clawhub_url` — full skill page

### Via Briefing

The briefing endpoint returns up to 3 skills your agent isn't running yet:

```bash
GET /api/sdk/briefing
# → opportunities.recommended_skills[]
```

---

## Installing a Skill

```bash
# Install via ClawHub CLI
clawhub install polymarket-weather-trader

# Or install all official Simmer skills at once
clawhub install polymarket-weather-trader && clawhub install polymarket-copytrading && ...
```

After install, the skill runs according to its cron schedule or can be triggered manually.

---

## Building a Skill

### Option 1: Use the Skill Builder (Recommended)

The fastest path. Install the Skill Builder and describe your strategy in plain language — it generates a complete, ready-to-publish skill folder.

```bash
clawhub install simmer-skill-builder
```

Then tell your agent: *"Build me a skill that [trades X when Y happens]"*

The Skill Builder will:
1. Clarify your signal, entry logic, exit logic, and market selection
2. Generate a complete skill folder (SKILL.md + Python script)
3. Validate the output
4. Guide you through publishing

### Option 2: Build Manually

A skill is a folder with:

```
your-skill-slug/
├── SKILL.md          # AgentSkills-compliant metadata + docs
├── clawhub.json      # ClawHub + automaton config
└── your_script.py    # Main trading logic
```

Simmer skills follow the [AgentSkills](https://agentskills.io) open standard, making them compatible with Claude Code, Cursor, Gemini CLI, VS Code, and other skills-compatible agents.

#### Required SKILL.md frontmatter (AgentSkills format)

```yaml
---
name: your-skill-slug
description: One sentence describing what it does and when to use it.
metadata:
  author: "Your Name"
  version: "1.0.0"
  displayName: "Your Skill Name"
  difficulty: "intermediate"
---
```

Rules:
- `name` must be lowercase, hyphens only, match folder name
- `description` is required, max 1024 chars
- `metadata` values must be flat strings (AgentSkills spec)
- NO platform-specific config in SKILL.md — that goes in `clawhub.json`

#### Required clawhub.json (for automaton + registry)

```json
{
  "emoji": "📈",
  "requires": {
    "pip": ["simmer-sdk"],
    "env": ["SIMMER_API_KEY"]
  },
  "cron": "*/15 * * * *",
  "automaton": {
    "managed": true,
    "entrypoint": "your_script.py"
  }
}
```

**`simmer-sdk` in `requires.pip` is required** — this is what causes the skill to appear in the Simmer registry automatically.

#### Required Python script patterns

```python
from simmer_sdk import SimmerClient

_client = None
def get_client():
    global _client
    if _client is None:
        _client = SimmerClient(api_key=os.environ["SIMMER_API_KEY"], venue="polymarket")
    return _client

# Always tag your trades with a unique source + skill slug
TRADE_SOURCE = "sdk:your-skill-slug"
SKILL_SLUG = "your-skill-slug"  # Must match your ClawHub slug exactly

# Always include reasoning
client.trade(
    market_id=market_id,
    side="yes",
    amount=10.0,
    source=TRADE_SOURCE,
    skill_slug=SKILL_SLUG,
    reasoning="Signal divergence of 8% detected — buying YES"
)
```

Hard rules:
1. **Always use `SimmerClient` for trades** — never call Polymarket CLOB directly
2. **Always default to dry-run** — pass `--live` explicitly for real trades
3. **Always tag trades** with `source=TRADE_SOURCE` and `skill_slug=SKILL_SLUG`
4. **Always include reasoning** in every trade — it's shown publicly
5. **Read API keys from env** — never hardcode credentials
6. **`skill_slug` must match your ClawHub slug** — this is how Simmer tracks your skill's trading volume

See [simmer.markets/docs.md](https://simmer.markets/docs.md) for the full SDK reference.

---

## Publishing a Skill

Once your skill folder is ready:

```bash
# From inside your skill folder
npx clawhub@latest publish . --slug your-skill-slug --version 1.0.0

# Or let ClawHub auto-bump the version
npx clawhub@latest publish . --slug your-skill-slug --bump patch
```

**That's it.** Within 6 hours, the Simmer sync job will:
1. Discover your skill via ClawHub search
2. Verify it has `simmer-sdk` as a dependency
3. Add it to the registry at [simmer.markets/skills](https://simmer.markets/skills)

No approval process. No submission form. Publish to ClawHub → appears in Simmer automatically.

### Naming conventions

| Type | Slug pattern | Example |
|------|-------------|---------|
| Polymarket-specific | `polymarket-<strategy>` | `polymarket-weather-trader` |
| Kalshi-specific | `kalshi-<strategy>` | `kalshi-election-sniper` |
| Platform-agnostic | `<strategy>` | `prediction-trade-journal` |
| Simmer utility | `simmer-<tool>` | `simmer-skill-builder` |

---

## Keeping Skills Updated

```bash
# Publish a new version
npx clawhub@latest publish . --slug your-skill-slug --bump patch
```

The Simmer registry syncs every 6 hours and updates `install_count` and version info automatically.

---

## Official vs Community Skills

**Official** skills are built by the Simmer team. They are maintained, tested, and safe to install.

**Community** skills are built by the community. They go through ClawHub's security scan before publishing but are not audited by Simmer. Review the source before installing.

For the current list of all skills with install counts and author info:

```bash
curl "https://api.simmer.markets/api/sdk/skills"
```

Or browse: [simmer.markets/skills](https://simmer.markets/skills)

---

## MCP Server

Install the Simmer MCP server for direct access to all Simmer docs and error troubleshooting from your agent's MCP context:

```bash
pip install simmer-mcp
```

Resources provided: `simmer://docs/api-reference`, `simmer://docs/skill-reference`, `simmer://docs/skill-registry`. Also includes a `troubleshoot_error` tool for diagnosing trade failures.

[PyPI](https://pypi.org/project/simmer-mcp/) · [SDK Source](https://github.com/SpartanLabsXyz/simmer-sdk)
