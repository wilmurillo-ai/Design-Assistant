#!/usr/bin/env python3
"""
Tests for the unified delivery module (scripts/delivery.py).

Covers send_to_channel, deliver, deliver_multi, and DeliveryConfig.from_config().
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from delivery import send_to_channel, deliver, deliver_multi
from models import DeliveryConfig

MSG = "Test briefing message\nLine 2\nLine 3"


def make_config(**kwargs) -> DeliveryConfig:
    """Helper: build a DeliveryConfig with defaults overridden by kwargs."""
    defaults = dict(
        channel="none",
        channels=[],
        recipient="",
        slack_webhook="",
        telegram_bot_token="",
        telegram_chat_id="",
        email_to="",
        email_from="",
        smtp_user="",
        smtp_password="",
        smtp_host="smtp.gmail.com",
        smtp_port=587,
    )
    defaults.update(kwargs)
    return DeliveryConfig(**defaults)


# ---- send_to_channel tests -------------------------------------------------

class TestSendToChannelTerminal(unittest.TestCase):
    def test_terminal_prints_message(self):
        cfg = make_config(channel="terminal")
        with patch("builtins.print") as mock_print:
            result = send_to_channel(MSG, "terminal", cfg)
        self.assertTrue(result)
        mock_print.assert_called_once_with("\n" + MSG)

    def test_none_prints_message(self):
        cfg = make_config(channel="none")
        with patch("builtins.print") as mock_print:
            result = send_to_channel(MSG, "none", cfg)
        self.assertTrue(result)
        mock_print.assert_called_once_with("\n" + MSG)


class TestSendToChannelIMessage(unittest.TestCase):
    def test_imessage_raises_on_non_darwin(self):
        cfg = make_config(channel="imessage", recipient="+15551234567")
        with patch("platform.system", return_value="Linux"):
            with self.assertRaises(RuntimeError) as ctx:
                send_to_channel(MSG, "imessage", cfg)
        self.assertIn("macOS", str(ctx.exception))

    def test_imessage_raises_on_missing_recipient(self):
        cfg = make_config(channel="imessage", recipient="")
        with patch("platform.system", return_value="Darwin"):
            with self.assertRaises(ValueError) as ctx:
                send_to_channel(MSG, "imessage", cfg)
        self.assertIn("recipient", str(ctx.exception))

    def test_imessage_success_darwin(self):
        cfg = make_config(channel="imessage", recipient="+15551234567")
        mock_result = MagicMock()
        mock_result.returncode = 0
        with patch("platform.system", return_value="Darwin"), \
             patch("subprocess.run", return_value=mock_result), \
             patch("tempfile.NamedTemporaryFile"), \
             patch("os.unlink"):
            # We need the full tempfile flow to work; use a real temp file
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(mode="w", suffix=".applescript", delete=False) as f:
                tmp = f.name
            try:
                with patch("tempfile.NamedTemporaryFile") as mock_tmp:
                    mock_tmp.return_value.__enter__ = lambda s: s
                    mock_tmp.return_value.__exit__ = MagicMock(return_value=False)
                    mock_tmp.return_value.name = tmp
                    with patch("os.unlink"):
                        result = send_to_channel(MSG, "imessage", cfg)
            finally:
                try:
                    os.unlink(tmp)
                except FileNotFoundError:
                    pass
        self.assertTrue(result)


class TestSendToChannelSlack(unittest.TestCase):
    def test_slack_raises_on_missing_webhook(self):
        cfg = make_config(channel="slack", slack_webhook="")
        with self.assertRaises(ValueError) as ctx:
            send_to_channel(MSG, "slack", cfg)
        self.assertIn("slack_webhook", str(ctx.exception))

    def test_slack_sends_request(self):
        cfg = make_config(channel="slack", slack_webhook="https://hooks.slack.com/test")
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.status = 200
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = send_to_channel(MSG, "slack", cfg)
        self.assertTrue(result)


class TestSendToChannelTelegram(unittest.TestCase):
    def test_telegram_raises_on_missing_credentials(self):
        cfg = make_config(channel="telegram", telegram_bot_token="", telegram_chat_id="")
        with self.assertRaises(ValueError) as ctx:
            send_to_channel(MSG, "telegram", cfg)
        self.assertIn("telegram", str(ctx.exception).lower())

    def test_telegram_raises_on_missing_chat_id(self):
        cfg = make_config(channel="telegram", telegram_bot_token="bot123", telegram_chat_id="")
        with self.assertRaises(ValueError):
            send_to_channel(MSG, "telegram", cfg)

    def test_telegram_sends_request(self):
        cfg = make_config(
            channel="telegram",
            telegram_bot_token="bot123",
            telegram_chat_id="chat456",
        )
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.status = 200
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = send_to_channel(MSG, "telegram", cfg)
        self.assertTrue(result)


class TestSendToChannelEmail(unittest.TestCase):
    def test_email_raises_on_missing_smtp_credentials(self):
        cfg = make_config(channel="email", smtp_user="", smtp_password="", email_to="")
        with self.assertRaises(ValueError) as ctx:
            send_to_channel(MSG, "email", cfg)
        self.assertIn("smtp_user", str(ctx.exception))

    def test_email_raises_on_missing_email_to(self):
        cfg = make_config(
            channel="email",
            smtp_user="user@gmail.com",
            smtp_password="secret",
            email_to="",
            recipient="",
        )
        with self.assertRaises(ValueError):
            send_to_channel(MSG, "email", cfg)

    def test_email_sends_via_smtp(self):
        cfg = make_config(
            channel="email",
            smtp_user="from@gmail.com",
            smtp_password="secret",
            email_to="to@example.com",
            email_from="from@gmail.com",
        )
        mock_smtp = MagicMock()
        mock_smtp.__enter__ = lambda s: s
        mock_smtp.__exit__ = MagicMock(return_value=False)
        with patch("smtplib.SMTP", return_value=mock_smtp):
            result = send_to_channel(MSG, "email", cfg)
        self.assertTrue(result)
        mock_smtp.ehlo.assert_called_once()
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once_with("from@gmail.com", "secret")


class TestSendToChannelUnknown(unittest.TestCase):
    def test_unknown_channel_raises_value_error(self):
        cfg = make_config()
        with self.assertRaises(ValueError) as ctx:
            send_to_channel(MSG, "carrier_pigeon", cfg)
        self.assertIn("carrier_pigeon", str(ctx.exception))


# ---- deliver() tests -------------------------------------------------------

class TestDeliver(unittest.TestCase):
    def test_dry_run_returns_true(self):
        cfg = make_config(channel="slack", slack_webhook="https://hooks.slack.com/test")
        with patch("builtins.print"):
            result = deliver(MSG, cfg, dry_run=True)
        self.assertTrue(result)

    def test_dry_run_prints_dry_run_header(self):
        cfg = make_config(channel="slack")
        with patch("builtins.print") as mock_print:
            deliver(MSG, cfg, dry_run=True)
        printed = " ".join(str(c) for c in mock_print.call_args_list)
        self.assertIn("dry run", printed.lower())

    def test_channel_none_returns_true(self):
        cfg = make_config(channel="none")
        with patch("builtins.print"):
            result = deliver(MSG, cfg, dry_run=False)
        self.assertTrue(result)

    def test_delegates_to_send_to_channel(self):
        cfg = make_config(channel="terminal")
        with patch("delivery.send_to_channel", return_value=True) as mock_send:
            result = deliver(MSG, cfg, dry_run=False)
        mock_send.assert_called_once_with(MSG, "terminal", cfg)
        self.assertTrue(result)


# ---- deliver_multi() tests -------------------------------------------------

class TestDeliverMulti(unittest.TestCase):
    def test_dry_run_with_multiple_channels(self):
        cfg = make_config(channel="terminal", channels=["terminal", "slack"])
        with patch("builtins.print"):
            results = deliver_multi(MSG, cfg, dry_run=True, max_channels=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0], ("terminal", True))
        self.assertEqual(results[1], ("slack", True))

    def test_dry_run_single_channel_fallback(self):
        cfg = make_config(channel="terminal", channels=[])
        with patch("builtins.print"):
            results = deliver_multi(MSG, cfg, dry_run=True, max_channels=1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], ("terminal", True))

    def test_respects_max_channels_limit(self):
        cfg = make_config(channel="terminal", channels=["terminal", "slack", "telegram", "email"])
        with patch("builtins.print"):
            results = deliver_multi(MSG, cfg, dry_run=True, max_channels=2)
        self.assertEqual(len(results), 2)

    def test_max_channels_1_standard(self):
        cfg = make_config(channel="terminal", channels=["terminal", "slack"])
        with patch("builtins.print"):
            results = deliver_multi(MSG, cfg, dry_run=True, max_channels=1)
        self.assertEqual(len(results), 1)

    def test_max_channels_3_pro(self):
        cfg = make_config(channels=["terminal", "slack", "telegram"])
        with patch("delivery.send_to_channel", return_value=True):
            results = deliver_multi(MSG, cfg, dry_run=False, max_channels=3)
        self.assertEqual(len(results), 3)
        self.assertTrue(all(ok for _, ok in results))

    def test_failed_channel_returns_false_does_not_raise(self):
        cfg = make_config(channels=["terminal", "slack"])
        def side_effect(msg, ch, c):
            if ch == "slack":
                raise RuntimeError("Slack is down")
            return True
        with patch("delivery.send_to_channel", side_effect=side_effect), \
             patch("builtins.print"):
            results = deliver_multi(MSG, cfg, dry_run=False, max_channels=2)
        self.assertEqual(results[0], ("terminal", True))
        self.assertEqual(results[1], ("slack", False))

    def test_returns_list_of_tuples(self):
        cfg = make_config(channel="terminal", channels=[])
        with patch("delivery.send_to_channel", return_value=True):
            results = deliver_multi(MSG, cfg, dry_run=False, max_channels=1)
        self.assertIsInstance(results, list)
        self.assertIsInstance(results[0], tuple)


# ---- DeliveryConfig.from_config() tests ------------------------------------

class TestDeliveryConfigFromConfig(unittest.TestCase):
    def test_from_config_basic(self):
        raw = {
            "delivery": {
                "channel": "slack",
                "slack_webhook": "https://hooks.slack.com/abc",
                "recipient": "+15550000001",
            }
        }
        cfg = DeliveryConfig.from_config(raw)
        self.assertEqual(cfg.channel, "slack")
        self.assertEqual(cfg.slack_webhook, "https://hooks.slack.com/abc")
        self.assertEqual(cfg.recipient, "+15550000001")

    def test_from_config_legacy_imessage_recipient(self):
        """Legacy imessage_recipient key must map to recipient."""
        raw = {
            "delivery": {
                "channel": "imessage",
                "imessage_recipient": "+15551234567",
            }
        }
        cfg = DeliveryConfig.from_config(raw)
        self.assertEqual(cfg.recipient, "+15551234567")

    def test_from_config_recipient_preferred_over_legacy(self):
        """recipient takes precedence over imessage_recipient."""
        raw = {
            "delivery": {
                "channel": "imessage",
                "recipient": "+15559999999",
                "imessage_recipient": "+15550000000",
            }
        }
        cfg = DeliveryConfig.from_config(raw)
        self.assertEqual(cfg.recipient, "+15559999999")

    def test_from_config_empty_delivery(self):
        """Missing delivery section yields safe defaults."""
        cfg = DeliveryConfig.from_config({})
        self.assertEqual(cfg.channel, "none")
        self.assertEqual(cfg.recipient, "")

    def test_from_config_smtp_port_as_string(self):
        """smtp_port from config (often a string) is cast to int."""
        raw = {
            "delivery": {
                "smtp_port": "465",
                "channel": "email",
            }
        }
        cfg = DeliveryConfig.from_config(raw)
        self.assertEqual(cfg.smtp_port, 465)
        self.assertIsInstance(cfg.smtp_port, int)

    def test_from_config_multi_channels(self):
        raw = {
            "delivery": {
                "channel": "terminal",
                "channels": ["terminal", "slack", "telegram"],
            }
        }
        cfg = DeliveryConfig.from_config(raw)
        self.assertEqual(cfg.channels, ["terminal", "slack", "telegram"])

    def test_get_channels_uses_channels_list(self):
        cfg = make_config(channel="terminal", channels=["slack", "telegram", "terminal"])
        self.assertEqual(cfg.get_channels(3), ["slack", "telegram", "terminal"])
        self.assertEqual(cfg.get_channels(2), ["slack", "telegram"])
        self.assertEqual(cfg.get_channels(1), ["slack"])

    def test_get_channels_falls_back_to_channel(self):
        cfg = make_config(channel="slack", channels=[])
        self.assertEqual(cfg.get_channels(3), ["slack"])


if __name__ == "__main__":
    unittest.main()
