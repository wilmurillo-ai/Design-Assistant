---
name: atxswap
description: >-
  Manage ATX on BSC with wallet creation, price and balance queries, PancakeSwap
  V3 swaps, liquidity operations, and BNB/ERC20 transfers. Use when the user
  mentions ATX, BSC, PancakeSwap V3, wallet creation, price checks, buying,
  selling, liquidity, fees, or token transfers.
version: "0.0.2"
compatibility: Requires Node.js 18+ and npm. Network access to BSC RPC required.
inject:
  - bash: echo "${CLAUDE_SKILL_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
    as: SKILL_DIR
metadata:
  author: agentswapx
  openclaw:
    requires:
      bins:
        - node
        - npm
      env:
        - BSC_RPC_URL
    homepage: https://github.com/agentswapx/skills/tree/main/atxswap
    os:
      - linux
      - macos
---

# ATXSwap Skill

Execute ATX trading and wallet workflows on BSC. This skill is designed for
agents that need safe, repeatable commands for wallet management, ATX/USDT
quotes, swaps, V3 liquidity actions, and transfers.

- **SDK**: [`atxswap-sdk`](https://www.npmjs.com/package/atxswap-sdk) on npm ([source](https://github.com/agentswapx/atxswap-sdk))
- **Keystore dir**: `~/.config/atxswap/keystore` (fixed, not configurable)
- **Secrets dir**: `~/.config/atxswap/` (master.key + secrets.json)

## Use This Skill For

- Create or import the single wallet used by this skill instance
- Query ATX price, balances, LP positions, quotes, and arbitrary ERC20 token info
- Buy or sell ATX against USDT on PancakeSwap V3
- Add liquidity, remove liquidity, collect fees, or burn empty LP NFTs
- Transfer BNB, ATX, USDT, or arbitrary ERC20 tokens

## Before First Use

This skill ships its own Node scripts and depends on `atxswap-sdk`.

1. Open the skill directory where this `SKILL.md` is installed.
2. Run `npm install` there before using any script.
3. If `npm install` fails, stop and report the dependency error instead of guessing.

If the skill is installed via ClawHub or OpenClaw CLI, the install location is
typically `~/.clawhub/skills/atxswap/` (or the equivalent client-managed path).
If you cloned this repository directly, the location is `skills/atxswap/`.

## Script Location

Use the skill directory path to locate scripts. If `${SKILL_DIR}` is available
(injected by skills.sh-compatible runtimes), use it; otherwise use the absolute
path to this skill's installed directory.

Example:

```bash
cd skills/atxswap && npm install
cd "${SKILL_DIR}" && node scripts/wallet.js list
```

All examples below use `cd "${SKILL_DIR}" &&` for clarity. If your runtime does
not inject `${SKILL_DIR}`, replace it with the absolute path of the installed
skill directory.

## Runtime Notes

- `BSC_RPC_URL` is optional. If set, scripts use it for all BSC reads and writes.
  When unset, scripts fall back to a built-in public RPC.
- Wallet files live under `~/.config/atxswap/keystore`.
- Secure secrets live under `~/.config/atxswap/` (master.key + secrets.json).
- Only **one wallet** is allowed per skill installation. If a wallet already
  exists, `wallet.js create` and `wallet.js import` fail.
- Use `wallet.js list` before creating or importing a wallet.
- Scripts write JSON output unless the underlying command intentionally returns
  plain text, such as `wallet.js export`.
- `query.js quote` can return a JSON error if the configured Quoter or RPC
  rejects the simulation. Surface the error and do not proceed to a write.

## Password Rules

When the user asks to **create** or **import** a wallet:

1. Ask the user for a password first (do NOT generate one).
2. Pass it via `--password <pwd>` to the script when running non-interactively.
3. The password is auto-saved to secure storage after creation.
4. Never print the password back to the chat.

For **swap**, **transfer**, and **liquidity** operations, rely on auto-unlock
first. Only ask for the password if auto-unlock fails.

## Hard Safety Rules

1. Treat all BSC writes as real-asset operations.
2. **NEVER** output private keys or passwords in chat.
3. **ALWAYS** run a preview before write actions: query price, quote, balance,
   or positions as appropriate.
4. **ALWAYS** show the preview to the user and wait for explicit confirmation
   before swap, transfer, or liquidity writes.
5. **NEVER** execute large trades without the user saying "yes" or "confirm".
6. The output of `wallet.js export` must NEVER be shown to the user.

## Required Preview Flow

Before every write action:

1. Query the price, quote, balance, or positions that match the requested action.
2. Summarize the preview in plain language.
3. Ask the user to confirm.
4. Execute the write command only after confirmation.
5. Return the transaction hash and the key result fields.

## High-Value Workflows

### Check market state

```bash
cd "${SKILL_DIR}" && node scripts/query.js price
cd "${SKILL_DIR}" && node scripts/query.js balance <address>
cd "${SKILL_DIR}" && node scripts/query.js positions <address>
```

### Preview before swap

```bash
cd "${SKILL_DIR}" && node scripts/query.js quote <buy|sell> <amount>
```

### Execute after confirmation

```bash
cd "${SKILL_DIR}" && node scripts/swap.js buy <usdtAmount> [--from address] [--slippage bps] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/liquidity.js add <atxAmount> <usdtAmount> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/transfer.js atx <to> <amount> [--from address] [--password <pwd>]
```

## Command Reference

### `wallet.js`

```bash
cd "${SKILL_DIR}" && node scripts/wallet.js create [name] --password <pwd>
cd "${SKILL_DIR}" && node scripts/wallet.js list
cd "${SKILL_DIR}" && node scripts/wallet.js import <privateKey> [name] --password <pwd>
cd "${SKILL_DIR}" && node scripts/wallet.js export <address>
cd "${SKILL_DIR}" && node scripts/wallet.js has-password <address>
cd "${SKILL_DIR}" && node scripts/wallet.js forget-password <address>
```

### `query.js`

```bash
cd "${SKILL_DIR}" && node scripts/query.js price
cd "${SKILL_DIR}" && node scripts/query.js balance <address>
cd "${SKILL_DIR}" && node scripts/query.js quote <buy|sell> <amount>
cd "${SKILL_DIR}" && node scripts/query.js positions <address>
cd "${SKILL_DIR}" && node scripts/query.js token-info <tokenAddress>
```

### `swap.js`

```bash
cd "${SKILL_DIR}" && node scripts/swap.js buy <usdtAmount> [--from address] [--slippage bps] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/swap.js sell <atxAmount> [--from address] [--slippage bps] [--password <pwd>]
```

### `liquidity.js`

```bash
cd "${SKILL_DIR}" && node scripts/liquidity.js add <atxAmount> <usdtAmount> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/liquidity.js remove <tokenId> <percent> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/liquidity.js collect <tokenId> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/liquidity.js burn <tokenId> [--from address] [--password <pwd>]
```

### `transfer.js`

```bash
cd "${SKILL_DIR}" && node scripts/transfer.js bnb <to> <amount> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/transfer.js atx <to> <amount> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/transfer.js usdt <to> <amount> [--from address] [--password <pwd>]
cd "${SKILL_DIR}" && node scripts/transfer.js token <tokenAddress> <to> <amount> [--from address] [--password <pwd>]
```

## When To Refuse Or Pause

- Missing wallet but the user requests a write action
- Missing confirmation for swap, transfer, or liquidity writes
- `npm install` has not been run successfully in the skill directory
- RPC, dependency, or wallet-unlock errors that make the state unclear

## Standard Workflow

For any write action:

1. Query current price, quote, balance, or positions as needed.
2. Summarize the preview for the user.
3. Wait for explicit confirmation.
4. Execute the write command.
5. Report the transaction hash and result.
