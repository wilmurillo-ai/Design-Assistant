# Output JSON Schema — v5.3.0

**Internal data structure for Dream Card image rendering.** The user never sees raw JSON. This schema drives the HTML+CSS template that Playwright renders as a PNG image card. The text layer (Layer 1) is formatted directly in the conversation — only the image card (Layer 2) consumes this JSON.

Six permanent perspectives always present. Three guest perspectives selected from a pool of seven based on dream content. After the initial reading, the user may invite additional unheard guests (Phase 4), which produces a supplemental JSON block.

## Full Structure

```json
{
  "dream_summary": "string — One-sentence dream summary (30 chars max)",
  "keywords": ["string — Dream keywords, 3-6 items"],
  "mood": "string — Mood classification, see enum below",
  "color_scheme": "string — Color scheme name, corresponds to mood",
  "visual_elements": ["string — Visual element IDs, max 5, see visual-mapping.md"],
  "guest_selection": ["string — JSON keys of the 3 selected guests, e.g. 'egyptianPriest', 'yorubaBabalawo', 'scandinavianVolva'"],
  "interpretations": {
    "chineseMystic": {
      "icon": "🔮",
      "title": "Chinese Mystic",
      "content": "string — Main interpretation, 100-200 chars",
      "fortune": "string — Fortune verdict: great-fortune / fortune / neutral-good / neutral / neutral-bad / inauspicious / great-misfortune",
      "advice": "string — One-line advice in do/don't format"
    },
    "greekOracle": {
      "icon": "🏛️",
      "title": "Greek Oracle",
      "content": "string — Myth/oracle-based interpretation, 100-200 chars",
      "lesson": "string — One-line moral lesson",
      "advice": "string — One specific action suggestion"
    },
    "slavicVedunya": {
      "icon": "🌲",
      "title": "Slavic Vedunya",
      "content": "string — Slavic folk interpretation, 100-200 chars",
      "omen": "string — Omen classification: yav-omen / nav-omen / prav-omen",
      "advice": "string — One folk wisdom suggestion"
    },
    "europeanProphet": {
      "icon": "📖",
      "title": "European Prophet",
      "content": "string — European prophetic interpretation, 100-200 chars",
      "prophecy": "string — One-line prophecy (Nostradamus style)",
      "advice": "string — One specific suggestion"
    },
    "northernShaman": {
      "icon": "❄️",
      "title": "Northern Shaman",
      "content": "string — Shamanic interpretation, 100-200 chars",
      "journey": "string — Spirit journey description, one line",
      "advice": "string — One transformation suggestion"
    },
    "indianBrahman": {
      "icon": "🕉️",
      "title": "Indian Brahman",
      "content": "string — Vedic Swapna Shastra interpretation, 100-200 chars",
      "dreamType": "string — Swapna Shastra type: drishta / shruta / anubhuta / prarthita / kalpita / bhavika / doshaja",
      "advice": "string — One dharma-based suggestion or remedy"
    },
    "GUEST_1_KEY": {
      "icon": "string — Guest-specific icon",
      "title": "string — Guest name in user's language",
      "content": "string — Guest interpretation, 100-200 chars",
      "verdict": "string — Guest-specific verdict field (see guest schemas below)",
      "advice": "string — One tradition-specific suggestion"
    },
    "GUEST_2_KEY": { "..." },
    "GUEST_3_KEY": { "..." }
  },
  "overall_advice": "string — Combined advice, 1-2 sentences, neutral tone",
  "shareable_text": "string — Shareable text with emoji, suitable for social media, 60 chars max"
}
```

The `guest_selection` array contains exactly 3 JSON keys from the guest pool. The `interpretations` object always contains 6 permanent keys + 3 guest keys = 9 total.

## Guest Schema Definitions

### Egyptian Priest (egyptianPriest)

```json
{
  "icon": "𓂀",
  "title": "Egyptian Priest",
  "content": "string — Pharaonic temple interpretation, 100-200 chars",
  "verdict": "string — Divine verdict: blessed-of-netjer / under-maat / opposite-meaning / under-chaos / warned-by-duat",
  "advice": "string — One ritual or action suggestion"
}
```

### Japanese Miko (japaneseMiko)

```json
{
  "icon": "⛩️",
  "title": "Japanese Miko",
  "content": "string — Shinto/Onmyodo interpretation, 100-200 chars",
  "dreamClass": "string — Onmyodo classification: rei-mu / shin-mu / aku-mu",
  "advice": "string — One shrine practice or purification suggestion"
}
```

### Mesoamerican Daykeeper (mesoamericanDaykeeper)

```json
{
  "icon": "mayan",
  "title": "Mesoamerican Daykeeper",
  "content": "string — Tonalpohualli/Xibalba interpretation, 100-200 chars",
  "daySign": "string — Associated Tonalpohualli day-sign (one of 20)",
  "advice": "string — One ritual acknowledgment suggestion"
}
```

### Polynesian Navigator (polynesianNavigator)

