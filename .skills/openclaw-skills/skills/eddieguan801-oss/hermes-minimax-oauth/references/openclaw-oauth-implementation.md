# OpenClaw MiniMax OAuth Implementation Reference

Source: `/usr/lib/node_modules/openclaw/dist/oauth-By37UYEo.js`

## OAuth Configuration

```javascript
const MINIMAX_OAUTH_CONFIG = {
    cn: {
        baseUrl: "https://api.minimaxi.com",
        clientId: "78257093-7e40-4613-99e0-527b14b39113"
    },
    global: {
        baseUrl: "https://api.minimax.io",
        clientId: "78257093-7e40-4613-99e0-527b14b39113"
    }
};

const MINIMAX_OAUTH_SCOPE = "group_id profile model.completion";
const MINIMAX_OAUTH_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:user_code";
```

## Endpoints

```javascript
function getOAuthEndpoints(region) {
    const config = MINIMAX_OAUTH_CONFIG[region];
    return {
        codeEndpoint: `${config.baseUrl}/oauth/code`,
        tokenEndpoint: `${config.baseUrl}/oauth/token`,
        clientId: config.clientId,
        baseUrl: config.baseUrl
    };
}
```

## PKCE Generation

```javascript
function generatePkce() {
    const verifier = base64urlencode(randomBytes(32));
    const challenge = base64urlencode(sha256(verifier));
    const state = base64urlencode(randomBytes(16));
    return { verifier, challenge, state };
}
```

## Authorization Code Request

```javascript
async function requestOAuthCode(params) {
    const response = await fetch(endpoints.codeEndpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "x-request-id": randomUUID()
        },
        body: toFormUrlEncoded({
            response_type: "code",
            client_id: endpoints.clientId,
            scope: MINIMAX_OAUTH_SCOPE,
            code_challenge: params.challenge,
            code_challenge_method: "S256",
            state: params.state
        })
    });
    // Returns: { verification_uri, user_code, expired_in, interval, state, base_resp }
}
```

## Token Polling

```javascript
async function pollOAuthToken(params) {
    const response = await fetch(endpoints.tokenEndpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        },
        body: toFormUrlEncoded({
            grant_type: MINIMAX_OAUTH_GRANT_TYPE,
            client_id: endpoints.clientId,
            user_code: params.userCode,
            code_verifier: params.verifier
        })
    });
    // Response status values: "error", "pending", "success"
    // Success returns: { access_token, refresh_token, expired_in, resource_url }
}
```

## Login Flow

```javascript
async function loginMiniMaxPortalOAuth(params) {
    const { verifier, challenge, state } = generatePkce();
    const oauth = await requestOAuthCode({ challenge, state, region });
    
    // Show user: oauth.verification_uri and oauth.user_code
    // Poll until status === "success" or timeout
    
    while (Date.now() < expireTimeMs) {
        const result = await pollOAuthToken({ userCode: oauth.user_code, verifier, region });
        if (result.status === "success") return result.token;
        if (result.status === "error") throw new Error(result.message);
        await sleep(pollIntervalMs);
    }
    throw new Error("Timed out");
}
```

## Token Response Structure

Success:
```json
{
    "status": "success",
    "access_token": "...",
    "refresh_token": "...",
    "expired_in": 3600,
    "resource_url": "..."
}
```

Pending (keep polling):
```json
{
    "status": "pending",
    "message": "current user code is not authorized"
}
```

Error:
```json
{
    "status": "error",
    "message": "An error occurred. Please try again later"
}
```

## Test Command

```bash
curl -X POST "https://api.minimax.io/oauth/code" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "response_type=code&client_id=78257093-7e40-4613-99e0-527b14b39113&scope=group_id+profile+model.completion&code_challenge=test&code_challenge_method=S256&state=test"
```

Expected response:
```json
{
    "verification_uri": "https://platform.minimax.io/oauth-authorize?user_code=M9ZmbtkFDY&client=OpenClaw",
    "user_code": "M9ZmbtkFDY",
    "expired_in": 1776633969032,
    "interval": 1000,
    "state": "test",
    "base_resp": {"status_code": 0, "status_msg": "success"}
}
```
