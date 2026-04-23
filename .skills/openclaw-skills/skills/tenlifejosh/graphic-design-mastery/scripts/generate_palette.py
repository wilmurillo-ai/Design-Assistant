#!/usr/bin/env python3
"""
Color Palette Generator for the Graphic Design Mastery Skill System.

Generates complete, production-ready color palettes from a single brand color input.
Outputs CSS custom properties, hex values, and contrast ratio verification.

Usage:
    python generate_palette.py "#3b82f6"
    python generate_palette.py "#3b82f6" --name "ocean" --format css
    python generate_palette.py "#3b82f6" --format json
    python generate_palette.py "#3b82f6" --dark-mode
"""

import sys
import json
import math
import colorsys


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple (0-255)."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """Convert RGB (0-255) to hex string."""
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def rgb_to_hsl(r, g, b):
    """Convert RGB (0-255) to HSL (h: 0-360, s: 0-100, l: 0-100)."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return round(h * 360, 1), round(s * 100, 1), round(l * 100, 1)


def hsl_to_rgb(h, s, l):
    """Convert HSL (h: 0-360, s: 0-100, l: 0-100) to RGB (0-255)."""
    h, s, l = h / 360.0, s / 100.0, l / 100.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return round(r * 255), round(g * 255), round(b * 255)


