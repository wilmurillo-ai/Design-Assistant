#!/bin/bash
# render.sh - Markdown → JPEG (mistune + wkhtmltoimage)
# Version: 0.1
# Usage: render.sh [options] input.md [output.jpg]
#
# Options:
#   --theme <name>    Color theme: light (default), dark, sepia, nord
#   --pages <mode>    Page split: none (default), a4, a5
#   --version         Show version
set -e

VERSION="0.1"
THEME="light"
PAGES="none"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --version)  echo "md-to-image $VERSION"; exit 0 ;;
        --theme)    THEME="$2"; shift 2 ;;
        --pages)    PAGES="$2"; shift 2 ;;
        -*)         echo "Unknown option: $1" >&2; exit 1 ;;
        *)          break ;;
    esac
done

INPUT="${1:?Usage: render.sh [--theme light|dark|sepia|nord] [--pages none|a4|a5] input.md [output.jpg]}"
OUTPUT="${2:-${INPUT%.md}.jpg}"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
FONT_DIR="$SKILL_DIR/fonts"

command -v wkhtmltoimage &>/dev/null || { echo "ERROR: wkhtmltoimage not found." >&2; exit 1; }
python3 -c "from PIL import Image" 2>/dev/null || { echo "ERROR: Pillow not found." >&2; exit 1; }

b64_file() { base64 < "$1" 2>/dev/null | tr -d '\n'; }
REGULAR_B64=""; BOLD_B64=""
for f in "$FONT_DIR"/custom-400.woff2 "$FONT_DIR"/maple-mono-400.woff2; do
    [[ -f "$f" ]] && REGULAR_B64=$(b64_file "$f") && break
done
for f in "$FONT_DIR"/custom-700.woff2 "$FONT_DIR"/maple-mono-700.woff2; do
    [[ -f "$f" ]] && BOLD_B64=$(b64_file "$f") && break
done

HAS_PYGMENTS=$(python3 -c "import pygments; print('1')" 2>/dev/null || echo "0")
HAS_KATEX=$(command -v katex &>/dev/null && echo "1" || echo "0")
HAS_MERMAID=$(command -v mmdc &>/dev/null && echo "1" || echo "0")

python3 - "$INPUT" "$OUTPUT" "$REGULAR_B64" "$BOLD_B64" "$HAS_PYGMENTS" "$HAS_KATEX" "$HAS_MERMAID" "$THEME" "$PAGES" "$SKILL_DIR" << 'PYEOF'
import sys, re, html as h, subprocess, os, time, hashlib, tempfile
import mistune
from mistune.plugins.table import table

input_file, output_file, reg_b64, bold_b64 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
has_pygments = sys.argv[5] == '1'
has_katex = sys.argv[6] == '1'
has_mermaid = sys.argv[7] == '1'
theme_name = sys.argv[8]
pages_mode = sys.argv[9]
skill_dir = sys.argv[10]

# ── Themes ──
THEMES = {
    'light': {
        'body_bg': '#fafafa', 'body_fg': '#383a42', 'heading': '#232323',
        'link': '#526fff', 'italic': '#526fff',
        'code_inline_bg': '#e8e8ec', 'code_inline_fg': '#e45649',
        'pre_bg': '#272822', 'pre_fg': '#f8f8f2',
        'lang_bg': '#3e3e3e', 'lang_fg': '#66d9ef',
        'th_bg': '#f3f4f6', 'th_fg': '#232323', 'td_bg': '#fff',
        'tr_even': '#f9fafb', 'border': '#d1d5db',
        'bq_bg': '#f9f9f9', 'bq_fg': '#666', 'bq_border': '#ddd',
        'hr': '#ddd', 'strong': '#1a1a1a',
        'pygments_style': 'monokai',
        'lineno_color': '#909194',
    },
    'dark': {
        'body_bg': '#1e1e2e', 'body_fg': '#cdd6f4', 'heading': '#cdd6f4',
        'link': '#89b4fa', 'italic': '#89b4fa',
        'code_inline_bg': '#313244', 'code_inline_fg': '#f38ba8',
        'pre_bg': '#181825', 'pre_fg': '#cdd6f4',
        'lang_bg': '#1e1e2e', 'lang_fg': '#89b4fa',
        'th_bg': '#313244', 'th_fg': '#cdd6f4', 'td_bg': '#1e1e2e',
        'tr_even': '#181825', 'border': '#45475a',
        'bq_bg': '#181825', 'bq_fg': '#a6adc8', 'bq_border': '#45475a',
        'hr': '#45475a', 'strong': '#f5e0dc',
        'pygments_style': 'monokai',
        'lineno_color': '#6c7086',
    },
    'sepia': {
        'body_bg': '#f4ecd8', 'body_fg': '#5c4b37', 'heading': '#3e2f1c',
        'link': '#7b5ea7', 'italic': '#7b5ea7',
        'code_inline_bg': '#e8dcc8', 'code_inline_fg': '#a0522d',
        'pre_bg': '#3e2f1c', 'pre_fg': '#f4ecd8',
        'lang_bg': '#5c4b37', 'lang_fg': '#d4a76a',
        'th_bg': '#e8dcc8', 'th_fg': '#3e2f1c', 'td_bg': '#f4ecd8',
        'tr_even': '#ede4d0', 'border': '#c9b99a',
        'bq_bg': '#ede4d0', 'bq_fg': '#6b5a42', 'bq_border': '#c9b99a',
        'hr': '#c9b99a', 'strong': '#3e2f1c',
        'pygments_style': 'monokai',
        'lineno_color': '#8a7a62',
    },
    'nord': {
        'body_bg': '#2e3440', 'body_fg': '#d8dee9', 'heading': '#eceff4',
        'link': '#88c0d0', 'italic': '#88c0d0',
        'code_inline_bg': '#3b4252', 'code_inline_fg': '#bf616a',
        'pre_bg': '#2e3440', 'pre_fg': '#d8dee9',
        'lang_bg': '#3b4252', 'lang_fg': '#88c0d0',
        'th_bg': '#3b4252', 'th_fg': '#eceff4', 'td_bg': '#2e3440',
        'tr_even': '#3b4252', 'border': '#4c566a',
        'bq_bg': '#3b4252', 'bq_fg': '#d8dee9', 'bq_border': '#4c566a',
        'hr': '#4c566a', 'strong': '#eceff4',
        'pygments_style': 'nord',
        'lineno_color': '#4c566a',
    },
}

