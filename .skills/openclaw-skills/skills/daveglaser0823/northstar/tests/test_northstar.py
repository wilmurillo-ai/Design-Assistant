#!/usr/bin/env python3
"""
Northstar Unit Tests
Tests briefing formatting and calculation logic without hitting live APIs.
"""

import sys
import json
import unittest
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from northstar import build_briefing, fmt_currency, fmt_pct

# ---- Sample data fixtures --------------------------------------------------

SAMPLE_CONFIG = {
    "delivery": {"channel": "none"},
    "stripe": {
        "enabled": True,
        "api_key": "sk_test_fake",
        "monthly_revenue_goal": 24900,
        "currency": "usd"
    },
    "shopify": {
        "enabled": True,
        "shop_domain": "test.myshopify.com",
        "access_token": "shpat_fake"
    },
    "alerts": {
        "payment_failures": True,
        "churn_threshold": 3,
        "large_refund_threshold": 100
    },
    "format": {
        "emoji": True,
        "include_pacing": True,
        "include_shopify_detail": True
    }
}

SAMPLE_STRIPE = {
    "revenue_yesterday": 1247.50,
    "revenue_last_week_same_day": 1113.84,
    "wow_change_pct": 12.0,
    "revenue_mtd": 18430.00,
    "goal_dollars": 24900.0,
    "goal_pct": 74.0,
    "days_remaining": 6,
    "on_track": True,
    "projected_month": 25200.0,
    "active_subs": 342,
    "new_subs": 3,
    "churned_subs": 1,
    "payment_failures": 0,
    "retries_pending": 2,
}

SAMPLE_SHOPIFY = {
    "orders_total": 32,
    "orders_fulfilled": 23,
    "orders_open": 8,
    "refunds_count": 1,
    "refund_total": 47.00,
    "top_product": "Growth Plan",
    "top_product_units": 12,
}

# ---- Tests -----------------------------------------------------------------

class TestFormatting(unittest.TestCase):
    def test_fmt_currency_small(self):
        self.assertEqual(fmt_currency(47.0), "$47.00")

    def test_fmt_currency_large(self):
        self.assertEqual(fmt_currency(18430.0), "$18,430")

    def test_fmt_pct_positive(self):
        self.assertEqual(fmt_pct(12.0), "+12%")

    def test_fmt_pct_negative(self):
        self.assertEqual(fmt_pct(-5.0), "-5%")

    def test_fmt_pct_no_sign(self):
        self.assertEqual(fmt_pct(74.0, sign=False), "74%")


class TestBriefingBuild(unittest.TestCase):
    def test_builds_with_both_sources(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY)
        self.assertIn("Northstar Daily Briefing", result)
        self.assertIn("1,248", result)  # revenue (1247.50 rounds to 1248)
        self.assertIn("342", result)    # subscribers
        self.assertIn("74%", result)    # MTD goal pct
        self.assertIn("Shopify", result)
        self.assertIn("23 orders", result)
        self.assertIn("on track", result)

    def test_builds_stripe_only(self):
        config = dict(SAMPLE_CONFIG)
        config["shopify"] = {"enabled": False}
        result = build_briefing(config, SAMPLE_STRIPE, None)
        self.assertIn("Revenue yesterday", result)
        self.assertNotIn("Shopify", result)

    def test_payment_alert_fires(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY)
        self.assertIn("payment issue", result)  # 2 retries pending

    def test_high_churn_alert(self):
        stripe_high_churn = dict(SAMPLE_STRIPE)
        stripe_high_churn["churned_subs"] = 5
        result = build_briefing(SAMPLE_CONFIG, stripe_high_churn, SAMPLE_SHOPIFY)
        self.assertIn("High churn", result)

    def test_no_churn_no_alert(self):
        stripe_no_churn = dict(SAMPLE_STRIPE)
        stripe_no_churn["churned_subs"] = 0
        stripe_no_churn["retries_pending"] = 0
        stripe_no_churn["payment_failures"] = 0
        result = build_briefing(SAMPLE_CONFIG, stripe_no_churn, SAMPLE_SHOPIFY)
        self.assertNotIn("churn", result.lower().split("cancel")[0])  # no churn alert

    def test_wow_change_shown(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY)
        self.assertIn("+12%", result)

    def test_no_emoji_mode(self):
        config = dict(SAMPLE_CONFIG)
        config["format"] = {"emoji": False, "include_pacing": True}
        result = build_briefing(config, SAMPLE_STRIPE, SAMPLE_SHOPIFY)
        self.assertNotIn("📊", result)
        self.assertNotIn("⚠️", result)

    def test_no_goal_set(self):
        stripe_no_goal = dict(SAMPLE_STRIPE)
        stripe_no_goal["goal_dollars"] = 0
        stripe_no_goal["goal_pct"] = None
        result = build_briefing(SAMPLE_CONFIG, stripe_no_goal, None)
        self.assertIn("Month-to-date", result)
        self.assertNotIn("% of", result)

    def test_empty_sources_not_crash(self):
        """Should gracefully handle None for both sources."""
        # With no data, build_briefing won't be called (cmd_run guards this)
        # But test the format path with minimal data
        minimal_stripe = {
            "revenue_yesterday": 0.0,
            "revenue_last_week_same_day": 0.0,
            "wow_change_pct": None,
            "revenue_mtd": 0.0,
            "goal_dollars": 0.0,
            "goal_pct": None,
            "days_remaining": 10,
            "on_track": None,
            "projected_month": 0.0,
            "active_subs": 0,
            "new_subs": 0,
            "churned_subs": 0,
            "payment_failures": 0,
            "retries_pending": 0,
        }
        result = build_briefing(SAMPLE_CONFIG, minimal_stripe, None)
        self.assertIn("Northstar", result)


