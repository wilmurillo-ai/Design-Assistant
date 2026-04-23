#!/usr/bin/env python3
"""
fetch_emails.py - Fetch emails from an IMAP mailbox and output JSON

Usage:
  python3 fetch_emails.py --days 3
  python3 fetch_emails.py --days 7 --max 50 --preset qq
  python3 fetch_emails.py --days 3 --with-sent     # also fetch Sent folder (better relationship analysis)
  python3 fetch_emails.py --days 3 --profile       # enable contact profile mode

Environment variables:
  EMAIL_USER     Mailbox account (e.g. user@163.com)
  EMAIL_PASS     IMAP app password (NOT your login password)
  IMAP_HOST      Custom IMAP server (overrides preset)
  IMAP_PORT      Custom IMAP port (default 993)
"""

import imaplib
import email
import email.header
import email.utils
import json
import os
import sys
import argparse
from datetime import datetime, timedelta
from collections import defaultdict


# ── Extend IMAP4_SSL to support RFC 2971 ID command ──────────────────────────
class IMAP4_SSL_WithID(imaplib.IMAP4_SSL):
    """
    Extended imaplib.IMAP4_SSL that supports sending the RFC 2971 ID command.

    163/188 mail servers require the ID command to be sent after LOGIN and
    before SELECT; otherwise they return 'Unsafe Login. Please contact
    kefu@188.com for help'. Standard imaplib does not support ID, so we
    write directly to the underlying socket.

    Sending ID to other servers (QQ, Gmail, etc.) is harmless — it will
    either be acknowledged or ignored.
    """
    def send_id(self, name="EmailSummarizer", version="1.0", vendor="OpenClaw"):
        tag = self._new_tag()
        cmd = f'{tag.decode()} ID ("name" "{name}" "version" "{version}" "vendor" "{vendor}")\r\n'
        self.send(cmd.encode())
        while True:
            resp = self.readline()
            if resp.startswith(tag):
                return resp


# ── Mailbox presets ───────────────────────────────────────────────────────────
# Format: (imap_host, port, sent_folder_name)
PRESETS = {
    "exmail":   ("imap.exmail.qq.com",   993, "Sent Messages"),  # Tencent Exmail
    "qq":       ("imap.qq.com",          993, "Sent Messages"),  # QQ Mail
    "gmail":    ("imap.gmail.com",       993, "[Gmail]/Sent Mail"),
    "outlook":  ("outlook.office365.com",993, "Sent Items"),
    "163":      ("imap.163.com",         993, "已发送"),          # 163 Mail (Chinese folder name)
}


def decode_header_value(raw):
    """Decode an encoded email header field into a plain string."""
    parts = email.header.decode_header(raw or "")
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                decoded.append(part.decode(charset or "utf-8", errors="replace"))
            except Exception:
                decoded.append(part.decode("utf-8", errors="replace"))
        else:
            decoded.append(str(part))
    return "".join(decoded).strip()