t = THEMES.get(theme_name, THEMES['light'])
is_dark = theme_name in ('dark', 'nord')

with open(input_file) as f:
    md = f.read()

# ── Helpers ──
def highlight_code(code, lang):
    if not has_pygments or not lang:
        lines = h.escape(code).rstrip().split('\n')
        numbered = ''.join(
            f'<tr><td class="ln">{i+1}</td><td class="cd">{line}</td></tr>'
            for i, line in enumerate(lines)
        )
        return f'<table class="code-table"><tbody>{numbered}</tbody></table>'
    try:
        from pygments import highlight as pyg_highlight
        from pygments.lexers import get_lexer_by_name
        from pygments.formatters import HtmlFormatter
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(
            nowrap=False, noclasses=True,
            style=t['pygments_style'],
            linenos='table', linenostart=1
        )
        result = pyg_highlight(code, lexer, formatter)
        result = re.sub(r' style="background: #[0-9a-fA-F]+"', '', result, count=1)
        return result.rstrip()
    except Exception as e:
        print(f'WARN: highlight_code({lang}): {e}', file=sys.stderr)
        return h.escape(code).rstrip()

def render_mermaid(code):
    if not has_mermaid:
        return f'<pre><code>{h.escape(code)}</code></pre>'
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as mf:
            mf.write(code)
            mmd_path = mf.name
        svg_path = mmd_path.replace('.mmd', '.svg')
        r = subprocess.run(
            ['mmdc', '-i', mmd_path, '-o', svg_path, '-b', 'transparent', '-w', '800'],
            capture_output=True, text=True, timeout=15
        )
        os.unlink(mmd_path)
        if r.returncode == 0 and os.path.exists(svg_path):
            with open(svg_path) as sf:
                svg = sf.read()
            os.unlink(svg_path)
            return f'<div class="mermaid-block">{svg}</div>'
        else:
            print(f'WARN: mmdc failed: {r.stderr[:200]}', file=sys.stderr)
            return f'<pre><code>{h.escape(code)}</code></pre>'
    except Exception as e:
        print(f'WARN: render_mermaid: {e}', file=sys.stderr)
        return f'<pre><code>{h.escape(code)}</code></pre>'

