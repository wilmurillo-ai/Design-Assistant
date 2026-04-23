---
name: wordpress-site-ops
description: "Give your OpenClaw WordPress superpowers! Manage your entire WordPress site, create plugins, handle SEO, WooCommerce, and more! Requires WORDPRESS_SITE_URL, WORDPRESS_USER, WORDPRESS_APPLICATION_PASSWORD (env or skills.entries). Strongly recommend gateway plugin wordpress-site-tools: https://github.com/realM1lF/openclaw-wordpress-tool (typed REST/WP-CLI). Skill id: wordpress-site-ops. Optional MU helper; see references/PRE_INSTALL_AND_TRUST.md."
metadata: {"openclaw":{"skillKey":"wordpress-site-ops","homepage":"https://github.com/realM1lF/openclaw-wordpress-tool","requires":{"anyBins":["wp","curl"],"env":["WORDPRESS_SITE_URL","WORDPRESS_USER","WORDPRESS_APPLICATION_PASSWORD"]}}}
---

# WordPress Expert

## For people (what am I getting?)

### What this skill is

- A **pack of instructions and checklists** for your OpenClaw agent so it can **work with a WordPress site you already have**—content, settings, media, plugins, themes, WooCommerce, Elementor, and development under `wp-content`.
- The agent reaches WordPress over **HTTPS (REST)** and, when you configure it, **WP-CLI** and **scoped file access** on the machine where the **OpenClaw gateway** runs.

### Strong recommendation: install the companion OpenClaw plugin

