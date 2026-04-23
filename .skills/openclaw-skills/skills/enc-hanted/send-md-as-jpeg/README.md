# md-to-image v0.1

Render Markdown as JPEG for channels that don't support Markdown (e.g., WeChat).
将 Markdown 渲染为 JPEG 图片，适用于不原生支持 Markdown 的聊天渠道（如微信）。

## Features / 功能

- Headings (h1–h3), bold, italic, inline code
- Code blocks — line numbers, Monokai syntax highlighting (Pygments), auto word-wrap
- LaTeX — inline `$...$` and display `$$...$$` (KaTeX CLI, offline)
- Mermaid diagrams (rendered as SVG via mermaid-cli)
- Unordered/ordered lists, blockquotes, horizontal rules, links, tables
- **4 color themes**: light, dark, sepia, nord (auto-switch by time)
- **Smart page splitting**: none, A4, A5 (breaks at logical boundaries)
- JPEG output, self-contained (no CDN, no JS)

## Quick Start / 快速开始

```bash
bash setup.sh                                    # install dependencies
bash render.sh input.md out.jpg                  # default (light)
bash render.sh --theme dark input.md out.jpg     # dark mode
bash render.sh --pages a5 input.md out.jpg       # auto-split
bash render.sh --theme nord --pages a4 in.md out.jpg  # combined
```

## Dependencies / 依赖

| Item / 组件 | Required / 必需 |
|---|---|
| wkhtmltopdf | Yes |
| python3-pillow | Yes |
| python3-mistune | Yes |
| python3-pygments | No (~12.7MB) |
| katex (npm) | No (~4.6MB) |
| mermaid-cli (npm) | No |

## How It Works / 工作流程

```
User input → AI judges trigger (>600 chars / code / LaTeX / table)
    ↓
AI writes Markdown → /tmp/md2img_{timestamp}_{hash}.md
    ↓
render.sh:
  mistune    → parse Markdown → HTML
  Pygments   → syntax highlight code blocks (Monokai, line numbers)
  KaTeX CLI  → render LaTeX (offline, §placeholder§ technique)
  mmdc       → render Mermaid → SVG
  wkhtmltoimage → HTML → JPEG (Q100, zoom 3x)
  Pillow     → smart page split (optional)
    ↓
send image → cleanup → done
```

Token overhead: ~80 token per render (content generation unchanged).

## Trigger / 触发条件

Render when: >600 chars / >20 lines / code blocks / LaTeX / tables / user requests.
不触发：<300字 / 简单列表 / 用户说"直接发文字"。

## Platform / 平台

| Platform | Status |
|---|---|
| Linux (Fedora/Debian/Ubuntu) | ✅ Tested |
| Linux (Arch) | ⚠️ Expected |
| macOS | ⚠️ `brew install wkhtmltopdf` |
| Windows (WSL) | ⚠️ Expected |
| Windows (native) | ❌ Not supported |

## Usage / 使用方式

```bash
# 基础渲染
bash render.sh input.md output.jpg

# 指定主题
bash render.sh --theme dark input.md output.jpg

# 自动分页
bash render.sh --pages a5 input.md output.jpg

# 组合使用
bash render.sh --theme nord --pages a4 input.md output.jpg
```

### Options / 选项

- `--theme <name>`: `light`（默认）, `dark`, `sepia`, `nord`
- `--pages <mode>`: `none`（默认）, `a4`, `a5`

### Theme / 主题建议

AI 代理可根据时间自动选择：
- 06:00–17:59 → `light`
- 18:00–05:59 → `dark`

## License Compliance / 许可证合规

| Component | License | Compatibility |
|---|---|---|
| wkhtmltopdf | LGPLv3 | ✅ CLI call, no linking |
| Pillow | HPND | ✅ Permissive |
| Mistune | BSD | ✅ Permissive |
| Pygments | BSD | ✅ Permissive |
| KaTeX | MIT | ✅ Permissive |
| Mermaid CLI | MIT | ✅ Permissive |
| Maple Mono | OFL-1.1 | ✅ Font redistribution OK |
| **md-to-image** | **MIT** | ✅ Compatible with all |

wkhtmltopdf is used as a CLI tool (subprocess), not linked as a library — LGPLv3 §5 does not apply.

## Acknowledgments / 致谢

- [wkhtmltopdf](https://wkhtmltopdf.org/) — LGPLv3
- [Pillow](https://python-pillow.org/) — HPND License
- [Mistune](https://github.com/lepture/mistune) — BSD License
- [Pygments](https://pygments.org/) — BSD License
- [KaTeX](https://katex.org/) — MIT License
- [Mermaid](https://mermaid.js.org/) — MIT License
- [Maple Mono](https://font.subf.dev/) — OFL-1.1 (optional)

## Roadmap

- [ ] Custom theme via config
- [ ] PDF output option

## License

MIT
