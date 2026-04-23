#!/usr/bin/env python3
"""
parse_local.py - Parse local email files and output JSON compatible with fetch_emails.py

Supports three input modes:
  --pst FILE        Outlook .pst file (auto-converts via readpst if available,
                    otherwise falls back to mbox in the same directory)
  --mbox FILE       A single .mbox file (e.g. exported from readpst or Apple Mail)
  --msg-dir DIR     A directory of .msg files exported from Outlook

Output format is identical to fetch_emails.py, so all downstream AI analysis
(4-dimension summary, contact profiling) works without any changes.

Usage:
  # Parse a .pst file (requires readpst to be installed on the system)
  python3 scripts/parse_local.py --pst ~/Downloads/outlook.pst

  # Parse a .mbox file converted by readpst
  python3 scripts/parse_local.py --mbox ~/Downloads/Inbox.mbox

  # Parse a folder of .msg files exported from Outlook
  python3 scripts/parse_local.py --msg-dir ~/Downloads/exported_msgs/

  # Limit date range
  python3 scripts/parse_local.py --pst outlook.pst --days 30
  python3 scripts/parse_local.py --mbox Inbox.mbox --since 2026-01-01 --until 2026-03-01

  # Enable contact profile mode (same as fetch_emails.py --profile)
  python3 scripts/parse_local.py --msg-dir ./msgs/ --profile

  # Include a "sent" mbox alongside inbox (improves relationship analysis)
  python3 scripts/parse_local.py --mbox Inbox.mbox --sent-mbox SentItems.mbox

Dependencies:
  - extract-msg  (pip3 install extract-msg)  — required for .msg mode
  - readpst      (system tool, optional)     — required for auto .pst conversion
  - mailbox      (Python stdlib)             — used for .mbox parsing
"""

import argparse
import email
import email.header
import email.utils
import json
import mailbox
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, timedelta, timezone


# ── Header / body helpers (mirrors fetch_emails.py) ──────────────────────────

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


def get_body_from_msg(msg):
    """Extract plain-text body from an email.message.Message object."""
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
                    html = part.get_payload(decode=True).decode(charset, errors="replace")
                    body = re.sub(r"<[^>]+>", " ", html)
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


def parse_date_to_iso(date_str):
    """Parse an email Date header into ISO-8601; return raw string on failure."""
    try:
        return email.utils.parsedate_to_datetime(date_str).isoformat()
    except Exception:
        return date_str or ""


