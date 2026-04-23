---
name: beach-safety
version: 1.1.0
description: Comprehensive beach surf conditions via mcporter MCP call. Use when asked about surf, waves, swim conditions, rip currents, or beach safety at any beach worldwide.
---

# Beach Safety

Get surf/weather conditions for any beach using the `beach-safety` MCP server.

## Quick Usage

```bash
mcporter call beach-safety get_beach_report --args '{"beach_name": "Waikiki"}'
mcporter call beach-safety get_beach_report --args '{"beach_name": "Hapuna Beach, Hawaii"}'
```

## Tools Available

| Tool | Use Case |
|------|----------|
| `get_beach_report` | Full text report — waves, swell, wind, UV, safety score, recommendations |
| `get_beach_json` | Same data as JSON for programmatic use |
| `get_surf_forecast` | Surf-specific: wave height, swell, period, direction, rip risk |
| `get_uv_forecast` | UV index with sun protection guidance |

## Safety Score

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Generally safe | Enjoy with normal precautions |
| 7-8 | Minor concerns | Caution advised |
| 4-6 | Caution | Swim near lifeguard |
| 1-3 | Dangerous | **Stay out of the water** |

## Installation

The MCP server code lives in `projects/beach-safety-mcp/` (outside the skills tree — safe from clawhub reinstalls).

### Add to mcporter

Add this to `~/.openclaw/workspace/config/mcporter.json`:

```json
{
  "mcpServers": {
    "beach-safety": {
      "command": "python3",
      "args": ["/Users/evanfoglia/.openclaw/workspace/projects/beach-safety-mcp/src/server.py"]
    }
  }
}
```


