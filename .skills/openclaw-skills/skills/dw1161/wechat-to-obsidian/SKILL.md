---
name: wechat-to-obsidian
version: 1.0.0
description: Clip WeChat public articles (mp.weixin.qq.com) to Obsidian vault — headless browser, full text + images in original order, no broken links. 将微信公众号文章无损剪藏到 Obsidian，图文顺序保留，图片自动下载到 attachments 目录。
metadata:
  openclaw:
    requires:
      bins:
        - agent-browser
        - curl
    install:
      - id: agent-browser
        kind: node
        package: agent-browser
        bins: [agent-browser]
        label: "Install agent-browser (headless browser CLI)"
---

# WeChat → Obsidian Clipper

Clips a WeChat public article to your Obsidian vault:

- **Headless** — uses `agent-browser` (no visible window, fast)
- **Full fidelity** — extracts text and images in their original DOM order
- **Images downloaded** — saves to `attachments/` next to the note using `curl` with correct `Referer` header (required to avoid 403)
- **Clean Markdown** — Obsidian `![[filename]]` embed syntax

## Requirements

- `agent-browser` ≥ 0.17: `npm install -g agent-browser && agent-browser install`
- `curl` (pre-installed on macOS/Linux)
- An Obsidian vault accessible on the local filesystem

## Trigger

User sends a `mp.weixin.qq.com` link and says something like:
- "存 Obsidian" / "剪藏" / "帮我存"
- "save to Obsidian" / "clip this" / "save article"

## Standard Workflow

### Step 1 — Open page (headless)

```bash
agent-browser open "<wechat_url>"
agent-browser wait --load networkidle
```

### Step 2 — Get title

```bash
agent-browser get title
```

### Step 3 — Scroll to trigger lazy-loaded images

WeChat uses lazy loading — must scroll before extracting image URLs.

```bash
agent-browser eval "
(async () => {
  window.scrollTo(0, document.body.scrollHeight);
  await new Promise(r => setTimeout(r, 2000));
  const step = 600;
  for (let y = 0; y < document.body.scrollHeight; y += step) {
    window.scrollTo(0, y);
    await new Promise(r => setTimeout(r, 300));
  }
  return 'done';
})()"
```

### Step 4 — Extract content in DOM order

**Important:** Use classic `function(){}` syntax, not arrow functions — arrow functions inside `JSON.stringify()` cause a syntax error in agent-browser eval.

```bash
agent-browser eval "
(function() {
  var nodes = document.querySelectorAll('#js_content p, #js_content section, #js_content img');
  var result = [];
  var imgIdx = 0;
  nodes.forEach(function(node) {
    if (node.tagName === 'IMG') {
      var src = node.currentSrc || node.src || node.dataset.src || '';
      if (src && src.includes('mmbiz') &&
          !src.includes('mmbiz.qlogo') &&
          !src.includes('profile')) {
        var h = node.naturalHeight || node.height || 0;
        var alt = (node.alt || '').toLowerCase();
        if ((h >= 50 || h === 0) &&
            !alt.includes('二维码') &&
            !alt.includes('引导') &&
            !alt.includes('赞赏')) {
          result.push({ type: 'img', idx: imgIdx++, src: src });
        }
      }
    } else {
      var text = node.innerText ? node.innerText.trim() : '';
      if (text && text.length > 3) result.push({ type: 'text', text: text });
    }
  });
  return JSON.stringify(result);
})()"
```

**Image filter rules** (skip these):
- `mmbiz.qlogo` — author avatar
- `mp_profile` — account profile image
- height < 50px — decorative dividers
- alt containing `二维码` / `引导` / `赞赏` — QR codes and tip prompts

### Step 5 — Confirm save location

**Always ask the user** before writing. Suggest a directory based on topic:

> 📂 Suggested: `<vault_root>/<topic_directory>/`
> 📄 Filename: `<title-keywords-YYYY-MM-DD>.md`
> 🖼 Images → same folder's `attachments/` directory
> Confirm, or pick a different location?

### Step 6 — Download images

```bash
mkdir -p "<note_dir>/attachments"

# Must include Referer header — WeChat returns 403 without it
curl -s -L --fail \
  -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  -e 'https://mp.weixin.qq.com/' \
  "<image_url>" -o "<note_dir>/attachments/<filename>"
```

Naming convention: `<slug>-图00.png`, `图01.jpg` … numbered in DOM order.
Extension: check `wx_fmt=jpeg` → `.jpg`, otherwise → `.png`.

**Shell tip for batch download** — use a function, not `declare -A` (zsh doesn't support associative arrays):

```bash
download_img() {
  local idx=$1 url=$2
  local ext="png"
  echo "$url" | grep -q "wx_fmt=jpeg" && ext="jpg"
  local fname=$(printf "<slug>-图%02d.%s" "$idx" "$ext")
  curl -s -L --fail \
    -A 'Mozilla/5.0' \
    -e 'https://mp.weixin.qq.com/' \
    "$url" -o "$fname" \
    && echo "OK $fname" || echo "FAIL $fname"
}
```

### Step 7 — Write the note

Strictly follow the DOM order from Step 4 — insert images at their original positions, not at the top or bottom.

```markdown
# {Article Title}

**Source:** WeChat — {Author / Account Name}
**Original URL:** {URL}
**Clipped:** {YYYY-MM-DD}
**Tags:** #{tag1} #{tag2}

---

{paragraph text}

![[slug-图00.jpg]]

{more paragraph text}

![[slug-图01.png]]

...

---

**References:**
- {any links from the article}
```

### Step 8 — Close browser

```bash
agent-browser close
```

### Step 9 — Report to user

Tell the user:
- Note path
- Number of images downloaded
- ⚠️ Reminder: if you move the note, move the `attachments/` folder with it. Obsidian's `![[]]` does a global vault search so links won't break immediately, but it's cleaner to keep them together.

---

## Gotchas (hard-won lessons)

| # | Issue | Fix |
|---|-------|-----|
| 1 | Lazy-loaded images return empty `src` | Always scroll the full page before extracting |
| 2 | WeChat images return 403 | `curl` must pass `-e 'https://mp.weixin.qq.com/'` as Referer |
| 3 | Image order wrong | Traverse DOM nodes in order — don't collect images separately |
| 4 | `zsh: bad substitution` | zsh doesn't support `declare -A`; use a shell function instead |
| 5 | `SyntaxError: missing ) after argument list` in agent-browser eval | Use classic `function(){}` not arrow functions inside `JSON.stringify()` |
| 6 | `async` eval hangs | Wrap in `(async () => { ... })()` — no outer `await` needed |
