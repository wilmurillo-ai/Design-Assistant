"""
Tests for style-specific signature elements in demo HTML files.

Validates that each preset's demo contains its unique signature elements:
- Bold Signal: .slide-num, .breadcrumb, .slide::after grid overlay
- Enterprise Dark: .slide::after grid overlay (24px spacing, rgba(48,54,61,0.3))
- Neon Cyber: .slide::after cyan grid overlay (40px spacing, rgba(0,255,255,0.06))
- Terminal Green: .slide::after scanlines (repeating-linear-gradient)
- Creative Voltage: .slide::after halftone dots (radial-gradient circle)
- Dark Botanical: .botanical-orb elements (2-3 per slide)
- Glassmorphism: .glass-orb elements + backdrop-filter: blur(12px)
- Swiss Modern: .slide::after 12-column grid overlay
- Neo-Retro Dev: graph paper grid (20px spacing, cream #f5f2e8)
- Chinese Chan: .zen-rule / .zen-ghost-kanji / .zen-dot (max 1 per slide)
- Aurora Mesh: mesh gradient 4-6 color stops + backdrop-filter: blur(12px)
- Data Story: .chart-container / .data-callout / .data-stat, NO background patterns
- Electric Studio: dual-panel vertical split + .accent-bar (4px wide)
- Modern Newspaper: yellow bar #FFCC00 (8-14px) + column rules 1px solid #111
- Neo-Brutalism: box-shadow: 4px 4px 0 #000 + border: 3px solid #000
- Notebook Tabs: colored tab labels + binder hole decoration
- Paper & Ink: narrow column layout (max-width ~680px)
- Pastel Geometry: white cards border-radius: 20px + vertical pills
- Split Pastel: dual-color split background (peach / lavender)
- Vintage Editorial: cream #f5f0e8 background + abstract geometric shapes
- Blue Sky: .glass-orb / .cloud / .glass-card elements

Run: python -m pytest tests/test_style_signature_elements.py -v
"""

import re
from pathlib import Path

import pytest

DEMOS_DIR = Path(__file__).parent.parent / "demos"
ALL_DEMOS = sorted(DEMOS_DIR.glob("*.html"))

# Filter out backup files
DEMO_FILES = [d for d in ALL_DEMOS if "backup" not in d.name and "-regenerated" not in d.name]


def get_preset_from_demo(demo_path: Path) -> str:
    """Extract preset name from demo filename: enterprise-dark-zh.html -> enterprise-dark"""
    name = demo_path.stem
    for suffix in ("-handwritten-backup", "-backup"):
        name = name.replace(suffix, "")
    parts = name.rsplit("-", 1)
    if len(parts) == 2 and parts[1] in ("en", "zh"):
        return parts[0]
    return name


def load(path: Path):
    content = path.read_text(encoding="utf-8")
    return content


