---
name: colipu-api
description: >-
  Colipu (科力普) B2B procurement API integration for enterprise purchasing.
  Provides product search by SKU/keyword, pricing and stock queries, order
  creation and lifecycle management, logistics tracking, billing reconciliation,
  invoice processing, and after-sales returns. Use when the user mentions
  Colipu, 科力普, 企业采购, SKU, 下单, 订单状态, 物流, 发票, 对账, or 售后退货.
required_env_vars:
  - COLIPU_USERNAME
  - COLIPU_PASSWORD  
optional_env_vars:
  - COLIPU_BASE_URL
  - COLIPU_TOKEN_FILE
  - COLIPU_TOKEN_PERSIST
secret_handling:
  redact_in_logs: true
  forbid_echo: true    
---

# Colipu 科力普采购助手

Enterprise B2B procurement API client for Colipu (科力普).
Covers the full procurement lifecycle: product lookup, ordering, logistics, billing, and after-sales.

## Prerequisites

1. **Get API credentials**: Contact [cip_tech@colipu.com](mailto:cip_tech@colipu.com) for business cooperation and account setup.

2. **Environment variables** (required before first use):
   - `COLIPU_USERNAME` — API account username
   - `COLIPU_PASSWORD` — API account password
   - `COLIPU_BASE_URL` — optional, defaults to `https://api.ucip.colipu.com/cip`
   - `COLIPU_TOKEN_FILE` — optional, token cache file path (used only when persistence is enabled)
   - `COLIPU_TOKEN_PERSIST` — optional, defaults to `0`; set to `1` to enable token disk persistence

3. **Python** with `requests` available in the current environment.

3. **Token** is auto-fetched and kept in memory by default (12 h TTL, auto-refresh).
   To persist token on disk, explicitly set both `COLIPU_TOKEN_PERSIST=1` and `COLIPU_TOKEN_FILE=/secure/path/colipu_token.json`.
   Avoid storing token files in shared, synced, or backed-up workspace directories.

## Core Rules

1. **Never fabricate data** — always call the API; never guess prices, stock, or order status.
2. **Never use web_search** as a substitute for API data.
3. **Ask for missing params** — if SKU, order ID, or date range is missing, ask the user before calling.
4. **SKU format** — alphanumeric, case-sensitive, use lowercase (e.g. `2h1075`, `1049204`).
5. **All commands** run via: `python scripts/colipu_client.py <command> [args]`
6. **On any API error**: show `errormsg` to the user and suggest a corrective action.

## Task Router

Match user intent to the command below, then execute.

### Product

| Intent | Command | Required Args |
|--------|---------|---------------|
| Browse categories | `categories` | — |
| Product detail | `product-detail` | `--sku SKU` |
| Check price | `product-price` | `--skus SKU1,SKU2` |
| Check stock | `product-stock` | `--skus SKU1 --area CODE` |

- Area code format: `省编号_市编号_区编号`, use `*` for all regions.
- `--customer-code` is optional on price/stock queries.

### Order

| Intent | Command | Required Args |
|--------|---------|---------------|
| Place order | `order-submit` | `--data order.json` or `--json '{...}'` |
| Confirm order | `order-confirm` | `--order-id ID` |
| Cancel order | `order-cancel` | `--order-id ID` |
| Query order detail | `order-info` | `--order-id ID` |
| Query order status | `order-state` | `--order-id ID` |
| Confirm receipt | `order-signconfirm` | `--order-id ID` |

### Logistics

| Intent | Command | Required Args |
|--------|---------|---------------|
| Track by order | `logistics` | `--order-id ID` |
| Track by delivery | `delivery-logistics` | `--delivery-code CODE` |

### Billing & Invoice

| Intent | Command | Required Args |
|--------|---------|---------------|
| Reconciliation | `bill-reconciliation` | `--start-date YYYY-MM-DD --end-date YYYY-MM-DD` |
| Apply for settlement | `bill-apply` | `--data bill.json` |

### After-sales

| Intent | Command | Required Args |
|--------|---------|---------------|
| Apply return/exchange | `aftersale-apply` | `--data return.json` |
| Query return status | `aftersale-info` | `--apply-code CODE` |
| Cancel return | `aftersale-cancel` | `--apply-code CODE` |

### Messages

| Intent | Command | Required Args |
|--------|---------|---------------|
| Get messages | `messages` | `--type 302,303` |
| Delete messages | `message-delete` | `--ids ID1,ID2` |

Message type codes: 202=price change, 203=stock change, 204=on/off shelf,
205=product change, 206=product pool change, 302=order status, 303=return status,
304=return audit, 700=bill audit, 701=bill invoice, 801=order split.