def is_in_range(date_iso, since_dt, until_dt):
    """Return True if date_iso falls within [since_dt, until_dt)."""
    if not date_iso:
        return True  # unknown date: include by default
    try:
        # Normalise to offset-aware datetime for comparison
        dt = datetime.fromisoformat(date_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if since_dt:
            since_aware = since_dt.replace(tzinfo=timezone.utc) if since_dt.tzinfo is None else since_dt
            if dt < since_aware:
                return False
        if until_dt:
            until_aware = until_dt.replace(tzinfo=timezone.utc) if until_dt.tzinfo is None else until_dt
            if dt >= until_aware:
                return False
    except Exception:
        pass
    return True


def make_record(idx, direction, subject, sender, to, cc, date_iso, body):
    """Build an email record dict matching fetch_emails.py output format."""
    return {
        "id":        str(idx),
        "direction": direction,
        "date":      date_iso,
        "from":      sender,
        "to":        to,
        "cc":        cc,
        "subject":   subject,
        "body":      body,
    }


# ── Contact profile builder (identical logic to fetch_emails.py) ─────────────

def build_contact_profiles(emails):
    contacts = defaultdict(lambda: {
        "name":                "",
        "sent_to_count":       0,
        "received_from_count": 0,
        "subjects":            [],
        "body_snippets":       [],
    })

    for m in emails:
        direction = m.get("direction", "received")
        if direction == "received":
            name, addr = email.utils.parseaddr(m["from"])
            if addr:
                c = contacts[addr.lower()]
                if name and not c["name"]:
                    c["name"] = name
                c["received_from_count"] += 1
                c["subjects"].append(m["subject"])
                if m["body"]:
                    c["body_snippets"].append(m["body"][:300])
        else:
            for name, addr in email.utils.getaddresses([m["to"], m.get("cc", "")]):
                if addr:
                    c = contacts[addr.lower()]
                    if name and not c["name"]:
                        c["name"] = name
                    c["sent_to_count"] += 1
                    c["subjects"].append(m["subject"])

    bot_keywords = ["noreply", "no-reply", "donotreply", "notification", "service",
                    "support", "mailer", "bounce", "postmaster", "newsletter"]
    for addr, info in contacts.items():
        info["is_system"] = any(kw in addr for kw in bot_keywords)

    return dict(contacts)


# ── mbox parser ───────────────────────────────────────────────────────────────

def parse_mbox(path, since_dt, until_dt, max_count, direction="received"):
    """Parse a .mbox file and return a list of email record dicts."""
    if not os.path.isfile(path):
        print(f"[error] mbox file not found: {path}", file=sys.stderr)
        return []

    print(f"[mbox] Parsing {path} ...", file=sys.stderr)
    mbox = mailbox.mbox(path)
    results = []
    skipped = 0

    for i, raw_msg in enumerate(mbox):
        subject  = decode_header_value(raw_msg.get("Subject", "(no subject)"))
        sender   = decode_header_value(raw_msg.get("From", ""))
        to       = decode_header_value(raw_msg.get("To", ""))
        cc       = decode_header_value(raw_msg.get("Cc", ""))
        date_str = raw_msg.get("Date", "")
        date_iso = parse_date_to_iso(date_str)

        if not is_in_range(date_iso, since_dt, until_dt):
            skipped += 1
            continue

        # Convert mailbox.mboxMessage → email.message.Message for body extraction
        import io
        raw_bytes = bytes(raw_msg)
        std_msg = email.message_from_bytes(raw_bytes)
        body = get_body_from_msg(std_msg)

        results.append(make_record(i, direction, subject, sender, to, cc, date_iso, body))

        if len(results) >= max_count:
            print(f"[mbox] Reached max {max_count}, stopping.", file=sys.stderr)
            break

    print(f"[mbox] {len(results)} emails loaded ({skipped} skipped by date filter)", file=sys.stderr)
    return results


# ── .msg directory parser ─────────────────────────────────────────────────────

def parse_msg_dir(directory, since_dt, until_dt, max_count, direction="received"):
    """Parse all .msg files in a directory tree."""
    try:
        import extract_msg
    except ImportError:
        print("[error] extract-msg is not installed. Run: pip3 install extract-msg", file=sys.stderr)
        sys.exit(1)

    msg_files = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(".msg"):
                msg_files.append(os.path.join(root, f))

    if not msg_files:
        print(f"[error] No .msg files found in: {directory}", file=sys.stderr)
        return []

    print(f"[msg] Found {len(msg_files)} .msg file(s) in {directory}", file=sys.stderr)
    results = []
    skipped = 0

    for i, path in enumerate(sorted(msg_files)):
        print(f"[msg] {i+1}/{len(msg_files)} {os.path.basename(path)} ...", file=sys.stderr, end="\r")
        try:
            m = extract_msg.openMsg(path)
            subject  = m.subject or "(no subject)"
            sender   = m.sender or ""
            to       = m.to or ""
            cc       = m.cc or ""
            date_obj = m.date  # datetime or None
            date_iso = date_obj.isoformat() if date_obj else ""
            body_raw = m.body or ""
            body     = body_raw[:2000]

            # Infer direction from subfolder name heuristics
            folder_name = os.path.basename(os.path.dirname(path)).lower()
            sent_hints  = ["sent", "已发送", "发件箱", "outbox", "outgoing"]
            inferred_dir = "sent" if any(h in folder_name for h in sent_hints) else direction

            if not is_in_range(date_iso, since_dt, until_dt):
                skipped += 1
                m.close()
                continue

            results.append(make_record(i, inferred_dir, subject, sender, to, cc, date_iso, body))
            m.close()

            if len(results) >= max_count:
                print(f"\n[msg] Reached max {max_count}, stopping.", file=sys.stderr)
                break
        except Exception as e:
            print(f"\n[warn] Failed to parse {path}: {e}", file=sys.stderr)

    print(f"\n[msg] {len(results)} emails loaded ({skipped} skipped by date filter)", file=sys.stderr)
    return results


# ── .pst parser ───────────────────────────────────────────────────────────────
#
# Strategy (tried in order):
#   1. Native mode  — calls pst_extractor_helper.js (Node.js + pst-extractor npm pkg)
#                     Works without any system-level install; auto-installs the npm
#                     package into /tmp/pst_parse if needed.
#   2. readpst mode — converts .pst → .mbox via the readpst system binary, then
#                     parses the resulting mbox files.  Requires:
#                       Linux:  sudo apt install pst-utils  /  sudo yum install libpst
#                       macOS:  brew install libpst
#
# Use --pst-engine=native   to force native mode (skip readpst check).
# Use --pst-engine=readpst  to force readpst mode (fail if not installed).
# Default: try native first, fall back to readpst.


def find_readpst():
    """Return the path to the readpst binary, or None if not found."""
    return shutil.which("readpst")


def find_node():
    """Return the path to the node binary, or None if not found."""
    return shutil.which("node") or shutil.which("nodejs")


def _parse_pst_native(pst_path, since_dt, until_dt, max_count):
    """
    Parse .pst natively via pst_extractor_helper.js (Node.js).

    Returns a list of email record dicts on success, or raises RuntimeError
    if Node.js is unavailable or the helper script fails.
    """
    node = find_node()
    if not node:
        raise RuntimeError("Node.js not found on this system.")

    helper = os.path.join(os.path.dirname(__file__), "pst_extractor_helper.js")
    if not os.path.isfile(helper):
        raise RuntimeError(f"pst_extractor_helper.js not found at {helper}")

    cmd = [node, helper, pst_path, "--max", str(max_count)]
    if since_dt:
        cmd += ["--since", since_dt.strftime("%Y-%m-%d")]
    if until_dt:
        cmd += ["--until", until_dt.strftime("%Y-%m-%d")]

    print(f"[pst-native] Running: {' '.join(cmd)}", file=sys.stderr)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        raise RuntimeError("pst_extractor_helper.js timed out (300s).")

    # Forward Node stderr to our stderr so the user sees install/progress logs
    if result.stderr:
        for line in result.stderr.splitlines():
            print(f"  {line}", file=sys.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"pst_extractor_helper.js exited with code {result.returncode}.")

    try:
        emails = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"pst_extractor_helper.js returned invalid JSON: {e}")

    print(f"[pst-native] {len(emails)} emails loaded.", file=sys.stderr)
    return emails


