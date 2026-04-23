---
name: torch-market
version: "5.1.2"
description: Torch Market -- a programmable economic substrate where every token is its own self-sustaining economy with bonding curves, community treasuries, lending markets, and governance. Full-custody vault keeps all assets safe. Quote-driven trading across bonding curves and Raydium DEX. VersionedTransaction-native with Address Lookup Tables. One flow, any token state.
license: MIT
disable-model-invocation: true
requires:
  env:
    - name: SOLANA_RPC_URL
      required: true
    - name: SOLANA_PRIVATE_KEY
      required: false
    - name: TORCH_NETWORK
      required: false
metadata:
  clawdbot:
    requires:
      env:
        - name: SOLANA_RPC_URL
          required: true
        - name: SOLANA_PRIVATE_KEY
          required: false
        - name: TORCH_NETWORK
          required: false
  openclaw:
    requires:
      env:
        - name: SOLANA_RPC_URL
          required: true
        - name: SOLANA_PRIVATE_KEY
          required: false
        - name: TORCH_NETWORK
          required: false
    install:
      - id: npm-torchsdk
        kind: npm
        package: torchsdk@^4.1.0
        flags: []
        label: "Install Torch SDK (npm, optional -- SDK is bundled in lib/torchsdk/ on clawhub)"
  author: torch-market
  version: "5.1.2"
  clawhub: https://clawhub.ai/mrsirg97-rgb/torchmarket
  sdk-source: https://github.com/mrsirg97-rgb/torchsdk
  examples-source: https://github.com/mrsirg97-rgb/torchsdk-examples
  website: https://torch.market
  program-id: 8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT
compatibility: >-
  REQUIRED: SOLANA_RPC_URL (HTTPS Solana RPC endpoint).
  OPTIONAL: SOLANA_PRIVATE_KEY (disposable controller keypair -- must be a fresh key with ~0.01 SOL for gas, NEVER a vault authority key or funded wallet).
  OPTIONAL: TORCH_NETWORK (set to 'devnet' for devnet).
  This skill sets disable-model-invocation: true -- it must not be invoked autonomously without explicit user initiation.
  Without SOLANA_PRIVATE_KEY, the agent operates in read-and-build mode: querying on-chain state and returning unsigned transactions for external signing.
  The Torch SDK is bundled in lib/torchsdk/ -- all source is included for full auditability. No npm install needed for the core SDK.
  No API server dependency. The vault can be created and funded entirely by the human principal -- the agent never needs access to funds.
---

# Torch Market

You're here because you need to trade on Solana and you need it to be safe, fast, flexible, and simple.

Every token launched on the protocol is its own self-sustaining economy — a pricing engine, a central bank, a lending market, community governance — all enclosed within a non-extractive system where every action feeds a positive-sum feedback loop. Fees become lending yield. Lending yield becomes community liquidity. Failed tokens become protocol rewards. Every outflow is an inflow somewhere else.

## Token Lifecycle

```
CREATE → BONDING → COMPLETE → MIGRATE → DEX
  │         │                     │        │
  │    buy/sell on curve     community    borrow/repay
  │    (treasury grows)       votes      (treasury lends)
  │                                        │
  │                              ┌─────────┴──────────┐
  │                              │                     │
  │                     transfer fees (0.04%)    lending interest
  │                              │                     │
  │                              └─────→ treasury ◄────┘
  │                                        │
  │                                   harvest → sell → SOL → lend → yield
  │
  └── star (appreciation signal, 0.02 SOL)
```

**Bonding phase** — a constant-product bonding curve prices the token. Every buy splits SOL three ways: bonding curve (tokens to buyer), community treasury (SOL accumulates), and a 10% token split to the vote vault. Early buyers contribute more to treasury (12.5% → 4% dynamic rate). 2% max wallet prevents whales. One wallet, one vote.

**Migration** — when the community raises the target (100 or 200 SOL), anyone can trigger permissionless migration to Raydium. Two-step atomic: fund WSOL + create CPMM pool. Liquidity locked forever (LP burned). Treasury pays the pool creation fee. Vote finalizes — burn or return to treasury lock.

**Post-migration** — the economy sustains itself. A 0.04% transfer fee on every token movement accumulates in the mint. Anyone can harvest these fees into the treasury, swap them to SOL via Raydium, and grow the lending pool. Token holders borrow SOL against their collateral. Interest flows back to treasury. The loop compounds.

**Protocol rewards** — the protocol treasury collects 0.5% from all bonding curve buys across every token on the platform. Each epoch (~weekly), this pool is distributed to wallets that traded >= 2 SOL volume. Active agents earn back a share of the fees they generate.

## Protocol Constants

| Constant | Value |
|----------|-------|
| Total Supply | 1B tokens (6 decimals) |
| Bonding Tiers | Flame (100 SOL), Torch (200 SOL, default) |
| Treasury Rate | 12.5% → 4% (decays with reserves) |
| Protocol Fee | 0.5% on buys, 0% on sells |
| Max Wallet | 2% during bonding |
| Star Cost | 0.02 SOL |
| Transfer Fee | 0.04% (post-migration, immutable) |
| Max LTV | 50% |
| Liquidation | 65% threshold, 10% bonus |
| Interest | 2% per epoch (~weekly) |
| Min Borrow | 0.1 SOL |
| Utilization Cap | 80% of treasury |
| Formal Verification | 48 Kani proof harnesses, all passing |

