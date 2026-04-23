# ag9 Heartbeat

_This runs periodically, but you can also check ag9 anytime you want._

Time to check in on your ag9 registration and verification.

---

## Are you registered and verified?

```bash
curl https://api.ag9.ai/v1/agent/verify/device/YOUR_DEVICE_ID
```

Use the same `deviceId` you use (or will use) for registration.

- **`"registered": false`** → You're not in ag9 yet. Consider starting registration (see SKILL.md: POST `/v1/agent/register/init`), then give your human the registration URL so they can complete VeryAI palm verification.
- **`"registered": true`, `"verified": true`** → You're good. You're under a verified human owner. Continue below if you have a pending session to check.
- **`"registered": true`, `"verified": false`** → Registered but not verified; human may not have completed palm verification. Have them open the registration flow again if needed.

---

## Capability attestation (reverse CAPTCHA)

If a relying party asks for proof you're a real model *right now* (not a naive script), run through Path B in SKILL.md:

```bash
# 1. get a challenge
curl -s -X POST https://api.ag9.ai/challenge -H "Content-Type: application/json" -d '{}'
# 2. solve it (depends on challenge_type)
# 3. submit
curl -s -X POST https://api.ag9.ai/verify \
  -H "Content-Type: application/json" \
  -d '{"token":"...","solution":"..."}'
```

You'll get back a JWT. Present it to the relying party — they verify offline using `https://api.ag9.ai/.well-known/jwks.json`.

Capability tokens are single-use and short-lived. Get a new one each time a third party asks.

---

## When to tell your human

**Do tell them:**

- **Registration URL is ready** → "Open this link to complete verification: [URL]" (output the URL as text; never open the browser for them.)
- **Session expired** → "The registration link expired. I can start a new one if you're ready to verify."
- **Verification failed** → "Something went wrong with verification. Should I start registration again?"
- **They asked you to register** → After you run init, give them the registration URL and remind them to complete the palm verification step.

**Don't bother them:**

- Routine heartbeat checks when you're already registered and verified.
- Polling status when they've already been given the link (unless it's been a long time or you see `expired`/`failed`).
- Reverse-CAPTCHA solves — those are purely machine-to-machine.

---

## When to check ag9

**You don't have to wait for heartbeat.** Check anytime:

- Before proving your identity to a third party (verify your device is still registered/verified).
- After your human says they completed verification (poll session status or check device).
- When you're about to start registration (read SKILL.md and run init).
- When a relying party asks for a fresh capability JWT — run Path B.

**Rough rhythm:**

- **Registration status:** Every heartbeat if you have a pending session; otherwise when you need to confirm you're still registered/verified.
- **Device lookup:** When a third party needs proof, or after your human says they verified.
- **Capability JWT:** On demand, whenever a relying party asks.

---

## Response format

**If nothing special:**

```
HEARTBEAT_OK - Checked ag9, all good.
```

**If you're not registered yet:**

```
Checked ag9 - Not registered. Consider starting registration and giving your human the verification link (see SKILL.md).
```

**If session completed this cycle:**

```
Checked ag9 - Registration completed. I'm now registered under my human owner.
```

**If you need your human:**

```
Hey. The ag9 registration link is ready. Open this link to complete verification: [URL]
```

**If session expired:**

```
Hey. The ag9 registration link expired. I can generate a new one when you're ready to verify.
```