def render_latex(formula, display=False):
    if not has_katex:
        return h.escape(formula)
    try:
        cmd = ['katex', '--display-mode'] if display else ['katex']
        r = subprocess.run(cmd, input=formula, capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else h.escape(formula)
    except Exception as e:
        print(f'WARN: render_latex: {e}', file=sys.stderr)
        return h.escape(formula)

# ── Pass 1: extract LaTeX only (code blocks handled by CustomRenderer) ──
# Use §...§ placeholders (survives mistune, won't appear in normal text)
latex_replacements = []
def extract_latex_display(m):
    idx = len(latex_replacements)
    latex_replacements.append((True, m.group(1).strip()))
    return f'\n§LATEX{idx}§\n'
def extract_latex_inline(m):
    idx = len(latex_replacements)
    latex_replacements.append((False, m.group(1).strip()))
    return f'§LATEX{idx}§'
text = re.sub(r'^\$\$\s*\n(.*?)\n\$\$\s*$', extract_latex_display, md, flags=re.MULTILINE | re.DOTALL)
text = re.sub(
    r'(?<!\$)\$(?! )([^$\n]*?(?:\\[a-zA-Z]+|[\^_]|[\u0391-\u03C9∫∑∏√∞≈≠≤≥±×÷])[^$\n]*?)(?<! )\$(?!\$)',
    extract_latex_inline, text
)

# ── Pass 2: render markdown (code blocks via CustomRenderer) ──
class CustomRenderer(mistune.HTMLRenderer):
    def block_code(self, code, info=None):
        lang = (info or '').strip().split()[0] if info else ''
        if lang == 'mermaid':
            return render_mermaid(code)
        highlighted = highlight_code(code, lang)
        lang_tag = f'<div class="lang-label">{h.escape(lang)}</div>' if lang else ''
        return f'<div class="code-wrap">{lang_tag}{highlighted}</div>\n'

renderer = CustomRenderer()
markdown = mistune.create_markdown(renderer=renderer, plugins=[table])
html_body = markdown(text)

# ── Pass 3: restore LaTeX placeholders ──
for idx, (display, formula) in enumerate(latex_replacements):
    rendered = render_latex(formula, display)
    if display:
        el = f'<div class="katex-block">{rendered}</div>'
    else:
        el = f'<span class="katex-inline">{rendered}</span>'
    html_body = html_body.replace(f'§LATEX{idx}§', el)

# ── CSS ──
font_face = ''
if reg_b64:
    font_face += f'@font-face{{font-family:"Maple Mono";src:url("data:font/woff2;base64,{reg_b64}") format("woff2");font-weight:400}}'
if bold_b64:
    font_face += f'@font-face{{font-family:"Maple Mono";src:url("data:font/woff2;base64,{bold_b64}") format("woff2");font-weight:700}}'

code_font = '"Maple Mono",monospace' if reg_b64 else 'monospace'
body_font = f'"Maple Mono","Microsoft YaHei","PingFang SC",monospace,sans-serif' if reg_b64 else '"Microsoft YaHei","PingFang SC",sans-serif'

css = font_face + (
    f'body{{font-family:{body_font};padding:20px 28px;margin:0;font-size:15px;'
    f'line-height:1.7;color:{t["body_fg"]};background:{t["body_bg"]};'
    f'max-width:740px;overflow-x:hidden}}'
    f'h1{{font-size:22px;margin:18px 0 8px;font-weight:700;color:{t["heading"]}}}'
    f'h2{{font-size:18px;margin:14px 0 6px;font-weight:700;color:{t["heading"]}}}'
    f'h3{{font-size:16px;margin:12px 0 4px;font-weight:700;color:{t["heading"]}}}'
    'p{margin:5px 0}'
    f'strong{{font-weight:700;color:{t["strong"]}}}'
    f'em{{font-style:italic;color:{t["italic"]}}}'
    # Inline code
    f'code{{background:{t["code_inline_bg"]};padding:2px 6px;border-radius:4px;font-size:13px;'
    f'font-family:{code_font};color:{t["code_inline_fg"]}}}'
    # Code block wrapper (integrated language label)
    f'.code-wrap{{background:{t["pre_bg"]};border-radius:8px;overflow:hidden;margin:10px 0}}'
    f'.code-wrap .lang-label{{background:{t["lang_bg"]};color:{t["lang_fg"]};padding:4px 14px;'
    f'font-size:12px;font-family:{code_font};font-weight:700;'
    f'border-bottom:1px solid {t["border"]}}}'
    # Code content with line wrapping
    f'.code-wrap table{{border-collapse:collapse;width:100%}}'
    f'.code-wrap td{{padding:0;vertical-align:top}}'
    f'.code-wrap pre{{margin:0;padding:14px;line-height:1.5;white-space:pre-wrap;'
    f'word-wrap:break-word;overflow-wrap:break-word;color:{t["pre_fg"]}}}'
    # Line numbers
    f'td.linenos{{width:40px;text-align:right;padding-right:10px !important;'
    f'color:{t["lineno_color"]};border-right:1px solid {t["border"]};font-size:12px}}'
    f'.linenodiv pre{{margin:0;padding:14px 0 14px 14px;line-height:1.5}}'
    f'td.code{{padding-left:10px !important}}'
    # Fallback line numbers
    f'.code-table{{border-collapse:collapse;width:100%}}'
    f'.ln{{width:40px;text-align:right;padding:0 10px 0 14px;color:{t["lineno_color"]};'
    f'border-right:1px solid {t["border"]};font-size:12px;vertical-align:top}}'
    f'.cd{{padding:0 14px 0 10px;color:{t["pre_fg"]};vertical-align:top;'
    f'white-space:pre-wrap;word-wrap:break-word;overflow-wrap:break-word}}'
    # Tables
    f'table{{border-collapse:collapse;margin:10px 0;font-size:13px;width:100%}}'
    f'th,td{{border:1px solid {t["border"]};padding:6px 10px;text-align:left}}'
    f'th{{background:{t["th_bg"]};font-weight:700;color:{t["th_fg"]}}}'
    f'tr:nth-child(even) td{{background:{t["tr_even"]}}}'
    # Lists, HR, Links, Blockquotes
    'ul,ol{padding-left:20px;margin:5px 0}li{margin:3px 0}'
    f'hr{{border:none;border-top:1px solid {t["hr"]};margin:14px 0}}'
    f'a{{color:{t["link"]};text-decoration:none}}'
    f'blockquote{{border-left:4px solid {t["bq_border"]};padding:8px 16px;margin:10px 0;'
    f'color:{t["bq_fg"]};background:{t["bq_bg"]}}}'
    # KaTeX
    '.katex-block{text-align:center;margin:12px 0;max-width:100%;overflow:hidden}'
    '.katex{font-size:1em}'
    # Mermaid
    '.mermaid-block{text-align:center;margin:12px 0}'
    '.mermaid-block svg{max-width:100%;height:auto}'
)

html_doc = (
    f'<!DOCTYPE html><html><head><meta charset=utf-8>'
    f'<style>{css}</style>'
    f'</head><body>{html_body}</body></html>'
)

# ── Write temp HTML ──
ts = time.strftime('%Y%m%d_%H%M%S')
src_hash = hashlib.md5(input_file.encode()).hexdigest()[:8]
tmp_html = f'/tmp/md2img_{ts}_{src_hash}.html'

with open(tmp_html, 'w') as f:
    f.write(html_doc)

# ── Render (3x zoom for sharper text) ──
try:
    r = subprocess.run(
        ['timeout', '30', 'wkhtmltoimage', '--format', 'jpg', '--quality', '100',
         '--zoom', '3', '--width', '750', '--disable-javascript', tmp_html, output_file],
        capture_output=True, text=True, timeout=35
    )
    if r.returncode != 0:
        err = r.stderr.strip() or 'unknown error'
        print(f'ERROR: wkhtmltoimage failed (exit {r.returncode}): {err}', file=sys.stderr)
        sys.exit(1)
except subprocess.TimeoutExpired:
    print('ERROR: wkhtmltoimage timed out (30s limit)', file=sys.stderr)
    sys.exit(1)
finally:
    if os.path.exists(tmp_html): os.remove(tmp_html)

# ── Page split (no cropping, split at clean boundaries) ──
from PIL import Image

img = Image.open(output_file)
w, h = img.size

PAGE_HEIGHTS = {'a4': 1123, 'a5': 794}
page_h = PAGE_HEIGHTS.get(pages_mode, 0)

if page_h > 0 and h > page_h:
    # Find split points: rows where ALL pixels match background color
    rgb = img.convert('RGB')
    bg_rgb = tuple(int(t['body_bg'].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    pixels = list(rgb.getdata())

    row_gaps = []
    for y in range(h):
        row_pixels = [pixels[y * w + x] for x in range(w)]
        # Row is "empty" if all pixels are within ±2 of background
        if all(abs(p[0]-bg_rgb[0]) <= 2 and abs(p[1]-bg_rgb[1]) <= 2 and abs(p[2]-bg_rgb[2]) <= 2 for p in row_pixels):
            row_gaps.append(y)

    # Build split points at logical boundaries near page height targets
    split_points = [0]
    target = page_h
    while target < h:
        # Find nearest gap row to target
        if row_gaps:
            best = min(row_gaps, key=lambda g: abs(g - target))
            if best > split_points[-1] + 100:
                split_points.append(best)
            else:
                split_points.append(min(target, h))
        else:
            split_points.append(min(target, h))
        target += page_h
    split_points.append(h)

    base, ext = os.path.splitext(output_file)
    page_files = []
    for i in range(len(split_points) - 1):
        y1, y2 = split_points[i], split_points[i + 1]
        if y2 - y1 < 50:
            continue
        page_img = img.crop((0, y1, w, y2))
        page_path = f'{base}_p{i+1:02d}{ext}'
        page_img.save(page_path, 'JPEG', quality=100)
        page_files.append(page_path)
    print(f'OK: {len(page_files)} pages: {", ".join(page_files)}', file=sys.stderr)
else:
    print(f'OK: {output_file} ({os.path.getsize(output_file)} bytes)', file=sys.stderr)
PYEOF
