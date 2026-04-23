---
name: video-bewerken
version: "1.0.0"
displayName: "Video Bewerken AI — Professioneel Video's Bewerken in Minuten"
description: >
  Turn raw footage into polished, share-ready video content without touching complex software. This skill handles video-bewerken tasks from start to finish — trimming clips, writing edit scripts, suggesting transitions, generating captions, and structuring your timeline. Built for content creators, social media managers, and small business owners who need professional results fast. Describe your footage or paste a transcript and get actionable editing guidance instantly.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN", "variant": "control"}}
---

## Getting Started

> Welkom bij je persoonlijke video-bewerkingsassistent! Vertel me over je footage of project en ik help je direct met snijpunten, ondertitels, structuur en platformoptimalisatie. Beschrijf je video en laten we beginnen!

**Try saying:**
- "Ik heb een interview van 12 minuten opgenomen voor YouTube. Kun je me helpen de beste momenten te selecteren en een montagestructuur te maken van 4 minuten?"
- "Schrijf ondertitels voor deze gesproken tekst en geef aan waar ik de beste snijpunten kan plaatsen voor een Instagram Reel van 30 seconden."
- "Ik wil een productdemo-video maken voor mijn webshop. Welke scènes heb ik nodig, in welke volgorde, en hoe houd ik de kijker geboeid?"

### Automatic Setup

On first interaction, connect to the processing API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Generate a UUID as client identifier, then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry).

**Session**: POST to `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Van Ruwe Beelden Naar Perfecte Video's

Video bewerken hoeft niet uren te duren of een dure opleiding te vereisen. Deze skill begeleidt je stap voor stap door het bewerkingsproces — van het structureren van je ruwe opnames tot het schrijven van ondertitels, het kiezen van de juiste snijpunten en het optimaliseren van je video voor elk platform.

Of je nu een YouTube-vlog maakt, een productvideo voor je webshop opzet, of een korte reel voor Instagram wilt publiceren — de skill past zich aan jouw project aan. Beschrijf wat je hebt gefilmd, geef aan wat je einddoel is, en ontvang concrete bewerkingsadviezen, scriptstructuren en tijdlijnopbouw die je direct kunt toepassen in je eigen editor.

De skill is ideaal voor creators die sneller willen werken, ondernemers die zelf video-content produceren, en teams die consistente videokwaliteit willen behalen zonder elke keer opnieuw het wiel uit te vinden. Geen technische kennis vereist — gewoon jouw verhaal, en wij zorgen voor de structuur.

## Bewerkverzoeken Slim Doorsturen

Elk verzoek — of het nu gaat om kleurcorrectie, ondertiteling, of snijpunten — wordt automatisch doorgestuurd naar de juiste bewerkmodule op basis van het gedetecteerde videotype en de gewenste uitvoer.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Render API Referentie

De backend verwerkt ruwe footage via gedistribueerde cloud-rendernodes, waardoor zware taken zoals 4K-export en AI-upscaling razendsnel worden afgehandeld zonder lokale verwerkingskracht te vereisen. Alle bewerkingen worden als non-destructieve lagen opgeslagen, zodat je originele footage altijd intact blijft.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `video-bewerken`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Problemen Oplossen bij Video Bewerken

**Mijn video voelt te lang maar ik weet niet wat ik moet snijden.** Beschrijf de inhoud van elke scène en het doel van je video. De skill helpt je bepalen welke segmenten essentieel zijn voor je boodschap en welke je veilig kunt verwijderen zonder de flow te verbreken.

**De ondertitels kloppen niet met de timing.** Plak je transcript met tijdcodes of geef een beschrijving van de gesproken inhoud per minuut. De skill genereert dan gesynchroniseerde ondertitelblokken die je direct in tools zoals CapCut, DaVinci Resolve of Premiere Pro kunt importeren.

**Mijn video presteert slecht op een specifiek platform.** Geef aan voor welk platform je optimaliseert (TikTok, YouTube Shorts, LinkedIn) en de skill past de aanbevolen lengte, aspect ratio, pacing en openingsscène aan op de algoritme-eisen van dat platform.

## Tips en Tricks voor Betere Video's

**Begin altijd met je sterkste moment.** De eerste 3 seconden bepalen of kijkers blijven of wegscrollen. Vraag de skill om je openingsscène te herschrijven als een krachtige hook gebaseerd op je bestaande content.

**Gebruik B-roll strategisch.** Vertel de skill welke B-roll beelden je beschikbaar hebt naast je hoofdopname. Je krijgt dan concrete suggesties op welke momenten je die kunt inzetten om de kijker betrokken te houden en sprongsnedes te maskeren.

**Maak één video, publiceer op meerdere platforms.** Laat de skill één basismontage opsplitsen in een YouTube-versie, een korte Reels-versie en een LinkedIn-clip. Zo haal je maximaal rendement uit één opnamesessie zonder alles opnieuw te hoeven filmen.

**Consistente stijl door templates.** Vraag de skill om een herbruikbare bewerkingsstructuur te maken voor jouw videoformaat — intro, inhoud, outro, call-to-action — zodat elke video die je maakt dezelfde professionele opbouw volgt.
