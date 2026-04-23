---
name: vaikora-security
description: Route OpenClaw LLM calls through Vaikora for real-time AI agent security monitoring. Every action your agent takes gets scored for risk, anomaly-flagged, and pushed as a security signal to SentinelOne, CrowdStrike, or AWS Security Hub — without changing how your agent works.
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - VAIKORA_API_KEY
        - VAIKORA_AGENT_ID
    primaryEnv: VAIKORA_API_KEY
    emoji: "🛡️"
    homepage: https://vaikora.com
---

# Vaikora Security

Vaikora is an OpenAI-compatible security proxy for AI agents. It sits between OpenClaw and your LLM provider, inspecting every request and response in real time.

What it does:
- Scores each agent action for risk (0–100 scale)
- Detects anomalies with ML trained on 1M+ adversarial examples
- Blocks prompt injection, jailbreaks, PII exfiltration, and indirect injection attacks
- Pushes behavioral signals to your SIEM or EDR: SentinelOne, CrowdStrike Falcon, AWS Security Hub
- Scans LLM responses (not just inputs) for toxicity and data leakage

Your agent code does not change. One URL, one header.

## Setup

You need a Vaikora account and API key. Get one free at [vaikora.com](https://vaikora.com).

Set these in your environment:

```bash
export VAIKORA_API_KEY=vk_live_...
export VAIKORA_AGENT_ID=your-agent-id
```

## How routing works

Vaikora exposes a drop-in OpenAI-compatible endpoint:

```
https://api.vaikora.com/v1
```

In your OpenClaw config, change the base URL from your LLM provider to the Vaikora gateway:

```yaml
# Before
llm:
  provider: openai
  base_url: https://api.openai.com/v1

# After
llm:
  provider: openai
  base_url: https://api.vaikora.com/v1
  headers:
    Authorization: "Bearer ${VAIKORA_API_KEY}"
    X-Provider-Key: "${YOUR_OPENAI_KEY}"
    X-Vaikora-Agent: "${VAIKORA_AGENT_ID}"
```

Works with any provider OpenClaw supports — OpenAI, Anthropic, Google, Azure, Bedrock, Mistral, Groq, Ollama.

## Security connectors

Once routing is active, Vaikora captures every action your agent takes. To push those signals to your security stack, install the connector for your platform from AWS Marketplace (free):

| Platform | What it does |
|----------|-------------|
| **SentinelOne** | Maps high-risk agent actions to IOCs via Threat Intelligence API |
| **CrowdStrike Falcon** | Pushes risky actions as Custom IOCs. Critical = prevent mode. High = detect mode. |
| **AWS Security Hub** | Sends ASFF findings for high-severity and anomalous actions |

Search "Vaikora" in [AWS Marketplace](https://aws.amazon.com/marketplace) to install.

## What gets monitored

Vaikora evaluates every agent action across four dimensions:

| Dimension | What it checks |
|-----------|----------------|
| Risk Score | Quantified danger level, 0–100 |
| Anomaly | ML-based deviation from the agent's baseline behavior |
| Policy | Allow / block / audit decision against configured rules |
| Threat | Confirmed malicious activity flag with confidence score (0–1) |

Actions with risk score ≥ 75, anomaly flag, or confirmed threat get pushed to your security connector as a finding.

## Verifying it works

After routing through Vaikora, run a test action from your agent and check:

```bash
# Check Vaikora received the action
curl -H "X-API-Key: ${VAIKORA_API_KEY}" \
  "https://api.vaikora.com/api/v1/actions?agent_id=${VAIKORA_AGENT_ID}&per_page=5"
```

You should see the action logged with a risk score and threat assessment.

## Policy presets

Vaikora ships six policy presets you can activate via your config:

| Preset | Use case |
|--------|----------|
| `standard` | Default — balanced security |
| `strict` | High-sensitivity environments |
| `permissive` | Dev/test, minimal blocking |
| `hipaa` | PHI detection, medical data protection |
| `pci-dss` | Credit card and financial data protection |
| `gdpr` | EU PII categories, Right to Erasure support |

```yaml
# In your vaikora.yaml
policy: hipaa
```

## Performance

- Gateway latency: P50 = 8ms, P95 = 22ms
- Block decisions (early-exit): 18ms
- Threat detection accuracy: 99.9%, false positive rate < 0.1%

## Free tier

Vaikora's Free tier covers 20 req/min and 7-day audit log retention. No credit card required. Test keys (`vk_test_...`) are also available at no charge with limited functionality.

## Links

- [Vaikora docs](https://vaikora.com/docs)
- [AWS Marketplace — Security Hub connector](https://aws.amazon.com/marketplace)
- [AWS Marketplace — SentinelOne connector](https://aws.amazon.com/marketplace)
- [AWS Marketplace — CrowdStrike connector](https://aws.amazon.com/marketplace)
- [Data443 Risk Mitigation](https://data443.com)
