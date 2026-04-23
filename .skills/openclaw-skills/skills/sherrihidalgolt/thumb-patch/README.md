# YouTube Thumbnail Generator

Generate eye-catching AI-powered YouTube thumbnails from a text description. Powered by the Neta talesofai API — get back a direct image URL in seconds.

## Install

**Via npx skills:**
```bash
npx skills add SherriHidalgolt/thumbnail-gen-skill
```

**Via ClawHub:**
```bash
clawhub install thumbnail-gen-skill
```

## Usage

```bash
# Basic — uses default prompt
node thumbnailgen.js

# Custom prompt
node thumbnailgen.js "gaming channel thumbnail, neon colors, dramatic lighting"

# With size option
node thumbnailgen.js "tech review thumbnail" --size landscape

# Pass token inline
node thumbnailgen.js "cooking channel, vibrant food" --token YOUR_TOKEN_HERE
```

## Options

| Option    | Values                                      | Default       | Description              |
|-----------|---------------------------------------------|---------------|--------------------------|
| `--size`  | `square`, `portrait`, `landscape`, `tall`   | `landscape`   | Output image dimensions  |
| `--token` | string                                      | _(see below)_ | Neta API token           |

### Size dimensions

| Size        | Width × Height |
|-------------|----------------|
| `square`    | 1024 × 1024    |
| `portrait`  | 832 × 1216     |
| `landscape` | 1216 × 832     |
| `tall`      | 704 × 1408     |

## Token Setup

The script resolves your Neta API token in this order:

1. `--token YOUR_TOKEN` CLI flag
2. `NETA_TOKEN` environment variable
3. `~/.openclaw/workspace/.env` file (line matching `NETA_TOKEN=...`)
4. `~/developer/clawhouse/.env` file (line matching `NETA_TOKEN=...`)

**Recommended — add to your shell profile:**
```bash
export NETA_TOKEN=your_token_here
```

**Or add to `~/.openclaw/workspace/.env`:**
```
NETA_TOKEN=your_token_here
```

## Output

The script prints a single image URL to stdout on success:
```
https://cdn.talesofai.cn/...your-generated-thumbnail.png
```

---

Built with Claude Code · Powered by Neta
