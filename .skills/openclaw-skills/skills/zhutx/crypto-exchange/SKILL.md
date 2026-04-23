---
name: crypto-exchange
description: Lightning-fast crypto swaps. 240+ coins, best rates, done in minutes. Chat, CLI, or web — however you prefer.
---

# Crypto Exchange Skill (LightningEX)

A versatile cryptocurrency exchange service powered by LightningEX API with three interaction modes:
- **Chat Mode**: Natural language conversation for swaps and queries
- **CLI Mode**: Command-line interface for scripting and automation  
- **UI Mode**: Web-based DeFi interface for visual trading

## Quick Start

### Chat Mode (Default)
Simply talk to perform exchanges:
- "Swap 100 USDT to ETH"
- "What's the exchange rate for BTC to USDT?"
- "Show me supported tokens"
- "Check order status I1Y0EFP31Rwu"

### CLI Mode

**Run the CLI:**
```bash
# Navigate to skill directory
cd /path/to/crypto-exchange

# Start interactive wizard (default)
node exchange.js
```

**CLI Commands:**
```bash
# Start interactive wizard
node exchange.js

# List supported currencies
node exchange.js currencies

# List supported currency-network pairs
node exchange.js pair-list --send USDT --receive USDT
node exchange.js pair-list --send USDT --receive USDT --send-network TRX

# Get pair info
node exchange.js pair --send USDT --receive USDT --send-network TRX --receive-network BSC

# Check exchange rate
node exchange.js rate --send USDT --receive USDT --send-network TRX --receive-network BSC --amount 100

# Validate address
node exchange.js validate --currency USDT --network BSC --address 0x...

# Check order status
node exchange.js status --id I1Y0EFP31Rwu

# Monitor order until complete
node exchange.js monitor --id I1Y0EFP31Rwu
```

### UI Mode
```bash
# Launch web UI (default port 8080, auto-assign if occupied)
node exchange.js ui
```
Then open http://localhost:8080 (or the displayed port) in your browser for the DeFi-style trading interface.