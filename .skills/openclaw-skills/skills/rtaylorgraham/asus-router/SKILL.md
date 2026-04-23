---
name: asus-router
description: Monitor and manage Asus routers running AsusWRT firmware. Supports status checks, device listing, presence detection, AiMesh mesh topology, WAN diagnostics, and reboots. Works with ZenWiFi, RT-AX, GT-AX, and other AsusWRT-based routers.
metadata: {"clawdbot":{"emoji":"📡","requires":{"bins":["ping"],"pip":["asusrouter","aiohttp"]}}}
---

# Asus Router Management

Manage Asus routers via the `asusrouter` Python library. Works with any Asus router running stock AsusWRT or Merlin firmware.

## Setup

### 1. Install dependencies
```bash
pip install asusrouter aiohttp
```

### 2. Create config file
Copy `config.example.yaml` to `config.yaml` and fill in your router details:
```bash
cp skills/asus-router/config.example.yaml skills/asus-router/config.yaml
```

Edit `config.yaml` with your router's IP, username, and password.

### 3. Verify connection
```bash
python3 skills/asus-router/router.py status
```

## Supported Routers
Any Asus router with the AsusWRT web interface:
- **ZenWiFi** (XT8, XT12, XD6, etc.) — full AiMesh support
- **RT-AX** series (RT-AX86U, RT-AX88U, etc.)
- **GT-AX** gaming series
- **Merlin firmware** variants
- **AiMesh nodes** (RP-AX56, RP-AX58, etc.)

## Commands

All commands use `router.py`. Activate your venv first if using one.

### Quick Status
```bash
python3 router.py status          # WAN, CPU, RAM, mesh nodes, client count
python3 router.py status --json   # Machine-readable output
```

### List Connected Devices
```bash
python3 router.py clients              # All devices
python3 router.py clients --online     # Online only
python3 router.py clients --filter "iphone"   # Search by name/IP/MAC
python3 router.py clients --json       # JSON output
```

### Who's Home (Presence Detection)
```bash
python3 router.py who
```
Checks for known devices defined in `config.yaml` to determine who's home.

### WAN Details
```bash
python3 router.py wan          # IP, gateway, DNS, lease, dual-WAN
python3 router.py wan --json
```

### AiMesh Topology
```bash
python3 router.py mesh         # Which clients connect to which node
python3 router.py mesh --json
```

### Find a Device
```bash
python3 router.py find "samsung"
python3 router.py find "192.168.1.100"
python3 router.py find "AA:BB:CC:DD:EE:FF"
```

### Network Latency Check
```bash
python3 router.py ping
```
Pings targets defined in `config.yaml` (default: gateway + Cloudflare + Google).

### Reboot Router
```bash
python3 router.py reboot --confirm
```
⚠️ Requires `--confirm` flag. Causes 2-3 min downtime.

## Common Tasks

### "Is the internet down?"
1. `status` — check WAN link state
2. `ping` — check latency to external IPs
3. `wan` — check DHCP lease and DNS

### "What's using bandwidth?"
`clients --online --json` — check `rx_speed`/`tx_speed` fields

### "Who's home?"
`who` — checks for devices listed in `config.yaml` under `known_devices`

### "Why is WiFi slow?"
1. `mesh` — check client distribution across nodes
2. `status` — check CPU/RAM (high CPU = overloaded)
3. `find <device>` — check signal strength (rssi)

## Configuration

All settings live in `config.yaml`. See `config.example.yaml` for the full template.

Key settings:
- `router.host` — Router IP address
- `router.username` — Admin username
- `router.password` — Admin password
- `router.ssl` — Use HTTPS (default: false)
- `known_devices` — Devices for presence detection
- `ping_targets` — Custom ping targets for latency checks

## JSON Output
Add `--json` to any command for machine-readable output. Useful for cron jobs, heartbeat checks, and alerting.

## Integration with Home Assistant
For persistent monitoring, also install `ha-asusrouter` via HACS:
https://github.com/Vaskivskyi/ha-asusrouter
