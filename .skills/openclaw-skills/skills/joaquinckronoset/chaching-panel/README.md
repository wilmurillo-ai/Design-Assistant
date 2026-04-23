# Chaching Panel — OpenClaw Skill

Control a [Chaching](https://github.com/joaquinckronoset/chaching) LED panel (64x32 HUB75 on ESP32-S3) from OpenClaw.

Display text, numbers, shapes, graphs, dashboard panels, and play sounds — all via HTTP from any OpenClaw channel (WhatsApp, Telegram, Slack, etc.).

## Installation

### From ClawHub
```bash
clawhub install chaching-panel
```

### From Git
```bash
cd ~/.openclaw/skills
git clone https://github.com/joaquinckronoset/chaching-panel.git
```

## Configuration

Add the panel's IP address to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "chaching-panel": {
        "enabled": true,
        "env": {
          "CHACHING_PANEL_IP": "192.168.1.50"
        }
      }
    }
  }
}
```

Replace `192.168.1.50` with your panel's actual IP (shown on the panel during boot, or check your router's DHCP table).

## Requirements

- Chaching panel with firmware v1.7.0+ (includes the HTTP API)
- Panel and OpenClaw host on the same local network
- `curl` available on the host machine

## Usage examples

Talk to your OpenClaw agent:

- "Show HELLO in green on the panel"
- "Play the coin sound"
- "Draw a red circle in the center of the panel"
- "Show Bitcoin price at 64,770 with a chart"
- "Set panel brightness to 30%"
- "Reset the panel to normal"

## API Reference

See [SKILL.md](SKILL.md) for the complete HTTP API documentation.

## License

MIT
