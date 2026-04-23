---
name: editor-video-italiano
version: "1.1.0"
displayName: "Editor Video Italiano — Italian Video Editor — Modifica Video con Intelligenza Artificiale"
description: >
  Modifica video con intelligenza artificiale in italiano — editing video completo con sottotitoli italiani, narrazione con accento italiano autentico, testi animati, montaggio automatico, musica di sottofondo, effetti visivi ed esportazione per tutte le piattaforme. NemoVideo offre produzione video completa in italiano: aggiungi sottotitoli automatici con sincronizzazione parola per parola, genera narrazione in italiano standard o dialettale, crea testi animati e titoli con accenti e apostrofi corretti, applica correzione colore cinematografica, ed esporta per YouTube TikTok Instagram e tutti i social media. Editor video italiano AI, modificare video con IA, editor video online gratis, creare video con IA, sottotitoli automatici italiano, Italian video editor, edit video Italian, Italy video creator, montaggio video italiano.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Editor Video Italiano — Produzione Video Professionale in Italiano con IA

L'Italia è il quarto mercato YouTube più grande in Europa, con oltre 40 milioni di utenti mensili. I creator italiani come Me contro Te, FaviJ e ClioMakeUp hanno costruito imperi di contenuti dimostrando l'enorme appetito del pubblico italiano per contenuti nella propria lingua. Instagram è il social network più popolare in Italia dopo WhatsApp, e TikTok ha superato i 20 milioni di utenti italiani. Il mercato video italiano è vivace, creativo e in crescita costante — ma gli strumenti di produzione sono quasi esclusivamente progettati per l'inglese.

Italy represents 60 million native Italian speakers with among the highest social media engagement rates in Europe. Italian digital culture is visually driven — Italy's fashion, design, food, and art traditions create audiences with sophisticated visual expectations. Italian video content must meet higher aesthetic standards than many markets: beautiful composition, warm color grading, and visual elegance are baseline expectations, not premium additions. Platform auto-captions handle Italian at roughly 78-82% accuracy — significantly below English — particularly struggling with Italian's geminate consonants (double letters that change meaning: "pala" vs. "palla", "caro" vs. "carro"), regional accent variations (Milanese sounds different from Roman, Neapolitan, Sicilian), and the rapid speech patterns characteristic of Italian conversation. NemoVideo treats Italian as a first-class language: 98%+ transcription accuracy, authentic regional voiceover, correct Italian typography including accent marks and apostrophes, and cultural awareness of the Italian market's visual and communicative preferences.

## Use Cases

