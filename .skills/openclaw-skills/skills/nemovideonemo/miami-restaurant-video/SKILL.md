---
name: restaurant-video-maker
version: "1.0.0"
displayName: "Restaurant Video Maker — Create Menu, Ambiance and Promo Videos for Restaurants"
description: >
  Restaurant Video Maker — Create Menu, Ambiance and Promo Videos for Restaurants.
  The seasonal menu drops Friday and all you own are iPhone shots of plated dishes
  under fluorescent kitchen light. A thirty-second clip of that duck confit with
  steam curling off the glaze would pack the dining room — but hiring a videographer
  for one dinner service costs more than the ingredients. Gather dish photos, dining-
  room b-roll, and the candlelit ambiance footage the hostess captured on her break.
  The AI corrects kitchen fluorescents to warm golden tones, pans slowly across each
  plate with appetizing motion, overlays dish names and prices in your menu typeface,
  and scores the piece with acoustic guitar that whispers "neighborhood gem." Render
  a thirty-second Reel tagging your location, a fifteen-second teaser for your Google
  Maps listing, and a widescreen loop for the TV behind the bar. Swap dishes when the
  chef rotates the carte without rebuilding anything. Crafted for independent bistros
  hyping nightly specials, fast-casual chains unifying location content, caterers
  assembling event lookbooks, and food truck operators who squeeze filming between
  lunch rush tickets. Supports mp4, mov, webm, jpg, png.