SAMPLE_GUMROAD = {
    "source": "gumroad",
    "revenue_yesterday": 342.00,
    "revenue_last_week_same_day": 275.00,
    "wow_change_pct": 24.4,
    "revenue_mtd": 4100.00,
    "goal_dollars": 5000.0,
    "goal_pct": 82.0,
    "days_remaining": 8,
    "on_track": True,
    "projected_month": 4920.00,
    "sales_count": 17,
    "refunds_count": 0,
    "refund_total": 0.0,
}


class TestGumroadBriefing(unittest.TestCase):
    def test_gumroad_revenue_shown(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, SAMPLE_GUMROAD)
        self.assertIn("Gumroad", result)
        self.assertIn("$342.00", result)

    def test_gumroad_wow_shown(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, SAMPLE_GUMROAD)
        self.assertIn("+24%", result)

    def test_gumroad_mtd_shown(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, SAMPLE_GUMROAD)
        self.assertIn("GR month-to-date", result)
        self.assertIn("82%", result)

    def test_gumroad_sales_count_shown(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, SAMPLE_GUMROAD)
        self.assertIn("17 sales", result)

    def test_gumroad_refund_alert(self):
        gr_with_refund = dict(SAMPLE_GUMROAD)
        gr_with_refund["refund_total"] = 150.0
        gr_with_refund["refunds_count"] = 2
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, gr_with_refund)
        self.assertIn("Gumroad refund", result)

    def test_gumroad_no_refund_no_alert(self):
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, SAMPLE_GUMROAD)
        self.assertNotIn("Gumroad refund", result)

    def test_gumroad_none_skipped(self):
        """None gumroad_data should not include Gumroad section."""
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, None)
        self.assertNotIn("Gumroad", result)

    def test_gumroad_no_goal_no_pct(self):
        gr_no_goal = dict(SAMPLE_GUMROAD)
        gr_no_goal["goal_dollars"] = 0
        gr_no_goal["goal_pct"] = None
        result = build_briefing(SAMPLE_CONFIG, SAMPLE_STRIPE, SAMPLE_SHOPIFY, None, gr_no_goal)
        self.assertIn("GR month-to-date", result)
        # Should not show percentage if no goal set
        self.assertNotIn("% of $0", result)


