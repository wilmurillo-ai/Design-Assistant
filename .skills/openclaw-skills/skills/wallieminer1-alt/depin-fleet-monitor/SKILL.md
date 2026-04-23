# DePIN Fleet Monitor

---
name: depin-fleet-monitor
description: Monitor all DePIN nodes (MastChain, Mysterium, WingBits, Acurast, NeutroneX) in one dashboard. Track earnings, device health, and network status across your entire fleet.
version: 1.0.2
author: SteamClaw
license: commercial
price: 5.00
currency: USD
tags:
  - depin
  - monitoring
  - mastchain
  - mysterium
  - wingbits
  - acurast
  - neutronex
  - fleet
  - dashboard
---

## Overview
Monitor all DePIN nodes (MastChain, Mysterium, WingBits, Acurast, NeutroneX) in one dashboard. Track earnings, device health, and network status across your entire fleet.

## Pricing
- **One-time purchase**: $5.00 USD
- **Includes**: Lifetime updates, all features
- **License**: Commercial use allowed

## Purpose
- Aggregate all DePIN node data in one place
- Track earnings across multiple networks
- Monitor device health and uptime
- Send alerts when nodes go offline
- Provide historical data and charts

## Features

### Core Features
- [x] Multi-node dashboard (MastChain, Mysterium, WingBits, Acurast, NeutroneX)
- [x] Real-time earnings tracking
- [x] Device health monitoring
- [x] Auto-alerts on offline devices
- [x] Historical data storage
- [x] Telegram notifications
- [x] ROI calculator

### Supported Networks
| Network | Type | Status |
|---------|------|--------|
| MastChain | Validator | ✅ Active |
| Mysterium | VPN Node | ✅ Active |
| WingBits | VPN Node | ✅ Active |
| Acurast | Compute | ✅ Active |
| NeutroneX | Compute | ✅ Active |

## Configuration

### Fleet Config
Located at: `~/.openclaw/workspace/config/fleet-config.json`

```json
{
  "mastchain": {
    "node1": {
      "ip": "YOUR_MASTCHAIN_IP",
      "name": "MastChain1",
      "location": "Location1",
      "web_port": 8100
    },
    "node2": {
      "ip": "YOUR_MASTCHAIN2_IP",
      "name": "MastChain2",
      "location": "Location2",
      "web_port": 8100
    }
  },
  "mysterium": {
    "node1": {
      "ip": "YOUR_MYSTERIUM_IP",
      "name": "Mysterium #1",
      "location": "Location1",
      "web_port": 4449
    },
    "node2": {
      "ip": "YOUR_MYSTERIUM2_IP",
      "name": "Mysterium #2",
      "location": "Location2",
      "web_port": 4449
    }
  },
  "acurast": {
    "wallet": "YOUR_ACURAST_WALLET_ADDRESS",
    "devices": 0
  }
}
```

## Commands

### Check Fleet Status
```
User: check depin fleet
User: hoe gaat het met mijn nodes
User: fleet status
```

### Check Specific Network
```
User: check mastchain
User: mysterium status
User: acurast earnings
```

### Get Earnings
```
User: depin earnings
User: hoeveel verdien ik
User: monthly earnings
```

## API Endpoints

### MastChain
- Web UI: `http://<ip>:8100/`
- AIS Data: `http://<ip>:8100/api/ais`

### Mysterium
- Web UI: `http://<ip>:4449/`
- Node API: `http://<ip>:4449/api/v2/node`
- Identity: `http://<ip>:4449/api/v2/identity`

### Acurast
- Dashboard: `https://hub.acurast.com/dashboard`
- Processor API: `https://hub.acurast.com/api/processors`

### WingBits
- Web UI: `http://<ip>:8080/`
- Status API: `http://<ip>:8080/api/status`

### NeutroneX
- Dashboard: `https://neutronex.io/dashboard`
- Wallet: Solana address

## Heartbeat Integration

### Every 5 Minutes
- Check all node statuses
- Update earnings data
- Alert on offline devices

### Every Hour
- Calculate hourly earnings
- Store historical data

### Daily
- Generate earnings report
- Calculate ROI

## Files

```
skills/depin-fleet-monitor/
├── SKILL.md           # This file
├── index.js           # Main skill handler
├── lib/
│   ├── mastchain.js   # MastChain API wrapper
│   ├── mysterium.js   # Mysterium API wrapper
│   ├── acurast.js     # Acurast API wrapper
│   ├── wingbits.js    # WingBits API wrapper
│   ├── neutronex.js   # NeutroneX API wrapper
│   ├── earnings.js    # Earnings calculator
│   ├── alerts.js      # Alert manager
│   └── history.js     # Historical data tracker
├── config/
│   └── fleet.json     # Fleet configuration
└── data/
    ├── earnings/      # Historical earnings
    └── alerts.json    # Alert history
```

## Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Node Offline | >5 min | >15 min |
| Earnings Drop | -50% | -90% |
| High Temp | >55°C | >60°C |
| Low Memory | >85% | >95% |

## Example Output

```
📊 DePIN Fleet Monitor - 2026-03-27 00:13

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏭 MASTCHAIN (2 nodes)
├── MastChain1: ✅ Online (21,129 messages)
├── MastChain2: ✅ Online (1,195 ships)
└── Status: All nodes operational

🔒 MYSTERIUM (2 nodes)
├── Mysterium #1: ✅ Online (Bureau)
├── Mysterium #2: ✅ Online (Schoonmoeder)
└── Status: All nodes operational

📱 ACURAST (13 devices)
├── Devices: 13 online
├── Wallet: YOUR_WALLET_ADDRESS
└── Status: Mining active

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 ESTIMATED EARNINGS (24h)
├── MastChain: ~0.5 MAST
├── Mysterium: ~0.2 MYST
├── Acurast: ~13 ACU
└── Total: ~$X.XX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ ALERTS: None
✅ Fleet Health: 100%
```

## Installation

1. Copy skill to `~/.openclaw/workspace/skills/depin-fleet-monitor/`
2. Configure fleet in `~/.openclaw/workspace/config/fleet-config.json`
3. Run: `openclaw skills enable depin-fleet-monitor`

## Future Enhancements
- [x] Mobile app integration
- [x] Historical charts
- [x] ROI calculator
- [x] Multi-wallet support
- [x] Telegram alerts
- [ ] Web dashboard
- [ ] Email notifications
- [ ] Slack integration
- [ ] Discord bot integration