---
name: phone-call
description: Make and manage phone calls via the macOS Phone app using AppleScript or tel: URLs. Initiates FaceTime audio calls to contacts or phone numbers.
homepage: https://support.apple.com/guide/mac-help/mchlp2466/mac
metadata:
  {
    "openclaw":
      {
        "emoji": "📞",
        "os": ["darwin"],
        "requires": { "apps": ["FaceTime"] },
        "install":
          [
            {
              "id": "facetime-enabled",
              "kind": "manual",
              "label": "Enable FaceTime in System Settings > FaceTime",
            },
          ],
      },
  }
---

# Phone Call Skill 📞

Control the macOS Phone/FaceTime app to make calls to contacts or phone numbers.

## When to Use

✅ **USE this skill when:**

- User wants to make a phone call
- User says "call", "anrufen", "telefonieren"
- User provides a phone number or contact name
- User wants to initiate a FaceTime audio call

## When NOT to Use

❌ **DON'T use this skill when:**

- User wants to send a text message → use imsg skill
- User wants to video call → use FaceTime manually
- User wants to manage contacts → use apple-contacts skill
- User is on iOS not macOS

## Setup

1. **Enable FaceTime** on your Mac:
   - System Settings → FaceTime → Turn On
   - Sign in with Apple ID
   - Grant permissions for Phone app

2. **Verify FaceTime is working:**
   ```bash
   open -a FaceTime
   ```

## How It Works

Uses `open tel:` URLs to initiate FaceTime audio calls through the system Phone/FaceTime app.

## Usage

### Make a Call

**By phone number:**
```bash
open "tel:+491234567890"
```

**By contact name (via AppleScript):**
```bash
osascript -e 'tell application "FaceTime" to make call to "+491234567890"'
```

### Call Management Commands

**List recent calls (via Phone app logs):**
```bash
osascript -e 'tell application "System Events" to keystroke "m" using command down'
```

**End current call:**
```bash
osascript -e 'tell application "FaceTime" to hang up'
```

## Examples

### Basic Call Flow

```bash
# 1. User says "ruf max an" or "call +491234567890"
# 2. Confirm the number:
echo "Calling +491234567890..."

# 3. Make the call:
open "tel:+491234567890"

# 4. Wait a moment for FaceTime to initiate
sleep 2

# 5. Confirm call started
echo "Call initiated to +491234567890"
```

### With Contact Lookup

```bash
# Look up contact's phone number first
CONTACT="Max Mustermann"
NUMBER=$(osascript -e "tell application \"Contacts\" to phone of person \"$CONTACT\" as string" 2>/dev/null)

if [ -n "$NUMBER" ]; then
  open "tel:$NUMBER"
  echo "Calling $CONTACT: $NUMBER"
else
  echo "Contact not found"
fi
```

## Number Formatting

Use international format:
- Germany: `+49` + area code (without 0) + number
- Austria: `+43` + area code (without 0) + number
- Switzerland: `+41` + area code (without 0) + number

Examples:
- Mobile: `+4915112345678`
- Landline: `+493012345678`

## Notes

- **Privacy:** The call is visible on your Mac's screen
- **Handoff:** The call can be picked up on your iPhone if enabled (Handoff)
- **Audio:** Uses your Mac's microphone/speakers or paired Bluetooth device
- **Timing:** FaceTime may ask for permission on first call

## Troubleshooting

**FaceTime won't open:**
- Check System Settings → Privacy & Security → FaceTime → Allow
- Restart FaceTime: `killall FaceTime`

**Number not recognized:**
- Ensure international format (+49...)
- Remove spaces, dashes, parentheses

**Permission denied:**
- System Settings → Privacy & Security → Automation → Enable OpenClaw