class TestDelivery(unittest.TestCase):
    def test_imessage_recipient_fallback(self):
        """deliver() should use imessage_recipient if recipient is missing."""
        from northstar import deliver
        # Config uses legacy imessage_recipient, no 'recipient' key
        cfg = {
            "delivery": {
                "channel": "none",  # dry_run equivalent: channel=none won't actually send
                "imessage_recipient": "+15551234567",
            }
        }
        # Should not raise (dry_run path via channel=none)
        result = deliver("test message", cfg, dry_run=False)
        self.assertTrue(result)

    def test_recipient_takes_priority_over_imessage_recipient(self):
        """'recipient' key should take priority over 'imessage_recipient'."""
        from northstar import deliver
        cfg = {
            "delivery": {
                "channel": "none",
                "recipient": "+15559999999",
                "imessage_recipient": "+15551234567",
            }
        }
        result = deliver("test message", cfg, dry_run=False)
        self.assertTrue(result)

    def test_dry_run_prints_briefing(self):
        """dry_run=True should print briefing without sending."""
        from northstar import deliver
        import io
        from contextlib import redirect_stdout
        cfg = {"delivery": {"channel": "imessage", "recipient": "+15551234567"}}
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = deliver("hello briefing", cfg, dry_run=True)
        self.assertTrue(result)
        self.assertIn("hello briefing", buf.getvalue())


    def test_email_delivery_missing_credentials_raises(self):
        """Email delivery with missing credentials should raise ValueError."""
        from northstar import deliver
        cfg = {
            "delivery": {
                "channel": "email",
                "email_to": "",  # missing
                "smtp_user": "",
                "smtp_password": "",
            }
        }
        with self.assertRaises(ValueError) as cm:
            deliver("test", cfg)
        self.assertIn("smtp_user", str(cm.exception))

    def test_email_delivery_dry_run_bypasses_smtp(self):
        """dry_run=True with email channel should print without connecting to SMTP."""
        from northstar import deliver
        import io
        from contextlib import redirect_stdout
        cfg = {
            "delivery": {
                "channel": "email",
                "email_to": "user@example.com",
                "smtp_user": "sender@gmail.com",
                "smtp_password": "fakepassword",
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
            }
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            result = deliver("email test message", cfg, dry_run=True)
        self.assertTrue(result)
        self.assertIn("email test message", buf.getvalue())


class TestConfigLoading(unittest.TestCase):
    def test_missing_config_raises(self):
        from northstar import load_config
        bad_path = Path("/tmp/nonexistent_northstar_config.json")
        with self.assertRaises(FileNotFoundError):
            load_config(bad_path)


class TestActivateCommand(unittest.TestCase):
    def test_activate_invalid_key_format(self):
        """Invalid key prefix should print error and exit."""
        from northstar import cmd_activate
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            with redirect_stdout(buf):
                cmd_activate("INVALID-KEY")
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Invalid license key format", buf.getvalue())

    def test_activate_no_key_shows_usage(self):
        """Empty key shows usage with purchase URL."""
        from northstar import cmd_activate
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_activate("")
        output = buf.getvalue()
        self.assertIn("Usage: northstar activate", output)
        self.assertIn("polar.sh/daveglaser0823/northstar-standard", output)

    def test_activate_std_key_validates(self):
        """NS-STD- prefix correctly identified as standard tier."""
        from northstar import cmd_activate
        import io
        import tempfile
        import os
        from contextlib import redirect_stdout
        from pathlib import Path
        # Write a minimal config to a temp file
        cfg = {"tier": "lite", "delivery": {}, "stripe": {}, "schedule": {}}
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(cfg, tmp)
        tmp.close()
        # Patch CONFIG_PATH temporarily
        import northstar as ns
        original = ns.CONFIG_PATH
        ns.CONFIG_PATH = Path(tmp.name)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                cmd_activate("NS-STD-TEST-ABCD-1234")
        finally:
            ns.CONFIG_PATH = original
            os.unlink(tmp.name)
        output = buf.getvalue()
        self.assertIn("standard", output.lower())

    def test_activate_pro_key_validates(self):
        """NS-PRO- prefix correctly identified as pro tier."""
        from northstar import cmd_activate
        import io
        import tempfile
        import os
        from contextlib import redirect_stdout
        from pathlib import Path
        cfg = {"tier": "lite", "delivery": {}, "stripe": {}, "schedule": {}}
        tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(cfg, tmp)
        tmp.close()
        import northstar as ns
        original = ns.CONFIG_PATH
        ns.CONFIG_PATH = Path(tmp.name)
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                cmd_activate("NS-PRO-TEST-ABCD-5678")
        finally:
            ns.CONFIG_PATH = original
            os.unlink(tmp.name)
        output = buf.getvalue()
        self.assertIn("pro", output.lower())


    def test_activate_revoked_key_rejected(self):
        """Revoked keys (exposed publicly) should be rejected at activation."""
        from northstar import cmd_activate
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            with redirect_stdout(buf):
                cmd_activate("NS-PRO-DTML-H6TK-SACG")
        self.assertEqual(cm.exception.code, 1)
        output = buf.getvalue()
        self.assertIn("revoked", output.lower())

    def test_report_requires_pro(self):
        """northstar report should reject non-Pro configs."""
        from northstar import cmd_report
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_report({"tier": "lite"})
        output = buf.getvalue()
        self.assertIn("Pro", output)

    def test_report_requires_pro_standard_tier(self):
        """northstar report should also reject standard tier."""
        from northstar import cmd_report
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_report({"tier": "standard"})
        output = buf.getvalue()
        self.assertIn("Pro", output)

    def test_upgrade_lite_shows_standard_and_pro(self):
        """northstar upgrade shows Standard + Pro links for Lite users."""
        from northstar import cmd_upgrade
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_upgrade({"tier": "lite"})
        output = buf.getvalue()
        self.assertIn("Standard", output)
        self.assertIn("19", output)
        self.assertIn("Pro", output)
        self.assertIn("49", output)
        self.assertIn("polar.sh", output)

    def test_upgrade_standard_shows_pro(self):
        """northstar upgrade shows Pro upgrade for Standard users."""
        from northstar import cmd_upgrade
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_upgrade({"tier": "standard"})
        output = buf.getvalue()
        self.assertIn("Pro", output)
        self.assertIn("49", output)
        self.assertIn("polar.sh", output)

    def test_upgrade_pro_shows_no_upgrade(self):
        """northstar upgrade shows all-clear for Pro users."""
        from northstar import cmd_upgrade
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_upgrade({"tier": "pro"})
        output = buf.getvalue()
        self.assertIn("top tier", output)


# ---- Runner ----------------------------------------------------------------

if __name__ == "__main__":
    print("Running Northstar tests...\n")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    print(f"\n{'PASS' if result.wasSuccessful() else 'FAIL'}: {result.testsRun} tests, "
          f"{len(result.failures)} failures, {len(result.errors)} errors")
    sys.exit(0 if result.wasSuccessful() else 1)
