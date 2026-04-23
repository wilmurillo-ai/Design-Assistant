---
name: carsxe
description: >
  Access the full suite of CarsXE vehicle data APIs — VIN decoding, license plate lookup,
  market value, vehicle history, safety recalls, lien/theft checks, OBD-II diagnostic code
  decoding, vehicle images, international VIN decoding, Year/Make/Model lookups, and plate/VIN
  OCR from images. Use this skill any time the user asks about a vehicle by VIN, plate, make/model,
  or OBD code. Also triggers for: "what's this car worth", "check for recalls", "vehicle history
  report", "decode this plate", "what does check engine code X mean", or any automotive data query.
  Always use this skill when working with CarsXE APIs — do not guess API behavior without it.
---

# CarsXE Skill

CarsXE provides a REST API for comprehensive vehicle data. All endpoints are at
`https://api.carsxe.com` and require an API key passed as `?key=YOUR_API_KEY`.

> **API Key setup**: The user must have a CarsXE API key from https://api.carsxe.com/dashboard/developer.
> If no key is configured, ask the user to provide it before making any API calls.

See `references/api-reference.md` for full endpoint details, parameters, and response formats.

---

## Quick API Map

| User intent | Endpoint | Parameters |
|---|---|---|
| Decode a VIN / get specs | `GET /specs` | `vin` |
| Decode a license plate | `GET /platedecoder` | `plate`, `country` (required), `state` (optional) |
| Market value | `GET /marketvalue` | `vin` |
| Vehicle history report | `GET /history` | `vin` |
| Vehicle images | `GET /images` | `make`, `model` + optional filters |
| Safety recalls | `GET /recalls` | `vin` |
| Lien & theft check | `GET /lientheft` | `vin` |
| International VIN | `GET /internationalvin` | `vin` |
| Year/Make/Model lookup | `GET /ymm` | `year`, `make`, `model`, optional `trim` |
| OBD code diagnosis | `GET /obd` | `code` |
| VIN OCR from image | `POST /vinocr` | `imageUrl` in JSON body |
| Plate OCR from image | `POST /platerecognition` | `imageUrl` in JSON body |

---

## Workflow

### 1. Authenticate
Always confirm or ask for the API key before making requests. The key is passed as a query param:
```
https://api.carsxe.com/specs?key=USER_API_KEY&vin=WBAFR7C57CC811956
```

### 2. Choose the right endpoint
Match the user's query to the table above. When context is ambiguous:
- VIN provided → prefer `/specs` first, then chain to other endpoints as needed
- Plate provided → use `/platedecoder` to resolve VIN, then chain if needed
- Make/Model/Year only → use `/ymm` or `/images`
- OBD code (P/C/B/U + digits) → use `/obd`
- Image URL provided → use `/vinocr` or `/platerecognition` (POST)

### 3. Chain requests when helpful
A common power workflow: plate → VIN → specs + history + recalls in parallel.
Example: *"Is this plate stolen and does it have open recalls?"*
1. `GET /platedecoder` → extract VIN
2. In parallel: `GET /lientheft` + `GET /recalls`

### 4. Present results
Format output clearly with sections per API call. Use Markdown tables or lists for specs,
highlight important findings (open recalls, theft records, salvage titles) prominently.

---

## Error Handling

| HTTP Status | Meaning | Action |
|---|---|---|
| 401 / `invalid key` | Bad or missing API key | Ask user to check their key |
| 404 / `no results` | VIN/plate not found in database | Inform user, suggest double-checking |
| 429 | Rate limit exceeded | Wait and retry, inform user |
| 5xx | Server error | Retry once, then report error |

Always check the `error` field in JSON responses — CarsXE sometimes returns HTTP 200 with an error body.

---

## Examples

**"What are the specs for VIN WBAFR7C57CC811956?"**
→ `GET https://api.carsxe.com/specs?key=KEY&vin=WBAFR7C57CC811956`

**"Decode California plate 7XER187"**
→ `GET https://api.carsxe.com/platedecoder?key=KEY&plate=7XER187&state=CA&country=US`

**"What's my car worth? VIN WBAFR7C57CC811956"**
→ `GET https://api.carsxe.com/marketvalue?key=KEY&vin=WBAFR7C57CC811956`

**"Does this car have any recalls? 1C4JJXR64PW696340"**
→ `GET https://api.carsxe.com/recalls?key=KEY&vin=1C4JJXR64PW696340`

**"My check engine light shows P0300"**
→ `GET https://api.carsxe.com/obd?key=KEY&code=P0300`

**"Extract the VIN from this photo: https://example.com/vin.jpg"**
→ `POST https://api.carsxe.com/vinocr?key=KEY` with body `{"imageUrl":"https://example.com/vin.jpg"}`

---

## Reference Files

- `references/api-reference.md` — Full parameter lists, response field descriptions, and edge cases for all 11 endpoints. Read this when you need exact field names or want to use optional filters.