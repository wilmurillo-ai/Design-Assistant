#!/usr/bin/env python3
"""
Northstar Plan Gating Tests (Phase 1 Step 3)

Verifies that feature access is correctly gated per tier (lite, standard, pro).
Focus: FEATURE GATING behavior, not API functionality or HMAC spoofing
(HMAC spoofing tests already exist in test_northstar_pro.py).
"""

import sys
import io
import hmac
import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts dir to path
scripts_dir = str(Path(__file__).parent.parent / "scripts")
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

# Load northstar first (needed by northstar_pro)
import northstar  # noqa: F401,E402

import importlib.util  # noqa: E402


def load_pro():
    """Load northstar_pro module fresh for testing."""
    pro_path = Path(__file__).parent.parent / "scripts" / "northstar_pro.py"
    spec = importlib.util.spec_from_file_location("northstar_pro", pro_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["northstar_pro"] = mod
    spec.loader.exec_module(mod)
    return mod


pro = load_pro()

# ── Config helpers ──────────────────────────────────────────────────────────

def make_config(tier="lite", key=None, token=None,
                stripe_enabled=True, shopify_enabled=False):
    """Build a test config dict."""
    config = {"tier": tier}
    if key:
        config["license_key"] = key
    if token:
        config["license_token"] = token
    if stripe_enabled:
        config["stripe"] = {
            "enabled": True,
            "api_key": "sk_live_test123",
            "monthly_revenue_goal": 10000,
            "currency": "usd",
        }
    if shopify_enabled:
        config["shopify"] = {
            "enabled": True,
            "shop_domain": "test.myshopify.com",
            "access_token": "shpat_test123",
        }
    return config


def make_pro_config(**kwargs):
    key = "NSP-TEST-1234-ABCD"
    secret = b"northstar-v1-dg0823-k92x7"
    token = hmac.new(secret, f"{key.upper()}:pro".encode(), hashlib.sha256).hexdigest()
    return make_config(tier="pro", key=key, token=token, **kwargs)


def make_standard_config(**kwargs):
    key = "NSS-TEST-5678-EFGH"
    secret = b"northstar-v1-dg0823-k92x7"
    token = hmac.new(secret, f"{key.upper()}:standard".encode(), hashlib.sha256).hexdigest()
    return make_config(tier="standard", key=key, token=token, **kwargs)


# ── 1. TestReportGating ─────────────────────────────────────────────────────

class TestReportGating(unittest.TestCase):
    """cmd_report() checks tier directly and returns (no sys.exit)."""

    def _capture_report(self, config):
        """Run cmd_report and capture stdout."""
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            northstar.cmd_report(config)
        return buf.getvalue()

    def test_report_blocked_for_lite(self):
        """Lite tier gets 'requires Pro tier' message and returns without sys.exit."""
        config = make_config(tier="lite")
        output = self._capture_report(config)
        self.assertIn("Pro", output)
        # Also verify the exact gating message from the code
        self.assertIn("report", output.lower())

    def test_report_blocked_for_standard(self):
        """Standard tier gets 'requires Pro tier' message and returns without sys.exit."""
        config = make_standard_config()
        output = self._capture_report(config)
        self.assertIn("Pro", output)

    def test_report_allowed_for_pro(self):
        """Pro tier does NOT print the Pro-required message (gating passes)."""
        config = make_pro_config()
        # Mock the API calls so they don't hit Stripe/Shopify
        with patch.object(northstar, "fetch_stripe_metrics") as mock_stripe:
            mock_stripe.return_value = {
                "revenue_yesterday": 500.0,
                "revenue_last_week_same_day": 400.0,
                "wow_change_pct": 25.0,
                "revenue_mtd": 8000.0,
                "goal_dollars": 10000.0,
                "goal_pct": 80.0,
                "days_remaining": 5,
                "days_in_month": 31,
                "on_track": True,
                "projected_month": 10500.0,
                "active_subs": 100,
                "new_subs": 2,
                "churned_subs": 0,
                "payment_failures": 0,
                "retries_pending": 0,
                "mrr": 5000.0,
            }
            # Also mock the Pro trend fetch called inside cmd_report
            with patch.object(pro, "fetch_7day_trend", side_effect=Exception("no stripe")):
                buf = io.StringIO()
                with patch("sys.stdout", buf):
                    northstar.cmd_report(config)
                output = buf.getvalue()

        # Should NOT show "requires Pro tier" gating message
        self.assertNotIn("requires Pro tier", output)
        self.assertNotIn("Upgrade at:", output)


# ── 2. TestDigestGating ─────────────────────────────────────────────────────

class TestDigestGating(unittest.TestCase):
    """cmd_digest() uses require_pro() which calls sys.exit(1) on failure."""

    def test_digest_blocked_for_lite(self):
        """Lite tier triggers sys.exit(1) via require_pro."""
        config = make_config(tier="lite")
        with self.assertRaises(SystemExit) as ctx:
            with patch("sys.stdout", io.StringIO()):
                pro.cmd_digest(config)
        self.assertEqual(ctx.exception.code, 1)

    def test_digest_blocked_for_standard(self):
        """Standard tier triggers sys.exit(1) via require_pro."""
        config = make_standard_config()
        with self.assertRaises(SystemExit) as ctx:
            with patch("sys.stdout", io.StringIO()):
                pro.cmd_digest(config)
        self.assertEqual(ctx.exception.code, 1)

    def test_digest_allowed_for_pro(self):
        """Pro tier does NOT call sys.exit - gating passes, API calls are mocked."""
        config = make_pro_config()
        fake_stripe_data = {
            "revenue_yesterday": 200.0,
            "revenue_last_week_same_day": 180.0,
            "wow_change_pct": 11.0,
            "revenue_mtd": 4000.0,
            "goal_dollars": 10000.0,
            "goal_pct": 40.0,
            "days_remaining": 8,
            "days_in_month": 31,
            "on_track": False,
            "projected_month": 7000.0,
            "active_subs": 50,
            "new_subs": 1,
            "churned_subs": 0,
            "payment_failures": 0,
            "retries_pending": 0,
            "mrr": 2500.0,
        }
        # Mock everything that would make real network calls.
        # cmd_digest imports fetch_stripe_metrics from northstar, so patch it there.
        with patch.object(northstar, "fetch_stripe_metrics", return_value=fake_stripe_data):
            with patch.object(pro, "fetch_7day_trend", return_value=[]):
                with patch.object(pro, "deliver_multi"):
                    with patch("sys.stdout", io.StringIO()):
                        try:
                            pro.cmd_digest(config, dry_run=True)
                        except SystemExit:
                            self.fail("cmd_digest raised SystemExit for a valid Pro config")


# ── 3. TestTrendGating ──────────────────────────────────────────────────────

class TestTrendGating(unittest.TestCase):
    """cmd_trend() uses require_pro() which calls sys.exit(1) on failure."""

    def test_trend_blocked_for_lite(self):
        """Lite tier triggers sys.exit(1) via require_pro."""
        config = make_config(tier="lite")
        with self.assertRaises(SystemExit) as ctx:
            with patch("sys.stdout", io.StringIO()):
                pro.cmd_trend(config)
        self.assertEqual(ctx.exception.code, 1)

    def test_trend_blocked_for_standard(self):
        """Standard tier triggers sys.exit(1) via require_pro."""
        config = make_standard_config()
        with self.assertRaises(SystemExit) as ctx:
            with patch("sys.stdout", io.StringIO()):
                pro.cmd_trend(config)
        self.assertEqual(ctx.exception.code, 1)

    def test_trend_allowed_for_pro(self):
        """Pro tier does NOT call sys.exit - gating passes, API calls are mocked."""
        config = make_pro_config()
        mock_trend = [
            {"date": "2026-03-17", "label": "Mon", "revenue_cents": 50000},
            {"date": "2026-03-18", "label": "Tue", "revenue_cents": 60000},
            {"date": "2026-03-19", "label": "Wed", "revenue_cents": 55000},
            {"date": "2026-03-20", "label": "Thu", "revenue_cents": 70000},
            {"date": "2026-03-21", "label": "Fri", "revenue_cents": 80000},
            {"date": "2026-03-22", "label": "Sat", "revenue_cents": 45000},
            {"date": "2026-03-23", "label": "Sun", "revenue_cents": 40000},
        ]
        with patch.object(pro, "fetch_7day_trend", return_value=mock_trend):
            with patch("sys.stdout", io.StringIO()):
                try:
                    pro.cmd_trend(config)
                except SystemExit:
                    self.fail("cmd_trend raised SystemExit for a valid Pro config")


# ── 4. TestMultiChannelGating ────────────────────────────────────────────────

class TestMultiChannelGating(unittest.TestCase):
    """deliver_multi() limits channels based on tier."""

    def _run_deliver_multi(self, config, message="test"):
        """Run deliver_multi, capturing the max_channels argument used."""
        captured_max = {}

        # We need to patch the underlying unified_deliver_multi
        # The call chain is: pro.deliver_multi -> delivery.deliver_multi
        # Patch at the delivery module level
        with patch("delivery.deliver_multi") as mock_deliver:
            mock_deliver.return_value = True
            pro.deliver_multi(message, config, dry_run=True)
            if mock_deliver.called:
                # max_channels is the 4th positional arg
                call_args = mock_deliver.call_args
                if call_args.args:
                    captured_max["max_channels"] = call_args.args[3] if len(call_args.args) > 3 else None
                elif call_args.kwargs:
                    captured_max["max_channels"] = call_args.kwargs.get("max_channels")
        return captured_max

    def test_lite_no_delivery(self):
        """Lite tier: deliver_multi limits to 1 channel (max_channels=1)."""
        config = make_config(tier="lite")
        result = self._run_deliver_multi(config)
        self.assertEqual(result.get("max_channels"), 1,
                         "Lite tier should have max_channels=1")

    def test_standard_single_channel(self):
        """Standard tier: deliver_multi limits to 1 channel (max_channels=1)."""
        config = make_standard_config()
        result = self._run_deliver_multi(config)
        self.assertEqual(result.get("max_channels"), 1,
                         "Standard tier should have max_channels=1")

    def test_pro_multi_channel(self):
        """Pro tier: deliver_multi allows 3 channels (max_channels=3)."""
        config = make_pro_config()
        result = self._run_deliver_multi(config)
        self.assertEqual(result.get("max_channels"), 3,
                         "Pro tier should have max_channels=3")


# ── 5. TestIsProGating ───────────────────────────────────────────────────────

class TestIsProGating(unittest.TestCase):
    """is_pro() correctly identifies valid Pro configs."""

    def test_is_pro_false_for_lite(self):
        """Lite tier is not Pro."""
        config = make_config(tier="lite")
        self.assertFalse(pro.is_pro(config))

    def test_is_pro_false_for_standard(self):
        """Standard tier is not Pro."""
        config = make_standard_config()
        self.assertFalse(pro.is_pro(config))

    def test_is_pro_true_for_valid_pro(self):
        """Valid Pro config with correct HMAC token is Pro."""
        config = make_pro_config()
        self.assertTrue(pro.is_pro(config))

    def test_is_pro_false_for_spoofed_pro(self):
        """
        tier=pro with no valid token is NOT Pro.
        Config edit alone cannot grant Pro access -- HMAC token must match.
        """
        # Spoofed: manually set tier=pro but provide no token
        config = make_config(tier="pro", key=None, token=None)
        # verify_license_token returns False for pro tier with no key
        self.assertFalse(northstar.verify_license_token(config))
        self.assertFalse(pro.is_pro(config))

    def test_is_pro_false_for_wrong_token(self):
        """tier=pro with a token that doesn't match the key is NOT Pro."""
        # Build config with a token signed for a different key
        config = make_config(tier="pro")
        config["license_key"] = "NSP-FAKE-XXXX-YYYY"
        config["license_token"] = "deadbeef" * 8  # garbage token, 64 hex chars
        self.assertFalse(northstar.verify_license_token(config))
        self.assertFalse(pro.is_pro(config))


# ── 6. TestUpgradeDisplay ────────────────────────────────────────────────────

class TestUpgradeDisplay(unittest.TestCase):
    """cmd_upgrade() shows appropriate tier options based on current tier."""

    def _capture_upgrade(self, config):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            northstar.cmd_upgrade(config)
        return buf.getvalue()

    def test_upgrade_from_lite_shows_both_tiers(self):
        """Lite users see both Standard and Pro upgrade options."""
        config = make_config(tier="lite")
        output = self._capture_upgrade(config)
        self.assertIn("Standard", output)
        self.assertIn("Pro", output)

    def test_upgrade_from_standard_shows_pro_only(self):
        """Standard users see Pro upgrade but NOT Standard as an upgrade option."""
        config = make_standard_config()
        output = self._capture_upgrade(config)
        self.assertIn("Pro", output)
        # "Standard (current)" is shown as current tier label - that's fine.
        # But there should NOT be a "Upgrade to Standard" option.
        # Check that "Standard" only appears as the current tier description,
        # not as a new tier to purchase.
        self.assertNotIn("Get Standard:", output)
        self.assertNotIn("$19/month\n  ┣", output)  # Standard tier block shown for lite only

    def test_upgrade_from_pro_shows_top_tier(self):
        """Pro users see a 'top tier / no upgrades' message."""
        config = make_pro_config()
        output = self._capture_upgrade(config)
        # The code says "No upgrades available -- you're at the top tier."
        top_tier_message = (
            "top tier" in output.lower()
            or "No upgrades" in output
            or "no upgrades" in output.lower()
        )
        self.assertTrue(top_tier_message,
                        f"Expected top-tier message in Pro upgrade output, got:\n{output}")


# ── 7. TestDataSourceGating ─────────────────────────────────────────────────

class TestDataSourceGating(unittest.TestCase):
    """
    Data source gating behavior verification.

    NOTE: Data source gating is NOT currently implemented per tier.
    Lite tier allows all configured data sources (Stripe, Shopify, etc.).
    These tests document current behavior so we know if it changes.
    """

    def test_lite_can_fetch_all_configured_sources(self):
        """
        NOTE: data source gating is not currently implemented per tier -
        Lite allows all configured sources.

        Lite + Shopify config: cmd_run DOES attempt shopify fetch (no gating).
        We verify that fetch_shopify_metrics is called for a lite config that
        has shopify configured -- confirming the current ungated behavior.
        """
        config = make_config(tier="lite", shopify_enabled=True)

        with patch.object(northstar, "fetch_stripe_metrics") as mock_stripe, \
             patch.object(northstar, "fetch_shopify_metrics") as mock_shopify, \
             patch.object(northstar, "deliver") as mock_deliver, \
             patch.object(northstar, "save_state"), \
             patch.object(northstar, "load_state", return_value={"runs": 0}):

            mock_stripe.return_value = {
                "revenue_yesterday": 100.0,
                "revenue_last_week_same_day": 90.0,
                "wow_change_pct": 11.0,
                "revenue_mtd": 2000.0,
                "goal_dollars": 10000.0,
                "goal_pct": 20.0,
                "days_remaining": 7,
                "days_in_month": 31,
                "on_track": False,
                "projected_month": 8000.0,
                "active_subs": 20,
                "new_subs": 0,
                "churned_subs": 0,
                "payment_failures": 0,
                "retries_pending": 0,
                "mrr": 500.0,
            }
            mock_shopify.return_value = {
                "orders_total": 5,
                "orders_fulfilled": 4,
                "orders_open": 1,
                "refunds_count": 0,
                "refund_total": 0.0,
                "top_product": "Widget",
                "top_product_units": 4,
            }
            mock_deliver.return_value = True

            with patch("sys.stdout", io.StringIO()):
                northstar.cmd_run(config, dry_run=True)

        # Assert shopify was attempted -- no tier gating blocked it
        mock_shopify.assert_called_once()

    def test_lite_can_fetch_stripe_without_gating(self):
        """
        NOTE: Stripe fetch is also ungated by tier.
        Lite tier fetches Stripe just like Standard/Pro.
        Documents current behavior - no tier check before data source fetch.
        """
        config = make_config(tier="lite")

        with patch.object(northstar, "fetch_stripe_metrics") as mock_stripe, \
             patch.object(northstar, "deliver") as mock_deliver, \
             patch.object(northstar, "save_state"), \
             patch.object(northstar, "load_state", return_value={"runs": 0}):

            mock_stripe.return_value = {
                "revenue_yesterday": 50.0,
                "revenue_last_week_same_day": 40.0,
                "wow_change_pct": 25.0,
                "revenue_mtd": 1000.0,
                "goal_dollars": 10000.0,
                "goal_pct": 10.0,
                "days_remaining": 10,
                "days_in_month": 31,
                "on_track": False,
                "projected_month": 3000.0,
                "active_subs": 10,
                "new_subs": 0,
                "churned_subs": 0,
                "payment_failures": 0,
                "retries_pending": 0,
                "mrr": 300.0,
            }
            mock_deliver.return_value = True

            with patch("sys.stdout", io.StringIO()):
                northstar.cmd_run(config, dry_run=True)

        # Stripe fetch was NOT gated by tier
        mock_stripe.assert_called_once()


if __name__ == "__main__":
    unittest.main()