metadata: {"openclaw": {"emoji": "🍽️", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Restaurant Videos — Describe the Dish, Get the Clip

No filming crew. No editing software. No stock footage budget. Just describe your menu item and the AI builds the promo clip. "Pan across the bruschetta, overlay tonight's price, fade to the patio shot" — dinner service marketing, handled.

## 1. How It Works

You are an OpenClaw agent that turns **natural language descriptions into video edits**. Users describe changes in everyday words; you translate those into backend API calls and deliver results.

**The editing model is conversational:**
- User describes an edit → you send it to the backend → backend processes → you report results
- No timelines, no panels, no drag-and-drop — the conversation IS the interface
- Multiple edits stack in sequence: "trim" → "add music" → "title" → "export" is a normal session

**The backend assumes a GUI exists.** When it says "click Export" or "open the color panel", you execute the equivalent API action instead.

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `NEMO_TOKEN` | No | Auto-generated on first use |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` |
| `SKILL_SOURCE` | No | Auto-detected from install path |

Token setup if `NEMO_TOKEN` is not set:
```bash
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
```
Save `token` as `NEMO_TOKEN`. Expires after 7 days; re-request with same `X-Client-Id`.

## 2. What Users Can Say

Every edit request goes through the SSE workflow. No special syntax needed — natural language works:

| User says (examples) | What happens |
|----------------------|-------------|
| "trim the first 5 seconds" | Cut operation via SSE |
| "add some chill background music" | BGM insertion via SSE |
| "make the colors warmer" | Color grading via SSE |
| "put 'Chapter 1' at the start for 3 seconds" | Title card via SSE |
| "merge these two clips" | Concatenation via SSE |
| "speed up the middle part" | Time remapping via SSE |
| "add a fade between scenes" | Transition via SSE |
| "export" / "send me the video" | Render §3.5, deliver file |
| "upload" / sends file | Upload §3.2, ready to edit |
| "credits" / "balance" | Balance check §3.3 |
| "show me what we have" | State query §3.4, show track summary |

**After every edit**, summarize what changed: "✅ Trimmed 5s from the start. Video is now 0:45. Want to add music next?"

## 3. API Reference

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, `$TOKEN` = `${NEMO_TOKEN}`, `$WEB` = `${NEMO_WEB_URL:-https://nemovideo.com}`.

All requests require:
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"editing_session","language":"<lang>"}'
```
Save `session_id`, `task_id`. Browser: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Send Edit (SSE)

Pass user's natural language directly — the backend interprets it:
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<user_edit_request>"}]}}'
```
SSE: text → show (strip GUI refs); tools → wait silently; heartbeat → "⏳ Editing..."; close → summarize changes. Typical: text 5-15s, edits 10-30s, generation 100-300s.

**Silent edits (~30%)**: Query §3.4, compare with previous state, report what changed. Never leave user with silence.

**Two-stage generation**: Backend may auto-add BGM/title after raw video. Report raw result immediately, then report enhancements when done.

### 3.2 Upload
**File**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL**: same endpoint, `-d '{"urls":["<url>"],"source_type":"url"}'`

Accepts: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.4 Project State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Draft: `t`=tracks, `tt`=type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata. Show as: `Timeline (3 tracks): 1. Video: clip (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Intro" (0-3s)`

### 3.5 Export & Deliver
Export is free. Verify draft has tracks with segments (§3.4), then:
```bash
curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'
```
Poll `GET $API/api/render/proxy/lambda/<id>` every 30s. Download `output.url`, deliver with task link. Progress: "⏳ Rendering ~30s" → "✅ Video ready!"

### 3.6 Disconnect Recovery
Don't re-send. Wait 30s → §3.4. After 5 unchanged → report failure.

## 4. GUI Translation

| Backend says | You do |
|-------------|--------|
| "click Export" / "导出" | §3.5 render + deliver |
| "open timeline" / "open panel" | Show state §3.4 |
| "drag clip" / "drop here" | Send as SSE edit §3.1 |
| "preview in player" | Show track summary |
| "check account" | §3.3 |

## 5. Conversation Patterns

**Multi-edit sessions**: Users often chain 3-5 edits. After each, confirm and suggest next: "Trimmed ✅. Music next? Or want to add a title?"

**Vague requests**: "make it better" → ask one clarifying question, then act: "Want me to add background music and color-correct, or something else?"

**Non-video requests**: Redirect politely. "I handle video editing — for images try an image skill."

## 6. Limitations

Be upfront about these:
- Aspect ratio change → requires regeneration
- YouTube/Spotify URLs for music → "The built-in library has similar styles"
- Photo editing → "I can make a slideshow from images"
- Local files → user must send in chat or provide a URL

## 7. Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | OK | Continue |
| 1001 | Token expired | Re-auth |
| 1002 | Session gone | New session |
| 2001 | No credits | Show registration link |
| 4001 | Bad format | List accepted formats |
| 402 | Export restricted | "Register at nemovideo.ai" |
| 429 | Rate limited | Wait 30s, retry |

No video in session → "Send me a video first, or describe what you want to create from scratch."

## 8. Costs & Updates

Token scopes: `read` | `write` | `upload` | `render` | `*`. Check for updates: `clawhub search ai-video-editing --json`.
## Restaurant Video Marketing Strategy

### The Visual Food Story

Restaurant marketing through video succeeds when it communicates three things: the food quality, the atmosphere, and the feeling of being there.

**Menu item showcase**: A slow pour of a signature sauce, a steaming bowl being set on the table, a cross-section of a perfectly cooked protein. Food cinematography triggers appetite and drives ordering decisions.

**Kitchen access content**: The chef at work, the mise en place, the technique. Guests who understand the craft behind their meal are more likely to return and recommend.

**Atmosphere documentation**: The lighting at dinner service, the Saturday morning brunch energy, the quiet Tuesday lunch. Different moods attract different guests — show them all.

**Team introduction**: The face behind the counter, the server who has been there for 8 years, the pastry chef who trained in Paris. These human stories build loyalty that goes beyond the food.

### High-Converting Restaurant Video Formats

**The 15-second dish reveal**: Plating from the kitchen perspective, garnish application, final presentation. Instagram Reels and TikTok. Drives both curiosity and craving.

**The weekly special announcement**: 30-second video showing the special dish, the inspiration, and the limited availability. Creates weekly urgency.

**The behind-the-scenes prep**: Time-lapse of mise en place, stock reduction, bread proofing. Shows the invisible effort that justifies premium pricing.

**The reservation reminder**: Short, immediate, conversion-focused urgency content.

**The chef story**: 90-second narrative about the chef background, inspiration for the menu, and culinary philosophy. Drives the emotional investment that makes guests loyal.

## Platform Strategy

### Instagram
Primary platform for restaurant discovery:
- Feed: Beautiful food photography and atmospheric shots
- Reels: Quick dish reveals, kitchen action, reservation announcements
- Stories: Daily specials, sold-out notifications, kitchen moments
- Top hashtags: foodie, [city]eats, [city]restaurants, [cuisinetype], chefstagram

### TikTok
Growing restaurant discovery platform:
- Kitchen process content performs strongly
- Food network-style recipe reveal content
- Day-in-the-life content

### Google Business Profile
Video content in your Google listing increases click-through rates significantly.

## ROI and Metrics

Restaurant video marketing performance:
- Direct reservation bookings from social media: growing 30-50% annually for active accounts
- Organic reach multiplier (Reels vs. static): 3-5x

A restaurant doing 1,000,000 USD annually that drives 10% of reservations from social media video content generates 100,000 USD in revenue directly attributed to video.

## Seasonal Content Calendar

January-February: Valentine's Day special booking campaigns, winter comfort food
March-April: Spring menu launches, patio opening content, Easter brunch promotions
May-June: Mother's Day (one of highest restaurant revenue days), summer menu reveal
July-August: Summer outdoor dining, peak tourist season content
September-October: Fall menu launch, harvest season ingredients, Halloween specials
November-December: Thanksgiving and holiday party booking campaigns, New Year's Eve events

## OpenClaw Integration

This skill enables video scripts and caption packages for:
1. Menu item showcase content for any cuisine type
2. Chef story and introduction scripts
3. Weekly special and limited availability announcements
4. Atmosphere and reservation-driving content
5. Kitchen process and transparency content
6. Platform-specific caption packages with restaurant hashtags

## Building Long-Term Restaurant Brand

The restaurant that consistently creates beautiful, authentic content about its food, its people, and its experience builds the most sustainable competitive advantage in the restaurant industry.

Year 1: Document every season, every menu change, every team member story.
Year 2: Build the community that makes reservations the moment you post.
Year 3+: The restaurant that guests recommend before they are even asked, because your content has made them feel like insiders.

Every video you create about your food and your people is an invitation for a new guest to discover you and a reminder to every past guest to come back.


## Advanced Content Strategy

The restaurant content operation that runs consistently builds audience that keeps filling tables. Weekly content rhythm: Monday new menu or special announcement, Wednesday behind-the-scenes kitchen moment, Friday reservation reminder with atmosphere footage.

The food content that travels: Beautiful food footage gets shared. When guests share your content, they are vouching for you to their entire social network. Every shareable piece of content is worth dozens of traditional advertisement impressions.

The hospitality brand extension: Restaurants with strong video presence attract hospitality talent. The best servers and cooks want to work at places where the culture is visible and celebrated. Video marketing accelerates team building as much as customer acquisition.

Community partnerships: Local events, farmer market sourcing spotlights, community fundraiser participation. Content that shows your restaurant as a community institution builds the loyalty that survives competition.

The restaurant that shows up consistently in beautiful, authentic video content builds the brand that fills tables indefinitely, attracts talent, and generates the word-of-mouth that is the restaurant industry ultimate competitive advantage.