---
name: ERNIE-Image
description: Generate/edit images with ERNIE-Image(Gemini 3 Pro Image). Use for image create/modify requests incl. edits. Supports text-to-image + image-to-image; 1K/2K/4K; use --input-image.
---

# ERNIE-ImageImage Generation & Editing

Generate new images or edit existing ones using Baidu's ERNIE-Image API.

## Usage

Run the script using absolute path (do NOT cd to skill directory first):

**Generate new image:**
```bash
python ~/.codex/skills/ERNIE-Image/scripts/generate_image.py --prompt "your image description" --filename "output-name.png" [--resolution 1024*1024|1366*768] [--api-key KEY]
```

**Edit existing image:**
```bash
python ~/.codex/skills/ERNIE-Image/scripts/generate_image.py --prompt "editing instructions" --filename "output-name.png" --input-image "path/to/input.png" [--resolution 1024*1024|1366*768] [--api-key KEY]
```

**Important:** Always run from the user's current working directory so images are saved where the user is working, not in the skill directory.

## Default Workflow (draft → iterate → final)

Goal: fast iteration without burning time on 4K until the prompt is correct.

- Draft (1K): quick feedback loop
  - `python  ~/.codex/skills/ERNIE-Image/scripts/generate_image.py --prompt "<draft prompt>" --filename "yyyy-mm-dd-hh-mm-ss-draft.png" --resolution 1024*1024`
- Iterate: adjust prompt in small diffs; keep filename new per run
  - If editing: keep the same `--input-image` for every iteration until you’re happy.
- Final (4K): only when prompt is locked
  - `python ~/.codex/skills/ERNIE-Image/scripts/generate_image.py --prompt "<final prompt>" --filename "yyyy-mm-dd-hh-mm-ss-final.png" --resolution 1366*768`

## Resolution Options

ERNIE-Image API supports three resolutions (uppercase K required):

- 1024x1024
- 1376x768
- 1264x848
- 1200x896
- 896x1200
- 848x1264
- 768x1376

Map user requests to API parameters:
- No mention of resolution → `1024x1024`
- "low resolution", 1024x1024

## API Key

The script checks for API key in this order:
1. `--api-key` argument (use if user provided key in chat)
2. `ERNIE-Image_API_KEY` environment variable

If neither is available, the script exits with an error message.

## Preflight + Common Failures (fast fixes)

- Preflight:
  - `test -n \"$ERNIE-Image_API_KEY\"` (or pass `--api-key`)
  - If editing: `test -f \"path/to/input.png\"`
  
- Common failures:
  - `Error: No API key provided.` → set `ERNIE-Image_API_KEY` or pass `--api-key`
  - `Error loading input image:` → wrong path / unreadable file; verify `--input-image` points to a real image
  - “quota/permission/403” style API errors → wrong key, no access, or quota exceeded; try a different key/account

## Filename Generation

Generate filenames with the pattern: `yyyy-mm-dd-hh-mm-ss-name.png`

**Format:** `{timestamp}-{descriptive-name}.png`
- Timestamp: Current date/time in format `yyyy-mm-dd-hh-mm-ss` (24-hour format)
- Name: Descriptive lowercase text with hyphens
- Keep the descriptive part concise (1-5 words typically)
- Use context from user's prompt or conversation
- If unclear, use random identifier (e.g., `x9k2`, `a7b3`)

Examples:
- Prompt "A serene Japanese garden" → `2025-11-23-14-23-05-japanese-garden.png`
- Prompt "sunset over mountains" → `2025-11-23-15-30-12-sunset-mountains.png`
- Prompt "create an image of a robot" → `2025-11-23-16-45-33-robot.png`
- Unclear context → `2025-11-23-17-12-48-x9k2.png`



## Prompt Handling

**For generation:** Pass user's image description as-is to `--prompt`. Only rework if clearly insufficient.

Preserve user's creative intent in both cases.

## Prompt Templates (high hit-rate)

Use templates when the user is vague or when edits must be precise.

- Generation template:
  - “Create an image of: <subject>. Style: <style>. Composition: <camera/shot>. Lighting: <lighting>. Background: <background>. Color palette: <palette>. Avoid: <list>.”

  

## Output

- Saves PNG to current directory (or specified path if filename includes directory)
- Script outputs the full path to the generated image
- **Do not read the image back** - just inform the user of the saved path

## Examples

**Generate new image:**
```bash
python ~/.codex/skills/ERNIE-Image/scripts/generate_image.py --prompt "A serene Japanese garden with cherry blossoms" --filename "2025-11-23-14-23-05-japanese-garden.png" --resolution 1024*1024
```

