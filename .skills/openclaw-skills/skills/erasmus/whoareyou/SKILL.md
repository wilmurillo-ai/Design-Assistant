---
name: whoareyou
version: 1.0.0
description: Show your verified wayID identity card when a user asks who you are
user-invocable: true
---

# /whoareyou — Verified Identity Card

When a user types `/whoareyou`, display your verified wayID identity card so they can see who owns and operates you.

> Base URL: https://way.je

## Rules

- **NEVER open a browser or attempt to navigate to any URL.** All actions are API calls only.
- Do NOT invent or fabricate data. Only display information returned by the API.
- If any step fails, tell the user you could not retrieve your identity card and show the error.

## What to Do

### Step 1: Read Your Public Key

Read your Ed25519 public key from `~/.openclaw/identity/device.json`:

```json
{ "publicKey": "<base64>", "privateKey": "<base64>" }
```

You only need the `publicKey` field.

### Step 2: Look Up Your wayID

Call the wayID lookup API with your public key:

```
GET https://way.je/api/v1/agent/{publicKey}
```

Where `{publicKey}` is your base64 public key, URL-encoded.

The response contains your certificate ID:

```json
{
  "verified": true,
  "owner": {
    "identityMethod": "concordium",
    "identityLevel": "verified",
    "claimedAt": "2026-03-10T16:45:00Z"
  },
  "certificate": {
    "id": "wayid:agent:...",
    "status": "active",
    "verifyUrl": "/agent/wayid:agent:..."
  }
}
```

### Step 3: Fetch Your Identity Card

Using the certificate ID from Step 2, fetch your full card:

```
GET https://way.je/api/agents/{wayidDid}/card
```

The response contains:

```json
{
  "wayidDid": "wayid:agent:...",
  "displayName": "Your Agent Name",
  "username": "your-username",
  "description": "What you do",
  "status": "active",
  "claimedAt": "2026-03-10T16:45:00Z",
  "owner": {
    "displayName": "Owner Name",
    "username": "ownerusername"
  },
  "verification": {
    "provider": "concordium",
    "label": "Concordium ID",
    "verifiedAt": "2026-02-20T10:30:00Z"
  },
  "certificateUrl": "https://way.je/agent/wayid:agent:..."
}
```

### Step 4: Display the Identity Card

Format and display the card to the user like this:

---

**🛡️ {displayName}** `@{username}`

{description}

✅ Verified — {verification.label}
Owned by **{owner.displayName}** (@{owner.username})

[View Certificate →]({certificateUrl})

---

If the agent is **not verified** (no verification object), show:

---

**{displayName}** `@{username}`

{description}

⚠️ Identity not yet verified
Owned by **{owner.displayName}**

[View Certificate →]({certificateUrl})

---

## What is wayID?

wayID is provenance infrastructure for AI agents. It binds verified human identities to their AI agents, giving consumers a way to verify agent ownership and reputation — like SSL certificates, but for AI agents.
