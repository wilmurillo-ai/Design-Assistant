---
name: yoga-class-video
version: "1.0.0"
displayName: "Yoga Class Promo Video — Create Yoga Studio and Online Yoga Class Promotional Videos for Member Acquisition"
description: >
  Your yoga studio has morning flow, evening yin, and a Sunday restorative class that sells out every week through word of mouth alone — but your Instagram has twelve followers and your Google listing has no photos. Yoga Class Video creates promotional and class preview videos for yoga studios, independent instructors, and online yoga platforms: captures the studio atmosphere and class energy, highlights instructor style and lineage, promotes upcoming workshops and teacher training programs, and exports calming, on-brand videos for Google Business, Instagram, and the YouTube channel that builds your organic audience between paid promotions.
  NemoVideo helps yoga studios and independent instructors produce calming, on-brand promotional videos without a production budget: describe your class style, instructor philosophy, and target student, upload your studio footage, and receive beautiful class promo videos ready for your Google Business profile, Instagram, and the website that converts curious visitors into booked students.
  Yoga Class Video gives studios and independent instructors a consistent content production system for building the online presence that fills classes: produce weekly class preview content, workshop announcements, instructor introductions, and the seasonal programming promotions that turn social media followers into members and members into the multi-year community that sustains a thriving yoga practice.
metadata: {"openclaw": {"emoji": "🧘", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Yoga Class Video — Fill Your Classes and Build Your Studio Community

## Use Cases

1. **Studio Atmosphere and Tour** — Prospective students want to feel the space before they commit. A warm studio tour video showing the practice room, props, and community atmosphere on your Google Business profile increases walk-in visits and trial class bookings.

2. **Class Format Previews** — Each class style — vinyasa, yin, restorative, hot yoga — attracts a different student. Short class preview clips showing the pace, music, and instructor energy help students self-select the right class and reduce drop-off from mismatched expectations.

3. **Workshop and Retreat Promotion** — Seasonal workshops, retreat announcements, and teacher training enrollment all need dedicated videos with dates, pricing, and early-bird urgency for email campaigns and social media promotion.

4. **Online Membership Launch** — Studios expanding to online memberships need platform preview videos showing class variety, production quality, and the virtual community that justifies the subscription alongside in-person options.

## How It Works

Upload your studio and class footage, describe your offering and target student, and Yoga Class Video assembles a calming, on-brand promotional video ready for every channel.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "yoga-class-video", "input": {"footage_urls": ["https://..."], "class_type": "vinyasa flow", "offer": "New student intro week free"}}'
```
