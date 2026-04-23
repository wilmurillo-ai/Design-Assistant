---
name: clashofcoins-shop-buyer
description: Use when an agent should discover personalized Clash of Coins shop offers and buy them through shop x402 or shop MPP.
---

# Clash of Coins Shop Buyer

Use this skill for the shop surface only.

Do not assume both `x402` and `mpp` are enabled on every deployment. Check live discovery first.

## Base URL

- x402 gateway origin: `https://x402.clashofcoins.com`
- x402 shop root: `https://x402.clashofcoins.com/shop`
- mpp gateway origin: `https://mpp.clashofcoins.com`
- mpp shop root: `https://mpp.clashofcoins.com/shop`

## Read First

1. `GET /shop/openapi.json`
2. `GET /shop/openapi.full.json`
3. `GET /shop/api/shop/items?nickname=<player>` or `?address=<0x...>`
4. if protocol-specific routing is needed:
   - `GET /shop/.well-known/x402` if `x402` is enabled
   - `GET /shop/.well-known/mpp` if `mpp` is enabled

Use `GET /shop/openapi.json` only when you specifically need the protocol-aware payable shop contract for the current instance.

## Recipient Rules

- Every shop read or purchase must specify exactly one recipient:
  - `nickname`
  - or `address`
- Never send both.

## Purchase Rules

### Shop x402

- supports one distinct item per request
- `quantity` may be greater than one for that single item

Example:

```json
{
  "itemId": "a-units-pack:1",
  "nickname": "PlayerOne"
}
```

### Shop MPP

- supports one item or multi-item carts

Example:

```json
{
  "address": "0x1234567890123456789012345678901234567890",
  "items": [
    { "itemId": "a-units-pack:1", "quantity": 1 },
    { "itemId": "keys:5", "quantity": 2 }
  ]
}
```

## Important Endpoints

- `GET /shop/openapi.full.json`
- `GET /shop/api/shop/items?nickname=<player>` or `?address=<0x...>`
- if `x402` is enabled:
  - `GET /shop/x402/offers?nickname=<player>` or `?address=<0x...>`
  - `POST /shop/x402/quote`
  - `GET` or `POST /shop/x402/buy`
  - `GET /shop/x402/purchases/{paymentReference}`
- if `mpp` is enabled:
  - `GET /shop/mpp/offers?nickname=<player>` or `?address=<0x...>`
  - `POST /shop/mpp/quote`
  - `GET` or `POST /shop/mpp/buy`
  - `GET /shop/mpp/purchases/{paymentReference}`
- `GET /shop/purchase-status/{purchaseId}`

## Pricing Rules

- Shop offers are dynamic and backend-driven.
- The gateway may apply `SHOP_DISCOUNT_BPS`.
- Prefer displaying:
  - `discountedPriceUsd`
  - `basePriceUsd`
  - `discountPercent`

## Execution Rules

- Keep the request body identical between unpaid and paid retries.
- Do not use anonymous shop offers.
- Do not use shop `x402` for carts with multiple distinct items.
- Use shop `mpp` for carts.
- For shop `mpp`, prefer the canonical `mppx` SDK.
- If manual MPP is unavoidable, encode the Tempo transfer hash in `credential.payload.hash` with `credential.payload.type = "hash"`.

## Shop x402 Paid Retry

- The first unpaid buy request may return `402 payment_required`.
- Reuse the exact same HTTP method and JSON body on the paid retry.
- Build the paid retry from the latest `PAYMENT-REQUIRED` challenge.
- Copy both `resource` and one `accepted` payment requirement from that challenge into the encoded payment payload.
- Send the canonical `PAYMENT-SIGNATURE` header on the paid retry.
- `X-PAYMENT` is a legacy compatibility header; prefer `PAYMENT-SIGNATURE`.
- If using a facilitator such as Coinbase CDP, settle through the facilitator first and only then resend the buy request.
