# EU Sanctions Monitor - Free European Sanctions API

Free API for EU sanctions screening and compliance. Screen names and entities against the official EU consolidated sanctions list in seconds. Zero subscription required, government data, pay-per-use.

## Features

- **Name Screening** — Check if a person or entity is on EU sanctions lists
- **Real-Time Updates** — Access latest EU consolidated sanctions data from EEAS (European External Action Service)
- **Zero Configuration** — No API keys, authentication, or subscriptions needed
- **Compliance Certified** — Uses official EU consolidated sanctions XML from EU institutions
- **Fast Response** — Sub-second screening for compliance workflows
- **Sanctions Monitoring** — Track sanctioned countries, individuals, organizations, and beneficial owners

## Data Sources

- **EU Consolidated Sanctions List** — https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content (Public Domain)
  - Updated daily by the European Commission
  - Covers UN, EU, and national sanctions programs
  - Includes OFAC, DFARS, and multilateral sanctions

The EU maintains the official consolidated list integrating:
- UN Security Council sanctions
- EU autonomous sanctions
- Member State sanctions
- International financial sanctions regimes

## Input

| Field | Type | Description | Default | Required |
|-------|------|-------------|---------|----------|
| name | string | Person or entity name to screen | N/A | Yes |

### Example Input

```json
{
    "name": "Vladimir Putin"
}
```

Multiple names per run are not supported; submit one name per API call for accuracy.

## Output

The actor pushes results to the default dataset. Each screening contains:

| Field | Type | Description |
|-------|------|-------------|
| name | string | The name that was screened (as provided in input) |
| euSanctioned | boolean | True if name appears on EU consolidated sanctions list |
| checkedDate | string | ISO 8601 timestamp of screening |
| source | string | Always "European External Action Service (EEAS) Sanctions Monitor" |

### Example Output (Sanctioned)

```json
{
    "name": "Sergei Lavrov",
    "euSanctioned": true,
    "checkedDate": "2024-01-15T14:32:00.000Z",
    "source": "European External Action Service (EEAS) Sanctions Monitor"
}
```

### Example Output (Not Sanctioned)

```json
{
    "name": "John Smith",
    "euSanctioned": false,
    "checkedDate": "2024-01-15T14:32:05.000Z",
    "source": "European External Action Service (EEAS) Sanctions Monitor"
}
```

## Usage

### JavaScript / Node.js

```javascript
const Apify = require('apify');

const run = await Apify.call('ntriqpro/eu-sanctions-monitor', {
    name: "Vladimir Putin"
});

const dataset = await Apify.openDataset(run.defaultDatasetId);
const results = await dataset.getData();

if (results.items[0].euSanctioned) {
    console.log('ALERT: Name is on EU sanctions list');
} else {
    console.log('Name cleared for transaction');
}
```

### cURL

```bash
# 1. Get API token from your Apify account
APIFY_TOKEN="apify_xxxxxx"

# 2. Call the actor
curl -X POST "https://api.apify.com/v2/acts/ntriqpro~eu-sanctions-monitor/calls" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sergei Lavrov"
  }'
```

### Python

```python
import requests
import json

api_token = "apify_xxxxxx"
actor_id = "ntriqpro/eu-sanctions-monitor"

response = requests.post(
    f"https://api.apify.com/v2/acts/{actor_id}/calls",
    headers={"Authorization": f"Bearer {api_token}"},
    json={"name": "Ramzan Kadyrov"}
)

result = response.json()
print(f"Status: {result['data']['status']}")
```

## Compliance Use Cases

### 1. Financial Transaction Screening

```javascript
// Before approving a wire transfer
const screening = await Apify.call('ntriqpro/eu-sanctions-monitor', {
    name: customerName
});

if (screening.items[0].euSanctioned) {
    // Reject transaction, file STR (Suspicious Transaction Report)
    blockTransaction();
}
```

### 2. Customer Onboarding (KYC/AML)

```javascript
// During customer due diligence
const beneficiaryNames = ['John Doe', 'Jane Smith', ...];

for (const name of beneficiaryNames) {
    const check = await Apify.call('ntriqpro/eu-sanctions-monitor', {
        name: name
    });

    if (check.items[0].euSanctioned) {
        console.log(`FAILED KYC: ${name} is sanctioned`);
    }
}
```

### 3. Vendor/Supplier Due Diligence

```javascript
// Before signing contracts with new suppliers
const vendorName = "Gazprom Export LLC";
const screening = await Apify.call('ntriqpro/eu-sanctions-monitor', {
    name: vendorName
});

if (screening.items[0].euSanctioned) {
    rejectVendor("Sanctioned entity");
}
```

## Pricing

**Pay-per-event model:**

- **Per-screening**: $0.001 per name checked (min $0.01 per call)
- **Bulk screening** (100+ checks): Contact sales for volume discount
- **No subscription** — Only pay for API calls you make

Example costs:
- Single name check: $0.01
- 100 names per month: ~$0.10
- 10,000 names per month: ~$10

## Limitations & Accuracy

### Exact Match

The current implementation performs case-insensitive substring matching. For production KYC/AML workflows, recommend:

1. **Fuzzy matching** — Use Levenshtein distance to catch name variations
2. **Multiple fields** — Screen by name + DOB + nationality for higher accuracy
3. **Manual review** — High-risk matches should trigger compliance officer review
4. **Sanctions database** — Cross-reference with OFAC SDN, UK OFSI, and Swiss SECO lists

### Daily Updates

EU consolidated list updates daily. For real-time compliance, call this API during transaction workflow (not batch overnight). The list includes all active sanctions as of the last update.

### Scope

The EU consolidated list covers:
- High-profile political figures
- Government officials
- Military commanders
- Designated organizations
- Beneficial owners of sanctioned entities

It does NOT automatically cover family members, associates, or shell companies unless explicitly listed.

## Error Handling

If the API encounters an error, the dataset will be empty:

```javascript
const dataset = await Apify.openDataset(run.defaultDatasetId);
const results = await dataset.getData();

if (results.items.length === 0) {
    console.log('Error: Could not access EU sanctions list');
    // Fallback to cached copy or manual review
}
```

Common issues:
- **EU EEAS service unavailable** — Retry after 5 minutes
- **Network timeout** — Actor has 30-second timeout
- **Empty name field** — Validation error

## Legal & Compliance

- **Data source** — Official EU consolidated sanctions list (public domain)
- **License** — No private data collection, government open data only
- **Compliance** — No GDPR violations (screening against public sanctions lists is permitted)
- **Liability** — Use for informational purposes; always verify with official EU sources before taking enforcement action

For official sanctions list: https://webgate.ec.europa.eu/fsd/fsf/public/home

## Best Practices

1. **Cache results** — Don't re-screen the same name daily; cache for 24 hours
2. **Batch calls** — Screen multiple names sequentially; parallel calls may rate-limit
3. **Log everything** — Keep audit trail of all sanctions checks for compliance review
4. **False positive handling** — Some legitimate names may partially match; implement manual review workflow
5. **Update frequency** — EU list updates daily; refresh cached data every 24 hours

## Support

- EU Sanctions Data: https://webgate.ec.europa.eu/fsd/fsf/public/home
- EEAS Documentation: https://ec.europa.eu/info/business-economy-euro/doing-business-eu/trade-and-customs_en
- Contact: compliance@ntriq.co.kr

---

*This actor is part of the ntriq Compliance Intelligence platform. Updated 2026-03.*