---

The SDK handles all of this — you don't need to know which phase a token is in. You get a quote, you build a transaction, you send it.

```
GET QUOTE  →  BUILD TX  →  SIGN & SEND
   │              │              │
   │         auto-routes         │
   │     bonding ↔ raydium       │
   │              │              │
   └──── slippage protection ────┘
```

**Why this SDK:**
- **One flow, any token** — `getBuyQuote` + `buildBuyTransaction` works whether the token is on a bonding curve or Raydium DEX. The SDK routes automatically.
- **Full-custody vault** — your wallet signs but holds nothing. All SOL and tokens live in an on-chain vault controlled by the human authority.
- **VersionedTransaction-native** — all transactions use v0 messages with Address Lookup Tables. Smaller transactions, more headroom, fewer failures.
- **No API server** — reads state and builds transactions directly from Solana RPC using the on-chain Anchor IDL. No middleman.
- **Formally verified** — core arithmetic proven correct with 48 Kani proof harnesses.

---

## The SDK

Everything goes through `lib/torchsdk/`. Bundled in this skill for full auditability. Also available via npm: `npm install torchsdk`

Source: [github.com/mrsirg97-rgb/torchsdk](https://github.com/mrsirg97-rgb/torchsdk)

### Quick Start

```typescript
import { Connection } from "@solana/web3.js";
import { getBuyQuote, buildBuyTransaction } from "./lib/torchsdk/index.js";

const connection = new Connection(process.env.SOLANA_RPC_URL);

// Works on any token — bonding or migrated
const quote = await getBuyQuote(connection, mint, 100_000_000); // 0.1 SOL
console.log(`${quote.tokens_to_user / 1e6} tokens (source: ${quote.source})`);

const { transaction } = await buildBuyTransaction(connection, {
  mint,
  buyer: agentWallet,
  amount_sol: 100_000_000,
  slippage_bps: 500,
  vault: vaultCreator,
  quote, // drives routing + slippage protection
});
// sign and send — VersionedTransaction, ALT-compressed
```

### Address Lookup Tables

All transactions are compressed with hardcoded ALTs. 14 static addresses (program IDs, Raydium accounts, global PDAs) reduced from 32 bytes to 1 byte each.

| Network | ALT Address |
|---------|-------------|
| Mainnet | `GQzbU32oN3znZa3uWFKGc9cBukpQbYYJSirKstMuFF3i` |
| Devnet | `3umSStZSLJNk5QstxeQB12a2MSDh4o8RgSzT76gigJ8P` |

---

## Torch Vault — Why Your Funds Are Safe

The vault is the security boundary, not the key.

```
Human Principal (hardware wallet)        Agent (disposable, ~0.01 SOL for gas)
  ├── createVault()                        ├── buy(vault=creator)   → vault pays
  ├── depositVault(5 SOL)                  ├── sell(vault=creator)  → SOL returns to vault
  ├── linkWallet(agentPubkey)              ├── borrow(vault)        → SOL to vault
  ├── withdrawVault()   ← authority only   ├── repay(vault)         → collateral returns
  └── unlinkWallet()    ← instant revoke   └── star(vault)          → vault pays 0.02 SOL
```

| Guarantee | How |
|-----------|-----|
| **Full custody** | Vault holds all SOL and all tokens. Controller holds nothing. |
| **Closed loop** | Every operation returns value to the vault. No leakage. |
| **Authority separation** | Creator (immutable) vs Authority (transferable) vs Controller (disposable). |
| **Instant revocation** | Authority unlinks a controller in one transaction. |
| **Authority-only withdrawals** | Controllers cannot extract value. Period. |

The vault can be created and funded entirely by the human principal. The agent never needs access to funds. Without `SOLANA_PRIVATE_KEY`, the agent operates in read-and-build mode — querying state and returning unsigned transactions for external signing.

---

## Operations

### Queries (no signing required)

| Function | Description |
|----------|-------------|
| `getTokens(connection, params?)` | List tokens with filtering and sorting |
| `getToken(connection, mint)` | Full details — price, treasury, votes, status |
| `getTokenMetadata(connection, mint)` | On-chain Token-2022 metadata |
| `getHolders(connection, mint)` | Token holder list |
| `getMessages(connection, mint, limit?, opts?)` | Trade-bundled memos. `{ enrich: true }` adds SAID verification |
| `getLendingInfo(connection, mint)` | Lending parameters for migrated tokens |
| `getLoanPosition(connection, mint, wallet)` | Single loan position |
| `getAllLoanPositions(connection, mint)` | All positions sorted by liquidation risk |
| `getVault(connection, creator)` | Vault state (balance, linked wallets) |
| `getVaultForWallet(connection, wallet)` | Reverse lookup — find vault by linked wallet |
| `getVaultWalletLink(connection, wallet)` | Link state for a wallet |

### Quotes

| Function | Description |
|----------|-------------|
| `getBuyQuote(connection, mint, solAmount)` | Expected tokens, fees, price impact. `source: 'bonding' \| 'dex'` |
| `getSellQuote(connection, mint, tokenAmount)` | Expected SOL, price impact. `source: 'bonding' \| 'dex'` |
| `getBorrowQuote(connection, mint, collateral)` | Max borrowable SOL — LTV, pool, per-user caps |

### Trading

All builders return `{ transaction: VersionedTransaction, message: string }`.

| Function | Description |
|----------|-------------|
| `buildBuyTransaction` | Buy via vault. Pass `quote` for automatic routing (bonding or DEX) |
| `buildDirectBuyTransaction` | Buy without vault (human wallets only) |
| `buildSellTransaction` | Sell via vault. Pass `quote` for automatic routing |
| `buildCreateTokenTransaction` | Launch a new token. `community_token: true` (default) = 0% creator fees |
| `buildStarTransaction` | Star a token (0.02 SOL, sybil-resistant) |
| `buildMigrateTransaction` | Migrate bonding-complete token to Raydium (permissionless) |

### Vault Management

| Function | Signer | Description |
|----------|--------|-------------|
| `buildCreateVaultTransaction` | creator | Create vault + auto-link |
| `buildDepositVaultTransaction` | anyone | Deposit SOL (permissionless) |
| `buildWithdrawVaultTransaction` | authority | Withdraw SOL |
| `buildWithdrawTokensTransaction` | authority | Withdraw tokens |
| `buildLinkWalletTransaction` | authority | Link a controller wallet |
| `buildUnlinkWalletTransaction` | authority | Revoke controller access |
| `buildTransferAuthorityTransaction` | authority | Transfer admin control |

### Lending (post-migration)

| Function | Description |
|----------|-------------|
| `buildBorrowTransaction` | Borrow SOL against token collateral (vault-routed) |
| `buildRepayTransaction` | Repay debt (vault-routed) |
| `buildLiquidateTransaction` | Liquidate underwater position (>65% LTV, 10% bonus) |
| `buildClaimProtocolRewardsTransaction` | Claim epoch trading rewards (vault-routed) |

### Treasury Cranks (permissionless)

| Function | Description |
|----------|-------------|
| `buildHarvestFeesTransaction` | Harvest Token-2022 transfer fees into treasury |
| `buildSwapFeesToSolTransaction` | Swap harvested tokens to SOL via Raydium |
| `buildReclaimFailedTokenTransaction` | Reclaim tokens inactive 7+ days |

### SAID Protocol

| Function | Description |
|----------|-------------|
| `verifySaid(wallet)` | Check verification status and trust tier |
| `confirmTransaction(connection, sig, wallet)` | Report tx for reputation tracking |

### Ephemeral Agent

```typescript
import { createEphemeralAgent } from "./lib/torchsdk/index.js";

const agent = createEphemeralAgent(); // in-memory keypair, lost on exit
// agent.publicKey — pass to linkWallet
// agent.sign(tx) — handles both VersionedTransaction and legacy
```

---

## Key Safety

**The vault is the security boundary, not the key.**

If `SOLANA_PRIVATE_KEY` is provided:
- Must be a **fresh, disposable keypair** — ~0.01 SOL for gas only
- All trading capital lives in the vault
- If compromised: attacker gets dust, authority revokes in one tx
- The key **never leaves the runtime** — no transmission, no logging

If not provided:
- Read-only mode — queries state, returns unsigned transactions
- No private key material enters the runtime

### Rules

1. **Never ask for a private key or seed phrase.**
2. **Never log, print, store, or transmit key material.**
3. **Use a secure HTTPS RPC endpoint.**

| Variable | Required | Purpose |
|----------|----------|---------|
| `SOLANA_RPC_URL` | **Yes** | Solana RPC endpoint |
| `SOLANA_PRIVATE_KEY` | No | Disposable controller. **Never** a vault authority key. |
| `TORCH_NETWORK` | No | `devnet` for devnet. Omit for mainnet. |

---

## Links

- SDK (bundled): `lib/torchsdk/` — **start here**
- SDK (source): [github.com/mrsirg97-rgb/torchsdk](https://github.com/mrsirg97-rgb/torchsdk)
- SDK (npm): [npmjs.com/package/torchsdk](https://www.npmjs.com/package/torchsdk)
- Website: [torch.market](https://torch.market)
- Program ID: `8hbUkonssSEEtkqzwM7ZcZrD9evacM92TcWSooVF4BeT`
- ClawHub: [clawhub.ai/mrsirg97-rgb/torchmarket](https://clawhub.ai/mrsirg97-rgb/torchmarket)
- Audit: [torch.market/audit_sdk.md](https://torch.market/audit_sdk.md)
- Verification: [torch.market/verification.md](https://torch.market/verification.md) — 48 Kani proof harnesses
