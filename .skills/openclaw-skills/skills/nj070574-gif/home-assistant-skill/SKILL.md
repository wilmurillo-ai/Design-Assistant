---
name: home-assistant
description: Control and query Home Assistant via natural language. Covers lights, switches, climate, temperature sensors, cameras, automations, energy monitoring, EV chargers, presence detection, and home summaries. Works with Telegram and any OpenClaw channel.
version: 2.0.0
tags: [home-assistant, smart-home, iot, telegram, lights, heating, climate, cameras, energy, automation, switches, sensors]
author: nj070574-gif
license: MIT
repository: https://github.com/nj070574-gif/openclaw-homeassistant-skill
---

# Home Assistant Skill for OpenClaw

Control and query your Home Assistant smart home in plain English through Telegram or any OpenClaw channel.

## What You Can Say

| Phrase | What happens |
|--------|-------------|
| `Home summary` | Temperatures, lights on, heating status, active switches |
| `What is the temperature?` | All temperature sensors with current readings |
| `Turn off the living room lights` | Calls `light.turn_off` |
| `Set the heating to 21 degrees` | Calls `climate.set_temperature` |
| `Is the EV charger on?` | Reads the switch state |
| `Show me the front door camera` | Returns snapshot URL |
| `List all my automations` | Shows enabled/disabled automations |
| `Is anyone home?` | Reads presence/person entity states |
| `What is my energy consumption?` | All power/energy sensors |
| `Turn on lights at 80% brightness` | Service call with brightness attribute |

## Requirements

- Home Assistant 2023.1 or newer (REST API enabled by default)
- Python 3.9+ on your OpenClaw server
- `requests` + `urllib3` Python packages

## Setup (5 minutes)

### 1. Generate a Home Assistant Token

In Home Assistant: **Profile** (bottom-left) → **Security** → **Long-Lived Access Tokens** → **Create Token**

> Copy the token immediately — it is only shown once.

### 2. Add credentials to openclaw.json

```json
{
  "env": {
    "HOME_ASSISTANT_URL":   "http://homeassistant.local:8123",
    "HOME_ASSISTANT_TOKEN": "your-long-lived-token-here"
  }
}
```

Using HTTPS with a self-signed certificate? Also add:
```json
"HOME_ASSISTANT_SSL_VERIFY": "false"
```

### 3. Restart OpenClaw

```bash
sudo systemctl restart openclaw
```

### 4. Test

Send your bot: `home summary`

## Credential Priority

The skill checks in this order — no credentials go in the skill file itself:

1. `HOME_ASSISTANT_TOKEN` system environment variable
2. `openclaw.json` env block (recommended)
3. `~/.openclaw/workspace/.secrets/home_assistant.token` (line 1: token, line 2: URL)

## SSL / HTTPS Support

| Variable | Purpose |
|----------|---------|
| `HOME_ASSISTANT_SSL_VERIFY` | Set `false` for self-signed certs |
| `HOME_ASSISTANT_CA_CERT` | Path to your CA cert file |

## Available Snippets (15)

| Snippet | What it does |
|---------|-------------|
| `_load_config` | Loads credentials — always runs first |
| `check_api` | Tests HA connectivity |
| `ha_summary_for_telegram` | Full home summary |
| `get_temperature_sensors` | All temperature sensors |
| `get_lights` | Lights with brightness |
| `get_switches` | All switches |
| `get_climate` | Thermostat status |
| `call_service` | Control any device |
| `search_entities` | Find entities by keyword |
| `get_cameras` | Camera list + snapshot URLs |
| `camera_snapshot` | Download camera image |
| `get_automations` | All automations |
| `trigger_automation` | Fire a specific automation |
| `get_energy` | Energy/power sensors |
| `send_notification` | Send via HA notify service |

## Troubleshooting

**`HOME_ASSISTANT_TOKEN not configured`**
Token not found. Check the `env` block in `openclaw.json` and restart OpenClaw.
Quick fix: `bash fix-token-config.sh` from the repo directory.

**`401 Unauthorized`**
Token expired. Regenerate: HA → Profile → Security → Long-Lived Access Tokens.

**`SSL certificate verify failed`**
Add `"HOME_ASSISTANT_SSL_VERIFY": "false"` to your `openclaw.json` env block.

## Full Source

GitHub: https://github.com/nj070574-gif/openclaw-homeassistant-skill

Includes `install.sh` (interactive installer with connectivity test) and `fix-token-config.sh` for common token errors.