def relative_luminance(r, g, b):
    """Calculate relative luminance per WCAG 2.1."""
    def linearize(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(color1_rgb, color2_rgb):
    """Calculate WCAG contrast ratio between two RGB colors."""
    l1 = relative_luminance(*color1_rgb)
    l2 = relative_luminance(*color2_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def generate_scale(base_hex, name="brand"):
    """
    Generate a 10-step color scale from a base color.
    Returns dict of {50, 100, 200, ..., 900, 950} -> hex.
    """
    r, g, b = hex_to_rgb(base_hex)
    h, s, l = rgb_to_hsl(r, g, b)

    # Define lightness targets for each step
    # Adjusted based on the base color's position
    lightness_map = {
        50:  max(95, l + (100 - l) * 0.92),
        100: max(90, l + (100 - l) * 0.82),
        200: max(82, l + (100 - l) * 0.65),
        300: max(70, l + (100 - l) * 0.45),
        400: max(58, l + (100 - l) * 0.22),
        500: l,  # Base
        600: l * 0.82,
        700: l * 0.65,
        800: l * 0.48,
        900: l * 0.35,
        950: l * 0.22,
    }

    # Adjust saturation: increase slightly for darks, decrease for lights
    scale = {}
    for step, target_l in lightness_map.items():
        target_l = max(2, min(98, target_l))
        if step < 500:
            adj_s = max(0, s * (0.6 + (500 - step) / 500 * 0.1))
        elif step > 500:
            adj_s = min(100, s * (1.0 + (step - 500) / 500 * 0.15))
        else:
            adj_s = s

        # Slight hue shift for richness (warm darks, cool lights)
        hue_shift = (step - 500) / 500 * 2
        adj_h = (h + hue_shift) % 360

        rgb = hsl_to_rgb(adj_h, adj_s, target_l)
        scale[step] = rgb_to_hex(*rgb)

    return scale


def generate_neutral_palette(base_hex):
    """Generate a neutral palette tinted with the base color's hue."""
    r, g, b = hex_to_rgb(base_hex)
    h, s, _ = rgb_to_hsl(r, g, b)

    # Very low saturation neutrals, tinted with brand hue
    tint_s = min(12, s * 0.15)

    neutrals = {
        50:  rgb_to_hex(*hsl_to_rgb(h, tint_s, 98)),
        100: rgb_to_hex(*hsl_to_rgb(h, tint_s, 96)),
        200: rgb_to_hex(*hsl_to_rgb(h, tint_s, 91)),
        300: rgb_to_hex(*hsl_to_rgb(h, tint_s, 83)),
        400: rgb_to_hex(*hsl_to_rgb(h, tint_s, 64)),
        500: rgb_to_hex(*hsl_to_rgb(h, tint_s, 46)),
        600: rgb_to_hex(*hsl_to_rgb(h, tint_s * 1.2, 37)),
        700: rgb_to_hex(*hsl_to_rgb(h, tint_s * 1.3, 27)),
        800: rgb_to_hex(*hsl_to_rgb(h, tint_s * 1.5, 18)),
        900: rgb_to_hex(*hsl_to_rgb(h, tint_s * 1.8, 11)),
        950: rgb_to_hex(*hsl_to_rgb(h, tint_s * 2.0, 6)),
    }
    return neutrals


def generate_semantic_colors():
    """Generate semantic status colors."""
    return {
        "success": {
            "light": "#d1fae5", "default": "#059669", "dark": "#065f46"
        },
        "warning": {
            "light": "#fef3c7", "default": "#d97706", "dark": "#92400e"
        },
        "error": {
            "light": "#fee2e2", "default": "#dc2626", "dark": "#991b1b"
        },
        "info": {
            "light": "#dbeafe", "default": "#2563eb", "dark": "#1e40af"
        }
    }


def format_css(brand_scale, neutral_scale, semantic, name="brand"):
    """Format the palette as CSS custom properties."""
    lines = [":root {"]
    lines.append(f"  /* {name.title()} Brand Scale */")
    for step, color in sorted(brand_scale.items()):
        lines.append(f"  --{name}-{step}: {color};")

    lines.append(f"\n  /* Neutral Scale (tinted with {name}) */")
    for step, color in sorted(neutral_scale.items()):
        lines.append(f"  --neutral-{step}: {color};")

    lines.append(f"\n  /* Semantic Alias Tokens */")
    lines.append(f"  --color-bg-primary: var(--neutral-50);")
    lines.append(f"  --color-bg-secondary: var(--neutral-100);")
    lines.append(f"  --color-bg-tertiary: var(--neutral-200);")
    lines.append(f"  --color-bg-inverse: var(--neutral-900);")
    lines.append(f"  --color-text-primary: var(--neutral-900);")
    lines.append(f"  --color-text-secondary: var(--neutral-600);")
    lines.append(f"  --color-text-tertiary: var(--neutral-400);")
    lines.append(f"  --color-text-inverse: var(--neutral-50);")
    lines.append(f"  --color-text-brand: var(--{name}-600);")
    lines.append(f"  --color-border-default: var(--neutral-200);")
    lines.append(f"  --color-border-strong: var(--neutral-300);")
    lines.append(f"  --color-action-primary: var(--{name}-600);")
    lines.append(f"  --color-action-primary-hover: var(--{name}-700);")
    lines.append(f"  --color-action-primary-light: var(--{name}-50);")

    lines.append(f"\n  /* Semantic Status Colors */")
    for status, shades in semantic.items():
        for shade_name, color in shades.items():
            lines.append(f"  --color-{status}-{shade_name}: {color};")

    lines.append("}")

    # Dark mode
    lines.append(f"\n[data-theme='dark'] {{")
    lines.append(f"  --color-bg-primary: var(--neutral-900);")
    lines.append(f"  --color-bg-secondary: var(--neutral-800);")
    lines.append(f"  --color-bg-tertiary: var(--neutral-700);")
    lines.append(f"  --color-bg-inverse: var(--neutral-50);")
    lines.append(f"  --color-text-primary: var(--neutral-50);")
    lines.append(f"  --color-text-secondary: var(--neutral-400);")
    lines.append(f"  --color-text-tertiary: var(--neutral-500);")
    lines.append(f"  --color-text-inverse: var(--neutral-900);")
    lines.append(f"  --color-text-brand: var(--{name}-400);")
    lines.append(f"  --color-border-default: var(--neutral-700);")
    lines.append(f"  --color-border-strong: var(--neutral-600);")
    lines.append(f"  --color-action-primary: var(--{name}-500);")
    lines.append(f"  --color-action-primary-hover: var(--{name}-400);")
    lines.append(f"  --color-action-primary-light: var(--{name}-950);")
    lines.append("}")

    return "\n".join(lines)


def format_json(brand_scale, neutral_scale, semantic, name="brand"):
    """Format the palette as JSON."""
    return json.dumps({
        name: brand_scale,
        "neutral": neutral_scale,
        "semantic": semantic,
    }, indent=2)


def print_contrast_report(brand_scale, neutral_scale):
    """Print contrast ratio report for key combinations."""
    white = (255, 255, 255)
    black_ish = hex_to_rgb(neutral_scale[900])

    print("\n=== CONTRAST RATIO REPORT ===")
    print(f"{'Combination':<40} {'Ratio':>8} {'AA':>5} {'AAA':>5}")
    print("-" * 62)

    for step, hex_color in sorted(brand_scale.items()):
        rgb = hex_to_rgb(hex_color)

        # On white
        cr_white = contrast_ratio(rgb, white)
        aa = "✓" if cr_white >= 4.5 else ("Lg" if cr_white >= 3 else "✗")
        aaa = "✓" if cr_white >= 7 else "✗"
        print(f"  brand-{step} ({hex_color}) on white    {cr_white:>8} {aa:>5} {aaa:>5}")

        # On dark
        cr_dark = contrast_ratio(rgb, black_ish)
        aa = "✓" if cr_dark >= 4.5 else ("Lg" if cr_dark >= 3 else "✗")
        aaa = "✓" if cr_dark >= 7 else "✗"
        print(f"  brand-{step} ({hex_color}) on dark     {cr_dark:>8} {aa:>5} {aaa:>5}")

    print("\nAA = 4.5:1 (normal text), Lg = 3:1 (large text only), AAA = 7:1")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_palette.py <hex_color> [--name NAME] [--format css|json]")
        print("Example: python generate_palette.py '#3b82f6' --name ocean --format css")
        sys.exit(1)

    base_color = sys.argv[1]
    name = "brand"
    fmt = "css"

    for i, arg in enumerate(sys.argv):
        if arg == "--name" and i + 1 < len(sys.argv):
            name = sys.argv[i + 1]
        if arg == "--format" and i + 1 < len(sys.argv):
            fmt = sys.argv[i + 1]

    brand_scale = generate_scale(base_color, name)
    neutral_scale = generate_neutral_palette(base_color)
    semantic = generate_semantic_colors()

    if fmt == "json":
        print(format_json(brand_scale, neutral_scale, semantic, name))
    else:
        print(format_css(brand_scale, neutral_scale, semantic, name))

    print_contrast_report(brand_scale, neutral_scale)
