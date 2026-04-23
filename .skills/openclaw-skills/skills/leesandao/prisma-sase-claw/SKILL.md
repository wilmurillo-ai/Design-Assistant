---
name: prisma-sase-claw
version: "1.1.6"
description: >
  How to interact with the Palo Alto Networks Prisma SASE API, including Prisma Access,
  Prisma SD-WAN, and Prisma Access Browser. Use this skill whenever the user wants to
  query, configure, monitor, or automate anything related to Prisma SASE, Prisma Access,
  Prisma SD-WAN, Prisma Access Browser, Palo Alto SASE, PANW SASE, or network security
  policies managed through the SASE platform. Also trigger when the user mentions
  tenant service groups (TSGs), SASE API tokens, security policy rules, SD-WAN sites,
  remote networks, GlobalProtect, or aggregate monitoring via the SASE platform.
tags: ["prisma", "sase", "palo-alto", "sd-wan", "network-security", "api", "prisma-access", "prisma-browser"]
metadata:
  openclaw:
    requires:
      bins:
        - curl
        - python3
---

# Prisma SASE API Integration

This skill generates working curl commands and Python scripts to interact with the Palo Alto Networks Prisma SASE platform API. It covers three main products:

- **Prisma Access** — Cloud-delivered network security (security policies, remote networks, GlobalProtect, service connections)
- **Prisma SD-WAN** — Software-defined WAN (site configs, routing, path policies, performance monitoring)
- **Prisma Access Browser** — Secure enterprise browser management

## Quick Reference

| Component | Base URL |
|-----------|----------|
| **API Gateway** | `https://api.sase.paloaltonetworks.com` |
| **Auth Endpoint** | `https://auth.apps.paloaltonetworks.com/oauth2/access_token` |

| Product | URL Prefix |
|---------|-----------|
| Prisma Access Config | `/sse/config/v1/...` |
| SD-WAN | `/sdwan/v2.1/api/...` |
| Aggregate Monitoring | `/mt/monitor/v1/...` |
| IAM | `/iam/v1/...` |
| Tenancy | `/tenancy/v1/...` |
| Subscription | `/subscription/v1/...` |

## Authentication

All API calls use OAuth2 client credentials flow. Credentials are loaded automatically from local `.env` files — **no sensitive data needs to be passed as arguments or declared in skill metadata**.

### Credential Setup

Users store their credentials in a `.env` file (see `scripts/.env.example` for the template). The auth helper searches these locations in order:

1. **Environment variables** — already exported in shell (`PRISMA_CLIENT_ID`, `PRISMA_CLIENT_SECRET`, `PRISMA_TSG_ID`)
2. **`.env` in current working directory** — project-level config
3. **`~/.sase/.env`** — global config shared across all projects

### Get an access token (bash)

```bash
# Source credentials from .env file first
set -a; source ~/.sase/.env 2>/dev/null || source .env 2>/dev/null; set +a

curl -s -X POST "https://auth.apps.paloaltonetworks.com/oauth2/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${PRISMA_CLIENT_ID}:${PRISMA_CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=tsg_id:${PRISMA_TSG_ID}"
```

The response returns a JWT access token valid for **15 minutes**. There is no refresh token — request a new one when it expires.

### Python authentication helper

When generating Python scripts, use the helper at `scripts/sase_auth.py` (relative to this skill directory). It automatically discovers credentials from `.env` files — no manual credential passing required:

```python
from sase_auth import SASEAuth
auth = SASEAuth()  # auto-discovers credentials from .env files
token = auth.get_token()
```

You can also point to a specific `.env` file:
```python
auth = SASEAuth(env_file="/path/to/my/.env")
```

### Required headers for all API calls

```
Authorization: Bearer <ACCESS_TOKEN>
Content-Type: application/json
```

Some services also require a **regional header**:
```
x-panw-region: <region_code>
```
Required for: Aggregate Monitoring, ZTNA Connector, Autonomous DEM.
Valid regions: `americas`, `au`, `ca`, `de`, `europe`, `in`, `jp`, `sg`, `uk`.

**Important:** Including `x-panw-region` on services that don't need it causes errors. Only add it when the endpoint requires it.

## Product-Specific Guides

Depending on what the user needs, read the relevant reference file for detailed endpoint documentation:

| User wants to... | Read this file |
|-------------------|---------------|
| Manage security policies, remote networks, GlobalProtect, service connections, decryption rules, or any Prisma Access configuration | `references/prisma-access.md` |
| Configure SD-WAN sites, routing, path policies, NAT, QoS, or query SD-WAN metrics/events | `references/prisma-sdwan.md` |
| Manage Prisma Access Browser settings, policies, or deployments | `references/prisma-browser.md` |
| Set up authentication, manage tokens, or troubleshoot auth issues | `references/authentication.md` |
| Query aggregate monitoring data, alerts, or multi-tenant reports | `references/monitoring.md` |