```json
{
  "icon": "🌊",
  "title": "Polynesian Navigator",
  "content": "string — Oceanic wayfinding interpretation, 100-200 chars",
  "voyage": "string — Dream-voyage classification: crossing / destination / aumakua-visit / po-journey",
  "advice": "string — One navigation-based suggestion"
}
```

### Yoruba Babalawo (yorubaBabalawo)

```json
{
  "icon": "🔮",
  "title": "Yoruba Babalawo",
  "content": "string — Ifá/Orisha interpretation, 100-200 chars",
  "dreamType": "string — Yoruba classification: aláálà / aláíbàje / asírí / ìríntì",
  "advice": "string — One ebo or ori-alignment suggestion"
}
```

### Arabian Sufist (arabianSufist)

```json
{
  "icon": "🌙",
  "title": "Arabian Sufist",
  "content": "string — Ibn Sirin/Sufi interpretation, 100-200 chars",
  "dreamType": "string — Islamic classification: ru-ya / hulm / nafsaniyya",
  "advice": "string — One spiritual counsel suggestion"
}
```

### Scandinavian Volva (scandinavianVolva)

```json
{
  "icon": "🪵",
  "title": "Scandinavian Volva",
  "content": "string — Norse seidr/prophetic interpretation, 100-200 chars",
  "wyrd": "string — Wyrd-thread classification: fate-bound / norn-woven / fylgja-warning / dis-counsel",
  "advice": "string — One wyrd-meeting suggestion"
}
```

## Mood Enum Values

| Value | Meaning |
|-------|---------|
| anxious | Anxiety, fear, tension |
| peaceful | Peace, beauty, comfort |
| sad | Sadness, loss, regret |
| surreal | Fantasy, absurdity, surrealism |
| exciting | Excitement, thrill, adventure |
| nostalgic | Nostalgia, warmth, longing |
| mystical | Mystery, spirituality, transcendence |

## Color Scheme and Mood Correspondence

The `color_scheme` value matches the `mood` value. Frontend looks up colors from the mood-to-color table in `visual-mapping.md`.

## Fortune Verdict Values (Chinese Mystic)

| JSON value | Meaning |
|------------|---------|
| great-fortune | Great fortune |
| fortune | Fortune |
| neutral-good | Neutral leaning good |
| neutral | Neutral |
| neutral-bad | Neutral leaning bad |
| inauspicious | Inauspicious |
| great-misfortune | Great misfortune |

## Omen Values (Slavic Vedunya)

| JSON value | Meaning |
|------------|---------|
| yav-omen | Sign from the material world (Yav) |
| nav-omen | Sign from the spirit world (Nav) |
| prav-omen | Sign from the divine order (Prav) |

## Divine Verdict Values (Egyptian Priest)

| JSON value | Meaning |
|------------|---------|
| blessed-of-netjer | Blessed by a god — auspicious |
| under-maat | Under Maat's order — favorable, just |
| opposite-meaning | Opposite-meaning principle applies — surface meaning inverts |
| under-chaos | Under Seth's chaos — challenging, but chaos seeds creation |
| warned-by-duat | Warned from Duat — a message from the underworld, pay attention |

## Swapna Shastra Dream Type Values (Indian Brahman)

| JSON value | Meaning |
|------------|---------|
| drishta | Seen — confirms waking impressions |
| shruta | Heard — processes received information |
| anubhuta | Experienced — karmic echoes from past |
| prarthita | Desired — reveals heart's true longing |
| kalpita | Imagined — mental projections and anxieties |
| bhavika | Prophetic — divine message, most significant |
| doshaja | From imbalance — physiological, but still meaningful |

## Onmyodo Dream Classification Values (Japanese Miko)

| JSON value | Meaning |
|------------|---------|
| rei-mu | Spirit dream — sent by kami or ancestors, most significant |
| shin-mu | Divine dream — prophetic, from high kami |
| aku-mu | Evil dream — caused by malevolent spirits, requires purification |

## Tonalpohualli Day-Sign Values (Mesoamerican Daykeeper)

| JSON value | Nahuatl name | Meaning |
|------------|--------------|---------|
| crocodile | Cipactli | Primordial creation, raw potential |
| wind | Ehecatl | Change, breath of life, communication |
| house | Calli | Stability, home, containment |
| lizard | Cuetzpallin | Growth, regeneration, adaptability |
| serpent | Coatl | Wisdom, transformation, life force |
| death | Miquiztli | Endings and beginnings, transformation |
| deer | Mazatl | Grace, swiftness, the hunt |
| rabbit | Tochtli | Fertility, abundance, playfulness |
| water | Atl | Emotion, purification, the primordial |
| dog | Itzcuintli | Loyalty, guidance through death, companionship |
| monkey | Ozomahtli | Artistry, play, creativity |
| grass | Malinalli | Endurance, perseverance, renewal |
| reed | Acatl | Authority, foundation, new cycle |
| jaguar | Ocelotl | Night power, shapeshifting, warrior spirit |
| eagle | Cuauhtli | Vision, courage, midday sun |
| vulture | Cozcacuauhqui | Purification, consumption, wisdom of endings |
| movement | Ollin | Earthquake, transformation, the dance of opposites |
| flint | Tecpatl | Sacrifice, precision, cutting truth |
| rain | Quiahuitl | Fertility, divine tears, cleansing |
| flower | Xochitl | Beauty, art, the fleeting and precious |

