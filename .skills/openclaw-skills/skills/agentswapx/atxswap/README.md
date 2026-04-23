# ATXSwap Skill

A single skill bundle for ATX trading on BSC. Works with **Claude / Cursor /
Codex CLI** (skills.sh runtime) and **OpenClaw / ClawHub** out of the same
directory, using a unified `SKILL.md` that declares both conventions.

[**中文文档**](./README.zh.md)

- **GitHub**: https://github.com/agentswapx/skills
- **SDK on npm**: [`atxswap-sdk`](https://www.npmjs.com/package/atxswap-sdk)
- **SDK source / docs**: [agentswapx/atxswap-sdk](https://github.com/agentswapx/atxswap-sdk)

## What This Skill Covers

- Create or import the single wallet used by the skill
- Query ATX price, balances, LP positions, and ERC20 token info
- Buy or sell ATX against USDT on PancakeSwap V3
- Add liquidity, remove liquidity, collect fees, and burn empty LP NFTs
- Transfer BNB, ATX, USDT, or arbitrary ERC20 tokens

## Directory Layout

```text
atxswap/
├── SKILL.md
├── README.md
├── README.zh.md
├── PUBLISH.md
├── CHANGELOG.md
├── .clawhubignore
├── .gitignore
├── package.json
└── scripts/
    ├── _helpers.js
    ├── wallet.js
    ├── query.js
    ├── swap.js
    ├── liquidity.js
    └── transfer.js
```

## Install

### OpenClaw / ClawHub (one-click)

```bash
openclaw skills install atxswap
# or
clawhub install atxswap
```

### Manual / skills.sh runtime

```bash
git clone https://github.com/agentswapx/skills.git
cd skills/atxswap && npm install
```

Optional RPC override:

```bash
export BSC_RPC_URL="https://bsc-rpc.publicnode.com"
```

## Common Commands

```bash
cd skills/atxswap && node scripts/wallet.js list
cd skills/atxswap && node scripts/query.js price
cd skills/atxswap && node scripts/query.js quote buy 1
```

When invoked through a `${SKILL_DIR}`-aware runtime, `cd "${SKILL_DIR}"` is
preferred so the skill works regardless of where the client installed it.

## Security Rules

1. Never expose private keys or passwords in chat output.
2. Always preview price, quote, balance, or positions before write actions.
3. Always wait for explicit user confirmation before swap, transfer, or liquidity writes.
4. Treat all write actions as mainnet asset operations.
