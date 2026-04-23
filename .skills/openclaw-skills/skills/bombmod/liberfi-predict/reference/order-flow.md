# Predict TEE Order Flow (Canonical)

This is the canonical end-to-end workflow the agent must follow when the
user asks to place a prediction market order via the **TEE auto flow**.
The user never sees POLY_* HMAC credentials, EIP-712 typed data, or
Solana transaction signatures — the LiberFi server signs everything via
the user's Privy TEE wallet.

> If the user explicitly asks to use their own Polymarket CLOB
> credentials or pre-signed Kalshi transactions, fall back to the legacy
> commands (`polymarket-order`, `kalshi-quote`, `kalshi-submit`) and
> warn that they are deprecated.

## Decision Tree

```
User says "I want to bet/buy/sell on <event>"
        │
        ├─ source = polymarket  →  see "Polymarket Flow" below
        └─ source = kalshi      →  see "Kalshi Flow" below
```

If the user did not specify a source, ask before doing anything else.

## Polymarket Flow

### Step 1 — Authentication gate

```bash
lfi status --json
```

If `authenticated: false`, run `lfi login key --json` (agent mode) or
prompt the user for `lfi login <email>` + `lfi verify <otpId> <code>`
(human mode). Do not proceed without a valid session.

### Step 2 — Setup check (idempotent)

```bash
lfi predict polymarket-setup-status --json
```

Inspect the response:

- `safe_deployed` (bool)
- `safe_address` (string, present when deployed)
- `usdc_approved` / `negrisk_approved` / `ctf_approved` (bools)

If **any** of those is `false`, run setup:

```bash
lfi predict polymarket-setup --json
```

This deploys the user's Safe wallet (Polygon) and approves all required
tokens via the Polymarket Builder Relayer. It is **gasless** (the relayer
pays) and idempotent — safe to call repeatedly. After it returns,
re-fetch `polymarket-setup-status` and confirm everything is `true`.

### Step 3 — Funding check

```bash
lfi predict polymarket-deposit-addresses --safe-address <safe_address> --json
```

Look up the Safe USDC balance (Polymarket UI shows it; or the agent can
query Polygon directly via the Bitget Wallet skill or block explorer).
**Recommend a minimum of $2 USDC on Polygon.**

If balance is insufficient:

1. Surface the **Polygon** deposit address from the response (e.g.
   `polygon` or `polygon_pos` key).
2. Tell the user: "Send at least $2 USDC on Polygon to `<address>`. The
   funds will be credited to your Polymarket Safe automatically. Run
   `lfi predict balance --source polymarket --user <address> --json` to
   re-check after the transfer confirms."
3. Stop the flow until the user confirms funding.

### Step 4 — Discover the token

If the user gave you an event slug or market URL but not a CLOB token
ID, fetch it:

```bash
lfi predict event <slug> --source polymarket --json
```

The response includes the markets with their YES/NO `clob_token_id`
values. Pick the one matching the user's intended outcome.

### Step 5 — Order parameters

Ask the user (one round trip if the intent is ambiguous):

| Question | Why |
|---|---|
| Market or limit order? | Drives `--order-type` |
| If limit: price + size + GTC vs GTD? | Required flags |
| If GTD: expiration time? | Required `--expiration` (epoch seconds) |
| If market BUY: USDC spend? | `--size` is the USDC amount |
| If market SELL: share count? | `--size` is the share count |

Optional (skip unless the user specifies): `--neg-risk`, `--fee-rate-bps`,
`--tick-size`, `--taker-address`. The server auto-resolves tick size and
fee rate via the existing PS endpoints.

### Step 6 — Confirm

Summarize the final order in plain language:

> You're about to BUY 10 shares of "Will BTC > $100k by EOY 2026 — YES"
> at $0.55/share (limit, Good-Til-Cancelled). Total cost ≈ $5.50 USDC
> plus tiny rounding. **Confirm? (yes/no)**

Wait for explicit `yes` (or Chinese equivalent). Never assume.