## Workflow: Product Inquiry

1. User gives SKU → `product-detail --sku <sku>` for full info.
2. User wants price → `product-price --skus <sku1,sku2>` returns 协议价/商城价/市场价.
3. User wants stock → `product-stock --skus <sku> --area <code>`.
4. User gives keyword only → `categories` first, then look up SKUs within a category
   (see `category/{id}/skus` in [references/product.md](references/product.md)).

## Workflow: Order Lifecycle

```
Submit ──→ Confirm ──→ Ship ──→ Deliver ──→ Sign receipt
  │           │                                  │
  └→ Cancel   └→ Revoke                 Reconcile / Invoice
                                                 │
                                         After-sales return
```

1. **Submit**: Build order JSON (required: `yggc_order`, `name`, province/city/county,
   `address`, `phone`/`mobile`, `payment`, `order_price`, `freight`, `sku` array).
   See [references/order.md](references/order.md) for full field spec.
   Run `order-submit --data order.json`.
2. **Confirm**: `order-confirm --order-id <id>` — supports whole-order or partial confirm.
3. **Track**: `order-state --order-id <id>` for status code; `logistics --order-id <id>` for tracking.
4. **Cancel** (before shipping only): `order-cancel --order-id <id>`.
5. **Sign receipt**: `order-signconfirm --order-id <id>`.

Order status codes: `0`=新建, `1`=签收, `-1`=拒收, `-2`=取消, `5`=发货, `3`=审批通过, `-3`=审批不通过.

## Workflow: After-sales Return

1. Build return JSON: `order_id` (required), `skus` array (`sku`/`num`/`price`),
   `apply_type` (`4`=退货, `5`=换货, `6`=维修, `7`=退款).
2. Submit: `aftersale-apply --data return.json`.
3. Track: `aftersale-info --apply-code <code>`.
4. Cancel if needed: `aftersale-cancel --apply-code <code>`.

Return audit status: `0`=待审核, `1`=审核通过, `2`=客户取消, `3`=客服取消, `4`=审核不通过.

## Error Handling

All responses follow: `{success, errorcode, errormsg, requestId, result}`.

| Code | Meaning | Suggested Action |
|------|---------|------------------|
| 0 | Success | Proceed normally |
| 5001 | Token expired | Client auto-refreshes; retry once |
| 5003 | Refresh token expired | Re-authenticate (client handles this) |
| 5004 | No data found | Tell user "no results found" |
| 5005 | Invalid params | Verify and correct parameters |
| 2060 | Duplicate order | Use a different order number |
| 2061 | Order not found | Verify order ID with user |
| 2062 | Order already confirmed | Inform user, no action needed |
| 2063 | Order already cancelled | Inform user, no action needed |
| 2065 | Submitting too fast | Wait briefly, then retry |

## Output Format

Present API results to users in a clear structured format:

- **Product**: Name / SKU / Price (协议价 · 商城价 · 市场价) / Stock / Brand / Unit
- **Order**: Order ID / Status / Total amount / SKU list / Receiver / Address
- **Logistics**: Carrier / Tracking number / Latest event / Full timeline
- **Billing**: Order ID / Status / Create date / Signed amount per SKU
- **Return**: Apply code / Audit status / Type / Reason / SKU details

## Auth Mechanism

Token = `MD5(username + password + timestamp + password)` lowercase hex.
Timestamp format: `yyyyMMdd`. TTL: 12 hours.
Header on all requests (except token fetch): `Colipu-Token: {access_token}`.

The client script handles auth automatically — no manual token management needed.

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `Error: set COLIPU_USERNAME and COLIPU_PASSWORD env vars` | Env vars not configured | Set both env vars before running |
| `Failed to get token: ...` | Wrong credentials or network issue | Verify username/password; check connectivity |
| `{"success": false, "errorcode": "-1", ...}` | Network timeout or connection refused | Check internet; retry after a moment |
| Token file corrupt / garbled | Previous write interrupted | Delete `.data/colipu_token.json` and retry; client will re-authenticate |
| Price / stock returns empty | SKU doesn't exist or wrong case | SKUs are case-sensitive — use lowercase |

## Detailed API Reference

For full request/response schemas and examples, read the reference files:

- Auth & token: [references/auth.md](references/auth.md)
- Product & categories: [references/product.md](references/product.md)
- Order lifecycle: [references/order.md](references/order.md)
- Billing & invoices: [references/billing.md](references/billing.md)
- After-sales returns: [references/aftersale.md](references/aftersale.md)
- Logistics tracking: [references/logistics.md](references/logistics.md)
- Message subscription: [references/message.md](references/message.md)
