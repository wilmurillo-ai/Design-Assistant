#!/usr/bin/env python3
"""
Font Pairing Recommendation Engine for the Graphic Design Mastery Skill System.

Given a design context (mood, purpose, audience), recommends optimal font pairings
from Google Fonts with complete CSS import code and usage examples.

Usage:
    python recommend_fonts.py --mood "luxury"
    python recommend_fonts.py --mood "tech" --purpose "landing-page"
    python recommend_fonts.py --mood "editorial" --purpose "blog"
    python recommend_fonts.py --list-moods
"""

import sys
import json

# ============================================================================
# FONT DATABASE
# ============================================================================

FONT_PAIRINGS = {
    "luxury": [
        {
            "display": "Cormorant Garamond",
            "display_weights": "400;500;600;700",
            "body": "Lato",
            "body_weights": "300;400;700",
            "mono": None,
            "character": "Refined elegance. The high-contrast strokes of Cormorant with the clean geometry of Lato creates a sophisticated contrast. Think luxury fashion, premium hospitality, fine dining.",
            "best_for": ["luxury brands", "fashion", "hospitality", "fine art", "jewelry"],
        },
        {
            "display": "Playfair Display",
            "display_weights": "400;700;900",
            "body": "Source Sans 3",
            "body_weights": "300;400;600",
            "mono": None,
            "character": "Classic luxury with modern clarity. Playfair's high contrast meets Source Sans's clean readability. Editorial luxury — magazines, upscale real estate, premium services.",
            "best_for": ["editorial", "real estate", "premium services", "magazines"],
        },
    ],

    "tech": [
        {
            "display": "Space Grotesk",
            "display_weights": "400;500;600;700",
            "body": "Manrope",
            "body_weights": "300;400;500;600;700",
            "mono": "JetBrains Mono",
            "character": "Geometric precision with warmth. Space Grotesk's distinctive letterforms signal innovation, while Manrope's generous x-height ensures readability. Developer tools, SaaS, fintech.",
            "best_for": ["SaaS", "developer tools", "fintech", "AI/ML", "startups"],
        },
        {
            "display": "Sora",
            "display_weights": "400;500;600;700;800",
            "body": "DM Sans",
            "body_weights": "400;500;700",
            "mono": "Fira Code",
            "character": "Modern authority. Sora's geometric confidence paired with DM Sans's clean neutrality. Enterprise software, cloud platforms, tech companies with authority.",
            "best_for": ["enterprise", "cloud platforms", "tech companies", "dashboards"],
        },
    ],

    "editorial": [
        {
            "display": "Instrument Serif",
            "display_weights": "400",
            "body": "DM Sans",
            "body_weights": "400;500;700",
            "mono": "IBM Plex Mono",
            "character": "Contemporary editorial. Instrument Serif's delicate serif forms create an editorial voice, while DM Sans keeps body text modern and clean. Blogs, magazines, cultural publications.",
            "best_for": ["blogs", "magazines", "cultural publications", "newsletters", "essays"],
        },
        {
            "display": "Fraunces",
            "display_weights": "400;700;900",
            "body": "Figtree",
            "body_weights": "300;400;500;600",
            "mono": None,
            "character": "Quirky editorial warmth. Fraunces's optical-size-aware variable design paired with Figtree's open friendliness. Personal blogs, creative writing, independent media.",
            "best_for": ["personal blogs", "creative writing", "independent media", "book reviews"],
        },
    ],

    "corporate": [
        {
            "display": "Plus Jakarta Sans",
            "display_weights": "400;500;600;700;800",
            "body": "Source Serif 4",
            "body_weights": "300;400;600",
            "mono": "Source Code Pro",
            "character": "Professional authority with warmth. Plus Jakarta's geometric confidence signals competence, while Source Serif adds gravitas to long-form content. Consulting, legal, finance.",
            "best_for": ["consulting", "legal", "finance", "annual reports", "whitepapers"],
        },
        {
            "display": "Outfit",
            "display_weights": "400;500;600;700;800",
            "body": "Lora",
            "body_weights": "400;500;600;700",
            "mono": None,
            "character": "Modern professionalism. Outfit's geometric sans-serif with Lora's brushed serif strokes. Strikes a balance between innovation and tradition. Corporate communications, presentations.",
            "best_for": ["corporate", "presentations", "HR communications", "training materials"],
        },
    ],

    "friendly": [
        {
            "display": "Bricolage Grotesque",
            "display_weights": "400;600;700;800",
            "body": "Nunito",
            "body_weights": "300;400;600;700",
            "mono": None,
            "character": "Warm and characterful. Bricolage Grotesque's humanist warmth with Nunito's rounded terminals creates an inviting, approachable personality. Education, health, community.",
            "best_for": ["education", "health", "community platforms", "children", "non-profits"],
        },
        {
            "display": "Rubik",
            "display_weights": "400;500;600;700;800",
            "body": "Karla",
            "body_weights": "400;500;700",
            "mono": None,
            "character": "Playful geometry. Rubik's slightly rounded corners with Karla's grotesque clarity. Approachable without being childish. Consumer apps, food & beverage, lifestyle.",
            "best_for": ["consumer apps", "food & beverage", "lifestyle", "fitness", "social"],
        },
    ],

    "brutalist": [
        {
            "display": "Archivo Black",
            "display_weights": "400",
            "body": "IBM Plex Mono",
            "body_weights": "300;400;500;600;700",
            "mono": "IBM Plex Mono",
            "character": "Raw, uncompromising. Archivo Black's massive weight with IBM Plex Mono's mechanical precision. Anti-design, punk, counter-culture, underground, experimental.",
            "best_for": ["experimental", "punk", "zines", "galleries", "counter-culture"],
        },
        {
            "display": "Space Mono",
            "display_weights": "400;700",
            "body": "Space Mono",
            "body_weights": "400;700",
            "mono": "Space Mono",
            "character": "Monospace everywhere. Space Mono for both display and body creates a brutalist, technical, no-nonsense aesthetic. Code art, hacker culture, brutalist web.",
            "best_for": ["brutalist web", "hacker culture", "code art", "crypto", "experimental tech"],
        },
    ],

    "minimal": [
        {
            "display": "Geist",
            "display_weights": "300;400;500;600;700",
            "body": "Geist",
            "body_weights": "300;400;500",
            "mono": "Geist Mono",
            "character": "Ultra-clean single-family system. Geist's Vercel-designed typeface handles both display and body with elegant simplicity. Minimalist products, developer tools, design tools.",
            "note": "Load from: https://cdn.jsdelivr.net/npm/geist@1.0.0/dist/fonts/geist-sans/",
            "best_for": ["minimalist products", "developer tools", "design tools", "portfolios"],
        },
        {
            "display": "Inter",
            "display_weights": "300;400;500;600;700",
            "body": "Crimson Text",
            "body_weights": "400;600;700",
            "mono": "JetBrains Mono",
            "character": "Minimal swiss with serif warmth. Inter's pixel-perfect clarity for UI elements, Crimson Text's old-style elegance for long-form. Portfolio sites, design agencies.",
            "note": "Inter is overused as a sole font — pairing with Crimson Text gives it new life.",
            "best_for": ["portfolios", "design agencies", "documentation", "technical writing"],
        },
    ],

    "warm": [
        {
            "display": "Fraunces",
            "display_weights": "300;400;700;900",
            "body": "Figtree",
            "body_weights": "300;400;500;600",
            "mono": None,
            "character": "Organically warm. Fraunces's variable optical sizing creates expressive headlines, while Figtree's open geometry keeps body text fresh. Bakeries, cafes, wellness, organic brands.",
            "best_for": ["bakeries", "cafes", "wellness", "organic brands", "crafts"],
        },
    ],
}

