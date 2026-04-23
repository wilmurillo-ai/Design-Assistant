# Lark OpenClaw Bridge

Connects your local OpenClaw instance to Lark via a relay server — no public IP required.

```
Lark → oc.atomecorp.net → Relay → WebSocket → Bridge (local) → OpenClaw
```

---

## Prerequisites

- Node.js ≥ v22.0.0
- OpenClaw ≥ v2026.2.0

---

## Setup

### Step 1: Install the bridge

```bash
curl -fsSL https://oc.atomecorp.net/lark/install.sh | bash
```

When prompted, provide your Lark App ID, App Secret, and Verification Token (from Lark Open Platform).

### Step 2: Configure OpenClaw

```bash
openclaw configure
```

Select **Model** (enter your API key) and **Gateway** (set an auth token, Loopback bind, Tailscale off).

Restart the bridge after:

```bash
cd ~/lark-openclaw-bridge && pm2 restart lark-openclaw-bridge
```

Confirm it's connected:

```bash
pm2 logs lark-openclaw-bridge --lines 5
# Expected: [RELAY-CLIENT] Connected to relay
```

### Step 3: Configure Lark Open Platform

Go to [https://open.larksuite.com](https://open.larksuite.com) and set up your app:

1. **Event Subscriptions** → Request URL: `https://oc.atomecorp.net/lark/webhook/<your-app-id>` → click Verify
2. **Permission Management** → apply for:
   - `im:message.p2p_msg:readonly` — receive p2p message events
   - `im:message.group_msg:readonly` — receive all group message events
   - `im:message:send_as_bot` — send / reply as bot
   - `im:message:readonly` — read message content (quoted/forwarded messages)
   - `im:message.reaction:write` — add emoji reactions to messages
   - `im:resource` — upload images; download message attachments
   - `im:chat:readonly` — read group info and member list
   - `contact:user.base:readonly` — read user basic info (name, department)
3. **Publish** the app and wait for admin approval

### Step 4: Test

Send a direct message to your bot in Lark. You should get a reply from OpenClaw.

---

## Troubleshooting

**`openclaw` not found after `nvm use 22`**

Reinstall after switching Node version:
```bash
npm install -g openclaw
```

**`gateway.auth.token missing` in bridge logs**

Run `openclaw configure`, select Gateway, and set an auth token.

**Bridge keeps reconnecting / `ETIMEDOUT`**

Check that `RELAY_SERVER_URL` in `.env` uses `wss://` not `ws://`:
```bash
grep RELAY_SERVER_URL ~/lark-openclaw-bridge/.env
# Should be: RELAY_SERVER_URL=wss://oc.atomecorp.net/lark/bridge
```

**Verification token mismatch**

Copy the Verification Token directly from Lark Open Platform → Event Subscriptions into `.env`.

---

## Relay Server

Live logs: `https://oc.atomecorp.net/lark/logs?token=atome&format=html`