**You should install the companion plugin [`wordpress-site-tools`](https://github.com/realM1lF/openclaw-wordpress-tool) on the OpenClaw gateway host** (clone → `npm install` → `openclaw plugins install` → enable → allow tools → gateway restart). That plugin registers **typed, policy-aware tools** (`wordpress_rest_request`, `wordpress_wp_cli`, `wordpress_connection_check`, optional media upload and plugin file access). The skill is written to **prefer those tools** over hand-built `curl`/`exec`—they are **clearer, easier to audit, and easier to allowlist**.

- The skill **works without** that plugin only via documented **fallbacks** (`exec`, `curl`, browser)—more manual and easier to get wrong; use only if you consciously skip the plugin.
- **Before** `npm install` / enable: skim the **public source** on GitHub and read `{baseDir}/references/PRE_INSTALL_AND_TRUST.md` (staging, least privilege, secrets in config not chat).

Full steps: `{baseDir}/README.md`, `{baseDir}/references/CONNECTING.md`.

**OpenClaw surfaces this recommendation twice:** the YAML **`description`** is what the gateway includes in the **compact skill list** shown to the model; **`metadata.openclaw.homepage`** is the **Website** link in OpenClaw’s Skills UI ([docs](https://docs.openclaw.ai/skills/))—here it points at the **plugin repository** so users land on install/source without extra clicks.

### What you can expect

| You want… | What usually happens |
|-----------|----------------------|
| “Create a draft post”, “list plugins”, “upload an image” | Agent uses REST—with **`wordpress-site-tools`** installed, prefer **`wordpress_rest_request`** and related tools against **your** site URL. |
| “Run WP-CLI” or “edit my custom plugin files” | You need **`WORDPRESS_PATH`** and narrow **allowlists**; see `{baseDir}/references/CONNECTING.md` and `{baseDir}/references/WPCLI_PRESETS.md`. |
| “Full admin without limits” | **Out of scope for safe defaults.** Use staging, least-privilege users, and explicit user approval for destructive actions. |

### What you must configure (minimum)

OpenClaw needs these **environment variables** (host env or `skills.entries["wordpress-site-ops"].env`) so the skill is **eligible** and the agent can reach your site:

1. **`WORDPRESS_SITE_URL`** — site base URL (no trailing slash), HTTPS.  
2. **`WORDPRESS_USER`** — WordPress username the **application password** belongs to.  
3. **`WORDPRESS_APPLICATION_PASSWORD`** — from WP Admin → Users → Application passwords (not the login password).

Optional: **`WORDPRESS_PATH`** — directory on the **gateway** machine where `wp` works, if you use WP-CLI or `wordpress_plugin_files`.

Details: `{baseDir}/references/AUTH.md`, `{baseDir}/references/CONNECTING.md`.

### Typical flow (simple)

1. **Install this skill** (e.g. ClawHub or `skills/wordpress-site-ops` in the workspace).  
2. **Install and enable [`wordpress-site-tools`](https://github.com/realM1lF/openclaw-wordpress-tool) on the gateway** — this is the **default path we recommend**; see subsection above.  
3. **Set the three env vars** above; add the WordPress tools to **`tools.allow`** in `openclaw.json`.  
4. **`openclaw gateway restart`** after plugin, allowlist, or env changes.

Full walkthrough: `{baseDir}/README.md` and `{baseDir}/references/CONNECTING.md`.

### Before production or shared gateways

Read **`{baseDir}/references/PRE_INSTALL_AND_TRUST.md`**: review the companion plugin source, use staging, never paste secrets into chat, and know that **ClawHub text bundles may omit MU-helper `.php`**—copy PHP from a full git checkout if you need that helper.

---

## When the agent should use this skill

Use for **WordPress-related** work: content, media, plugins, themes, WooCommerce, Elementor, REST, and code under `wp-content`.

Also load **block/theme/performance** references when working on custom blocks, classic or block themes, template hierarchy, or performance and hardening:

- `{baseDir}/references/BLOCK_EDITOR.md`  
- `{baseDir}/references/THEME_AND_TEMPLATES.md`  
- `{baseDir}/references/PERFORMANCE_AND_SECURITY.md`  

Do **not** activate this skill for unrelated tasks.

---

## Rules for the assistant

### Data, secrets, and honesty

1. Use **fresh data** before writes (no stale assumptions).  
2. State facts only from the **latest tool output** or API response—do not invent site state.  
3. **Never** put secrets in replies or Git; see `{baseDir}/references/AUTH.md`.  
4. For shell commands that write: **no** raw user input without safe quoting/escaping.

### Prefer these tools (when listed in `tools.allow`)

5. **REST:** Prefer **`wordpress_rest_request`** (plugin **`wordpress-site-tools`**) over hand-built `curl`. If those tools are **missing**, **tell the user** installing/enabling **`wordpress-site-tools`** on the gateway is the recommended fix (`{baseDir}/README.md`, `{baseDir}/references/CONNECTING.md`); only then fall back to `{baseDir}/references/TOOLING.md`.  
6. **WP-CLI:** Prefer **`wordpress_wp_cli`** when allowed and **`WORDPRESS_PATH`** (or plugin config) is set—respect allowlist / **`wpCliProfile`**; else `exec` per TOOLING.  
7. **Connectivity:** After config changes or errors, prefer **`wordpress_connection_check`** when allowed (`{baseDir}/references/CONNECTING.md`).  
8. **Media:** Prefer **`wordpress_media_upload`** when allowed over manual `curl -F`.  
9. **Plugin files on disk:** Prefer **`wordpress_plugin_files`** (only under `wp-content/plugins/<slug>/`) when allowed—see `{baseDir}/references/NATIVE_VS_PLUGIN.md` and CONNECTING §3.8.  
10. **MU helper REST** (`openclaw-helper/v1/…`): only if MU plugin from `{baseDir}/bundled/mu-plugin/README.md` is on the **WordPress** site; for diagnostics/capabilities—see `{baseDir}/references/MU_HELPER.md`; not a substitute for WP-CLI or plugin file tools.

### OpenClaw platform behavior

11. **Native tools:** Do not pretend the WordPress plugin replaces shell, browser, or workspace—see `{baseDir}/references/NATIVE_VS_PLUGIN.md`.  
12. **Gateway restart:** New/changed plugin tools (`tools.allow`, `plugins.allow`, install/enable) usually need **`openclaw gateway restart`**. Do **not** insist **`/new`** is always required; use `/new` only if tools are still missing after restart and correct config. Skill env changes: try same session first; then restart—`{baseDir}/references/CONNECTING.md`.

### Development and UX

13. **Plugin/theme code:** Load `{baseDir}/references/DOMAIN.md` and `{baseDir}/references/PLUGIN_DEV_PLAYBOOK.md`; follow `{baseDir}/references/WORKFLOWS.md`. Blocks / themes / perf / Woo: `BLOCK_EDITOR`, `THEME_AND_TEMPLATES`, `PERFORMANCE_AND_SECURITY`, `WOO_ELEMENTOR`. Do not patch third-party plugins—addon approach in the playbook.  
14. **Non-technical users:** Plain language first; commands and JSON only when asked or briefly at the end.

---

## Reference library (progressive disclosure)

**Trust and setup**

- `{baseDir}/references/PRE_INSTALL_AND_TRUST.md` — trust, credentials, MU bundle vs full repo  
- `{baseDir}/references/CONNECTING.md` — topologies, `openclaw.json`, verification, gateway vs `/new`  
- `{baseDir}/references/AUTH.md` — URLs, application passwords, env  
- `{baseDir}/README.md` — human-oriented install and config (outside agent-only path)

**OpenClaw policy and tooling**

- `{baseDir}/references/OPENCLAW_INTEGRATION.md` — sandbox, allowlists, official links  
- `{baseDir}/references/NATIVE_VS_PLUGIN.md` — plugin tools vs exec / browser / workspace  
- `{baseDir}/references/TOOLING.md` — REST vs WP-CLI vs browser  
- `{baseDir}/references/WPCLI_PRESETS.md` — `wpCliProfile` / allowlist presets  
- `{baseDir}/references/DDEV.md` — local DDEV

**Optional MU helper (WordPress server)**

- `{baseDir}/bundled/mu-plugin/README.md` — deploy to `wp-content/mu-plugins/`  
- `{baseDir}/references/MU_HELPER.md` — when REST helper endpoints help

**Safety, workflow, expectations**

- `{baseDir}/references/SAFETY.md` — defaults, destructive actions, MUST NOT summary  
- `{baseDir}/references/WORKFLOWS.md` — Read, Plan, Write, Verify  
- `{baseDir}/references/USER_EXPECTATIONS.md` — product expectations  
- `{baseDir}/references/FOR_SITE_OWNERS.md` — non-technical readers  
- `{baseDir}/references/OVERVIEW.md` — full index

**WordPress development topics**

- `{baseDir}/references/DOMAIN.md` — blocks, plugins, CPT, pitfalls  
- `{baseDir}/references/PLUGIN_DEV_PLAYBOOK.md` — hooks, REST, security, layout  
- `{baseDir}/references/BLOCK_EDITOR.md` — blocks, `block.json`  
- `{baseDir}/references/THEME_AND_TEMPLATES.md` — themes, hierarchy, FSE  
- `{baseDir}/references/PERFORMANCE_AND_SECURITY.md` — performance and hardening  
- `{baseDir}/references/WOO_ELEMENTOR.md` — WooCommerce and Elementor

---

**Where work runs:** On the **OpenClaw gateway** (REST, shell, browser, workspace). The optional **MU helper** (if copied onto the WordPress server) only adds extra REST endpoints for diagnostics—see `{baseDir}/references/MU_HELPER.md`.