AVAILABLE_MOODS = list(FONT_PAIRINGS.keys())


def get_google_fonts_url(pairing):
    """Generate the Google Fonts import URL."""
    families = []
    display = pairing["display"].replace(" ", "+")
    families.append(f"family={display}:wght@{pairing['display_weights']}")

    if pairing["body"] != pairing["display"]:
        body = pairing["body"].replace(" ", "+")
        families.append(f"family={body}:wght@{pairing['body_weights']}")

    if pairing.get("mono") and pairing["mono"] != pairing["body"]:
        mono = pairing["mono"].replace(" ", "+")
        families.append(f"family={mono}:wght@400;500;700")

    return f"https://fonts.googleapis.com/css2?{'&'.join(families)}&display=swap"


def format_css_usage(pairing):
    """Generate CSS usage example."""
    lines = []
    lines.append("/* Font Import */")
    url = get_google_fonts_url(pairing)
    lines.append(f'@import url("{url}");')
    lines.append("")
    lines.append("/* Font Variables */")
    lines.append(f"--font-display: '{pairing['display']}', {'serif' if 'Serif' in pairing['display'] or 'Garamond' in pairing['display'] or 'Playfair' in pairing['display'] or 'Fraunces' in pairing['display'] or 'Instrument' in pairing['display'] or 'Lora' in pairing['display'] or 'Crimson' in pairing['display'] else 'sans-serif'};")
    lines.append(f"--font-body: '{pairing['body']}', {'serif' if 'Serif' in pairing['body'] or 'Lora' in pairing['body'] or 'Crimson' in pairing['body'] or 'Source Serif' in pairing['body'] else 'sans-serif'};")
    if pairing.get("mono"):
        lines.append(f"--font-mono: '{pairing['mono']}', monospace;")
    lines.append("")
    lines.append("/* Usage */")
    lines.append(".display { font-family: var(--font-display); font-weight: 700; }")
    lines.append(".heading { font-family: var(--font-display); font-weight: 600; }")
    lines.append(".body    { font-family: var(--font-body); font-weight: 400; }")
    lines.append(".caption { font-family: var(--font-body); font-weight: 400; }")
    if pairing.get("mono"):
        lines.append(".code    { font-family: var(--font-mono); font-weight: 400; }")

    return "\n".join(lines)


