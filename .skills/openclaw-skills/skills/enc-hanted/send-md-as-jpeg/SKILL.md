---
name: md-to-image
description: "在即时通讯 app 中以图片形式更优雅的展示 Markdown。支持标题、代码高亮（行号、Monokai）、LaTeX 公式、Mermaid 图表、表格、列表。4 种色彩主题，智能分页。完全离线渲染。"
metadata:
  {
    "openclaw":
      {
        "emoji": "🖼️",
        "requires":
          {
            "bins": ["wkhtmltoimage", "python3"],
          },
        "install":
          [
            {
              "id": "setup",
              "kind": "script",
              "script": "setup.sh",
              "label": "Run setup.sh to install dependencies",
            },
          ],
      },
  }
---

# md-to-image (v0.1)

Render Markdown as a JPEG image and send it via `openclaw message send --media`.
Use this when the chat channel doesn't natively support Markdown rendering (e.g., WeChat).

## Trigger Conditions

Render as image when **any** of the following is true:

- Plain text length > 600 characters
- Line count > 20
- Contains fenced code blocks (` ``` `)
- Contains LaTeX formulas (`$...$` or `$$...$$`)
- Contains formatted tables
- User explicitly requests image output (e.g., "做成图", "render as image")

## Do NOT Render As Image

- Short answers (< 300 chars)
- Simple lists without code
- User says "直接发文字" or "plain text"

## Usage

```bash
bash render.sh input.md output.jpg
bash render.sh --theme dark input.md output.jpg
bash render.sh --pages a5 input.md output.jpg
bash render.sh --theme nord --pages a4 input.md output.jpg

# Send via channel
openclaw message send --channel <channel> --target "<id>" --media output.jpg
```

### Options

- `--theme <name>`: `light` (default), `dark`, `sepia`, `nord`
- `--pages <mode>`: `none` (default), `a4`, `a5`

### Theme Selection (for agent)

Auto-detect by local hour:
- 06:00–17:59 → `light`
- 18:00–05:59 → `dark`

Or let user choose. Pass `--theme <name>` to render.sh.

## Setup

```bash
bash /path/to/skills/md-to-image/setup.sh
```

## Dependencies

| Item | Required | Fallback |
|------|----------|----------|
| wkhtmltopdf | Yes | Cannot render |
| python3-pillow | Yes | Page split |
| python3-mistune | Yes | Markdown parser |
| python3-pygments | No | Plain code blocks (no syntax highlighting) |
| katex (npm) | No | LaTeX shown as raw text |
| mermaid-cli (npm) | No | Diagrams shown as code |

## Features

- Headings (h1–h3), bold, italic, inline code
- Code blocks with line numbers (Pygments Monokai, auto word-wrap)
- LaTeX (inline `$...$` and display `$$...$$`, KaTeX CLI offline)
- Mermaid diagrams (rendered as SVG)
- Unordered/ordered lists, blockquotes, horizontal rules, links, tables
- 4 color themes: light, dark, sepia, nord
- Smart page splitting (none / A4 / A5)
- JPEG output, self-contained (no CDN, no JS)

## Architecture

```
Markdown → mistune → HTML (code blocks via CustomRenderer)
LaTeX → extracted → §placeholder§ → KaTeX CLI → restored
Mermaid → mmdc → SVG → embedded
wkhtmltoimage → JPEG (Q100, 3x zoom)
→ [optional] Pillow page split
```