Read the appropriate reference file before generating API calls for that product area.

## Common API Patterns

### Prisma Access Configuration: Candidate/Running Config Model

Prisma Access uses a two-stage configuration model. Changes go to a "candidate" config first, then must be pushed to become the "running" config:

1. **Make changes** — POST/PUT/DELETE to config endpoints (creates candidate changes)
2. **Push candidate config:**
   ```bash
   curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions/candidate:push" \
     -H "Authorization: Bearer ${TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"folders": ["All"]}'
   ```
3. **Monitor the push job using the Father/Child Job pattern** (see below)
4. The candidate becomes the running configuration

Always remind the user that config changes won't take effect until pushed.

### Config Push Job Monitoring: Father/Child Job Pattern

**Critical:** A config push creates a **two-level job chain**. The initial response only returns the Father Job ID. You **must** find and monitor the Child Job to determine if the push truly succeeded.

#### Job Chain Structure

```
Father Job (CommitAndPush, type=53)   ← Returned by push API
│  Validates and commits candidate config
│  status=FIN, result=OK does NOT mean push succeeded!
│
└── Child Job (CommitAll, type=22)    ← Must be discovered via parent_id
    Actually pushes config to cloud firewalls
    This is the REAL result of the push
```

#### How to find Child Jobs

The API does not return child job IDs directly. After the Father Job completes, query recent jobs and filter by `parent_id`:

```bash
# 1. Push returns the Father Job ID
FATHER_JOB_ID=$(curl -s -X POST ".../config-versions/candidate:push" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"folders": ["Remote Networks"]}' | python3 -c "import sys,json; print(json.load(sys.stdin)['job_id'])")

# 2. After Father Job finishes, find Child Jobs
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/jobs?limit=10" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
for job in data.get('data', []):
    if str(job.get('parent_id')) == '${FATHER_JOB_ID}':
        print(f'Child Job {job[\"id\"]}: {job[\"status_str\"]} / {job[\"result_str\"]}')"
```

#### Monitoring procedure

1. **Poll Father Job** every 10 seconds until `status_str == "FIN"`
2. **Wait 10-30 seconds** for Child Job to appear
3. **Query `GET /jobs?limit=10`** and filter by `parent_id == father_job_id`
4. **Poll Child Job(s)** every 2 minutes until `status_str` is terminal
5. **Check Child Job result** to determine true push outcome

#### Job status reference

| `status_str` | `result_str` | Meaning |
|-------------|-------------|---------|
| `ACT` | `PEND` | Job is running |
| `FIN` | `OK` | Job completed successfully |
| `FIN` | `FAIL` | Job failed (check `details` field) |
| `PUSHFAIL` | `FAIL` | Push to cloud failed |
| `PUSHSUC` | `OK` | Push to cloud succeeded |

#### Reading error details from Child Job

The Child Job's `details` field is a JSON string containing per-region results:

```json
{
  "Remote-Networks-FW": {
    "status": "commit failed",
    "errors": ["error message here"],
    "result": "FAIL"
  },
  "job_details": [
    {"region": "Japan Central", "service_type": "FW", "commit_status": "Success"},
    {"region": "Singapore", "service_type": "FW", "commit_status": "Failure", "details": "..."}
  ]
}
```

Always parse the `details` field as JSON and check `job_details` for per-region status when diagnosing push failures.

**Common push failure reasons:**
- `"Failed to process the onboarding collect of sites"` — Cloud is still processing previous site changes. Wait 10-15 minutes and retry.
- `"application-tag -> X is not a valid reference"` — Invalid object reference in config. Fix the reference before retrying.
- `"Certificate X expired"` — An expired certificate is blocking the push. Renew or remove it.
- `"Internal server error with code 502"` — Cloud infrastructure issue. Check the status page and retry later.

### Prisma SASE Service Status Page

**Status Page URL:** https://sase.status.paloaltonetworks.com
**Status API:** https://sase.status.paloaltonetworks.com/api

**When to check the status page:**

1. **On first interaction of each day** — Before making any API calls, check the status page for active incidents or scheduled maintenance that may affect operations.
2. **After 2+ consecutive push failures** — If Child Jobs fail 2 or more times in a row (especially with 502 errors or "In Progress" timeouts), check the status page for service disruptions before retrying.
3. **On unexpected 5xx errors** — Any repeated 500/502/503 errors from the API should trigger a status page check.

**How to check programmatically:**

