"""
Northstar Delivery Module - Unified single source of truth for all message delivery.

Replaces duplicated deliver()/deliver_multi()/_send_to_channel() logic that
previously existed in both northstar.py and northstar_pro.py.

Created: Phase 1 Step 2 - Unified Delivery Module
"""

import json
import subprocess
import tempfile
import os
from datetime import datetime

from models import DeliveryConfig


def send_to_channel(message: str, channel: str, config: DeliveryConfig) -> bool:
    """
    Send a message to a single delivery channel.

    Args:
        message: The message text to deliver.
        channel: Channel name (imessage, slack, telegram, email, terminal, none).
        config: DeliveryConfig instance with all credentials.

    Returns:
        True on success.

    Raises:
        ValueError: For missing credentials or unknown channel.
        RuntimeError: For OS/API errors during send.
    """
    if channel in ("terminal", "none"):
        print("\n" + message)
        return True

    if channel == "imessage":
        import platform as _platform
        if _platform.system() != "Darwin":
            raise RuntimeError(
                "iMessage delivery requires macOS. "
                "You're on " + _platform.system() + ".\n"
                "Switch to Slack or Telegram delivery: run 'northstar setup' and choose a different channel."
            )
        if not config.recipient:
            raise ValueError("delivery.recipient must be set for iMessage")

        # Build AppleScript string with multi-line message support
        parts = message.split("\n")
        escaped_parts = [p.replace("\\", "\\\\").replace('"', '\\"') for p in parts]
        as_msg = ' & return & '.join(f'"{p}"' for p in escaped_parts)
        script = f'''
tell application "Messages"
    set targetService to 1st account whose service type = iMessage
    set targetBuddy to participant "{config.recipient}" of targetService
    send ({as_msg}) to targetBuddy
end tell
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".applescript", delete=False) as f:
            f.write(script)
            tmp_path = f.name
        try:
            result = subprocess.run(["osascript", tmp_path], capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"iMessage send failed: {result.stderr}")
        finally:
            os.unlink(tmp_path)
        return True

    elif channel == "slack":
        if not config.slack_webhook:
            raise ValueError("delivery.slack_webhook must be set for Slack")
        import urllib.request
        payload = json.dumps({"text": message}).encode()
        req = urllib.request.Request(
            config.slack_webhook,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200

    elif channel == "telegram":
        if not config.telegram_chat_id or not config.telegram_bot_token:
            raise ValueError("delivery.telegram_chat_id and telegram_bot_token required")
        import urllib.request
        url = f"https://api.telegram.org/bot{config.telegram_bot_token}/sendMessage"
        payload = json.dumps({"chat_id": config.telegram_chat_id, "text": message}).encode()
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return resp.status == 200

    elif channel == "email":
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        email_to = config.email_to or config.recipient
        email_from = config.email_from or config.smtp_user

        if not config.smtp_user or not config.smtp_password or not email_to:
            raise ValueError("Email delivery requires smtp_user, smtp_password, and email_to in config.")

        now = datetime.now()
        subject = f"Northstar Briefing - {now.strftime('%B %-d, %Y')}"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = email_from
        msg["To"] = email_to
        msg.attach(MIMEText(message, "plain"))

        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(config.smtp_user, config.smtp_password)
            server.sendmail(email_from, email_to, msg.as_string())
        return True

    else:
        raise ValueError(f"Unknown delivery channel: {channel}")


def deliver(message: str, config: DeliveryConfig, dry_run: bool = False) -> bool:
    """
    Single-channel delivery (core tier).

    Args:
        message: The message text to deliver.
        config: DeliveryConfig instance.
        dry_run: If True, prints the message without sending.

    Returns:
        True on success.
    """
    if dry_run or config.channel == "none":
        print("\n--- BRIEFING (dry run) ---")
        print(message)
        print("--- END ---\n")
        return True

    return send_to_channel(message, config.channel, config)


def deliver_multi(
    message: str,
    config: DeliveryConfig,
    dry_run: bool = False,
    max_channels: int = 1,
) -> list[tuple[str, bool]]:
    """
    Multi-channel delivery (Pro tier).

    Sends to all channels from config.get_channels(max_channels).
    Falls back to single config.channel if no channels list is set.

    Args:
        message: The message text to deliver.
        config: DeliveryConfig instance.
        dry_run: If True, prints instead of sending.
        max_channels: Maximum number of channels to send to (1 for Standard, 3 for Pro).

    Returns:
        List of (channel, success) tuples.
    """
    channels = config.get_channels(max_channels)

    results: list[tuple[str, bool]] = []
    for ch in channels:
        if dry_run:
            print(f"\n[DRY RUN - {ch.upper()}]\n{'=' * 50}\n{message}\n{'=' * 50}")
            results.append((ch, True))
        else:
            try:
                send_to_channel(message, ch, config)
                results.append((ch, True))
            except Exception as e:
                results.append((ch, False))
                print(f"  Warning: {ch} delivery failed: {e}")

    return results
