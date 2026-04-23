---
name: lap-adyen-data-protection-api
description: "Adyen Data Protection API skill. Use when working with Adyen Data Protection for requestSubjectErasure. Covers 1 endpoint."
version: 1.0.0
generator: lapsh
metadata:
  openclaw:
    requires:
      env:
        - ADYEN_DATA_PROTECTION_API_KEY
---

# Adyen Data Protection API
API version: 1

## Auth
ApiKey X-API-Key in header | Bearer basic

## Base URL
https://ca-test.adyen.com/ca/services/DataProtectionService/v1

## Setup
1. Set Authorization header with your Bearer token
3. POST /requestSubjectErasure -- create first requestSubjectErasure

## Endpoints

1 endpoints across 1 groups. See references/api-spec.lap for full details.

### requestSubjectErasure
| Method | Path | Description |
|--------|------|-------------|
| POST | /requestSubjectErasure | Submit a Subject Erasure Request. |

## Common Questions

Match user requests to endpoints in references/api-spec.lap. Key patterns:
- "Create a requestSubjectErasure?" -> POST /requestSubjectErasure
- "How to authenticate?" -> See Auth section

## Response Tips
- Check response schemas in references/api-spec.lap for field details
- Create/update endpoints typically return the created/updated object

## CLI

```bash
# Update this spec to the latest version
npx @lap-platform/lapsh get adyen-data-protection-api -o references/api-spec.lap

# Search for related APIs
npx @lap-platform/lapsh search adyen-data-protection-api
```

## References
- Full spec: See references/api-spec.lap for complete endpoint details, parameter tables, and response schemas

> Generated from the official API spec by [LAP](https://lap.sh)