```bash
# Get current SASE service status summary
curl -s "https://sase.status.paloaltonetworks.com/api/v2/status.json" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
status = data.get('status', {})
print(f'Overall: {status.get(\"description\", \"Unknown\")} ({status.get(\"indicator\", \"?\")})')
"

# Get active incidents
curl -s "https://sase.status.paloaltonetworks.com/api/v2/incidents/unresolved.json" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
incidents = data.get('incidents', [])
if not incidents:
    print('No active incidents')
else:
    for inc in incidents:
        print(f'⚠️  [{inc.get(\"impact\",\"?\")}] {inc.get(\"name\",\"?\")}')
        print(f'   Status: {inc.get(\"status\",\"?\")} | Updated: {inc.get(\"updated_at\",\"?\")[:19]}')
        for u in inc.get('incident_updates', [])[:1]:
            print(f'   Latest: {u.get(\"body\",\"\")[:200]}')
"

# Get scheduled maintenances
curl -s "https://sase.status.paloaltonetworks.com/api/v2/scheduled-maintenances/upcoming.json" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
maint = data.get('scheduled_maintenances', [])
if not maint:
    print('No upcoming maintenance')
else:
    for m in maint:
        print(f'🔧 {m.get(\"name\",\"?\")}')
        print(f'   Scheduled: {m.get(\"scheduled_for\",\"?\")[:19]} to {m.get(\"scheduled_until\",\"?\")[:19]}')
"
```

**Status indicator values:** `none` (operational), `minor`, `major`, `critical`.

### SD-WAN: Profile Initialization

After obtaining a token, the first SD-WAN API call must be:
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sdwan/v2.1/api/profile" \
  -H "Authorization: Bearer ${TOKEN}"
```
Skipping this causes 403 errors on subsequent SD-WAN calls.

### Aggregate Monitoring: POST-based Filtering

Monitoring queries use POST with structured filter bodies, not query parameters:

```json
{
  "filter": {
    "operator": "AND",
    "rules": [
      {"property": "severity", "operator": "in", "values": ["Critical", "High"]},
      {"property": "event_time", "operator": "last_n_days", "values": [7]}
    ]
  },
  "properties": [
    {"property": "total_count"},
    {"property": "severity"}
  ]
}
```

Filter operators: `in`, `gt`, `lt`, `last_n_minutes`, `last_n_hours`, `last_n_days`.

### Multi-tenant Aggregation

Add `?agg_by=tenant` to aggregate responses across a parent tenant and all child tenants.

### Common Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad request | Check request body/params |
| 401 | Unauthorized | Token expired or invalid — re-authenticate |
| 403 | Forbidden | Insufficient role permissions (or SD-WAN profile not initialized) |
| 409 | Conflict | Resource already exists or version conflict |

## Script Generation Guidelines

When generating scripts for the user:

1. **Never hardcode credentials** — always use the `.env` file auto-discovery mechanism via `SASEAuth()` or source from `.env` files in shell scripts.
2. **Handle token expiry** — tokens last 15 minutes. For long-running scripts, implement token refresh logic.
3. **Include error handling** — check HTTP status codes and print meaningful error messages.
4. **Use the auth helper** — for Python scripts, reference `scripts/sase_auth.py` for a reusable auth class.
5. **Remind about config push** — when generating Prisma Access config changes, always include the push step or remind the user it's needed.
6. **Initialize SD-WAN profile** — when generating SD-WAN scripts, include the profile initialization call.

## Tenant Service Groups (TSGs)

TSGs are the organizational hierarchy for multi-tenancy:
- A TSG contains tenants and/or child TSGs
- OAuth tokens are scoped to a specific TSG and its children
- The root TSG must be created via UI; child TSGs can be created via API
- Key endpoints:
  - `GET /tenancy/v1/tenant_service_groups` — list all TSGs (includes `parent_id` field)
  - `GET /tenancy/v1/tenant_service_groups/{tsg_id}` — get a single TSG's details

**Important:** The `/children` and `/ancestors` sub-endpoints (`/tenancy/v1/tenant_service_groups/{id}/children`) return 404 for most tenant types. To reliably list child TSGs, use `GET /tenancy/v1/tenant_service_groups` to fetch all TSGs and filter by `parent_id` in the response:

```bash
# List all TSGs, then filter children of a specific parent
curl -s "https://api.sase.paloaltonetworks.com/tenancy/v1/tenant_service_groups" \
  -H "Authorization: Bearer ${TOKEN}" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
parent_id = '${PRISMA_TSG_ID}'
for tsg in data.get('items', []):
    if tsg.get('parent_id') == parent_id:
        print(f\"  {tsg['display_name']} (ID: {tsg['id']})\")"
```

## IAM and Roles

Service accounts need appropriate roles assigned to perform API operations. Key roles:
- **Superuser** — full read/write
- **Security Admin** — security policy management
- **Network Admin** — network policy and logs
- **View Only Administrator** — read-only across all
- **SOC Analyst** — read-only for logs, reports, alerts

If the user gets 403 errors, suggest checking their service account's role assignments.