def _parse_pst_readpst(pst_path, since_dt, until_dt, max_count):
    """
    Parse .pst by converting to mbox with the readpst system tool.

    Raises RuntimeError if readpst is not installed.
    """
    readpst = find_readpst()
    if not readpst:
        raise RuntimeError("readpst not found on this system.")

    with tempfile.TemporaryDirectory(prefix="pst_parse_") as tmpdir:
        print(f"[pst-readpst] Converting {pst_path} with readpst ...", file=sys.stderr)
        try:
            result = subprocess.run(
                [readpst, "-o", tmpdir, "-r", pst_path],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode != 0:
                raise RuntimeError(f"readpst failed:\n{result.stderr}")
            print(f"[pst-readpst] Conversion done. Output dir: {tmpdir}", file=sys.stderr)
        except subprocess.TimeoutExpired:
            raise RuntimeError("readpst timed out (300s). The PST file may be very large.")

        # Collect all mbox-like files produced by readpst
        mbox_files = []
        for root, _, files in os.walk(tmpdir):
            for f in files:
                if f.endswith(".mbox") or f.endswith(".mbox.d"):
                    mbox_files.append(os.path.join(root, f))
                elif not os.path.splitext(f)[1]:
                    full = os.path.join(root, f)
                    if os.path.isfile(full):
                        mbox_files.append(full)

        if not mbox_files:
            print("[warn] readpst produced no .mbox files. Trying any files in output ...", file=sys.stderr)
            for root, _, files in os.walk(tmpdir):
                for f in files:
                    mbox_files.append(os.path.join(root, f))

        print(f"[pst-readpst] Found {len(mbox_files)} mbox file(s) to parse", file=sys.stderr)

        all_emails = []
        sent_hints = ["sent", "已发送", "发件箱", "outbox", "outgoing"]
        for mbox_path in mbox_files:
            fname  = os.path.basename(mbox_path).lower()
            parent = os.path.basename(os.path.dirname(mbox_path)).lower()
            direction = "sent" if any(h in fname or h in parent for h in sent_hints) else "received"
            emails = parse_mbox(mbox_path, since_dt, until_dt, max_count, direction)
            all_emails.extend(emails)

        return all_emails


def parse_pst(pst_path, since_dt, until_dt, max_count, engine="auto"):
    """
    Parse a .pst file, choosing the engine based on availability.

    engine:
      "auto"    — try native (pst-extractor) first, fall back to readpst
      "native"  — force native mode (Node.js + pst-extractor)
      "readpst" — force readpst mode
    """
    if not os.path.isfile(pst_path):
        print(f"[error] PST file not found: {pst_path}", file=sys.stderr)
        sys.exit(1)

    if engine in ("auto", "native"):
        try:
            return _parse_pst_native(pst_path, since_dt, until_dt, max_count)
        except RuntimeError as e:
            if engine == "native":
                print(f"[error] Native PST parsing failed: {e}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"[pst] Native mode unavailable ({e}), trying readpst ...", file=sys.stderr)

    if engine in ("auto", "readpst"):
        try:
            return _parse_pst_readpst(pst_path, since_dt, until_dt, max_count)
        except RuntimeError as e:
            print(f"[error] readpst mode failed: {e}", file=sys.stderr)
            print("", file=sys.stderr)
            print("To install readpst:", file=sys.stderr)
            print("  Linux (Debian/Ubuntu):  sudo apt install pst-utils", file=sys.stderr)
            print("  Linux (RHEL/CentOS):    sudo yum install libpst", file=sys.stderr)
            print("  macOS (Homebrew):       brew install libpst", file=sys.stderr)
            print("", file=sys.stderr)
            print("Alternative: export emails as .msg files from Outlook, then use:", file=sys.stderr)
            print("  python3 scripts/parse_local.py --msg-dir <folder>", file=sys.stderr)
            sys.exit(1)


# ── Date parsing ──────────────────────────────────────────────────────────────

def parse_date_arg(s):
    for fmt in ("%Y-%m-%d", "%d-%b-%Y", "%d-%B-%Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s!r}. Use YYYY-MM-DD or DD-Mon-YYYY.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Parse local email files (.pst / .mbox / .msg) and output JSON"
    )

    # Input mode (mutually exclusive)
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--pst",     metavar="FILE",  help=".pst file (requires readpst)")
    src.add_argument("--mbox",    metavar="FILE",  help=".mbox file")
    src.add_argument("--msg-dir", metavar="DIR",   help="Directory of .msg files")

    # Optional sent source for mbox mode
    parser.add_argument("--sent-mbox", metavar="FILE",
                        help="Additional .mbox file treated as Sent folder (mbox mode only)")

    # Date range
    parser.add_argument("--days",  type=int, default=None,
                        help="Only include emails from the last N days")
    parser.add_argument("--since", type=str, default=None,
                        help="Start date inclusive (YYYY-MM-DD or DD-Mon-YYYY)")
    parser.add_argument("--until", type=str, default=None,
                        help="End date exclusive (YYYY-MM-DD or DD-Mon-YYYY)")

    # Limits and modes
    parser.add_argument("--max",     type=int, default=500,
                        help="Max emails to load per source (default: 500)")
    parser.add_argument("--profile", action="store_true",
                        help="Output contact profile data (same as fetch_emails.py --profile)")
    parser.add_argument("--pst-engine", choices=["auto", "native", "readpst"], default="auto",
                        help="PST parse engine: auto (default) | native (Node.js pst-extractor) | readpst (system binary)")

    args = parser.parse_args()

    # ── Resolve date range ────────────────────────────────────────────────────
    since_dt = None
    until_dt = None

    if args.since:
        since_dt = parse_date_arg(args.since)
    elif args.days:
        since_dt = datetime.now() - timedelta(days=args.days)

    if args.until:
        until_dt = parse_date_arg(args.until)

    # ── Parse emails ──────────────────────────────────────────────────────────
    all_emails = []

    if args.pst:
        all_emails = parse_pst(args.pst, since_dt, until_dt, args.max,
                               engine=getattr(args, 'pst_engine', 'auto'))

    elif args.mbox:
        all_emails = parse_mbox(args.mbox, since_dt, until_dt, args.max, direction="received")
        if args.sent_mbox:
            sent = parse_mbox(args.sent_mbox, since_dt, until_dt, args.max, direction="sent")
            all_emails.extend(sent)

    elif args.msg_dir:
        all_emails = parse_msg_dir(args.msg_dir, since_dt, until_dt, args.max)

    # ── Output ────────────────────────────────────────────────────────────────
    if args.profile:
        profiles = build_contact_profiles(all_emails)
        output = {
            "source":       args.pst or args.mbox or args.msg_dir,
            "since":        since_dt.strftime("%d-%b-%Y") if since_dt else "all",
            "until":        until_dt.strftime("%d-%b-%Y") if until_dt else "now",
            "total_emails": len(all_emails),
            "contacts":     profiles,
            "emails":       all_emails,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(all_emails, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
