---
name: bumble
description: >
  Bumble session, auth, matches, messages, sending, and profile-photo export via
  Remote Browser Service. Use to resume an existing Bumble app session, inspect
  state, list matches, fetch/send messages, export profile photos, or
  re-authenticate only when Bumble is on get-started/auth pages.
---

# Bumble Client

## Session policy

- Always start from `https://bumble.com/app`.
- Reuse the existing `bumble` session whenever possible.
- If Bumble is already authenticated, do **not** run the auth flow again.
- If you gettin `get-started` or `auth` pages then start "Auth flow"
- Re-authenticate only when Bumble is clearly on `get-started`, `auth`, or SMS-confirmation pages.
- For non-auth actions, resume the stored session only; if Bumble is logged out, return an error instead of triggering auth.
- If Bumble is on a CAPTCHA screen, do **not** treat that as a normal logged-in state.
- If Bumble reaches a passkey screen after SMS verification, only **Not Now** may be used automatically; do **not** create or enroll a passkey automatically.
- Do **not** log out unless there is a significant reason.
- Use random 1–4 sec pauses between actions.
- Set location to San Francisco (37.79, -122.42) after session start.

## Local debug / inspection

```bash
python scripts/bumble_client.py state    # returns JSON
python scripts/bumble_client.py debug
python scripts/bumble_client.py matches  # JSON: matches[{name, expired}], expired true/false/null, counts
python scripts/bumble_client.py likes    # JSON: visible likes plus Beeline count/premium signal when available
python scripts/bumble_client.py messages "Kritika"  # returns JSON with author field
python scripts/bumble_client.py send "Kritika" "message text"
python scripts/bumble_client.py photos "Kritika" "/absolute/output/dir"
```

## Match selection policy

- Always switch matches from the left conversation bar.
- Do **not** assume the click worked just because the action returned 200.
- Verify that the active profile / conversation on the right changed to the requested match name.
- If the requested name is wrong or the active profile name does not match exactly, return an error instead of silently using the previously open match.

## Auth flow

Only when on get-started or auth page:

1. Tap "Continue with other methods" — selectors: `div.other-methods-button`, `span.other-methods-button-text`
2. Tap "Use cell phone number" — selectors: `span.action.text-break-words`, `button.primary.button--transparent span.action`
3. Ask the user to provide their phone number, then type that number (national digits; country is chosen in the UI) into the digits field and pass the same number on the CLI
4. Tap "Continue"
5. Stop on the SMS confirmation page and wait for a code

```bash
python scripts/bumble_client.py auth "<user_phone_number>"
```

## SMS code step

Only when Bumble is already on the confirm-phone page:

```bash
python scripts/bumble_client.py sms_code 233596
```

Current behavior:

- First tries the working fallback: type the full 6-digit code into the first OTP box.
- Prefer focusing the first OTP box once and typing the whole code without selecting each field individually.
- Falls back to per-digit entry if needed.
- Only reports success if Bumble actually leaves the confirm-phone page.
- If the SMS code is accepted but Bumble moves to a CAPTCHA challenge, return:
  - `state: "captcha_challenge"`
  - `sms_code_accepted: true`
  - an error saying manual CAPTCHA completion is required
- If the SMS code is accepted and Bumble moves to `/registration/passkey`, the client taps **Not Now** (skip for now). Do **not** tap **Create a passkey** or complete passkey enrollment automatically. `open_connections` also attempts the same skip if a stored session resumes on that screen.

## Messages

```bash
python scripts/bumble_client.py messages "Kritika"
```

- Returns JSON.
- Includes `author` for each message (`me` / `them` when HTML parsing succeeds).
- Should not trigger auth automatically.

## Send message

```bash
python scripts/bumble_client.py send "Kritika" "message text"
```

- Opens the requested match.
- Verifies Bumble accepted the draft before sending.
- Sends using the actual code path in `bumble_client.py`:
  - resolve send button bounds
  - tap/click by coordinates at the button center
  - fall back to accessibility-ref click only if needed
- Verifies the sent message appears in the visible thread before reporting success.

## Profile photos

```bash
python scripts/bumble_client.py photos "Anya" "/absolute/output/dir"
```

- Opens the requested match and verifies the right-side active profile name matches exactly.
- Taps the right-side profile photo area.
- Performs a best-effort photo advance/tap loop.
- Extracts unique Bumble CDN photo URLs from the active profile HTML.
- Downloads the photos into the provided directory.
- Resets back to the normal match thread view after export.