## Polynesian Voyage Values (Polynesian Navigator)

| JSON value | Meaning |
|------------|---------|
| crossing | A voyage in progress — transition between states |
| destination | Land has been sighted — a goal is within reach |
| aumakua-visit | Ancestral guardian appearing — protection and guidance |
| po-journey | Journey into the spirit world — deep spiritual knowledge |

## Yoruba Dream Type Values (Yoruba Babalawo)

| JSON value | Meaning |
|------------|---------|
| aláálà | True vision — sent by orisha or ancestors, must be taken seriously |
| aláíbàje | Corrupted dream — distorted by negative forces, requires cleansing |
| asírí | Secret dream — reveals hidden knowledge, may not be shared |
| ìríntì | Echo dream — reflects waking anxieties, informative but not prophetic |

## Islamic Dream Classification Values (Arabian Sufist)

| JSON value | Meaning |
|------------|---------|
| ru-ya | True vision from Allah — clear, vivid, remembered with peace |
| hulm | False dream from Shaytan — confused, frightening, quickly forgotten |
| nafsaniyya | Dream from the self — reflecting daily concerns |

## Wyrd-Thread Values (Scandinavian Volva)

| JSON value | Meaning |
|------------|---------|
| fate-bound | A thread that cannot be unwoven — accept and prepare |
| norn-woven | The fates are actively working — something is being decided |
| fylgja-warning | Your following spirit alerts you — watch for the sign |
| dis-counsel | Ancestral spirits advise you — honor their wisdom |

## Title Localization

The `title` field in each interpretation should be rendered in the user's language.

**Permanent perspectives:**
- English: "Chinese Mystic", "Greek Oracle", "Slavic Vedunya", "European Prophet", "Northern Shaman", "Indian Brahman"
- Chinese: "东方玄师", "希腊神谕", "斯拉夫维杜尼亚", "欧洲先知", "北方萨满", "印度婆罗门"
- Russian: "Китайский Мистик", "Греческий Оракул", "Славянская Ведунья", "Европейский Пророк", "Северный Шаман", "Индийский Брахман"

**Guest perspectives:**
- English: "Egyptian Priest", "Japanese Miko", "Mesoamerican Daykeeper", "Polynesian Navigator", "Yoruba Babalawo", "Arabian Sufist", "Scandinavian Volva"
- Chinese: "埃及祭司", "日本巫女", "中美洲日守者", "波利尼西亚领航者", "约鲁巴巴巴拉沃", "阿拉伯苏菲行者", "斯堪的纳维亚女先知"
- Russian: "Египетский Жрец", "Японская Мико", "Мезоамериканский Хранитель Дней", "Полинезийский Навигатор", "Йоруба Бабалаво", "Аравийский Суфий", "Скандинавская Вёльва"

The JSON key names (chineseMystic, greekOracle, etc.) always stay in English for programmatic access.

## Output Requirements

1. JSON must be valid and directly parseable (`JSON.parse`)
2. **JSON is internal-only** — never output raw JSON to the user. Use it to generate the image card via Playwright (see `dream-card-design.md`)
3. All string fields must be non-empty
4. `keywords` array: 3-6 elements
5. `visual_elements` array: 1-5 elements
6. `guest_selection` array: exactly 3 guest JSON keys
7. `interpretations` object: exactly 9 entries (6 permanent + 3 guest)
8. All nine `interpretation` content fields should be similar length (100-200 chars each)
9. Each perspective's unique field must clearly reflect that perspective's character
10. `shareable_text` should be engaging and worth resharing
11. `overall_advice` should extract commonalities across perspectives; if they fully contradict, acknowledge the divergence
12. **Language consistency**: All interpretation content must be in the same language the user used to describe their dream. Never mix languages within a single output card.

---

## Supplemental Guest Interpretations

When the user invites additional guests from the unheard pool (Phase 4), output a supplemental JSON block. This is a lightweight format that contains only the new interpretations — it does not repeat the Dream Card fields.

### Structure

```json
{
  "supplemental": true,
  "invited_guests": ["string — JSON keys of the invited guests, e.g. 'japaneseMiko', 'yorubaBabalawo'"],
  "interpretations": {
    "GUEST_KEY": {
      "icon": "string — Guest-specific icon",
      "title": "string — Guest name in user's language",
      "content": "string — Guest interpretation, 100-200 chars",
      "verdict": "string — Guest-specific verdict field (see guest schemas above)",
      "advice": "string — One tradition-specific suggestion"
    }
  }
}
```

### Rules

1. `supplemental` must be `true` to distinguish from the main Dream Card
2. `invited_guests` contains only the newly invited guest keys (not previously heard guests)
3. `interpretations` contains only the invited guest entries (1-4 entries, depending on how many unheard guests remain)
4. Each guest entry uses the same schema as in the main Dream Card (see Guest Schema Definitions above)
5. The same content length, voice, and language rules apply as the main Dream Card
6. If all 7 guests have been heard across main + supplemental outputs, no further invitation is offered
