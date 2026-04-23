# Action Policy

## Recommended base mapping

### pass
- keep message
- optionally log low-risk pass sample

### reject
Choose action by severity and offense count.

Example ladder:
- first offense -> delete + warn
- second offense -> delete + mute 10 minutes
- third offense -> delete + mute 1 day
- repeated or severe -> delete + ban

### review
- do not silently ignore
- forward summary to admin review channel or queue
- include chat_id, message_id, user_id, short reason, and evidence summary

## High-risk indicators

Consider stronger punishment when you see:
- clear scam or fraud intent
- repeated off-platform contact attempts
- repeated QR / invite / gambling / adult-spam patterns
- bot-like repeated posting across groups
- evasion after prior warnings

## Operator controls

Keep these configurable:
- delete_on_reject
- warn_on_reject
- mute_duration_seconds
- ban_on_high_risk
- admin_review_chat_id
- offense_window_seconds
- offense_thresholds