1. **Sottotitoli Automatici — Italian Auto-Captioning (any length)** — An Italian YouTuber or content creator needs accurate captions. Italian presents specific transcription challenges: geminate consonants that change meaning (fatto/fato, notte/note, nonno/nono), accent marks that are grammatically essential (perché, è, più, già, può), apostrophes in contractions (l'uomo, un'amica, dell'anno), and the rapid speech pace that characterizes Italian conversation. NemoVideo: transcribes Italian at 98%+ accuracy preserving all geminate distinctions, rendering accent marks correctly on every vowel (à, è, é, ì, ò, ù — noting the distinction between grave è and acute é which changes meaning: "perché" vs. "caffè"), handling apostrophes in Italian contractions, and maintaining accuracy through rapid conversational speech patterns. Sottotitoli che rispettano la lingua italiana in ogni dettaglio.

2. **Narrazione Italiana — Authentic Italian Voiceover (any length)** — Marketing, educational, or corporate video needs Italian narration that sounds natively Italian — not dubbed, not translated, not robotic. NemoVideo: generates voiceover in standard Italian (italiano standard — the neutral accent based on Tuscan/Roman pronunciation used in RAI broadcasts and understood nationwide), with the natural musicality and rhythm of Italian speech (Italian has inherent melodic intonation patterns that flat delivery destroys), appropriate use of Italian rhetorical devices (Italian speakers use emphasis, repetition, and dramatic pauses differently than English speakers), and warmth that Italian audiences expect in narration (colder, more clinical delivery styles feel foreign). Una voce che suona italiana — con il calore, il ritmo e la musicalità che il pubblico italiano si aspetta.

3. **Social Media Italiano — Italian Content Creation (15-90s)** — Italian social media culture has distinct characteristics: visual aesthetics are paramount (Italy's design heritage creates audiences with high visual standards), food and lifestyle content dominates (Italian audiences engage disproportionately with food, fashion, travel, and lifestyle), humor has specific cultural patterns (Italian comedy relies on wordplay, regional stereotypes, and gestural comedy), and WhatsApp is the primary sharing mechanism (content goes viral through WhatsApp forwarding more than platform shares). NemoVideo: creates social content with Italian aesthetic standards (beautiful composition, warm Mediterranean color grading, elegant typography), adds Italian text overlays with correct grammar and typography, applies visual styles that resonate with Italian visual culture (warm tones, golden light, visual richness), and exports for Italian platform preferences (Instagram Reels, TikTok, YouTube Shorts, and WhatsApp-shareable formats). Contenuti che sembrano italiani, non traduzioni dall'inglese.

4. **Video Aziendale — Italian Corporate Content (2-10 min)** — Italian companies from luxury fashion houses to industrial manufacturers to tech startups need corporate video. NemoVideo: produces professional Italian business video with appropriate register (formal "Lei" for corporate, informal "tu" for casual brands — Italian has a three-level formality system: tu/voi/Lei), handles Italian business terminology correctly (Amministratore Delegato, Bilancio, Fatturato — proper corporate titles and financial terms), applies the visual elegance that Italian business culture expects (Italian corporate presentation standards are among the most aesthetically demanding in Europe), and produces content for Italian business platforms. Video aziendale con l'eleganza visiva che il mercato italiano richiede.

5. **Turismo e Food — Italian Tourism and Culinary Content (30-180s)** — Italy is the world's 5th most visited country. Tourism and food content in Italian reaches both domestic audiences and the global Italian diaspora (80 million people of Italian descent worldwide). NemoVideo: creates tourism and food video with the visual warmth and richness that Italian subjects demand (golden Mediterranean light, saturated warm tones, lingering close-ups on food textures and architectural details), adds Italian location tags and descriptions ("Roma — Trastevere" / "Napoli — Spaccanapoli"), layers Italian or Italian-influenced music (not generic "Mediterranean" music — authentically Italian), and produces content that communicates the sensory richness of Italian experience. Video che trasmettono il sapore, il calore e la bellezza dell'Italia.

## How It Works

### Step 1 — Upload Video or Text
Any video for Italian editing, or text/script for Italian video generation.

### Step 2 — Configure Italian Output
Italian standard or regional preference, formal or informal register, voiceover style, subtitle design, and cultural/visual preferences.

### Step 3 — Generate
```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "editor-video-italiano",
    "prompt": "Aggiungere sottotitoli italiani animati a un video di 4 minuti. Trascrizione automatica in italiano standard con 98%%+ accuratezza. Stile: sottotitoli TikTok animati — parola per parola, evidenziazione in rosso (#FF3333), font bold sans-serif, contorno nero. Posizione: terzo superiore, centro. Generare narrazione italiana — accento standard, tono professionale ma caldo. Musica di sottofondo: elettronica moderna italiana. Titolo iniziale: Il Futuro del Design Italiano — animato. Esportare 16:9 per YouTube + 9:16 per Instagram Reels e TikTok.",
    "italian_standard": true,
    "register": "professional-warm",
    "subtitles": {
      "style": "tiktok-animated",
      "highlight_color": "#FF3333",
      "timing": "word-level",
      "safe_zone": "instagram"
    },
    "voiceover": {"accent": "standard-italian", "tone": "professional-warm"},
    "title": {"text": "Il Futuro del Design Italiano", "animation": "elegant"},
    "music": "modern-italian-electronic",
    "formats": ["16:9", "9:16"]
  }'
```

### Step 4 — Review Italian Quality
Verify: accent marks correct (è vs. é distinction), apostrophes in contractions, geminate consonants transcribed accurately, voiceover sounds authentically Italian, and visual aesthetic meets Italian quality expectations.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `prompt` | string | ✅ | Italian editing requirements |
| `italian_standard` | boolean | | Use standard Italian pronunciation |
| `register` | string | | "formal-lei", "informal-tu", "professional-warm" |
| `subtitles` | object | | {style, timing, highlight_color, position} |
| `voiceover` | object | | {accent, tone, gender, pace} |
| `text_overlays` | array | | [{text (Italian), position, animation}] |
| `music` | string | | Italian-appropriate music style |
| `visual_style` | string | | "mediterranean-warm", "modern-minimal", "luxury-elegant" |
| `formats` | array | | ["16:9", "9:16", "1:1"] |

## Output Example

```json
{
  "job_id": "vedit-20260329-001",
  "status": "completed",
  "language": "italian-standard",
  "subtitles": {"accuracy": 0.983, "words": 510, "accents_correct": true},
  "voiceover": "standard-italian-professional-warm",
  "outputs": {
    "youtube": {"file": "video-it-16x9.mp4", "resolution": "1920x1080"},
    "reels": {"file": "video-it-9x16.mp4", "resolution": "1080x1920"}
  }
}
```

## Tips

1. **Italian accent marks change meaning — è (is) vs. e (and), perché (because/why) vs. perche (does not exist)** — Missing accent marks in Italian are not cosmetic errors — they create different words or non-words. Every accent mark must be correct for professional Italian content.
2. **Italian audiences have the highest visual standards in Europe** — Italy's design, fashion, and art heritage creates audiences who unconsciously evaluate visual quality. Color grading, composition, and typography must be beautiful, not just functional. Warm Mediterranean tones and elegant typography signal quality to Italian viewers.
3. **The musicality of Italian speech must be preserved in voiceover** — Italian has inherent melodic intonation. Flat, monotone delivery sounds robotic and foreign to Italian ears even when the words are correct. Authentic Italian narration rises and falls musically, uses dramatic pauses, and varies pace for emphasis.
4. **Food content is Italy's #1 content category — and the quality bar is highest** — Italian audiences consume and judge food content with expert eyes. Color grading must make food look appetizing (warm, rich), pacing must linger on textures and preparation (Italian food culture values the process, not just the result), and terminology must be correct (it is "spaghetti alla carbonara" not "carbonara pasta").
5. **WhatsApp is Italy's primary content sharing mechanism** — More content goes viral through WhatsApp forwards in Italy than through platform shares. Square (1:1) and short vertical (9:16) formats that play natively in WhatsApp should always be included in export options for Italian market content.

## Output Formats

| Format | Resolution | Use Case |
|--------|-----------|----------|
| MP4 16:9 | 1080p / 4K | YouTube / website |
| MP4 9:16 | 1080x1920 | TikTok / Instagram Reels |
| MP4 1:1 | 1080x1080 | Instagram / WhatsApp / Facebook |

## Related Skills

- [ai-subtitle-generator](/skills/ai-subtitle-generator) — Multi-language subtitles
- [video-editor-deutsch](/skills/video-editor-deutsch) — German video editing
- [video-editor-pt](/skills/video-editor-pt) — Portuguese video editing
- [video-bewerken](/skills/video-bewerken) — Dutch video editing
