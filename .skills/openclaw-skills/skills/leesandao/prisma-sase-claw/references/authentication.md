# Prisma SASE Authentication Reference

## Credential Management

### Credential Storage (`.env` files)

Credentials are stored locally in `.env` files and auto-discovered at runtime. **No credentials are declared in skill metadata or passed as arguments.**

The auth helper searches these locations in order:
1. **Environment variables** — already exported in shell
2. **`.env` in current working directory** — project-level config
3. **`~/.sase/.env`** — global config shared across projects

Setup:
```bash
# Copy the template
cp scripts/.env.example ~/.sase/.env

# Edit with your credentials
vi ~/.sase/.env

# Lock down permissions (owner-only read/write)
chmod 600 ~/.sase/.env
```

### Prerequisites

Before you can authenticate:

1. **Create a Tenant Service Group (TSG)** — the root TSG must be created through the Prisma SASE UI at `https://app.prismaaccess.com`
2. **Create a Service Account** — generates a `client_id` and `client_secret`. The secret is shown only once and cannot be retrieved later.
3. **Assign Roles** — without roles, even a valid token won't authorize any operations.
4. **Store credentials** — save them to `~/.sase/.env` or a project-level `.env` file.

## OAuth2 Client Credentials Flow

### Token Request (bash)

```bash
# Source credentials from .env
set -a; source ~/.sase/.env 2>/dev/null || source .env 2>/dev/null; set +a

curl -s -X POST "https://auth.apps.paloaltonetworks.com/oauth2/access_token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "${PRISMA_CLIENT_ID}:${PRISMA_CLIENT_SECRET}" \
  -d "grant_type=client_credentials&scope=tsg_id:${PRISMA_TSG_ID}"
```

**Parameters:**

| Parameter | Location | Value |
|-----------|----------|-------|
| Authorization | Header | `Basic base64(client_id:client_secret)` |
| grant_type | Body | `client_credentials` |
| scope | Body | `tsg_id:<your_tsg_id>` |
| Content-Type | Header | `application/x-www-form-urlencoded` |

### Token Response

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "scope": "tsg_id:1234567890",
  "token_type": "Bearer",
  "expires_in": 899
}
```

- **Format:** JWT (can be decoded at jwt.io to verify claims)
- **Lifetime:** 899 seconds (~15 minutes)
- **No refresh token** — request a new token when it expires

### Using the Token

Include in all API requests:
```
Authorization: Bearer <access_token>
```

### Python Token Request

```python
from sase_auth import SASEAuth

# Auto-discovers credentials from .env files
auth = SASEAuth()
token = auth.get_token()

# Or point to a specific .env file
auth = SASEAuth(env_file="/path/to/custom/.env")

# Or pass credentials explicitly (not recommended)
auth = SASEAuth(
    client_id="your_client_id",
    client_secret="your_secret",
    tsg_id="your_tsg_id"
)
```

## Token Scoping

- A token is scoped to the TSG specified in the `scope` parameter
- The token grants access to that TSG and all its child TSGs
- To access a different part of the tenant hierarchy, request a new token with a different `tsg_id`

## Querying TSG Hierarchy

To list child TSGs under a parent, use `GET /tenancy/v1/tenant_service_groups` and filter by `parent_id`:

```bash
curl -s "https://api.sase.paloaltonetworks.com/tenancy/v1/tenant_service_groups" \
  -H "Authorization: Bearer ${TOKEN}"
```

Each item in the response includes a `parent_id` field. Filter client-side to find children of a specific TSG.

**Do NOT use** `GET /tenancy/v1/tenant_service_groups/{id}/children` or `/ancestors` — these sub-endpoints return 404 for most tenant types and are unreliable.

## Troubleshooting Authentication

| Error | Cause | Fix |
|-------|-------|-----|
| 401 Unauthorized | Invalid or expired token | Re-authenticate with valid credentials |
| 401 + "invalid_client" | Wrong client_id or client_secret | Verify credentials; regenerate if lost |
| 401 + "invalid_scope" | TSG ID doesn't exist or not accessible | Verify TSG ID in the UI |
| 403 Forbidden | Token valid but insufficient permissions | Check service account role assignments |
| 403 on SD-WAN calls | Profile not initialized | Call `GET /sdwan/v2.1/api/profile` first |
| 404 on `/children` or `/ancestors` | These sub-endpoints don't work for most TSG types | Use `GET /tenant_service_groups` and filter by `parent_id` instead |

## Security Best Practices

1. **Never hardcode credentials** — use environment variables or a secrets manager
2. **Rotate secrets regularly** — create new service account credentials periodically
3. **Least privilege** — assign only the roles needed for the API operations you'll perform
4. **Token caching** — cache tokens and reuse until near expiry rather than requesting a new one per call
5. **Secure storage** — store client_secret encrypted; it cannot be retrieved from the UI after creation

## Service Account Management via API

Once authenticated, you can manage service accounts programmatically:

```bash
# List service accounts
curl -s -X GET "https://api.sase.paloaltonetworks.com/iam/v1/service_accounts" \
  -H "Authorization: Bearer ${TOKEN}"

# Create a service account
curl -s -X POST "https://api.sase.paloaltonetworks.com/iam/v1/service_accounts" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "automation-account",
    "description": "Account for CI/CD pipeline"
  }'

# Assign a role to a service account
curl -s -X POST "https://api.sase.paloaltonetworks.com/iam/v1/access_policies" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "principal": "<service_account_id>",
    "role": "security_admin",
    "resource": "tsg:<tsg_id>"
  }'
```
