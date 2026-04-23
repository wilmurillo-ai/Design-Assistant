# Prisma Access Configuration API

Base path: `https://api.sase.paloaltonetworks.com/sse/config/v1/`

Prisma Access is the cloud-delivered security service. All configuration changes go through a candidate/running config model — changes are staged in a "candidate" config and must be explicitly pushed to become active.

## Table of Contents

1. [Security Policy Rules](#security-policy-rules)
2. [Addresses and Address Groups](#addresses-and-address-groups)
3. [Services and Service Groups](#services-and-service-groups)
4. [Threat Prevention Profiles](#threat-prevention-profiles)
5. [Remote Networks](#remote-networks)
6. [Service Connections](#service-connections)
7. [GlobalProtect / Mobile Users](#globalprotect--mobile-users)
8. [IKE and IPSec Configuration](#ike-and-ipsec-configuration)
9. [Certificate Management](#certificate-management)
10. [Authentication Infrastructure](#authentication-infrastructure)
11. [User and Group Management](#user-and-group-management)
12. [Decryption Rules](#decryption-rules)
13. [Traffic Steering and QoS](#traffic-steering-and-qos)
14. [Configuration Push](#configuration-push)

---

## Security Policy Rules

Security rules control traffic flow through Prisma Access.

### List security rules
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules?folder=All" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create a security rule
```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules?folder=All" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "allow-web-traffic",
    "from": ["trust"],
    "to": ["untrust"],
    "source": ["any"],
    "destination": ["any"],
    "application": ["web-browsing", "ssl"],
    "service": ["application-default"],
    "action": "allow",
    "log_end": true
  }'
```

### Update a security rule
```bash
curl -s -X PUT "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules/{rule_id}?folder=All" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

### Delete a security rule
```bash
curl -s -X DELETE "https://api.sase.paloaltonetworks.com/sse/config/v1/security-rules/{rule_id}?folder=All" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Other rule types

The same CRUD pattern applies to:
- `traffic-steering-rules` — traffic routing decisions
- `application-override-rules` — override app identification
- `decryption-rules` — SSL/TLS decryption policies
- `authentication-rules` — authentication enforcement
- `qos-policy-rules` — quality of service policies

All use the same base path and `?folder=` query parameter.

---

## Addresses and Address Groups

### List addresses
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sse/config/v1/addresses?folder=All" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create an address object
```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/addresses?folder=All" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "webserver-subnet",
    "ip_netmask": "10.0.1.0/24",
    "description": "Web server subnet"
  }'
```

Address types: `ip_netmask`, `ip_range`, `ip_wildcard`, `fqdn`.

### Address Groups
```bash
# List
GET /sse/config/v1/address-groups?folder=All

# Create (static group)
POST /sse/config/v1/address-groups?folder=All
{
  "name": "web-servers",
  "static": ["webserver-1", "webserver-2"],
  "description": "All web servers"
}

# Create (dynamic group)
POST /sse/config/v1/address-groups?folder=All
{
  "name": "tagged-servers",
  "dynamic": {"filter": "'web' and 'production'"}
}
```

---

## Services and Service Groups

### List services
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sse/config/v1/services?folder=All" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Create a service
```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/services?folder=All" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "custom-app-port",
    "protocol": {
      "tcp": {"port": "8443"}
    }
  }'
```

### Service Groups
```bash
POST /sse/config/v1/service-groups?folder=All
{
  "name": "web-services",
  "members": ["service-http", "service-https", "custom-app-port"]
}
```

---

## Threat Prevention Profiles

### Anti-Spyware Profiles
```bash
GET  /sse/config/v1/anti-spyware-profiles?folder=All
POST /sse/config/v1/anti-spyware-profiles?folder=All
```

### Vulnerability Protection Profiles
```bash
GET  /sse/config/v1/vulnerability-protection-profiles?folder=All
POST /sse/config/v1/vulnerability-protection-profiles?folder=All
```

### WildFire Antivirus Profiles
```bash
GET  /sse/config/v1/wildfire-anti-virus-profiles?folder=All
POST /sse/config/v1/wildfire-anti-virus-profiles?folder=All
```

### Other security profiles
- `file-blocking-profiles` — file blocking rules
- `dns-security-profiles` — DNS-layer protection
- `url-access-profiles` — URL filtering

---

## Remote Networks

Remote networks connect branch sites to Prisma Access via IPSec tunnels.

### List remote networks
```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sse/config/v1/remote-networks?folder=All" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Bandwidth Allocation Management

Bandwidth must be allocated to a location before Remote Network sites can be created there.

#### List current allocations
```bash
GET /sse/config/v1/bandwidth-allocations?folder=Remote%20Networks
# Response: {"data": [{"name": "hong-kong", "allocated_bandwidth": 50, "spn_name_list": ["hong-kong-myrtle"]}]}
```

#### Allocate bandwidth to a new location
```bash
POST /sse/config/v1/bandwidth-allocations?folder=Remote%20Networks
# Body: {"name": "ap-southeast-1", "allocated_bandwidth": 50}
# The "name" must match a location's "value" field from GET /locations
# Response includes the auto-assigned SPN: {"spn_name_list": ["ap-southeast-1-rhododendron"]}
```

#### Delete (deprovision) bandwidth from a location

**Important:** The DELETE endpoint uses a **different parameter pattern** than other config endpoints:

```bash
# ✅ Correct: use name + spn_name_list as query params, NO folder param
DELETE /sse/config/v1/bandwidth-allocations?name=hong-kong&spn_name_list=hong-kong-myrtle

# ❌ Wrong: "folder" is not allowed, "spn_name_list" is required
DELETE /sse/config/v1/bandwidth-allocations?folder=Remote%20Networks&name=hong-kong

# ❌ Wrong: request body is not supported for DELETE
DELETE /sse/config/v1/bandwidth-allocations -d '{"name":"hong-kong","spn_name_list":["hong-kong-myrtle"]}'
```

You must provide both `name` (location name) and `spn_name_list` (SPN name) as query parameters. Get these values from `GET /bandwidth-allocations` first.

**Note:** All bandwidth changes require a config push to take effect.

---

### Create a Remote Network Site — Full Procedure

Creating a Remote Network site requires creating **three resources in order** (IKE Gateway → IPSec Tunnel → Remote Network), and the `region` value must come from the API — **never guess or hardcode region codes**.

#### Step 1: Query available locations and bandwidth allocations

The `region` and `spn_name` values **must** come from these API queries:

```bash
# Get the correct region code for a location
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/locations?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}"
# Response includes: {"value": "hong-kong", "display": "Hong Kong", "region": "asia-east2", ...}
# Use the "region" field (e.g. "asia-east2") — NOT the "value" field

# Get available SPNs (only locations with allocated bandwidth can have sites)
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/bandwidth-allocations?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}"
# Response includes: {"name": "hong-kong", "spn_name_list": ["hong-kong-lily"], "allocated_bandwidth": 50}
# Use the SPN name from "spn_name_list"

# Get available IKE and IPSec crypto profiles
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/ike-crypto-profiles?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}"
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-crypto-profiles?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}"
```

**Critical:** The `region` value in the Remote Network payload must be the `region` field from the `/locations` response (e.g. `asia-east2` for Hong Kong), NOT the `value` field (e.g. `hong-kong`). Using wrong region codes causes sites to be created in the wrong location (e.g. `ap-southeast-1` is Singapore, not Hong Kong).

#### Step 2: Create IKE Gateway

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/ike-gateways?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HK-Site-1-IKE-GW",
    "local_address": {"interface": "vlan"},
    "peer_address": {"dynamic": {}},
    "authentication": {"pre_shared_key": {"key": "YourPSK"}},
    "protocol_common": {
      "passive_mode": true,
      "nat_traversal": {"enable": true},
      "fragmentation": {"enable": false}
    },
    "protocol": {
      "version": "ikev2",
      "ikev2": {"ike_crypto_profile": "PaloAlto-Networks-IKE-Crypto", "dpd": {"enable": true}},
      "ikev1": {"dpd": {"enable": true}}
    }
  }'
```

#### Step 3: Create IPSec Tunnel (references the IKE Gateway)

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/ipsec-tunnels?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HK-Site-1-IPSec-Tunnel",
    "auto_key": {
      "ike_gateway": [{"name": "HK-Site-1-IKE-GW"}],
      "ipsec_crypto_profile": "PaloAlto-Networks-IPSec-Crypto"
    },
    "tunnel_interface": "tunnel",
    "anti_replay": true
  }'
```

#### Step 4: Create Remote Network (references the IPSec Tunnel)

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/remote-networks?folder=Remote%20Networks" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "HK-Site-1",
    "region": "asia-east2",
    "spn_name": "hong-kong-lily",
    "license_type": "FWAAS-AGGREGATE",
    "ipsec_tunnel": "HK-Site-1-IPSec-Tunnel",
    "ecmp_load_balancing": "disable",
    "protocol": {}
  }'
```

#### Step 5: Push configuration and monitor (see SKILL.md Father/Child Job pattern)

#### Region code reference (common locations)

| Location | `region` code | Notes |
|----------|--------------|-------|
| Hong Kong | `asia-east2` | |
| Japan Central | `ap-northeast-1` | Also called asia-northeast |
| Singapore | `ap-southeast-1` | Often confused with Hong Kong |
| US East | `us-east-1` or `us-east4` | Varies by sub-location |

**Always query `/locations` to get the correct region code. Do not assume or hardcode.**

#### After push: Service IP allocation

After a successful push, the cloud provisions the site. The `details` field in the Remote Network response will be populated with:
- `service_ip_address` — IKE peer IP for the remote device to connect to
- `fqdn` — DNS name for the service endpoint
- `loopback_ip_address` — Loopback IP

For **new locations** (first site in a region), provisioning may take **10-30 minutes** before `details` is populated. Existing locations are typically faster.

#### Deleting Remote Network Sites

Delete in **reverse order**: Remote Network → IPSec Tunnel → IKE Gateway.

```bash
DELETE /sse/config/v1/remote-networks/{id}?folder=Remote%20Networks
DELETE /sse/config/v1/ipsec-tunnels/{id}?folder=Remote%20Networks
DELETE /sse/config/v1/ike-gateways/{id}?folder=Remote%20Networks
```

---

## Service Connections

Service connections link data centers or HQ to Prisma Access.

```bash
GET  /sse/config/v1/service-connections?folder=All
POST /sse/config/v1/service-connections?folder=All
```

---

## GlobalProtect / Mobile Users

### Locations and regions
```bash
GET /sse/config/v1/locations?folder=All
GET /sse/config/v1/regions?folder=All
```

---

## IKE and IPSec Configuration

### IKE Gateways
```bash
GET  /sse/config/v1/ike-gateways?folder=All
POST /sse/config/v1/ike-gateways?folder=All
```

### IPSec Tunnels
```bash
GET  /sse/config/v1/ipsec-tunnels?folder=All
POST /sse/config/v1/ipsec-tunnels?folder=All
```

### Crypto Profiles
```bash
GET  /sse/config/v1/ike-crypto-profiles?folder=All
POST /sse/config/v1/ike-crypto-profiles?folder=All
GET  /sse/config/v1/ipsec-crypto-profiles?folder=All
POST /sse/config/v1/ipsec-crypto-profiles?folder=All
```

---

## Certificate Management

```bash
GET  /sse/config/v1/certificates?folder=All
POST /sse/config/v1/certificates?folder=All
GET  /sse/config/v1/certificate-profiles?folder=All
GET  /sse/config/v1/trusted-certificate-authorities?folder=All
```

---

## Authentication Infrastructure

### LDAP Server Profiles
```bash
GET  /sse/config/v1/ldap-server-profiles?folder=All
POST /sse/config/v1/ldap-server-profiles?folder=All
```

### SAML Server Profiles
```bash
GET  /sse/config/v1/saml-server-profiles?folder=All
POST /sse/config/v1/saml-server-profiles?folder=All
```

### Other authentication backends
- `kerberos-server-profiles`
- `radius-server-profiles`
- `tacacs-server-profiles`
- `mfa-servers`
- `authentication-profiles`
- `authentication-sequences`

---

## User and Group Management

```bash
GET  /sse/config/v1/local-users?folder=All
POST /sse/config/v1/local-users?folder=All
GET  /sse/config/v1/local-user-groups?folder=All
GET  /sse/config/v1/dynamic-user-groups?folder=All
```

---

## Decryption Rules

```bash
GET  /sse/config/v1/decryption-rules?folder=All
POST /sse/config/v1/decryption-rules?folder=All
PUT  /sse/config/v1/decryption-rules/{id}?folder=All
```

---

## Traffic Steering and QoS

```bash
GET  /sse/config/v1/traffic-steering-rules?folder=All
POST /sse/config/v1/traffic-steering-rules?folder=All
GET  /sse/config/v1/qos-policy-rules?folder=All
POST /sse/config/v1/qos-policy-rules?folder=All
```

---

## Configuration Push

After making changes, push the candidate config to make it active.

**Important:** A push creates a **two-level job chain** (Father Job → Child Job). The Father Job only commits the candidate config; the Child Job performs the actual push to cloud. You must monitor both to confirm success. See SKILL.md "Config Push Job Monitoring: Father/Child Job Pattern" for the full procedure.

### Push candidate configuration

```bash
curl -s -X POST "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions/candidate:push" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"folders": ["Remote Networks"]}'
# Response: {"success": true, "job_id": "1234", "message": "CommitAndPush job enqueued..."}
```

### Monitor push result (Father + Child Jobs)

```bash
# Step 1: Wait for Father Job to finish
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/jobs/${FATHER_JOB_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
# Wait until status_str == "FIN"

# Step 2: Find Child Job by parent_id
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/jobs?limit=10" \
  -H "Authorization: Bearer ${TOKEN}"
# Filter: job["parent_id"] == FATHER_JOB_ID

# Step 3: Poll Child Job every 2 minutes until terminal status
curl -s "https://api.sase.paloaltonetworks.com/sse/config/v1/jobs/${CHILD_JOB_ID}" \
  -H "Authorization: Bearer ${TOKEN}"
# PUSHSUC/FIN+OK = success, PUSHFAIL/FIN+FAIL = failure
# Parse "details" field (JSON string) for per-region results and errors
```

### Check running configuration

```bash
curl -s -X GET "https://api.sase.paloaltonetworks.com/sse/config/v1/config-versions/running" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Other utility endpoints
- `tags` — tag management for objects
- `schedules` — schedule definitions
- `external-dynamic-lists` — external IP/URL lists