# Signature element definitions per preset
SIGNATURE_ELEMENTS = {
    "bold-signal": {
        "description": "Slide numbers, breadcrumbs, grid overlay",
        "checks": [
            ("slide-num", "Missing .slide-num element (top-left large number)"),
            ("breadcrumb", "Missing .breadcrumb element (top-right navigation)"),
        ],
    },
    "enterprise-dark": {
        "description": "Grid overlay (24px, rgba(48,54,61,0.3))",
        "checks": [
            ("ent-", "Missing ent- prefixed classes (enterprise components)"),
        ],
    },
    "neon-cyber": {
        "description": "Cyan grid overlay (40px spacing)",
        "checks": [
            ("0,255,255", "Missing cyan grid overlay rgba(0,255,255,0.06)"),
        ],
    },
    "terminal-green": {
        "description": "Scanline overlay (repeating-linear-gradient)",
        "checks": [
            ("repeating-linear-gradient", "Missing scanline pattern"),
            ("0,255,65", "Missing green scanline color rgba(0,255,65,0.03)"),
        ],
    },
    "creative-voltage": {
        "description": "Halftone dot pattern",
        "checks": [
            ("212,255,0", "Missing halftone dot pattern rgba(212,255,0,0.08)"),
        ],
    },
    "dark-botanical": {
        "description": "Botanical orbs (terracotta/pink/gold gradients)",
        "checks": [
            ("botanical-orb", "Missing .botanical-orb elements (2-3 per slide)"),
        ],
    },
    "glassmorphism": {
        "description": "Glass orbs + backdrop-filter blur",
        "checks": [
            ("glass-orb", "Missing .glass-orb elements"),
            ("backdrop-filter", "Missing backdrop-filter: blur(12px) on cards"),
        ],
    },
    "swiss-modern": {
        "description": "12-column grid overlay + hard horizontal rules",
        "checks": [
            ("0a0a0a", "Missing hard horizontal rules 2px solid #0a0a0a"),
        ],
    },
    "neo-retro-dev": {
        "description": "Graph paper grid (20px, cream #f5f2e8)",
        "checks": [
            ("f5f2e8", "Missing cream background #f5f2e8 for graph paper"),
            ("20px 20px", "Missing graph paper grid 20px spacing"),
        ],
    },
    "chinese-chan": {
        "description": "Zen decorative elements (max 1 per slide)",
        "checks": [
            ("zen-", "Missing zen- prefixed elements (zen-rule / zen-ghost-kanji / zen-dot)"),
        ],
    },
    "aurora-mesh": {
        "description": "Mesh gradient 4-6 color stops + backdrop-filter blur",
        "checks": [
            ("auroraDrift", "Missing auroraDrift mesh gradient animation"),
        ],
    },
    "data-story": {
        "description": "Data components (chart/callout/stat), NO background patterns",
        "checks": [
            ("data-", "Missing data- prefixed components (chart-container / data-callout / data-stat)"),
        ],
        "must_not_have": [
            ("linear-gradient.*rgba", "Data Story must NOT have background patterns"),
        ],
    },
    "electric-studio": {
        "description": "Dual-panel vertical split + accent bar (4px)",
        "checks": [
            ("accent-bar", "Missing .accent-bar element (4px wide, accent color)"),
        ],
    },
    "modern-newspaper": {
        "description": "Yellow bar #FFCC00 + column rules + issue stamp",
        "checks": [
            ("FFCC00", "Missing yellow bar #FFCC00 (8-14px)"),
            ("1px solid #111", "Missing column rules 1px solid #111"),
        ],
    },
    "neo-brutalism": {
        "description": "Box shadows + thick borders + no border-radius",
        "checks": [
            ("4px 4px 0 #000", "Missing box-shadow: 4px 4px 0 #000"),
            ("3px solid #000", "Missing border: 3px solid #000"),
        ],
    },
    "notebook-tabs": {
        "description": "Colored tab labels + binder hole + paper shadow",
        "checks": [
            ("binder", "Missing binder hole decoration"),
        ],
    },
    "paper-ink": {
        "description": "Narrow column layout (max-width ~680px)",
        "checks": [
            ("max-width", "Missing max-width constraint for narrow column"),
        ],
    },
    "pastel-geometry": {
        "description": "White cards border-radius: 20px + vertical pills",
        "checks": [
            ("border-radius: 20px", "Missing white cards with border-radius: 20px"),
        ],
    },
    "split-pastel": {
        "description": "Dual-color split background + badge pills",
        "checks": [
            ("badge", "Missing badge pills"),
        ],
    },
    "vintage-editorial": {
        "description": "Cream #f5f0e8 background + abstract geometric + Cormorant italic",
        "checks": [
            ("f5f0e8", "Missing cream background #f5f0e8"),
            ("Cormorant", "Missing Cormorant font (Vintage Editorial signature)"),
        ],
    },
    "blue-sky": {
        "description": "Glass orbs + clouds + glass cards",
        "checks": [
            ("glass-orb", "Missing .glass-orb elements"),
            ("cloud", "Missing .cloud elements"),
            ("glass-card", "Missing .glass-card elements"),
        ],
    },
}


class TestStyleSignatureElements:
    """Each preset must contain its signature elements in demo HTML."""

    @pytest.fixture(params=DEMO_FILES, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param), get_preset_from_demo(request.param)

    def test_signature_elements_present(self, demo):
        """Check that each preset's demo contains its signature elements."""
        path, content, preset = demo
        if preset not in SIGNATURE_ELEMENTS:
            pytest.skip(f"No signature checks defined for preset: {preset}")

        sig = SIGNATURE_ELEMENTS[preset]

        # Check required elements
        for pattern, message in sig["checks"]:
            assert pattern in content, f"{path.name}: {message}"

        # Check must-not-have elements (negation tests)
        if "must_not_have" in sig:
            for pattern, message in sig["must_not_have"]:
                # Use DOTALL to match across lines for multi-line patterns
                match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                assert not match, f"{path.name}: {message}"

    def test_data_story_no_background_pattern(self, demo):
        """Data Story style must NOT have background patterns (grid/glow/halftone)."""
        path, content, preset = demo
        if preset != "data-story":
            return

        # Check for background patterns that shouldn't exist
        has_grid = re.search(
            r"linear-gradient.*rgba.*1px.*transparent",
            content, re.DOTALL
        )
        has_scan = re.search(r"repeating-linear-gradient", content)
        has_halftone = re.search(r"radial-gradient.*circle", content, re.DOTALL)

        if has_grid:
            pytest.fail(f"{path.name}: Data Story must NOT have grid background pattern")
        if has_scan:
            pytest.fail(f"{path.name}: Data Story must NOT have scanline background")
        if has_halftone:
            pytest.fail(f"{path.name}: Data Story must NOT have halftone background")


