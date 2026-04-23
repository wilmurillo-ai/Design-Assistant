---
name: ntriq-domain-threat-intelligence-scorer
description: "Get country profiles with capital, region, population, currencies, languages, and borders from REST Countries API. Free public data."
version: 1.0.0
metadata:
  openclaw:
    primaryTag: data-intelligence
    tags: [cybersecurity,threat,domain]
    author: ntriq
    homepage: https://x402.ntriq.co.kr
---

# Domain Threat Intelligence Scorer

Score domains for threat indicators including typosquatting, malware hosting, phishing patterns, and reputation signals. Aggregates WHOIS age, DNS anomalies, certificate transparency, and blocklist status into a composite threat score.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `domain` | string | ✅ | Domain to analyze (e.g., `suspicious-bank-login.com`) |
| `check_blocklists` | boolean | ❌ | Query public blocklists (default: true) |
| `include_whois` | boolean | ❌ | Include registrar/age data (default: true) |

## Example Response

```json
{
  "domain": "paypa1-secure.com",
  "threat_score": 91,
  "threat_level": "critical",
  "indicators": {
    "typosquatting": {"detected": true, "target": "paypal.com", "technique": "digit_substitution"},
    "domain_age_days": 3,
    "ssl_cert_issuer": "Let's Encrypt",
    "blocklists_matched": ["PhishTank", "URLhaus"],
    "dns_anomalies": ["no MX record", "Cloudflare proxy"]
  },
  "recommendation": "Block immediately — active phishing infrastructure"
}
```

## Use Cases

- Email security gateway domain screening
- Brand protection monitoring for phishing lookalikes
- Threat intelligence enrichment for SIEM

## Access

```bash
# Service catalog
curl https://x402.ntriq.co.kr/services
```

Available on [Apify Store](https://apify.com/ntriqpro/domain-threat-intelligence-scorer) · [x402 micropayments](https://x402.ntriq.co.kr)
