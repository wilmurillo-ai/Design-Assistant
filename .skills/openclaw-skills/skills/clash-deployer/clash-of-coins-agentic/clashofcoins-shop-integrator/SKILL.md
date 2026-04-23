---
name: clashofcoins-shop-integrator
description: Use when an agent or platform should integrate with the Clash of Coins shop surface through shop discovery, x402, Tempo MPP, scanners, or OpenAPI metadata.
---

# Clash of Coins Shop Integrator

Use this skill for the shop surface only.

Do not assume both `x402` and `mpp` are enabled on every deployment. Check live discovery first.

## Base URL

- x402 gateway origin: `https://x402.clashofcoins.com`
- x402 shop root: `https://x402.clashofcoins.com/shop`
- mpp gateway origin: `https://mpp.clashofcoins.com`
- mpp shop root: `https://mpp.clashofcoins.com/shop`

## Read In This Order

1. `GET /shop/openapi.json`
2. `GET /shop/openapi.full.json`
3. `GET /shop/.well-known/agent.json`
4. `GET /shop/.well-known/x402` if `x402` is enabled
5. `GET /shop/.well-known/mpp` if `mpp` is enabled
6. `GET /shop/llms.txt`

Use `GET /shop/openapi.json` for protocol-aware payable shop discovery on the current instance. Use `GET /shop/openapi.full.json` for the full shop contract.

## Shop Contract

- personalized catalog from Clash backend
- exactly one recipient identifier per request
- backend delivery after payment settlement

## Channel Model

- shop `x402`
  - Base / USDC
  - one distinct item per request
- shop `mpp`
  - Tempo `tempo/charge`
  - supports carts

Both channels share:

- the same recipient validation
- the same catalog source
- the same SQLite ledger
- the same backend delivery pipeline

## Catalog Rules

- Always request a personalized catalog:
  - `GET /shop/api/shop/items?nickname=<player>`
  - or `GET /shop/api/shop/items?address=<0x...>`
- Do not assume a global anonymous catalog.
- Do not hardcode item ids or prices.

## Scanner Notes

Shop discovery routes:

- `GET /shop/openapi.json`
- `GET /shop/openapi.full.json`
- `GET /shop/llms.txt`
- `GET /shop/skill.md`
- `GET /shop/.well-known/agent.json`
- `GET /shop/.well-known/agents.json`
- `GET /shop/.well-known/402index-verify.txt`
- `GET /shop/.well-known/x402` if `x402` is enabled
- `GET /shop/.well-known/mpp` if `mpp` is enabled

Probe-compatible buy routes:

- `GET /shop/x402/buy` if `x402` is enabled
- `GET /shop/mpp/buy` if `mpp` is enabled

## Integration Rules

- Preserve request bodies between unpaid and paid retries.
- For shop `x402`, send paid retries in `PAYMENT-SIGNATURE`.
- For shop `x402`, copy `resource` and one `accepted` payment requirement from the latest `PAYMENT-REQUIRED` challenge into the encoded payment payload.
- For shop `x402`, settle through the facilitator before sending the paid retry.
- Prefer the canonical `mppx` SDK for Tempo MPP instead of constructing `Authorization: Payment` manually.
- If manual MPP is unavoidable, encode the Tempo transfer hash in `credential.payload.hash` with `credential.payload.type = "hash"`.
- Prefer `GET /shop/purchase-status/{purchaseId}` for user-facing status.
- Expect optional gateway discount fields in the shop catalog and quote responses.

## Registry Notes

When the task is scanner or registry specific, also read:

- `docs/integrations/x402scan.md`
- `docs/integrations/mppscan.md`
- `docs/integrations/bazaar.md`
- `docs/integrations/402index.md`