def get_body(msg):
    """Extract plain-text body from an email message (prefers text/plain)."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in disposition:
                continue
            if ctype == "text/plain":
                charset = part.get_content_charset() or "utf-8"
                try:
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                    break
                except Exception:
                    pass
            elif ctype == "text/html" and not body:
                charset = part.get_content_charset() or "utf-8"
                try:
                    import re
                    html = part.get_payload(decode=True).decode(charset, errors="replace")
                    body = re.sub(r"<[^>]+>", "", html)
                    body = re.sub(r"\s+", " ", body).strip()
                except Exception:
                    pass
    else:
        charset = msg.get_content_charset() or "utf-8"
        try:
            body = msg.get_payload(decode=True).decode(charset, errors="replace")
        except Exception:
            body = ""
    return body[:2000]


def connect(user, password, host, port):
    """Establish an IMAP connection and log in."""
    try:
        mail = IMAP4_SSL_WithID(host, port)
        mail.login(user, password)
        try:
            mail.send_id()
        except Exception:
            pass
        return mail
    except imaplib.IMAP4.error as e:
        print(f"[error] Login failed: {e}", file=sys.stderr)
        print("Hint: make sure IMAP is enabled and you are using an app password, not your login password.", file=sys.stderr)
        sys.exit(1)


def imap_utf7_encode(s):
    """
    Encode a Unicode string to IMAP modified UTF-7 (RFC 3501).
    Required for folder names containing non-ASCII characters (e.g. Chinese).
    """
    import base64
    res = []
    non_ascii = []

    def flush():
        if non_ascii:
            encoded = base64.b64encode("".join(non_ascii).encode("utf-16-be")).decode("ascii")
            res.append(f"&{encoded}-")
            non_ascii.clear()

    for ch in s:
        if ord(ch) < 128 and ch != "&":
            flush()
            res.append(ch)
        elif ch == "&":
            flush()
            res.append("&-")
        else:
            non_ascii.append(ch)
    flush()
    return "".join(res)


def fetch_folder(mail, folder, since_date_str, until_date_str, max_count, direction="received"):
    """Fetch emails from a specific IMAP folder and return a list of dicts.

    since_date_str / until_date_str: DD-Mon-YYYY strings for IMAP SEARCH.
    """
    # Try IMAP modified UTF-7 encoding first, then fall back to raw string
    encoded_folder = imap_utf7_encode(folder)
    status, _ = mail.select(f'"{encoded_folder}"', readonly=True)
    if status != "OK":
        status, _ = mail.select(f'"{folder}"', readonly=True)
    if status != "OK":
        status, _ = mail.select(folder, readonly=True)
    if status != "OK":
        print(f"[skip] Cannot select folder: {folder}", file=sys.stderr)
        return []

    # Build IMAP search criteria
    criteria = f'SINCE "{since_date_str}"'
    if until_date_str:
        criteria += f' BEFORE "{until_date_str}"'

    print(f"[search] {folder}: {criteria} ...", file=sys.stderr)
    _, data = mail.search(None, criteria)
    ids = data[0].split()
    print(f"[found] {len(ids)} email(s)", file=sys.stderr)

    ids = ids[-max_count:] if len(ids) > max_count else ids
    ids = list(reversed(ids))  # newest first

    results = []
    for i, uid in enumerate(ids):
        print(f"[fetch] {folder} {i+1}/{len(ids)} ...", file=sys.stderr, end="\r")
        _, msg_data = mail.fetch(uid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject  = decode_header_value(msg.get("Subject", "(no subject)"))
        sender   = decode_header_value(msg.get("From", ""))
        to       = decode_header_value(msg.get("To", ""))
        cc       = decode_header_value(msg.get("Cc", ""))
        date_str = msg.get("Date", "")
        body     = get_body(msg)

        try:
            parsed_date = email.utils.parsedate_to_datetime(date_str)
            date_iso = parsed_date.isoformat()
        except Exception:
            date_iso = date_str

        results.append({
            "id":        uid.decode(),
            "direction": direction,   # "received" or "sent"
            "date":      date_iso,
            "from":      sender,
            "to":        to,
            "cc":        cc,
            "subject":   subject,
            "body":      body,
        })

    print(f"\n[done] {folder}: {len(results)} email(s) fetched", file=sys.stderr)
    return results


def build_contact_profiles(emails):
    """
    Aggregate contact information from the email list.
    Returns dict: email_address -> { name, sent_to_count, received_from_count,
                                     subjects, body_snippets, is_system }
    """
    contacts = defaultdict(lambda: {
        "name":                "",
        "sent_to_count":       0,   # owner → contact
        "received_from_count": 0,   # contact → owner
        "subjects":            [],
        "body_snippets":       [],
    })

    for m in emails:
        direction = m.get("direction", "received")
        if direction == "received":
            addr_raw = m["from"]
            name, addr = email.utils.parseaddr(addr_raw)
            if addr:
                c = contacts[addr.lower()]
                if name and not c["name"]:
                    c["name"] = name
                c["received_from_count"] += 1
                c["subjects"].append(m["subject"])
                if m["body"]:
                    c["body_snippets"].append(m["body"][:300])
        else:
            # Sent: recipients are the contacts
            for name, addr in email.utils.getaddresses([m["to"], m.get("cc", "")]):
                if addr:
                    c = contacts[addr.lower()]
                    if name and not c["name"]:
                        c["name"] = name
                    c["sent_to_count"] += 1
                    c["subjects"].append(m["subject"])

    # Flag system/bot senders (no-reply addresses, notification bots, etc.)
    bot_keywords = ["noreply", "no-reply", "donotreply", "notification", "service",
                    "support", "mailer", "bounce", "postmaster", "newsletter"]
    for addr, info in contacts.items():
        info["is_system"] = any(kw in addr for kw in bot_keywords)

    return dict(contacts)


def main():
    parser = argparse.ArgumentParser(description="Fetch IMAP emails and output JSON")
    parser.add_argument("--days",      type=int, default=3,
                        help="Fetch emails from the last N days (default: 3). Ignored if --since is set.")
    parser.add_argument("--since",     type=str, default=None,
                        help="Start date, inclusive. Formats: YYYY-MM-DD or DD-Mon-YYYY (e.g. 2026-03-01 or 01-Mar-2026)")
    parser.add_argument("--until",     type=str, default=None,
                        help="End date, exclusive. Same format as --since. Defaults to today+1 (open-ended).")
    parser.add_argument("--max",       type=int, default=100,    help="Max emails per folder (default: 100)")
    parser.add_argument("--folder",    type=str, default="INBOX",help="Inbox folder name (default: INBOX)")
    parser.add_argument("--preset",    type=str, default="163",
                        choices=list(PRESETS.keys()),
                        help="Mailbox provider preset (default: 163)")
    parser.add_argument("--host",      type=str, help="Custom IMAP server (overrides preset)")
    parser.add_argument("--port",      type=int, help="Custom IMAP port (overrides preset)")
    parser.add_argument("--with-sent", action="store_true",
                        help="Also fetch Sent folder (improves relationship analysis)")
    parser.add_argument("--profile",   action="store_true",
                        help="Output contact profile data (for AI profiling)")
    args = parser.parse_args()

    # ── Resolve date range ────────────────────────────────────────────────────
    IMAP_FMT = "%d-%b-%Y"   # DD-Mon-YYYY used by IMAP SEARCH

    def parse_date_arg(s: str) -> datetime:
        """Accept YYYY-MM-DD or DD-Mon-YYYY."""
        for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y"):
            try:
                return datetime.strptime(s, fmt)
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {s!r}. Use YYYY-MM-DD or DD-Mon-YYYY.")

    if args.since:
        since_dt = parse_date_arg(args.since)
    else:
        since_dt = datetime.now() - timedelta(days=args.days)

    if args.until:
        until_dt    = parse_date_arg(args.until)
        until_str   = until_dt.strftime(IMAP_FMT)
    else:
        until_str   = None   # open-ended

    since_str = since_dt.strftime(IMAP_FMT)
    # ─────────────────────────────────────────────────────────────────────────

    user     = os.environ.get("EMAIL_USER") or input("Email account: ").strip()
    password = os.environ.get("EMAIL_PASS") or __import__("getpass").getpass("App password: ")

    default_host, default_port, default_sent_folder = PRESETS[args.preset]
    host = args.host or os.environ.get("IMAP_HOST") or default_host
    port = args.port or int(os.environ.get("IMAP_PORT", default_port))

    mail = connect(user, password, host, port)

    # Fetch inbox
    all_emails = fetch_folder(mail, args.folder, since_str, until_str, args.max, direction="received")

    # Optionally fetch sent folder
    if args.with_sent:
        sent = fetch_folder(mail, default_sent_folder, since_str, until_str, args.max, direction="sent")
        all_emails.extend(sent)

    mail.logout()

    if args.profile:
        profiles = build_contact_profiles(all_emails)
        output = {
            "owner_email":   user,
            "since":         since_str,
            "until":         until_str or "now",
            "total_emails":  len(all_emails),
            "contacts":      profiles,
            "emails":        all_emails,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(all_emails, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
