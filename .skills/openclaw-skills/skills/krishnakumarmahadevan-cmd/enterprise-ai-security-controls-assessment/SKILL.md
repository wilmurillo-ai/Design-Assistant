# Enterprise AI Security Controls Assessment

Assess your organization's AI security posture across 12 enterprise domains — Identity & Access, Data Protection, Prompt Injection Defense, Model Protection, API Security, Agent Permissioning, Output Filtering, Monitoring & Anomaly Detection, Compliance Mapping, Incident Response, Encryption & KMS, and Risk Intelligence. Each domain covers 5 controls (60 total) and produces prioritized remediation guidance.

---

## Usage

```json
{
  "tool": "enterprise_ai_security_controls_assessment",
  "input": {
    "organization_name": "Acme Corp",
    "industry": "Financial Services",
    "ai_maturity": "intermediate",
    "domains_to_assess": ["identity_access", "prompt_injection_defense", "api_security"],
    "current_controls": {
      "identity_access": {
        "mfa_enabled": true,
        "rbac_implemented": false,
        "service_account_rotation": "manual"
      },
      "prompt_injection_defense": {
        "input_validation": "basic",
        "system_prompt_hardening": false,
        "canary_tokens": false
      }
    }
  }
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `organization_name` | string | ✅ | Name of the organization being assessed |
| `industry` | string | ✅ | Industry vertical (e.g., Financial Services, Healthcare, Retail) |
| `ai_maturity` | string | ✅ | Current AI maturity level: `beginner`, `intermediate`, `advanced` |
| `domains_to_assess` | array | ❌ | Subset of domain keys to assess. Omit to assess all 12 domains |
| `current_controls` | object | ❌ | Key-value map of existing controls per domain (see domain keys below) |

### Domain Keys

| Key | Domain |
|-----|--------|
| `identity_access` | Identity & Access Control |
| `data_protection` | Data Protection |
| `prompt_injection_defense` | Prompt Injection Defense |
| `model_protection` | Model Protection |
| `api_security` | API Security |
| `agent_permissioning` | Agent Permissioning |
| `output_filtering` | Output Filtering |
| `monitoring_anomaly` | Monitoring & Anomaly Detection |
| `compliance_mapping` | Compliance Mapping |
| `incident_response` | Incident Response |
| `encryption_kms` | Encryption & Key Management (KMS) |
| `risk_intelligence` | Risk Intelligence |

---

## What You Get

- **Domain-by-domain scorecard** — maturity rating per domain (Initial / Developing / Defined / Managed / Optimizing)
- **Control gap analysis** — which of the 60 controls are missing, partial, or implemented
- **Prioritized remediation roadmap** — Quick Wins (0–30 days), Medium-term (30–90 days), Strategic (90+ days)
- **Compliance alignment** — mapped to NIST AI RMF, ISO 42001, SOC 2, and GDPR where applicable
- **Executive summary** — board-ready summary of AI security posture

---

## Example Output

```json
{
  "organization": "Acme Corp",
  "overall_maturity": "Developing",
  "overall_score": 42,
  "domain_scores": {
    "identity_access": { "score": 60, "maturity": "Defined", "gaps": 2 },
    "prompt_injection_defense": { "score": 20, "maturity": "Initial", "gaps": 4 },
    "api_security": { "score": 55, "maturity": "Developing", "gaps": 2 }
  },
  "top_risks": [
    "No system prompt hardening exposes models to override attacks",
    "RBAC not implemented — lateral movement risk across AI services",
    "No canary token monitoring for prompt exfiltration"
  ],
  "quick_wins": [
    "Enable RBAC on all AI service accounts (3 days)",
    "Deploy input sanitization layer before LLM endpoints (7 days)",
    "Rotate all AI API keys and set expiry policies (1 day)"
  ],
  "compliance_gaps": ["NIST AI RMF: GOVERN-1.1", "ISO 42001: 6.1.2", "SOC 2: CC6.1"]
}
```

---

## API Reference

**Base URL:** `https://portal.toolweb.in/apis/security/entaisecconass`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/ai-security/assess` | POST | Run full assessment |
| `/api/ai-security/domains` | GET | List all 12 domain definitions |
| `/api/ai-security/domain/{domain_key}` | GET | Get details for a specific domain |

**Authentication:** Pass your API key as `X-API-Key` header or `mcp_api_key` argument via MCP.

---

## Pricing

| Plan | Daily Limit | Monthly Limit | Price |
|------|-------------|---------------|-------|
| Free | 5 / day | 50 / month | $0 |
| Developer | 20 / day | 500 / month | $39 |
| Professional | 200 / day | 5,000 / month | $99 |
| Enterprise | 100,000 / day | 1,000,000 / month | $299 |

---

## About

**ToolWeb.in** — 200+ security APIs, CISSP & CISM certified, built for enterprise AI security practitioners.

Platforms: Pay-per-run · API Gateway · MCP Server · OpenClaw · RapidAPI · YouTube

- 🌐 [toolweb.in](https://toolweb.in)
- 🔌 [portal.toolweb.in](https://portal.toolweb.in)
- 🤖 [hub.toolweb.in](https://hub.toolweb.in) (MCP Server)
- 🦞 [toolweb.in/openclaw/](https://toolweb.in/openclaw/)
- ⚡ [rapidapi.com/user/mkrishna477](https://rapidapi.com/user/mkrishna477)
- 📺 [youtube.com/@toolweb-009](https://youtube.com/@toolweb-009)