### Step 7 — Place

```bash
lfi predict polymarket-place \
  --token-id <id> --side BUY \
  --order-type GTC --price 0.55 --size 10 --json
```

The server:

1. Calls PS `POST /orders/polymarket/prepare` — resolves tick/fee/salt,
   builds the canonical order message, returns EIP-712 typed-data + digest.
2. Calls Privy `eth_signTypedData_v4` against the user's TEE EVM wallet.
3. Derives Polymarket L2 HMAC credentials (signed L1 ClobAuth message)
   on first use and caches them per signer.
4. Calls PS `POST /orders/polymarket/execute` — PS posts the order to
   the Polymarket CLOB on the user's behalf.

The response includes the CLOB raw response (order ID, status, etc.).

### Step 8 — Verify

```bash
lfi predict orders --source polymarket --json
```

Show the user their open orders. If they want to cancel:

```bash
lfi predict cancel <orderId> --source polymarket --json
```

L2 HMAC headers are derived automatically from the caller's TEE wallet.

## Kalshi Flow

Kalshi orders are placed via the DFlow swap pipeline, so the flow is a
single command (no Safe deployment, no approval step):

### Step 1 — Authentication gate

Same as Polymarket. Require a valid `lfi status` session.

### Step 2 — Discover the mints

```bash
lfi predict event <slug> --source kalshi --json
```

The response gives you the `input_mint` (USDC) and `output_mint` (Kalshi
outcome token mint) for the chosen market.

### Step 3 — Confirm

Summarize and wait for explicit user confirmation.

### Step 4 — Place

```bash
lfi predict kalshi-place \
  --input-mint <usdcMint> --output-mint <outcomeMint> \
  --amount 500000 --slippage-bps 100 --json
```

`--amount` is in the input token's **smallest unit** (USDC = 6 decimals,
so `500000` = $0.50). The server:

1. Calls PS `POST /orders/kalshi/quote` with `userPublicKey` taken from
   the caller's JWT.
2. Calls Privy `signTransaction` (Solana) against the user's TEE SOL
   wallet.
3. Calls PS `POST /orders/kalshi/submit` with the signed transaction.

### Step 5 — Verify

```bash
lfi predict orders --source kalshi --wallet-address <userSolAddr> --json
lfi predict trades --wallet <userSolAddr> --source kalshi --json
```

## Common Pitfalls

| Pitfall | Correct approach |
|---|---|
| Calling `polymarket-place` without setup | Always run `polymarket-setup-status` first; auto-run `polymarket-setup` if not ready |
| Ignoring the funding check | Tell the user to deposit ≥ $2 USDC to the Safe before placing the first order |
| Skipping confirmation | NEVER call any `*-place` command without explicit user confirmation |
| Mixing TEE flow with `--poly-*` flags | The TEE `polymarket-place` does not accept POLY_* — those are only for the deprecated `polymarket-order` |
| Passing `--user-public-key` to `kalshi-place` | The TEE flow auto-fills it from JWT — flag does not exist on `kalshi-place` |
| Cancelling polymarket orders by hand-rolling POLY_* | Just use `lfi predict cancel <id> --source polymarket` — server derives L2 auth |

## Error Recovery

| Error | Likely cause | Fix |
|---|---|---|
| `EVM TEE wallet not provisioned` | Caller is anonymous or session is for a SOL-only account | Run `lfi login key` to create/refresh credentials |
| `setup_required` from PS | Safe not deployed or token approval missing | Run `lfi predict polymarket-setup --json` |
| `insufficient_balance` from CLOB | Safe USDC balance too low | Show deposit address and pause flow |
| `tick_size_invalid` | Price not a multiple of tick size | Re-fetch tick size and ask user to round price |
| `signature_invalid` from CLOB | Order message changed between prepare/execute (caller bug) | Re-run `polymarket-place`; do not modify intermediate fields |
| `cancel: order_not_found` | Already filled or already cancelled | Refresh `lfi predict orders` and inform user |
