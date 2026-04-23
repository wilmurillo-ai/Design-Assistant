# WooCommerce and Elementor

Notes for OpenClaw with **REST**, **WP-CLI**, or **browser**—without dedicated in-WordPress agent tools.

## WooCommerce

- Block-based cart/checkout behavior: see also [DOMAIN.md](DOMAIN.md) (block cart note) and [BLOCK_EDITOR.md](BLOCK_EDITOR.md) when touching Woo blocks.
- Product/order/coupon logic via **WooCommerce APIs** (REST `wc/v3` where possible) instead of ad-hoc PHP in third-party plugins.
- **OpenClaw:** prefer `wordpress_rest_request` with path under `wc/v3/...`; WP-CLI only with appropriate **`wpCliProfile`** ([WPCLI_PRESETS.md](WPCLI_PRESETS.md)). Do not run arbitrary PHP on the server instead of shop CRUD.
- **Variable products (order):** Create product (`variable`) → set attributes → create variations → verify with GET/list (REST or allowed WP-CLI).
- **Custom Woo-related plugin:** In plugin header `Requires Plugins: woocommerce`; admin notice if Woo is missing. **HPOS:** declare compatibility with custom order tables per [Woo docs](https://woocommerce.com/document/high-performance-order-storage/) when touching order plugins.
- No “shortcut” hacks that bypass shop data—CRUD through the official layer.

If REST is not enough: targeted **admin UI** (browser) or a **small custom plugin**—do not edit third-party plugin files. Scaffold hints: [PLUGIN_DEV_PLAYBOOK.md](PLUGIN_DEV_PLAYBOOK.md).

## Elementor

- Theme/layout integration: [THEME_AND_TEMPLATES.md](THEME_AND_TEMPLATES.md) for child themes and template overrides.
- **Custom Elementor-related plugin:** `Requires Plugins: elementor` in header; minimum version e.g. with `defined('ELEMENTOR_VERSION')` and `version_compare`; admin notice if Elementor is missing.
- **Existing** Elementor pages: understand structure, then change deliberately (editor, exports, or site-specific APIs—depending on access).
- **No professional design from scratch:** Point users to template kits / designers; you adjust content/structure.
- Use real **Elementor widgets**, not raw HTML in the text widget as a widget substitute.
- Before layout changes: read current structure/page layout (stale-data protection).
- Prefer new Elementor pages as **drafts**.
- Container model (nested containers) instead of legacy section/column where applicable.
- On tool/API errors: **no** silent HTML fallback—report errors.
- **Check frontend:** After visible changes load the affected URL (browser or allowed HTTP)—not only “code written”.

## Limits

No specialized **in-WordPress** helpers (e.g. dedicated admin tools) here. Decide per [TOOLING.md](TOOLING.md) whether REST, WP-CLI, browser, or a **small custom plugin** on the site is needed.

Future improvement: dedicated OpenClaw tools (track progress in maintainer source repo).
