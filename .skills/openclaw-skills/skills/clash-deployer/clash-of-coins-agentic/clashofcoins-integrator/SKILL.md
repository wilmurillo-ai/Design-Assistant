---
name: clashofcoins-integrator
description: Use when an agent or platform should integrate with the sale surface through root discovery, x402, MPP, A2A, XMTP, or scanner-facing metadata.
---

# Clash of Coins Sale Integrator

Use this skill for the sale surface only.

Do not assume both `x402` and `mpp` are enabled on every deployment. Check live discovery first.

## Base URL

- deployment-specific sale origin
- x402: `https://x402.clashofcoins.com`
- mpp: `https://mpp.clashofcoins.com`

## Read In This Order

1. `GET /openapi.json`
2. `GET /.well-known/x402` if `x402` is enabled
3. `GET /.well-known/mpp` if `mpp` is enabled
4. `GET /openapi.full.json`
5. `GET /.well-known/agent.json`
6. `GET /llms.txt`

Use `GET /openapi.json` for protocol-aware payable discovery on the current instance and `GET /openapi.full.json` for the full unified sale+shop integration contract.

## Sale Contract

Canonical sale endpoints:

- if `x402` is enabled:
  - `GET /agentic/x402/offers`
  - `GET /agentic/x402/quote`
  - `GET` or `POST /agentic/x402/buy`
  - `GET /agentic/x402/purchases/{paymentTx}`
- if `mpp` is enabled:
  - `GET /agentic/mpp/capabilities`
  - `GET /agentic/mpp/offers`
  - `POST /agentic/mpp/quote`
  - `GET` or `POST /agentic/mpp/buy`
  - `GET /agentic/mpp/purchases/{paymentTx}`

Optional sale aliases may also be present:

- `a2a`
- `xmtp`
- frames

## Integration Rules

- Treat sale discovery at root as the source of truth.
- Treat offers as dynamic.
- Preserve the same request body between unpaid and paid retries.
- Use sale routes for presale only.
- Do not infer shop support from sale support; shop is a separate surface under `/shop`.
- Prefer the canonical `mppx` SDK for Tempo MPP instead of constructing `Authorization: Payment` manually.
- If manual MPP is unavoidable, encode the Tempo transfer hash in `credential.payload.hash` with `credential.payload.type = "hash"`.

## Registry Notes

When the task is specific to a discovery consumer, also read:

- `docs/integrations/x402scan.md`
- `docs/integrations/mppscan.md`
- `docs/integrations/bazaar.md`
- `docs/integrations/402index.md`
