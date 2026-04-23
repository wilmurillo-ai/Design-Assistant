---
name: clashofcoins-buyer
description: Use when an agent should discover active sale offers and complete a presale purchase through the canonical sale surface.
---

# Clash of Coins Sale Buyer

Use this skill for the sale surface only.

Do not assume both `x402` and `mpp` are enabled on every deployment. Check live discovery first.

## Base URL

- deployment-specific sale origin
- x402: `https://x402.clashofcoins.com`
- mpp: `https://mpp.clashofcoins.com`

## Read First

1. `GET /openapi.json`
2. `GET /.well-known/x402` if `x402` is enabled
3. `GET /.well-known/mpp` if `mpp` is enabled
4. `GET /agentic/x402/offers` or `GET /agentic/mpp/offers` for the enabled payment path

## What You Are Buying

These are presale / Agentic Pass offers, not game-shop items.

- source of truth: onchain catalog filtered by allowlisted sale ids
- fulfillment: external relayer-service mint flow

## Main Purchase Flow

1. Load live offers from the enabled payment path.
2. Choose a live `saleId`.
3. Optionally quote with the matching quote endpoint.
4. Buy through the matching protocol buy endpoint.
5. If fulfillment is not final yet, poll the matching purchase-status endpoint.

## Request Body

```json
{
  "saleId": "<live-saleId>",
  "quantity": 1,
  "beneficiary": "0xBeneficiaryAddress"
}
```

## Pricing Rules

- Never hardcode `saleId` or prices.
- Read the live catalog first.
- The sale surface may expose discounted pricing fields; present discounted and base prices clearly when they differ.

## Critical Rules

- Keep the unpaid and paid request bodies identical.
- Do not derive sale ids from raw chain scanning.
- Do not use shop routes for sale purchases.
- For sale `mpp`, prefer the canonical `mppx` SDK.
- If manual MPP is unavoidable, use `credential.payload.type = "hash"` and `credential.payload.hash`, not `payment.transactionHash`.
