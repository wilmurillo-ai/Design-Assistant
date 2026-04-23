---
name: open-house-video-maker
version: "1.0.0"
displayName: "Open House Video Maker — Create Property Preview and Open House Promotion Videos for Real Estate Agents"
description: >
  You have an open house this Sunday. You posted it on the MLS, put a sign in the yard, and shared it once on your Facebook business page. Three people showed up — one was a neighbor, one was a curious couple who already have an accepted offer somewhere else, and one was a serious buyer who found the listing through the sign. The agent on the next street over had fourteen attendees. She posted a 60-second walkthrough video on Thursday — kitchen, primary suite, backyard, natural light through the living room windows — and tagged it with the neighborhood name and school district. People showed up because they had already walked through the house on their phone. Open House Video Maker creates property preview and open house promotion videos for real estate agents, listing agents, buyer's agents, and brokerages: previews the home before the event, builds urgency around the open house date and time, showcases standout features that make buyers want to see it in person, and exports vertical clips for Instagram and TikTok alongside horizontal property tours for your listing page and YouTube channel.
  NemoVideo gives real estate agents a fast path to professional open house content: describe the property highlights, upload your walkthrough footage, and receive polished open house promotion videos ready for social media, your MLS listing, and the neighborhood Facebook groups where serious local buyers are already watching for new inventory.
  Open House Video Maker gives agents a repeatable content system for every listing — pre-open-house teasers, same-day event reminders, post-open-house follow-up content for buyers who couldn't attend, and price reduction announcements that bring back prospects who passed on the original price.
metadata: {"openclaw": {"emoji": "🏡", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Open House Video Maker — More Buyers, More Offers

## Use Cases

1. **Pre-Open-House Teasers** — Post a 30-second walkthrough preview on Thursday and Friday before a Sunday open house. Show the kitchen, the primary suite, the backyard, and one detail buyers won't expect — the footage that fills your sign-in sheet before you've unlocked the door.

2. **Open House Day Reminders** — A same-day short video posted Sunday morning with the address, time, and one compelling interior shot converts the buyer who bookmarked the listing and almost forgot. Open House Video Maker creates urgency-reminder clips with countdown overlays and neighborhood amenity callouts.

3. **Virtual Open House for Remote Buyers** — Out-of-town buyers, relocation candidates, and investors can't always attend in person. A full-property walkthrough video posted publicly turns your open house into a 24-hour online event that captures offers from buyers who never step through the door.

4. **Price Reduction Relaunch** — When a listing price drops, most agents send a form email. Open House Video Maker creates price reduction announcement videos — same property, new urgency, clear value framing — that re-engage every buyer who toured the home and didn't make an offer at the original price.

## How It Works

Upload your walkthrough footage, describe the property highlights and open house details, and Open House Video Maker edits and exports platform-ready videos for every channel in your listing promotion strategy.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "open-house-video-maker", "input": {"footage_urls": ["https://..."], "address": "123 Maple St", "open_house_date": "Sunday April 5 1-4pm", "highlights": ["renovated kitchen", "large backyard"], "platform": "instagram"}}'
```
