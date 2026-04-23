# Meridian Payment Reference — x402 / Base USDC

## Overview

Meridian uses x402 — the HTTP 402 Payment Required standard. Payment is in USDC on Base mainnet. Settlement is handled by Coinbase's public facilitator at x402.org.

## 402 Response Body

When a request is unauthenticated, Meridian returns:

```json
{
  "x402_version": 1,
  "error": "Payment required",
  "accepts": [{
    "scheme": "exact",
    "network": "base",
    "max_amount_required": "10000",
    "resource": "https://meridianapi.nodeapi.ai/v1/reproject",
    "description": "Meridian: reproject",
    "mime_type": "application/octet-stream",
    "pay_to": "0x5253F82eCD3094337fd9c92f86e3a0E0BBdea48D",
    "max_timeout_seconds": 300,
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
  }]
}
```

- `max_amount_required`: atomic USDC units (1 USDC = 1,000,000 atomic). `10000` = $0.01
- `pay_to`: Meridian's wallet address on Base
- `asset`: USDC contract address on Base mainnet

## Signing (EIP-3009 transferWithAuthorization)

Use the `x402` Python client (recommended) or sign manually.

### With coinbase/x402 Python client

```python
pip install x402
```

```python
from x402.client import pay_for_request
import requests

# First call — get 402
r = requests.post("https://meridianapi.nodeapi.ai/v1/reproject", 
    files={"file": open("input.geojson", "rb")},
    data={"target_crs": "EPSG:3857"})

# pay_for_request handles signing + retry automatically
if r.status_code == 402:
    result = pay_for_request(
        url="https://meridianapi.nodeapi.ai/v1/reproject",
        payment_required=r.json(),
        private_key=WALLET_PRIVATE_KEY,  # Base wallet private key
        files={"file": open("input.geojson", "rb")},
        data={"target_crs": "EPSG:3857"}
    )
```

### Manual signing

The `X-PAYMENT` header value is a base64-encoded JSON payload:

```json
{
  "x402Version": 1,
  "scheme": "exact",
  "network": "base",
  "payload": {
    "signature": "<EIP-3009 signed authorization>",
    "authorization": {
      "from": "<payer address>",
      "to": "<pay_to from 402>",
      "value": "<max_amount_required>",
      "validAfter": 0,
      "validBefore": <unix timestamp + 300>,
      "nonce": "<random 32-byte hex>"
    }
  }
}
```

Sign using EIP-712 with the USDC contract's `TransferWithAuthorization` domain.

## x402 Client Libraries

- Python: `pip install x402` (coinbase/x402 on PyPI)
- TypeScript: `npm install x402`
- Docs: https://docs.cdp.coinbase.com/x402

## Pricing Formula

```
price = max(0.01, min(2.00, file_size_mb * 0.01))
```

Examples:
- 50 KB file → $0.01 (minimum)
- 2 MB file → $0.02
- 500 MB file → $2.00 (cap)

## Dev Mode

If the server is running with `DEV_MODE=true`, all payment verification is bypassed. Do not rely on this in production — `meridian.nodeapi.ai` runs with `DEV_MODE=false`.

## Idempotency

Each payment signature can only be used once. Replaying a signature returns a 402 error. Always generate a fresh nonce per request.
