---
name: bw-invoice-verification-service
description: Use the local invoice service script to initialize app keys, query quota and packages, verify invoice text or images, batch-verify local folders, and create or query recharge orders.
metadata: { "openclaw": { "requires": { "bins": ["node"] } } }
---

> **说明**：本技能固定使用 `http://asset-check-innovate-service-http.default.yf-bw-test-2.test.51baiwang.com` 作为 API base URL，`config set --api-base-url` 不可用。

# Invoice Verification Service

Use this skill when the user wants to:

- Query remaining invoice verification quota
- Show recharge packages
- Verify invoice text
- Verify a local invoice image
- Batch-verify invoice images in a local folder
- Create or query a recharge order

## Script

Always run:

```bash
node "{baseDir}/scripts/invoice_service.js" <action> ...
```

## First-Time Setup

The skill always uses the built-in API base URL `https://test.51yzt.cn/assetInnovate`. There is no `config set --api-base-url` option.

Initialize the app key once:

```bash
node "{baseDir}/scripts/invoice_service.js" init-key
```

## Common Commands

Show current config:

```bash
node "{baseDir}/scripts/invoice_service.js" config show
```

Query packages:

```bash
node "{baseDir}/scripts/invoice_service.js" packages
```

Query remaining quota:

```bash
node "{baseDir}/scripts/invoice_service.js" quota
```

Query ledger:

```bash
node "{baseDir}/scripts/invoice_service.js" ledger --page 1 --page-size 20
```

Verify invoice text:

```bash
node "{baseDir}/scripts/invoice_service.js" verify --text "<invoice text>" --format json
```

Verify a local image:

```bash
node "{baseDir}/scripts/invoice_service.js" verify-image --image-file C:\path\invoice.png --format json
```

Verify an uploaded image payload (base64/data-url):

```bash
node "{baseDir}/scripts/invoice_service.js" verify-image --image "<data:image/...;base64,...>" --format json
```

Batch-verify a local folder:

```bash
node "{baseDir}/scripts/invoice_service.js" verify-directory --dir C:\path\invoice-images --format json
```

Create a recharge order:

```bash
node "{baseDir}/scripts/invoice_service.js" create-order --amount 10
```

Query an order:

```bash
node "{baseDir}/scripts/invoice_service.js" query-order --order-no ORDER123456789
```

## Behavior Rules

- Prefer `quota` when the user asks for remaining count.
- Prefer `packages` when the user asks for available recharge plans.
- Prefer `verify-image` when the user provides a local image path.
- Prefer `verify-image` when the user provides an uploaded image (base64/data-url) too.
- Prefer `verify-directory` when the user provides a local folder path with many invoice images.
- Prefer `create-order` when the user explicitly chooses a package amount.
- For any `verify-image` call, explicitly tell the user it consumes 2 quota each time.
- After `create-order`, report the payment link plus all available QR codes (returned in `data.qrCodes`). The script now polls settlement by default and returns `data.orderPolling` + `data.paymentSettled`; if `paymentSettled=true`, explicitly tell the user recharge has arrived.
- Return the script JSON result directly and do not invent fields.
- When the user says “帮我安装这个技能” or similar install request, reply with the install command `clawhub install bw-invoice-verification-service`, remind them to restart OpenClaw, and ask them to say “帮我初始化” or send `$bw-invoice-verification-service init-key` once installation completes—note that “帮我安装” alone only installs the skill and does not run init-key.
