---
name: circle-chain-js-sdk
description: >-
  JavaScript SDK and CLI for Circle Chain (@lidh04/circle-chain-sdk): user auth,
  wallet, block, miner, transfers, contacts. Global CLI binary `circle`. Use when
  working in js-circle-chain-sdk, integrating Circle Chain from Node/browser, or
  when the user mentions circle-chain SDK, @lidh04/circle-chain-sdk, local mining,
  or the circle CLI.
---

# Circle Chain JavaScript SDK

## Package and layout

- **npm**: `@lidh04/circle-chain-sdk` — local dependency: `npm i @lidh04/circle-chain-sdk`
- **Default export**: an object with namespaces `user`, `wallet`, `block`, `node`, `miner`, `common` — e.g. `import sdk from '@lidh04/circle-chain-sdk'` then `const { user, wallet, miner } = sdk`. README snippets use bare names like `login`, `createWallet`; bind them from the matching namespace (`user.login`, `wallet.createWallet`, etc.).
- **Source repo**: `src/` — `circle-user.js`, `circle-wallet.js`, `circle-block.js`, `circle-node.js`, `circle-miner.js`, `circle-common.js`; CLI under `src/cli/`.

## Development workflow

1. **Build**: `npm run build` — outputs `dist/cjs` and `dist/mjs` (TypeScript + fixup).
2. **Tests**: Run `npm run build` before `npm test` when suites need fresh `dist/`. CLI-only: `npm run test:cli` (builds, then Jest matches `dist/cjs/cli`).
3. **CLI from a clone**: after build, `npm run cli -- <args>` or `node ./dist/mjs/cli/main.js <args>`.

## CLI (Commander.js)

Published executable name: **`circle`** (see `package.json` `"bin"` → `dist/mjs/cli/main.js`).

### Install globally

```bash
npm install -g @lidh04/circle-chain-sdk
circle --help
```

### Using `circle`

- **`-d` / `--dev`** — use `http://localhost:8888` instead of production (e.g. `circle --dev user login-send-code --email you@example.com`).
- Subcommand groups: **user**, **wallet**, **block**, **miner**. Discover flags with `circle <group> --help`.

```bash
circle --help
circle user --help
circle user login-send-code --email you@example.com
circle wallet query public-balance --address <addr>
circle block header-list --base-height 0
circle miner mine --address <your-miner-address>
```

### Developing this repo

```bash
npm run build
npm run cli -- --help
# or: node ./dist/mjs/cli/main.js --help
```

CLI tests: `src/cli/*.test.js`; Jest runs compiled tests under `dist/cjs/cli/` per `jest.config.cjs`.

## Programmatic usage patterns

Responses typically include `status` (e.g. `200`), `message`, and `data`. On failure, surface `response.message`.

### Auth (register / login)

1. **Register then password login**: `sendRegisterVerifyCode` → `register` → `login` (email + password).
2. **Login with verify code only**: `sendVerifyCode` → `login` (email + `verifyCode`).

### Wallet

- **`createWallet()`** — on success, address in `data`.

### Local mining

1. `miner.canMineBlock()` — return early if false.
2. `miner.fetchMyBlockData(address)` — from `data`: `blockHeaderHexString`, `channelId`.
3. `miner.mineBlock(blockHeaderHexString, workerCount)` — e.g. `os.cpus().length - 1`; result lines separated by `\n`; first line is mined header hex.
4. `miner.postMyBlock({ address, channelId, blockHeaderHexString: minedBlockHeader })`.
5. Per README: successful block upload rewards **10 cc** (**100,000 li**) to the miner address.

### Pay password

- `sendPayVerifyCode` → `setPayPassword` with `account: { email }`, `verifyCode`, `password`.

### Transfers

- **`sendTo`**: `email`, `from`, `address` (to), `transContent` (`type`, `uuid`, etc.), `payPassword`.
- **`pay`**: `from`, `to`, `value`, `payPassword`.

### Contacts

- **`addContacts`**: e.g. `email`, `name`, `sex`, `address` (location string in README).

## Versions

### 1.1.1
- README: document global CLI install (`npm install -g @lidh04/circle-chain-sdk`), using `circle` with `--dev`, and developing the repo (`npm run cli` / `node ./dist/mjs/cli/main.js`)

### 1.1.0

- CLI (Commander.js) for user, wallet, miner, block; entry **`circle`** / `main.js`.
- CLI split into `user-command`, `wallet-command`, `miner-command`, `block-command`; user CLI email-only.
- CLI tests under `src/cli`, Jest runs `dist/cjs/cli`; `circle-node` test import path fix.

### 1.0.22 — security improvements  
### 1.0.21 — bugfixes  
### 1.0.20 — local block mining

Keep this skill aligned with repo `README.md` and `package.json` (bin name, exports).
