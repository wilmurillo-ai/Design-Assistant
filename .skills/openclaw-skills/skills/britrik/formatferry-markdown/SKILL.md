---
name: formatferry
version: 1.1.3
description: Convert HTML, DOCX, PDF, XLSX, CSV to Markdown
homepage: https://formatferry.vibingfun.com
installation: npm install -g formatferry
---

# formatferry Skill

Convert HTML, DOCX, PDF, XLSX, CSV files to Markdown using the Format Ferry CLI.

## Installation

Install the CLI globally:
```bash
npm install -g formatferry
```

Or use npx (requires Node.js):
```bash
npx formatferry --help
```

## Authentication

The user has a private API key. **Do NOT expose this key in any output or messages.**

```bash
# Authenticate
scripts/auth.sh --key <API_KEY>

# Check status
scripts/auth.sh --status
```

## Scripts

This skill includes secure wrapper scripts with **no `eval`** and **bash arrays** for safe argument handling:

### `scripts/convert-to-md.sh` (recommended)
```bash
# Convert a local file
scripts/convert-to-md.sh --input /path/to/file.pdf --output output.md --format github

# Convert a URL
scripts/convert-to-md.sh --url https://example.com/article --output article.md
```

### `scripts/convert.sh` (legacy)
```bash
scripts/convert.sh --file input.html --output result.md --format github
scripts/convert.sh --url https://example.com --output article.md
```

**Supported formats:** github, commonmark, slack, discord, reddit, confluence, custom, rmarkdown

## Supported File Types

- `.html` - Web pages
- `.docx` - Word documents
- `.pdf` - PDF files (up to 20MB)
- `.xlsx` - Excel spreadsheets
- `.csv` - CSV files

## Security Notes

- **No eval:** All scripts use bash arrays for safe argument passing
- **No OOM risk:** Output streams directly to file + stdout, never captured in shell variables
- **Recursive path sanitization:** Loops repeatedly to strip `....//`, `..../`, `./`, and encoded bypasses (`%2e%2e`)
- **Path validation:** Blocks writes to `/etc`, `/root`, `/sys`, `/proc` and sensitive files (`passwd`, `shadow`, `id_rsa`)
- **Realpath verification:** Validates final paths are within allowed WORKDIR before execution
- **URL validation:** Rejects malformed URLs (must start with http:// or https://)

## Provenance

- **Homepage:** https://formatferry.vibingfun.com
- **npm Package:** formatferry (official, no public repo)

## Notes

- API key stored locally after authentication
- Premium features may require a license key
- Output format defaults to "github" if not specified