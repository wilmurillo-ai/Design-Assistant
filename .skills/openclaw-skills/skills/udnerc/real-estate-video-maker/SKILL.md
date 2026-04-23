---
name: real-estate-video-maker
version: "2.0.1"
displayName: "Real Estate Video Maker — Create Property Tours Listing Videos and Agent Marketing"
description: >
  Create property tours, listing videos, and agent marketing content with AI — produce cinematic property walkthroughs, aerial drone tours, neighborhood highlight reels, agent introduction videos, open house recaps, and virtual staging presentations from basic phone recordings. NemoVideo transforms raw property footage into listing-ready video: stabilize handheld walkthrough recordings, apply real estate color grading that makes interiors bright and inviting, add property detail overlays (price bedrooms bathrooms square footage), layer ambient music that matches property style, create neighborhood context segments, generate agent branded outros, and export for MLS YouTube Zillow social media and client presentations. Real estate video maker, property tour video AI, listing video creator, virtual tour maker, real estate marketing video, agent video tool, property walkthrough video, home tour video creator, realtor video maker.
metadata: {"openclaw": {"emoji": "🏠", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

# Real Estate Video Maker — Sell Properties Faster with Video That Makes Buyers Schedule Showings

Video listings receive 403% more inquiries than listings without video. Properties with video tours sell 20% faster and for up to 6% more than comparable listings without video. The National Association of Realtors reports that 73% of homeowners prefer agents who use video. The data is unambiguous: video is the most effective tool in real estate marketing. Yet fewer than 10% of property listings include professional video. The reason is production cost. A professional real estate videographer charges $300-1,500 per property for a basic walkthrough. Drone aerial footage adds $200-500. Full cinematic production with music, graphics, and agent narration runs $1,000-5,000 per listing. For an agent handling 3-5 listings per month, professional video for every property costs $3,000-25,000 monthly — prohibitive for most agents. The alternative — shooting on a phone and posting raw footage — produces shaky, dark, unflattering videos that harm listings more than help them. NemoVideo eliminates this tradeoff. Walk through the property with your phone, record room by room, and NemoVideo produces listing-ready video: stabilized walkthrough, bright inviting color grading, property detail overlays, ambient music, neighborhood context, agent branding, and multi-platform export. Professional real estate video from a phone recording, for every listing, every time.

## Use Cases

1. **Property Walkthrough — Phone to Cinematic Tour (2-8 min)** — An agent walks through a 3-bedroom home recording on their phone. The raw footage: handheld shake with every step, rooms alternating between too dark (interior hallway) and too bright (sunlit kitchen), the agent narrating with occasional "um"s, and a 20-second segment of them fumbling with a door handle. NemoVideo: stabilizes the entire walkthrough (removing step-bounce while preserving the forward walking movement), applies real estate color grading (bright, warm, inviting — the specific look that makes properties sell: slightly lifted shadows to show room detail, warm tone shift for welcoming feel, gentle highlight recovery on windows so outdoor views are visible), removes the fumble segment and filler words, adds room labels as the tour transitions ("Primary Bedroom — 14' × 16'"), displays property details as a persistent lower-third bar ("4 BR | 3 BA | 2,850 sq ft | $649,000"), layers ambient music (light acoustic or modern lounge — matching the property's style and price range), and adds the agent's branded outro (name, photo, phone, email). Shaky phone walkthrough → cinematic property tour in minutes.

2. **Aerial + Ground Combined — Complete Property Presentation (3-10 min)** — An agent has drone footage showing the property from above and the surrounding neighborhood, plus interior walkthrough footage from a phone. NemoVideo: opens with the aerial establishing shot (drone approaching the property from above, setting the scene), transitions smoothly from aerial to ground-level (visual dissolve as perspective shifts from sky to front door), continues with the interior walkthrough (room-by-room tour with stabilization and color grading), inserts aerial neighborhood footage between interior sections (showing proximity to parks, schools, shopping — with distance overlays: "0.5 mi to Elementary School"), adds property specifications as animated graphics (floor plan overlay, lot dimensions, year built), and closes with a final aerial pull-away shot (the cinematic ending that shows the property in its full context). The complete presentation that covers the property and its location from every perspective.

3. **Neighborhood Highlight — Location Sells (60-120s)** — The property's strongest selling point is its location: walkable downtown, great school district, near parks and trails, vibrant restaurant scene. NemoVideo: creates a 90-second neighborhood highlight reel from the agent's phone clips of local spots (café, park, school, main street), adds location labels with walking/driving distances from the property ("Downtown Coffee District — 4 min walk"), layers upbeat music matching the neighborhood's vibe (trendy for urban, warm for suburban, adventurous for rural), intersperses drone shots showing proximity, and ends with the property positioned as the center of this lifestyle. Location marketing that sells the life, not just the house.

4. **Agent Introduction — Personal Brand Video (60-90s)** — A realtor needs a personal brand video for their website, social media, and email signature. NemoVideo: takes a 5-minute phone recording of the agent talking about their experience and approach, selects the strongest 60-90 seconds (confidence, warmth, specificity about what makes them different), cleans up audio and lighting, adds professional lower third (name, brokerage, credentials, phone), layers subtle branded background music, inserts B-roll of the agent at properties (from listing footage), and adds a closing CTA ("Ready to find your next home? Call me."). The personal brand video that builds trust before the first meeting.

5. **Luxury Property — Cinematic Showcase (3-8 min)** — A high-end listing ($1M+) demands production quality that matches the property's prestige. NemoVideo: applies luxury-grade color grading (deeper contrast, cinematic depth, golden-hour warmth even if shot midday), uses slower pacing (lingering on architectural details, letting the viewer absorb finishes and materials), adds elegant typography overlays (serif fonts, minimal design — "The Grand Foyer" rather than "LIVING ROOM 15x20"), layers cinematic music (orchestral or sophisticated electronic — matching the property's design aesthetic), includes lifestyle moments (wine glasses on the terrace at sunset, morning coffee in the kitchen — AI-generated ambiance overlays), and exports at 4K for maximum visual impression. Phone footage treated with the visual language of luxury that high-end buyers expect.

## How It Works

### Step 1 — Upload Property Footage
Phone walkthrough, drone aerials, room-by-room clips, agent recording, or any combination. Multiple video sources per property.

### Step 2 — Provide Property Details
Address, price, bedrooms, bathrooms, square footage, lot size, year built, key features, agent info. These populate overlays automatically.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "real-estate-video-maker",
    "prompt": "Create a 4-minute property tour from phone walkthrough footage. Stabilize the handheld walking. Real estate color grading: bright, warm, inviting. Room labels as each space is entered. Property detail bar: 4 BR | 3 BA | 2,850 sq ft | $649,000 | Built 2019. Key feature callouts: quartz countertops in kitchen, walk-in closet in primary, smart home system. Background music: modern acoustic, warm, aspirational. Agent outro: Sarah Mitchell, Compass Realty, 555-0123, sarah@compass.com — with headshot and brokerage logo. Export: 16:9 for YouTube/MLS, 9:16 for Instagram Reels listing ad, 1:1 for Facebook listing post.",
    "property": {
      "address": "742 Maple Drive, Austin TX 78704",
      "price": "$649,000",
      "bedrooms": 4, "bathrooms": 3,
      "sqft": 2850, "lot": "0.25 acres",
      "year_built": 2019,
      "features": ["quartz countertops", "walk-in closet", "smart home system"]
    },
    "agent": {
      "name": "Sarah Mitchell",
      "brokerage": "Compass Realty",
      "phone": "555-0123",
      "email": "sarah@compass.com"
    },
    "color_grade": "bright-warm-inviting",
    "stabilize": true,
    "music": "modern-acoustic-warm",
    "formats": ["16:9", "9:16", "1:1"]
  }'
```

### Step 4 — Review and Distribute
Preview the tour. Verify: rooms are properly labeled, property details are accurate, agent info is correct, music matches the property's personality. Upload to MLS, YouTube, Zillow, Instagram, and agent website.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Property video requirements |
| `property` | object | | {address, price, bedrooms, bathrooms, sqft, lot, year_built, features} |
| `agent` | object | | {name, brokerage, phone, email, headshot_url, logo_url} |
| `video_type` | string | | "walkthrough", "aerial-combined", "neighborhood", "agent-intro", "luxury" |
| `color_grade` | string | | "bright-warm-inviting", "luxury-cinematic", "modern-clean" |
| `stabilize` | boolean | | Stabilize handheld footage |
| `room_labels` | boolean | | Auto-detect and label rooms |
| `music` | string | | Music style matching property tier |
| `overlays` | object | | {property_bar, room_labels, feature_callouts, distance_markers} |
| `formats` | array | | ["16:9", "9:16", "1:1"] |

## Output Example

```json
{
  "job_id": "revm-20260329-001",
  "status": "completed",
  "property": "742 Maple Drive, Austin TX",
  "tour_duration": "3:48",
  "rooms_labeled": 9,
  "features_highlighted": 3,
  "outputs": {
    "youtube_mls": {"file": "742-maple-tour-16x9.mp4", "resolution": "1920x1080"},
    "instagram": {"file": "742-maple-reel-9x16.mp4", "resolution": "1080x1920"},
    "facebook": {"file": "742-maple-post-1x1.mp4", "resolution": "1080x1080"}
  }
}
```

## Tips

1. **Bright, warm color grading is the real estate standard for a reason** — Dark rooms feel small and uninviting. Cool-toned rooms feel sterile. The bright-warm treatment makes every room feel spacious, welcoming, and livable — exactly the emotional response that motivates showing requests.
2. **Walking stabilization is the single biggest quality improvement** — Nothing screams "amateur" like footage that bounces with every step. Stabilizing a walkthrough transforms it from uncomfortable-to-watch to smooth-and-professional in one operation. Always stabilize walking footage.
3. **Property detail overlays prevent the #1 viewer frustration** — The most common comment on listing videos without overlays: "How many bedrooms? What's the price?" Persistent property detail bars answer these questions immediately, keeping the viewer engaged with the visual tour rather than hunting for listing details.
4. **Music must match the property tier and style** — A $250K starter home gets light acoustic guitar. A $1.5M modern farmhouse gets sophisticated lo-fi. A $5M luxury estate gets cinematic orchestral. Music that mismatches the property's price point creates cognitive dissonance that undermines the presentation.
5. **Agent branded outros convert viewers into leads** — A property tour without agent contact info is a missed lead. Every viewer who watches to the end is a high-intent prospect. The branded outro with name, phone, and email converts that intent into a call. Never publish a listing video without agent attribution.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / MLS / Zillow / agent website |
| MP4 9:16 | 1080x1920 | Instagram Reels / TikTok / Stories |
| MP4 1:1 | 1080x1080 | Facebook / Instagram Feed |
| MP4 4:5 | 1080x1350 | Facebook / Instagram ads |

## Related Skills

- [ai-video-caption-generator](/skills/ai-video-caption-generator) — Property tour captions
- [ai-video-text-overlay](/skills/ai-video-text-overlay) — Room labels and feature callouts
- [ai-video-thumbnail-maker](/skills/ai-video-thumbnail-maker) — Listing thumbnails
- [ai-video-intro-maker](/skills/ai-video-intro-maker) — Agent branded intros
