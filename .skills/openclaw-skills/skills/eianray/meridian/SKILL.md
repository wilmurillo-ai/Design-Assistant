---
name: meridian
description: Use the Meridian GIS API (meridian.nodeapi.ai) to process geospatial data. Handles the full x402 payment flow automatically — sends a request, reads the 402 payment quote, signs a USDC authorization on Base, and retries with the payment header. Use when asked to reproject, buffer, clip, dissolve, convert, validate, repair, or otherwise process GeoJSON or raster data. Also use when asked about Meridian's endpoints, pricing, or payment model.
---

# Meridian GIS API

Meridian processes GeoJSON and raster data via HTTP. All paid endpoints require an x402 micropayment in USDC on Base. No accounts or API keys needed.

**Base URL:** `https://meridian.nodeapi.ai`  
**Docs:** `https://meridian.nodeapi.ai/docs`  
**Pricing:** $0.01/MB, min $0.01, cap $2.00

## Payment Flow

Every paid endpoint follows this pattern:

1. POST to endpoint → receive `402 Payment Required` with price quote in response body
2. Sign an EIP-3009 `transferWithAuthorization` USDC authorization on Base using the wallet
3. Retry the same POST with `X-PAYMENT: <base64-encoded-payload>` header
4. Receive processed result

The quote in the 402 response is the exact amount charged. See `references/payment.md` for signing details and `references/endpoints.md` for the full endpoint list.

## Quick Usage Pattern

```python
import requests, json

# Step 1 — probe for price
r = requests.post("https://meridianapi.nodeapi.ai/v1/reproject",
    files={"file": ("input.geojson", geojson_bytes, "application/geo+json")},
    data={"target_crs": "EPSG:3857"})

if r.status_code == 402:
    payment_info = r.json()  # contains max_amount_required, pay_to, asset
    # Step 2 — sign payment (see references/payment.md)
    # Step 3 — retry with signed header
    signed = sign_eip3009(payment_info, wallet_key)
    r = requests.post("https://meridianapi.nodeapi.ai/v1/reproject",
        files={"file": ("input.geojson", geojson_bytes, "application/geo+json")},
        data={"target_crs": "EPSG:3857"},
        headers={"X-PAYMENT": signed})

result = r.json()
```

## Key Endpoints

| Operation | Endpoint | Key Params |
|-----------|----------|------------|
| Reproject | `POST /v1/reproject` | `target_crs` (required), `source_crs` (optional) |
| Buffer | `POST /v1/buffer` | `distance` in meters |
| Clip | `POST /v1/clip` | `file` + `mask` (two GeoJSON inputs) |
| Dissolve | `POST /v1/dissolve` | `field_name` (optional) |
| Convert | `POST /v1/convert` | `output_format`: geojson/shapefile/kml/gpkg |
| Schema | `POST /v1/schema` | — |
| Validate | `POST /v1/validate` | — |
| Repair | `POST /v1/repair` | — |
| Hillshade | `POST /v1/hillshade` | raster file |
| Batch | `POST /v1/batch` | up to 50 ops, single payment |

For the full endpoint list see `references/endpoints.md`.  
For payment signing implementation see `references/payment.md`.

## Notes

- All inputs should be GeoJSON (FeatureCollection). Other formats may work but GeoJSON is the safest path.
- Raster endpoints accept GeoTIFF input.
- Binary outputs (Shapefile, GeoTIFF, MBTiles) are returned as base64-encoded data in `result.data` with a `filename` field.
- Rate limit: 60 req/min per IP.
- Health check (free): `GET /v1/health`
