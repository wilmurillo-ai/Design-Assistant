---
name: socialcard
description: Generate social preview images (OG, Twitter, GitHub) with a fluent builder API. Single dependency — Pillow.
version: 0.1.3
metadata:
  openclaw:
    requires:
      bins:
        - pip
    install:
      - kind: uv
        package: socialcard
        bins: []
    homepage: https://github.com/HumanjavaEnterprises/huje.socialcard.OC-python.src
---

# SocialCard — Social Preview Images for AI Agents

Generate beautiful Open Graph, Twitter, and GitHub social preview images programmatically. Fluent builder API — chain methods, pick a preset and theme, render to file or bytes. Single dependency: Pillow.

> **Import:** `pip install socialcard` → `from socialcard import SocialCard`

## Install

```bash
pip install socialcard
```

Single dependency: `Pillow >= 10.0`.

## Quickstart

```python
from socialcard import SocialCard

SocialCard("og").title("My Project").subtitle("A cool tool").render("card.png")
```

## Core Capabilities

### Simple Card

```python
from socialcard import SocialCard

card = SocialCard("og").title("My Project").subtitle("Description").render("card.png")
```

### Full-Featured Card

```python
card = (
    SocialCard("twitter", theme="midnight")
    .badge("Open Source")
    .title("NostrKey Browser Extension")
    .subtitle("Sign Nostr events with your browser")
    .cards(["JavaScript", "Nostr", "NIP-07"])
    .footer("nostrkey.com")
    .accent("#a3e635")
    .grid()
    .glow()
    .render("card.png")
)
```

### Skill Cards (Structured)

```python
card = (
    SocialCard("github")
    .badge("OpenClaw")
    .title("Humanjava Ecosystem")
    .skill_cards([
        {"name": "Nostr|Key", "label": "Identity", "code": "NIP-07"},
        {"name": "Nostr|Social", "label": "Relationships", "code": "v0.1.0"},
        {"name": "Nostr|Calendar", "label": "Scheduling", "code": "NIP-52"},
    ])
    .footer("humanjava.com")
    .render("ecosystem.png")
)
```

Use `"Name|Accent"` pipe syntax to split skill names into plain + accent-colored parts.

### Render to Bytes (In-Memory)

```python
png_bytes = (
    SocialCard("og")
    .title("Generated Card")
    .render_bytes("PNG")
)
# Returns raw bytes — suitable for HTTP responses, S3 uploads, etc.
```

Supported formats: `PNG`, `JPEG`, `WEBP`.

### Custom Preset

```python
from socialcard.presets import custom

banner = custom("banner", 1920, 400)
SocialCard(banner).title("Wide Banner").render("banner.png")
```

### Custom Theme

```python
from socialcard.themes import Theme

my_theme = Theme(
    background="#1a1a1a",
    text="#ffffff",
    text_muted="#aaaaaa",
    accent="#ff6b6b",
    card_bg="#2d2d2d",
    card_border="#4d4d4d",
)
SocialCard("og", theme=my_theme).title("Custom Look").render("card.png")
```

## Presets

| Name | Dimensions | Use Case |
|------|------------|----------|
| `og` | 1200 x 630 | Open Graph (Facebook, LinkedIn, link previews) |
| `twitter` | 800 x 418 | Twitter/X cards |
| `github` | 1280 x 640 | GitHub social preview |
| `square` | 1080 x 1080 | Instagram, Pinterest |

Custom presets: up to 4096 x 4096.

## Themes

| Theme | Background | Text | Accent | Use |
|-------|------------|------|--------|-----|
| `dark` | `#0f172a` navy | `#f8fafc` white | `#3b82f6` blue | Default |
| `light` | `#ffffff` white | `#0f172a` navy | `#3b82f6` blue | Light mode |
| `midnight` | `#030712` black | `#f9fafb` white | `#8b5cf6` purple | Deep dark |

## Builder Methods

All content methods return `SocialCard` for chaining.

| Method | Description | Max Length |
|--------|-------------|-----------|
| `.badge(text)` | Small pill label at top | 100 chars |
| `.title(text)` | Main heading (52px, word-wrapped) | 200 chars |
| `.subtitle(text)` | Subheading (26px, word-wrapped) | 500 chars |
| `.cards(labels)` | Row of tag chips (18px) | — |
| `.skill_cards(skills)` | Structured cards with name/label/code | — |
| `.footer(text)` | Bottom text (18px) | 200 chars |
| `.accent(hex)` | Override accent color | — |
| `.grid()` | Subtle grid overlay | — |
| `.glow()` | Radial glow effect | — |
| `.render(path)` | Save to file, returns Image | — |
| `.render_bytes(fmt)` | Get PNG/JPEG/WEBP bytes | — |

## Response Format

### render()

Returns a `PIL.Image.Image` object and saves the file. Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp`.

### render_bytes()

Returns `bytes` (raw image data). Supported formats: `"PNG"`, `"JPEG"`, `"WEBP"`.

### skill_cards() Input Format

```python
[
    {
        "name": "Nostr|Key",     # Pipe splits into plain + accent-colored text
        "label": "Identity",      # Subtitle in muted color
        "code": "NIP-07",         # Code in accent color, monospace
    }
]
```

## Common Patterns

### Generate for Multiple Platforms

```python
for preset in ["og", "twitter", "github"]:
    SocialCard(preset).title("My Project").subtitle("Description").render(f"card-{preset}.png")
```

### Brand Colors

```python
# Override accent to match your brand
SocialCard("og").title("NostrKey").accent("#a3e635").render("card.png")
```

### Serve from a Web Endpoint

```python
png_bytes = SocialCard("og").title("Dynamic Card").render_bytes("PNG")
# Return as HTTP response with Content-Type: image/png
```

## Security

- **Path traversal blocked.** `..` components in render paths raise `ValueError`.
- **File extension allowlist.** Only `.png`, `.jpg`, `.jpeg`, `.webp` accepted by `render()`.
- **Dimension limits.** Custom presets capped at 4096 x 4096 to prevent memory exhaustion.
- **Input length limits.** Badge (100), title (200), subtitle (500), footer (200) characters max.
- **Font size limits.** 1–200px enforced.
- **No network access.** Everything renders locally.

## Configuration

### Fonts

Platform-aware font loading with automatic fallbacks:
- **macOS:** SF Pro Display → Arial Bold → Helvetica
- **Linux:** DejaVu Sans Bold
- **Windows:** Arial

Monospace: SF Mono → DejaVu Sans Mono → Consolas. Falls back to Pillow's built-in bitmap font if nothing found.

## Links

- [PyPI](https://pypi.org/project/socialcard/)
- [GitHub](https://github.com/HumanjavaEnterprises/huje.socialcard.OC-python.src)
- [huje.tools](https://huje.tools)
- [ClawHub](https://clawhub.ai/u/vveerrgg)

License: MIT
