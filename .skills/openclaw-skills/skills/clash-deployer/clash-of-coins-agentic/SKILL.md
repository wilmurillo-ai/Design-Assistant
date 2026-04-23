---
name: clashofcoins
description: Use when an agent should interact with the unified Clash of Coins commerce gateway and choose the correct sale or shop checkout surface.
---

# Clash of Coins Commerce

Use this skill as the top-level router for the unified `x402-sale` gateway.

Protocol availability is deployment-specific. Some instances are `x402`-only, some are `mpp`-only, and some expose both. Check live discovery before choosing a payment path.

## Base URL

- deployment-specific public origin
- x402: `https://x402.clashofcoins.com`
- mpp: `https://mpp.clashofcoins.com`

## Surfaces

### Sale

- discovery at the domain root
- paid routes under `/agentic/*`
- use for presale lots and Agentic Passes that mint NFTs
- x402-only and mpp-only deployments may use different public hosts

### Shop

- discovery under `/shop/*`
- paid routes under `/shop/*`
- use for recipient-scoped in-game goods delivered by the backend
- use `/shop/openapi.full.json` for the full shop contract
- use `/shop/openapi.json` for protocol-aware payable discovery on the current shop instance
- shop usually lives on the same host as the active sale surface for that deployment

## Included Skills

- `clashofcoins-buyer`
  - sale purchase flow
- `clashofcoins-integrator`
  - sale discovery and protocol integration
- `clashofcoins-shop-buyer`
  - shop purchase flow
- `clashofcoins-shop-integrator`
  - shop discovery and protocol integration

## Routing Rules

- If the task is to buy presale passes or NFT-linked sale lots, use `clashofcoins-buyer`.
- If the task is to buy game items for a nickname or address, use `clashofcoins-shop-buyer`.
- If the task is to wire scanners, OpenAPI, manifests, or agent registries for sale, use `clashofcoins-integrator`.
- If the task is to wire scanners, OpenAPI, manifests, or agent registries for shop, use `clashofcoins-shop-integrator`.

## Critical Rule

Do not treat sale and shop as one catalog.

- Sale uses onchain catalog + mint delivery.
- Shop uses backend offers + backend delivery.

## Shop x402 Retry Rule

- When using shop `x402`, the paid retry must preserve the exact request body and send a canonical `PAYMENT-SIGNATURE` built from the latest `PAYMENT-REQUIRED` challenge, including its `resource` and one `accepted` payment requirement.

## MPP Rule

- Prefer the canonical `mppx` SDK for Tempo MPP.
- Let `mppx` parse `WWW-Authenticate: Payment`, settle the Tempo transfer, and resend the request with `Authorization: Payment`.
- If manual MPP is unavoidable, the transfer hash belongs in `credential.payload.hash` with `credential.payload.type = "hash"`, not in `payment.transactionHash`.

## Discovery Consumers

If the task is specifically about scanner or registry compatibility, use the repo integration notes:

- `docs/integrations/x402scan.md`
- `docs/integrations/mppscan.md`
- `docs/integrations/bazaar.md`
- `docs/integrations/402index.md`