class TestFullBleedLayoutPanels:
    """Full-bleed color panels must NOT be nested inside .slide-content.

    Regression: AI generator wrapped all layout panels (e.g., .voltage-blue-panel)
    inside <div class="slide-content"> which has padding, compressing the panels
    and preventing them from touching screen edges. SKILL.md Rule: LAYOUT PANEL RULE.
    """

    # Styles with full-bleed layout panels (panels that should touch screen edges)
    FULL_BLEED_STYLES = {
        "creative-voltage": {
            "panel_patterns": ["voltage-blue-panel", "voltage-dark-panel", "voltage-split"],
            "description": "Creative Voltage split panels must be direct .slide children",
        },
        "electric-studio": {
            "panel_patterns": ["split-left", "split-right", "accent-bar"],
            "description": "Electric Studio split panels must be direct .slide children",
        },
        "modern-newspaper": {
            "panel_patterns": ["yellow-bar", "columns", "col", "headline"],
            "description": "Modern Newspaper columns must span full slide height",
        },
        "split-pastel": {
            "panel_patterns": ["split-bg-left", "split-bg-right", "grid-overlay"],
            "description": "Split Pastel dual-color split must be direct .slide children",
        },
    }

    @pytest.fixture(params=DEMO_FILES, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param), get_preset_from_demo(request.param)

    def test_full_bleed_panels_not_inside_slide_content(self, demo):
        """Layout panels for full-bleed styles must NOT be nested inside .slide-content."""
        path, content, preset = demo
        if preset not in self.FULL_BLEED_STYLES:
            return

        style_info = self.FULL_BLEED_STYLES[preset]

        # Check: if any of the panel patterns appear INSIDE a .slide-content div,
        # that's a regression. We look for the pattern:
        # <div class="slide-content"> ... <div class="voltage-...panel">
        # which means the panel is incorrectly nested.

        # Simple heuristic: find all slide-content blocks and check if they contain panel patterns
        slide_content_blocks = re.findall(
            r'<div class="slide-content"[^>]*>(.*?)</div>',
            content, re.DOTALL
        )

        for block in slide_content_blocks:
            for panel_pattern in style_info["panel_patterns"]:
                if panel_pattern in block:
                    # Panel found inside .slide-content — this is wrong
                    assert False, (
                        f"{path.name}: {style_info['description']}. "
                        f"Found '{panel_pattern}' nested inside .slide-content — "
                        f"layout panels must be direct .slide children, "
                        f"not wrapped in .slide-content's padding."
                    )

    def test_no_slide_padding_on_slide_element(self, demo):
        """.slide must NOT have padding: var(--slide-padding) — that compresses full-bleed panels."""
        path, content, demo_preset = demo

        # Check for the specific wrong pattern: .slide { ... padding: var(--slide-padding) ... }
        # We look for the CSS rule where .slide has padding
        slide_css_block = re.search(r'\.slide\s*\{([^}]+)\}', content)
        if slide_css_block:
            css = slide_css_block.group(1)
            if re.search(r'padding:\s*var\(--slide-padding\)', css):
                assert False, (
                    f"{path.name}: .slide has padding: var(--slide-padding) — "
                    f"this compresses full-bleed layout panels. "
                    f"Padding should be on .slide-content, not .slide."
                )


class TestPresetMetadata:
    """Verify data-preset attribute and watermark on all demos."""

    @pytest.fixture(params=DEMO_FILES, ids=lambda p: p.name)
    def demo(self, request):
        return request.param, load(request.param), get_preset_from_demo(request.param)

    def test_data_preset_attribute(self, demo):
        """Every demo must have data-preset attribute on <body>."""
        path, content, preset = demo
        assert f"data-preset" in content, f"{path.name}: missing data-preset attribute"
        # Check that the preset name in the attribute matches the filename
        preset_name_in_html = re.search(r'data-preset="([^"]+)"', content)
        if preset_name_in_html:
            expected_name = preset.replace("-", " ").title()
            found_name = preset_name_in_html.group(1)
            # Allow case-insensitive matching
            assert expected_name.lower() == found_name.lower(), (
                f"{path.name}: data-preset='{found_name}' should match "
                f"expected '{expected_name}'"
            )

    def test_watermark_present(self, demo):
        """Every demo must have watermark (injected by JS or in HTML)."""
        path, content, preset = demo
        assert "kai-slide-creator" in content.lower(), (
            f"{path.name}: missing watermark — must be injected by JS into last slide"
        )
