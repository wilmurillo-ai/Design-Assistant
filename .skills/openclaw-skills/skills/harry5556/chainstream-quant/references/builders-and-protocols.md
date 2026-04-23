# Builders and Protocols Reference

All supported DEXes, aggregators, bridges, and launchpad platforms.

## Swap Aggregators

Route across multiple DEXes for best price.

### Jupiter

| Property | Value |
|----------|-------|
| Builder ID | `jupiter` |
| Chains | Solana |
| Type | Aggregator |
| DEXes Routed | 20+ (Raydium, Orca, Meteora, Lifinity, etc.) |
| Features | Split routing, limit orders, DCA |

Best for Solana swaps — aggregates across all major Solana DEXes.

### Kyberswap

| Property | Value |
|----------|-------|
| Builder ID | `kyberswap` |
| Chains | Ethereum, BSC, Base, Polygon, Arbitrum, Avalanche, Optimism |
| Type | Aggregator |
| Features | Dynamic routing, MEV protection |

Multi-chain EVM aggregator with MEV protection.

### OpenOcean

| Property | Value |
|----------|-------|
| Builder ID | `openocean` |
| Chains | Ethereum, BSC, Base, Polygon, Arbitrum, Avalanche |
| Type | Aggregator |
| Features | Cross-DEX routing, limit orders |

Alternative EVM aggregator with competitive routing.

## Single-DEX Providers

Trade directly on a specific DEX.

### Uniswap V3

| Property | Value |
|----------|-------|
| Builder ID | `uniswap` |
| Chains | Ethereum, Base, Arbitrum, Polygon, Optimism |
| Type | Provider (single DEX) |
| Features | Concentrated liquidity, multiple fee tiers |

### PancakeSwap

| Property | Value |
|----------|-------|
| Builder ID | `pancakeswap` |
| Chains | BSC, Ethereum, Base |
| Type | Provider (single DEX) |
| Features | V3 concentrated liquidity, farming |

## Bridge Aggregators

### LiFi

| Property | Value |
|----------|-------|
| Builder ID | `lifi` |
| Source Chains | Solana, Ethereum, BSC, Base, Polygon, Arbitrum, Avalanche, Optimism, zkSync |
| Type | Bridge Aggregator |
| Bridges Routed | Wormhole, Stargate, Hop, Across, etc. |
| Features | Cross-chain swap + bridge, optimal route across bridges |

Primary bridge solution — aggregates across 10+ bridge protocols.

### FlowBridge

| Property | Value |
|----------|-------|
| Builder ID | `flowbridge` |
| Chains | EVM chains |
| Type | Bridge |
| Features | Fast EVM-to-EVM transfers |

## Launchpad Platforms

### PumpFun

| Property | Value |
|----------|-------|
| Builder ID | `pumpfun` |
| Chain | Solana |
| Type | Launchpad |
| Features | Bonding curve token creation, auto-migration to Raydium |

The dominant Solana token launchpad. Tokens graduate and migrate to Raydium when bonding curve completes.

### Raydium LaunchLab

| Property | Value |
|----------|-------|
| Builder ID | `raydium-launchlab` |
| Chain | Solana |
| Type | Launchpad |
| Features | Bonding curve, direct Raydium pool migration |

Raydium's native launchpad — tokens migrate directly to Raydium pools.

## Chain Support Matrix

| Chain | Aggregators | Providers | Bridges | Launchpads |
|-------|-------------|-----------|---------|------------|
| Solana | Jupiter | — | LiFi | PumpFun, Raydium LaunchLab |
| BSC | Kyberswap, OpenOcean | PancakeSwap | LiFi | — |
| Ethereum | Kyberswap, OpenOcean | Uniswap | LiFi, FlowBridge | — |
| Base | Kyberswap, OpenOcean | Uniswap, PancakeSwap | LiFi, FlowBridge | — |
| Polygon | Kyberswap, OpenOcean | Uniswap | LiFi | — |
| Arbitrum | Kyberswap, OpenOcean | Uniswap | LiFi | — |
| Avalanche | Kyberswap, OpenOcean | — | LiFi | — |
| Optimism | Kyberswap | Uniswap | LiFi | — |
| zkSync | — | — | LiFi | — |

## EVM Chain IDs

| Chain | Chain ID | Used In |
|-------|----------|---------|
| Ethereum | 1 | x402, Bridge |
| BSC | 56 | Swap, Bridge |
| Base | 8453 | x402 payment, Swap, Bridge |
| Polygon | 137 | Bridge |
| Arbitrum | 42161 | Bridge |
| Avalanche | 43114 | Bridge |
| Optimism | 10 | Bridge |
| zkSync | 324 | Bridge |
| Base Sepolia | 84532 | x402 testnet |
