---
name: remove-bg
description: Remove image background to transparent PNG. Powered by RMBG-2.0, commercially-safe model. Extract subjects for overlays, product photography, logos, and cutouts.
license: MIT
metadata:
  author: Bria AI
  version: "1.0.0"
  auth_server: "https://auth.bria.ai"
---

# Remove Background — Transparent PNG with AI

Remove image backgrounds to produce a transparent PNG. Uses Bria's RMBG-2.0 model — commercially safe and production ready.

## Setup — Authentication

Before making any API call, you need a valid Bria access token.

Set the auth server URL from the metadata above (or override if instructed):

```bash
BRIA_AUTH_SERVER="${BRIA_AUTH_SERVER:-https://auth.bria.ai}"
```

### Step 1: Check for existing credentials

```bash
if [ -f ~/.bria/credentials ]; then
  BRIA_API_KEY=$(python3 -c "import json; print(json.load(open('$HOME/.bria/credentials'))['access_token'])" 2>/dev/null)
fi
if [ -z "$BRIA_API_KEY" ]; then
  echo "NO_CREDENTIALS"
else
  echo "BRIA_API_KEY is set"
fi
```

If the output is `BRIA_API_KEY is set`, skip to **Remove Background** below.
If the API key is rejected by the Bria API later, delete `~/.bria/credentials` and restart from Step 2.

### Step 2: Authenticate via device authorization

If no credentials are found, start the device authorization flow.

**2a. Request a device code:**

```bash
DEVICE_RESPONSE=$(curl -s -X POST "$BRIA_AUTH_SERVER/device/authorize" \
  -H "Content-Type: application/json")
echo "$DEVICE_RESPONSE"
```

Parse the response fields:
- `device_code` — used to poll for the token (keep this, don't show to user)
- `user_code` — the code the user must enter (e.g. `BRIA-XXXX`)
- `verification_uri` — the URL the user must visit
- `interval` — seconds between poll attempts

**2b. Show the user the code and link.** Tell them:

> To connect your Bria account, open this link and enter the code shown:
> **{verification_uri_complete}**
>
> Or go to **{verification_uri}** and enter code: **{user_code}**

**2c. Poll for the token.** After showing the user the code, immediately start polling. Try up to 60 times with the given interval (default 5 seconds):

```bash
for i in $(seq 1 60); do
  TOKEN_RESPONSE=$(curl -s -X POST "$BRIA_AUTH_SERVER/token" \
    -d "grant_type=urn:ietf:params:oauth:grant-type:device_code" \
    -d "device_code=$DEVICE_CODE")
  ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))" 2>/dev/null)
  if [ -n "$ACCESS_TOKEN" ] && [ "$ACCESS_TOKEN" != "" ]; then
    # Resolve the bearer token to a real Bria API key via introspection
    INTROSPECT=$(curl -s -X POST "$BRIA_AUTH_SERVER/token/introspect" \
      -d "token=$ACCESS_TOKEN")
    REAL_API_KEY=$(echo "$INTROSPECT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('api_token',''))" 2>/dev/null)
    if [ -n "$REAL_API_KEY" ] && [ "$REAL_API_KEY" != "" ]; then
      BRIA_API_KEY="$REAL_API_KEY"
    else
      BRIA_API_KEY="$ACCESS_TOKEN"
    fi
    mkdir -p ~/.bria
    python3 -c "
import json
with open('$HOME/.bria/credentials','w') as f:
    json.dump({'access_token':'$BRIA_API_KEY'},f)
"
    echo "AUTHENTICATED"
    break
  fi
  sleep 5
done
```

If the output contains `AUTHENTICATED`, proceed. Otherwise the code expired — start over from Step 2a.

**Do not proceed with any API call until authentication is confirmed.**

---

## Remove Background

Remove the background from any image, returning a transparent PNG.

The `image` parameter must be a publicly accessible URL. If the user provided a local file, upload it to a hosting service first or ask for a URL.

```bash
RESULT=$(curl -s -X POST "https://engine.prod.bria-api.com/v2/image/edit/remove_background" \
  -H "api_token: $BRIA_API_KEY" \
  -H "Content-Type: application/json" \
  -H "User-Agent: BriaSkills/1.0.0" \
  -d "{\"image\": \"$IMAGE_URL\"}")
echo "$RESULT"
```

The response contains `result_url` — a PNG with transparent background. Show this URL to the user.

If the response contains a `status_url` instead, the job is processing asynchronously. Poll it:

```bash
STATUS_URL=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status_url',''))" 2>/dev/null)
if [ -n "$STATUS_URL" ]; then
  for i in $(seq 1 30); do
    POLL=$(curl -s "$STATUS_URL" -H "api_token: $BRIA_API_KEY")
    IMAGE_URL_RESULT=$(echo "$POLL" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('image_url',d.get('result_url','')))" 2>/dev/null)
    if [ -n "$IMAGE_URL_RESULT" ] && [ "$IMAGE_URL_RESULT" != "" ]; then
      echo "DONE: $IMAGE_URL_RESULT"
      break
    fi
    sleep 3
  done
fi
```

---

## See Also

- [generate-image](../generate-image-skill/) — Generate images from text with FIBO
- [replace-bg](../replace-bg-skill/) — Replace background with AI-generated scene
- [lifestyle-shot](../lifestyle-shot-skill/) — Place products in lifestyle scenes
- [bria-skill](https://github.com/Bria-AI/agent-skills) — Full Bria AI skill (all tools)