def format_html_link(pairing):
    """Generate HTML link tag."""
    url = get_google_fonts_url(pairing)
    lines = [
        '<link rel="preconnect" href="https://fonts.googleapis.com">',
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        f'<link href="{url}" rel="stylesheet">',
    ]
    return "\n".join(lines)


def recommend(mood, purpose=None):
    """Get font recommendations for a mood."""
    mood = mood.lower()
    if mood not in FONT_PAIRINGS:
        print(f"Unknown mood: '{mood}'")
        print(f"Available moods: {', '.join(AVAILABLE_MOODS)}")
        return

    pairings = FONT_PAIRINGS[mood]

    for i, pairing in enumerate(pairings):
        print(f"\n{'='*60}")
        print(f"  OPTION {i+1}: {pairing['display']} + {pairing['body']}")
        if pairing.get("mono"):
            print(f"  Mono: {pairing['mono']}")
        print(f"{'='*60}")
        print(f"\n  Character: {pairing['character']}")
        print(f"  Best for: {', '.join(pairing['best_for'])}")
        if pairing.get("note"):
            print(f"  Note: {pairing['note']}")
        print(f"\n  --- HTML Import ---")
        print(format_html_link(pairing))
        print(f"\n  --- CSS Usage ---")
        print(format_css_usage(pairing))
        print()


if __name__ == "__main__":
    if "--list-moods" in sys.argv:
        print("Available moods:")
        for mood in AVAILABLE_MOODS:
            count = len(FONT_PAIRINGS[mood])
            print(f"  {mood} ({count} pairing{'s' if count > 1 else ''})")
        sys.exit(0)

    mood = None
    purpose = None

    for i, arg in enumerate(sys.argv):
        if arg == "--mood" and i + 1 < len(sys.argv):
            mood = sys.argv[i + 1]
        if arg == "--purpose" and i + 1 < len(sys.argv):
            purpose = sys.argv[i + 1]

    if not mood:
        print("Usage: python recommend_fonts.py --mood <mood> [--purpose <purpose>]")
        print(f"Available moods: {', '.join(AVAILABLE_MOODS)}")
        sys.exit(1)

    recommend(mood, purpose)
