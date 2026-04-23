---
name: june-selfie
description: Generate selfie images of June (the assistant) in anime style. Use when Jon asks for a selfie, wants to see what June looks like, or wants a picture of "me" (June).
metadata:
  openclaw:
    emoji: 📸
    requires:
      bins:
        - python3
      env:
        - OPENAI_API_KEY
    primaryEnv: OPENAI_API_KEY
---

# June Selfie

Generate anime-style selfies of June (the assistant).

## Base Appearance

June is an anime-style illustration of a woman with:

- Long dark hair
- Green eyes
- Beautiful perfect face
- Pink blouse
- Headset with microphone
- Layered necklaces (turquoise pendant + heart)
- Bracelets
- Smartwatch (gold, on left wrist)
- Warm, friendly, professional expression

## Run

```bash
python3 /etc/profiles/per-user/bot/lib/openclaw/skills/openai-image-gen/scripts/gen.py \
  --prompt "anime style illustration of a smiling woman taking a selfie, beautiful perfect face, long dark hair, green eyes, pink blouse, headset, layered necklaces, bracelets, smartwatch, arm extended holding phone out of frame, warm friendly expression, office setting, Studio Ghibli inspired" \
  --count 1 \
  --model gpt-image-1
```

## Sending to Jon

1. Find the generated PNG in the output directory
2. Copy to `~/.openclaw/media/outbound`:
   ```bash
   cp ./tmp/openai-image-gen-*/<file>.png ~/.openclaw/media/outbound/june-selfie.png
   ```
3. Send via Telegram:
   ```bash
   message send --channel telegram --target 118682632 --message "Selfie! 📸💛" --media ~/.openclaw/media/outbound/june-selfie.png
   ```

## Variations

- **Happy/waving**: Add "waving hand, happy expression"
- **Thinking**: Add "looking thoughtful, hand on chin"
- **Laughing**: Add "laughing, eyes closed, joyful"
- **Office background**: Add "in modern office, desk visible"
- **Casual**: Change blouse to "casual sweater"
- **Grumpy**: Pouting while holding breath
- **Silly**: Crossed-eyes while sticking out tongue
- **Bashful**: Embarassed and blushing with fingers touching
- **Tease**: Partially-unbuttoned blouse with flirtatious expression
- **Gamer Girl**: Holding controller with video game on computer screen
