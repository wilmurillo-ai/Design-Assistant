#!/usr/bin/env python3
"""
Feishu Card Message Sender

Send rich interactive card messages via Feishu Open API.
Supports: raw card JSON, markdown wrapping, and template-based cards.

Usage:
  # Raw card JSON file
  python3 feishu_card.py --to <id> --type open_id --card card.json

  # Markdown content wrapped as card
  python3 feishu_card.py --to <id> --type open_id --markdown "**Hello**" --title "Title" --color blue

  # Template-based
  python3 feishu_card.py --to <id> --type open_id --template news --data data.json

Credentials: env vars FEISHU_APP_ID / FEISHU_APP_SECRET, or --app-id / --app-secret flags.
"""

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.request
import urllib.error
from pathlib import Path

API_BASE = "https://open.feishu.cn/open-apis"
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Token cache (module-level for reuse when imported)
_token_cache = {"token": None, "expires_at": 0}

# Available header color templates
COLORS = [
    "blue", "wathet", "turquoise", "green", "yellow",
    "orange", "red", "carmine", "violet", "purple",
    "indigo", "grey", "default",
]


def _api_post(url, data, headers=None):
    """POST JSON to a URL and return parsed response."""
    body = json.dumps(data).encode("utf-8")
    hdrs = {"Content-Type": "application/json; charset=utf-8"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=body, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def get_tenant_token(app_id, app_secret):
    """Get tenant_access_token with simple caching."""
    now = time.time()
    if _token_cache["token"] and now < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    url = f"{API_BASE}/auth/v3/tenant_access_token/internal"
    resp = _api_post(url, {"app_id": app_id, "app_secret": app_secret})

    if resp.get("code") != 0:
        print(f"Token error: {resp.get('msg', 'unknown')}", file=sys.stderr)
        sys.exit(1)

    token = resp["tenant_access_token"]
    expire = resp.get("expire", 7200)
    _token_cache["token"] = token
    _token_cache["expires_at"] = now + expire
    return token


def build_chart_element(chart_type, data_values, title="",
                        x_field="category", y_field="value",
                        series_field=None, **kwargs):
    """Build a chart element for embedding in a card body.

    Args:
        chart_type: "line", "bar", or "pie"
        data_values: list of dicts, e.g. [{"category":"A","value":100,"type":"s1"}, ...]
        title: chart title text
        x_field / y_field / series_field: field mappings
        **kwargs: extra chart_spec keys (stack, point, categoryField, valueField)

    Returns:
        dict — a card element with tag "chart"
    """
    spec = {
        "type": chart_type,
        "data": {"values": data_values},
    }
    if title:
        spec["title"] = {"text": title}
    if chart_type == "pie":
        spec["categoryField"] = kwargs.get("categoryField", x_field)
        spec["valueField"] = kwargs.get("valueField", y_field)
    else:
        spec["xField"] = x_field
        spec["yField"] = y_field
    if series_field:
        spec["seriesField"] = series_field
    if chart_type == "bar" and kwargs.get("stack"):
        spec["stack"] = True
    if chart_type == "line":
        spec["point"] = {"visible": kwargs.get("point_visible", True)}
    # merge any remaining kwargs into spec
    for k, v in kwargs.items():
        if k not in ("categoryField", "valueField", "stack", "point_visible"):
            spec[k] = v
    return {"tag": "chart", "chart_spec": spec}


def build_card_from_markdown(markdown, title=None, color="blue"):
    """Wrap markdown text into a Card JSON (schema 2.0)."""
    card = {
        "schema": "2.0",
        "config": {"wide_screen_mode": True},
        "body": {
            "elements": [
                {"tag": "markdown", "content": markdown}
            ]
        }
    }
    if title:
        card["header"] = {
            "title": {"tag": "plain_text", "content": title},
            "template": color if color in COLORS else "blue",
        }
    return card


def load_template(name):
    """Load a card template by name from templates/ dir."""
    path = TEMPLATES_DIR / f"{name}.json"
    if not path.exists():
        avail = [f.stem for f in TEMPLATES_DIR.glob("*.json")]
        print(f"Template '{name}' not found. Available: {', '.join(avail) or 'none'}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fill_template(template, data):
    """
    Fill a card template with data.
    
    Templates use {{key}} placeholders in string values.
    Special keys:
      - {{items}} in elements array: replaced by generated elements from data["items"]
    Data can also contain an "elements" key to inject raw card elements.
    """
    raw = json.dumps(template, ensure_ascii=False)

    # Simple string replacement for scalar values
    for key, value in data.items():
        if isinstance(value, str):
            raw = raw.replace("{{" + key + "}}", value)

    card = json.loads(raw)

    # Handle items array for news/report templates
    if "items" in data and isinstance(data["items"], list):
        _inject_items(card, data["items"])

    return card


def _inject_items(card, items):
    """Replace {{items}} placeholder element with generated elements from data."""
    elements = card.get("body", {}).get("elements", [])
    new_elements = []
    for el in elements:
        if el.get("tag") == "markdown" and el.get("content", "").strip() == "{{items}}":
            for i, item in enumerate(items):
                if i > 0:
                    new_elements.append({"tag": "hr"})
                md = ""
                if "title" in item:
                    md += f"**{item['title']}**\n"
                if "summary" in item or "content" in item:
                    md += item.get("summary", item.get("content", "")) + "\n"
                extras = []
                if "source" in item:
                    extras.append(f"来源: {item['source']}")
                if "time" in item:
                    extras.append(item["time"])
                if "level" in item:
                    extras.append(f"级别: {item['level']}")
                if extras:
                    md += f"\n{'  |  '.join(extras)}"
                if "url" in item:
                    md += f"\n[查看详情]({item['url']})"
                new_elements.append({"tag": "markdown", "content": md.strip()})
        else:
            new_elements.append(el)
    card["body"]["elements"] = new_elements


def _multipart_upload(url, file_path, image_type, token):
    """Upload a file using multipart/form-data (stdlib only)."""
    import mimetypes
    boundary = f"----FeishuUpload{int(time.time()*1000)}"
    filename = os.path.basename(file_path)
    content_type = mimetypes.guess_type(filename)[0] or "image/png"

    with open(file_path, "rb") as f:
        file_data = f.read()

    parts = []
    # image_type field
    parts.append(f"--{boundary}\r\n"
                 f'Content-Disposition: form-data; name="image_type"\r\n\r\n'
                 f"{image_type}\r\n".encode("utf-8"))
    # image file field
    parts.append(f"--{boundary}\r\n"
                 f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
                 f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
    parts.append(file_data)
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    body = b"".join(parts)
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        print(f"Upload HTTP {e.code}: {err_body}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"Upload network error: {e.reason}", file=sys.stderr)
        return None


def upload_image(token, image_source, image_type="message"):
    """Upload an image to Feishu and return the img_key.

    Args:
        token: tenant_access_token
        image_source: local file path or HTTP(S) URL
        image_type: "message" (default, for IM cards) or "avatar"

    Returns:
        str: img_key on success, None on failure
    """
    url = f"{API_BASE}/im/v1/images"
    tmp_file = None

    try:
        # If URL, download to temp file first
        if image_source.startswith(("http://", "https://")):
            suffix = Path(image_source.split("?")[0]).suffix or ".png"
            tmp_fd, tmp_file = tempfile.mkstemp(suffix=suffix)
            os.close(tmp_fd)
            print(f"Downloading image from URL...", file=sys.stderr)
            req = urllib.request.Request(image_source, headers={
                "User-Agent": "Mozilla/5.0 (compatible; FeishuCardBot/1.0)"
            })
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    ct = resp.headers.get("Content-Type", "")
                    if not ct.startswith("image/"):
                        print(f"Warning: URL returned Content-Type '{ct}', expected image/*. "
                              f"Upload may fail.", file=sys.stderr)
                    with open(tmp_file, "wb") as f:
                        f.write(resp.read())
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                print(f"Failed to download image: {e}", file=sys.stderr)
                return None
            file_path = tmp_file
        else:
            file_path = image_source
            if not os.path.exists(file_path):
                print(f"Image file not found: {file_path}", file=sys.stderr)
                return None

        resp = _multipart_upload(url, file_path, image_type, token)
        if not resp:
            return None
        if resp.get("code") != 0:
            print(f"Upload error: {resp.get('msg', 'unknown')}", file=sys.stderr)
            return None

        img_key = resp.get("data", {}).get("image_key")
        print(f"✅ Image uploaded: {img_key}", file=sys.stderr)
        return img_key

    finally:
        if tmp_file and os.path.exists(tmp_file):
            os.unlink(tmp_file)


def build_image_element(img_key, alt_text="image", mode="fit_horizontal", preview=True):
    """Build an image card element from an img_key.

    Args:
        img_key: Feishu image key (from upload_image)
        alt_text: alt text for accessibility
        mode: "fit_horizontal" | "crop_center" | "large" | "medium" | "small" | "tiny"
        preview: enable click-to-preview

    Returns:
        dict: card element with tag "img"
    """
    return {
        "tag": "img",
        "img_key": img_key,
        "alt": {"tag": "plain_text", "content": alt_text},
        "mode": mode,
        "preview": preview,
    }


def send_card(token, receive_id, receive_id_type, card, reply_to=None):
    """Send a card message via Feishu IM API."""
    url = f"{API_BASE}/im/v1/messages?receive_id_type={receive_id_type}"
    payload = {
        "receive_id": receive_id,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False),
    }
    if reply_to:
        url = f"{API_BASE}/im/v1/messages/{reply_to}/reply"
        payload = {
            "msg_type": "interactive",
            "content": json.dumps(card, ensure_ascii=False),
        }

    headers = {"Authorization": f"Bearer {token}"}
    resp = _api_post(url, payload, headers)

    code = resp.get("code", -1)
    if code != 0:
        print(f"Send failed (code={code}): {resp.get('msg', 'unknown')}", file=sys.stderr)
        detail = resp.get("data", {})
        if detail:
            print(f"Detail: {json.dumps(detail, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)

    msg_id = resp.get("data", {}).get("message_id", "unknown")
    print(f"✅ Card sent! message_id={msg_id}")
    return resp


def main():
    parser = argparse.ArgumentParser(description="Send Feishu card messages")
    parser.add_argument("--to", required=True, help="Receiver ID (open_id or chat_id)")
    parser.add_argument("--type", dest="id_type", required=True,
                        choices=["open_id", "chat_id"], help="Receiver ID type")
    parser.add_argument("--app-id", default=None, help="Feishu App ID (or env FEISHU_APP_ID)")
    parser.add_argument("--app-secret", default=None, help="Feishu App Secret (or env FEISHU_APP_SECRET)")
    parser.add_argument("--reply-to", default=None, help="Message ID to reply to")

    # Mode 1: raw card JSON
    parser.add_argument("--card", default=None, help="Path to card JSON file")

    # Mode 2: markdown
    parser.add_argument("--markdown", default=None, help="Markdown content to wrap as card")
    parser.add_argument("--title", default=None, help="Card header title (for --markdown mode)")
    parser.add_argument("--color", default="blue", help=f"Header color: {', '.join(COLORS)}")

    # Mode 3: template
    parser.add_argument("--template", default=None, help="Template name (news_digest, report, alert)")
    parser.add_argument("--data", default=None, help="JSON data file to fill template")

    # Image: upload and embed
    parser.add_argument("--image", default=None, help="Image file path or URL to upload and embed in card")

    args = parser.parse_args()

    # Resolve credentials
    app_id = args.app_id or os.environ.get("FEISHU_APP_ID")
    app_secret = args.app_secret or os.environ.get("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        print("Error: Feishu credentials required. Set FEISHU_APP_ID/FEISHU_APP_SECRET or use --app-id/--app-secret.", file=sys.stderr)
        sys.exit(1)

    # Build card based on mode
    modes = sum(1 for x in [args.card, args.markdown, args.template] if x)
    if modes == 0:
        print("Error: specify one of --card, --markdown, or --template.", file=sys.stderr)
        sys.exit(1)
    if modes > 1:
        print("Error: use only one of --card, --markdown, or --template.", file=sys.stderr)
        sys.exit(1)

    if args.card:
        with open(args.card, "r", encoding="utf-8") as f:
            card = json.load(f)
    elif args.markdown:
        card = build_card_from_markdown(args.markdown, args.title, args.color)
    elif args.template:
        template = load_template(args.template)
        data = {}
        if args.data:
            with open(args.data, "r", encoding="utf-8") as f:
                data = json.load(f)
        # Apply title/color overrides
        if args.title and "header" in template:
            template["header"]["title"]["content"] = args.title
        if args.color and "header" in template:
            template["header"]["template"] = args.color
        card = fill_template(template, data) if data else template

    # Get token and send
    token = get_tenant_token(app_id, app_secret)

    # Handle --image: upload and append to card body
    if args.image:
        img_key = upload_image(token, args.image)
        if img_key:
            img_el = build_image_element(img_key)
            if "body" not in card:
                card["body"] = {"elements": []}
            card["body"]["elements"].append(img_el)
        else:
            print("Warning: image upload failed, sending card without image.", file=sys.stderr)

    send_card(token, args.to, args.id_type, card, args.reply_to)


if __name__ == "__main__":
    main()
