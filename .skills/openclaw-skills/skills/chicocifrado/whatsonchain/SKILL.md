# whatsonchain

**Slug:** `whatsonchain`  
**Version:** 1.0.0

## Description

Access WhatsOnChain API for BSV/BTC blockchain data via REST calls. Manual key setup only, no automation.

## Features

- BSV mainnet and testnet data
- BTC explorer data
- Network info (difficulty, blocks, chainwork)
- Mempool statistics
- Block headers and stats
- Transaction details
- Address activity
- Inscriptions listing

## Security

- **Manual only** - No automation or credential extraction
- **No passwords** - API keys only (`mainnet_xx`)
- **No ~/.bashrc** - Use `~/.whatsonchain.conf`

## API Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/chain/info` | Network info | `bsv/main/chain/info` |
| `/mempool/info` | Mempool stats | `bsv/main/mempool/info` |
| `/block/headers` | Last 10 block headers | `bsv/main/block/headers` |
| `/block/height/{height}/stats` | Block stats | `bsv/main/block/height/942402/stats` |
| `/transactions/{txid}` | Transaction details | `bsv/main/transactions/{txid}` |
| `/addresses/{addr}/info` | Address activity | `bsv/main/addresses/{addr}/info` |
| `/inscriptions` | Inscription listing | `bsv/main/inscriptions` |

## Authentication

- **Free tier:** 3 requests/second (no API key required)
- **Premium:** Teranode platform API key
- **Header:** `Authorization: mainnet_yourapikey`

**Credentials Note:**
- The API key (`WO_API_KEY`) is optional for free-tier usage
- Export the key for premium features: `export WO_API_KEY="mainnet_yourapikey"`
- Store in `~/.whatsonchain.conf` if preferred
- No OAuth credentials or passwords are required
- Keys are plain text and stored locally
- Free tier allows 3 requests/second without any key
- Premium tier increases rate limits via API key

## Setup

1. Create account: https://platform.teranode.group
2. Get API key: https://platform.teranode.group/api-keys
3. Create project: https://platform.teranode.group/projects
4. Move API key to project (optional)
5. Export API key for premium usage (optional):
   ```bash
   export WO_API_KEY="mainnet_yourapikey"
   ```

## Usage

```bash
# Network info (free tier - no key required)
curl -s "https://api.whatsonchain.com/v1/bsv/main/chain/info"

# Mempool (free tier)
curl -s "https://api.whatsonchain.com/v1/bsv/main/mempool/info"

# Block stats (free tier)
curl -s "https://api.whatsonchain.com/v1/bsv/main/block/height/942402/stats"

# Transaction (free tier)
curl -s "https://api.whatsonchain.com/v1/bsv/main/transactions/{txid}"

# With API key (premium - optional)
curl -s -H "Authorization: mainnet_yourapikey" \
  "https://api.whatsonchain.com/v1/bsv/main/chain/info"
```

## Documentation

- [WhatsOnChain API](https://docs.whatsonchain.com/)
- [BSV Blockchain](https://docs.bsvblockchain.org/)
- [BRC Standards](https://bsv.brc.dev/)
- [Teranode Platform](https://platform.teranode.group/)

## Changelog

### v1.0.0
- Initial release with all API endpoints
- Manual key setup only, no automation
- Free tier (3 req/s) and premium tiers supported
- Credentials properly documented as optional
