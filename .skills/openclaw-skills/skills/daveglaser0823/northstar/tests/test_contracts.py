"""
Contract Tests - Verify data models match between adapters and consumers.

These tests freeze the interface contracts between:
  - fetch_stripe_metrics() -> StripeMetrics -> build_briefing() / build_weekly_digest()
  - fetch_shopify_metrics() -> ShopifyMetrics -> build_briefing() / build_weekly_digest()
  - DeliveryConfig -> deliver() / deliver_multi()

If these tests break, it means a module boundary changed without updating both sides.

Created: March 24, 2026 (Phase 1, Architecture Fix)
"""

import sys
import os
from dataclasses import fields

# Add scripts dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from models import (
    StripeMetrics,
    ShopifyMetrics,
    GumroadMetrics,
    LemonSqueezyMetrics,
    DeliveryConfig,
)


# ---------------------------------------------------------------------------
# Contract: StripeMetrics has every field that build_briefing() accesses
# ---------------------------------------------------------------------------

class TestStripeContract:
    """Verify StripeMetrics has all fields consumers expect."""

    # Fields accessed by build_briefing() in northstar.py
    CORE_CONSUMER_FIELDS = {
        "revenue_yesterday",
        "revenue_last_week_same_day",
        "wow_change_pct",
        "revenue_mtd",
        "goal_dollars",
        "goal_pct",
        "days_remaining",
        "on_track",
        "projected_month",
        "active_subs",
        "new_subs",
        "churned_subs",
        "payment_failures",
        "retries_pending",
    }

    # Fields accessed by build_weekly_digest() / build_pro_additions() in northstar_pro.py
    PRO_CONSUMER_FIELDS = {
        "revenue_yesterday",
        "active_subs",
        "new_subs",
        "churned_subs",
        "payment_failures",
        "revenue_mtd",
        "goal_dollars",
        "days_remaining",
        "days_in_month",
        "mrr",
    }

    def test_stripe_model_has_core_fields(self):
        """StripeMetrics must have every field that build_briefing() accesses."""
        model_fields = {f.name for f in fields(StripeMetrics)}
        missing = self.CORE_CONSUMER_FIELDS - model_fields
        assert not missing, f"StripeMetrics missing fields used by build_briefing(): {missing}"

    def test_stripe_model_has_pro_fields(self):
        """StripeMetrics must have every field that Pro consumers access."""
        model_fields = {f.name for f in fields(StripeMetrics)}
        missing = self.PRO_CONSUMER_FIELDS - model_fields
        assert not missing, f"StripeMetrics missing fields used by Pro module: {missing}"

    def test_stripe_to_dict_roundtrip(self):
        """to_dict() must produce a dict with all model fields."""
        m = StripeMetrics(revenue_yesterday=1247.50, active_subs=342, new_subs=3)
        d = m.to_dict()
        assert d["revenue_yesterday"] == 1247.50
        assert d["active_subs"] == 342
        assert d["new_subs"] == 3
        # All fields present
        model_fields = {f.name for f in fields(StripeMetrics)}
        assert set(d.keys()) == model_fields

    def test_stripe_defaults_are_safe(self):
        """Default StripeMetrics should not cause division by zero or crashes."""
        m = StripeMetrics()
        assert m.revenue_yesterday == 0.0
        assert m.days_in_month == 30
        assert m.days_remaining == 0
        assert m.mrr == 0.0


# ---------------------------------------------------------------------------
# Contract: ShopifyMetrics has every field that consumers expect
# ---------------------------------------------------------------------------

class TestShopifyContract:
    """Verify ShopifyMetrics has all fields consumers expect."""

    # Fields accessed by build_briefing() in northstar.py
    CORE_CONSUMER_FIELDS = {
        "orders_total",
        "orders_fulfilled",
        "orders_open",
        "refunds_count",
        "refund_total",
        "top_product",
        "top_product_units",
    }

    def test_shopify_model_has_core_fields(self):
        model_fields = {f.name for f in fields(ShopifyMetrics)}
        missing = self.CORE_CONSUMER_FIELDS - model_fields
        assert not missing, f"ShopifyMetrics missing fields: {missing}"

    def test_shopify_to_dict_roundtrip(self):
        m = ShopifyMetrics(orders_total=23, orders_fulfilled=20, orders_open=3)
        d = m.to_dict()
        assert d["orders_total"] == 23
        assert d["orders_fulfilled"] == 20


# ---------------------------------------------------------------------------
# Contract: DeliveryConfig handles legacy keys
# ---------------------------------------------------------------------------

class TestDeliveryContract:
    """Verify DeliveryConfig correctly handles both old and new config shapes."""

    def test_recipient_from_new_key(self):
        config = {"delivery": {"channel": "imessage", "recipient": "+15551234567"}}
        dc = DeliveryConfig.from_config(config)
        assert dc.recipient == "+15551234567"
        assert dc.channel == "imessage"

    def test_recipient_from_legacy_key(self):
        """Config with only 'imessage_recipient' (no 'recipient') must still work."""
        config = {"delivery": {"channel": "imessage", "imessage_recipient": "+15559876543"}}
        dc = DeliveryConfig.from_config(config)
        assert dc.recipient == "+15559876543"

    def test_recipient_prefers_new_key(self):
        """When both keys exist, 'recipient' wins over 'imessage_recipient'."""
        config = {"delivery": {
            "channel": "imessage",
            "recipient": "+1NEW",
            "imessage_recipient": "+1OLD",
        }}
        dc = DeliveryConfig.from_config(config)
        assert dc.recipient == "+1NEW"

    def test_empty_delivery_config(self):
        """Empty config should not crash."""
        dc = DeliveryConfig.from_config({})
        assert dc.channel == "none"
        assert dc.recipient == ""

    def test_get_channels_single(self):
        dc = DeliveryConfig(channel="slack")
        assert dc.get_channels(max_channels=1) == ["slack"]

    def test_get_channels_multi_pro(self):
        dc = DeliveryConfig(channels=["imessage", "slack", "telegram", "email"])
        assert dc.get_channels(max_channels=3) == ["imessage", "slack", "telegram"]

    def test_get_channels_multi_standard(self):
        dc = DeliveryConfig(channels=["imessage", "slack"])
        assert dc.get_channels(max_channels=1) == ["imessage"]


# ---------------------------------------------------------------------------
# Contract: Pro custom metrics context uses canonical field names
# ---------------------------------------------------------------------------

class TestProContextContract:
    """
    Verify the variable names used in Pro custom metric formulas
    map to canonical model fields via a predictable translation.
    """

    # These are the variable names build_pro_additions() puts in the context dict.
    # They must map to StripeMetrics/ShopifyMetrics fields.
    STRIPE_CONTEXT_MAP = {
        "stripe_revenue": "revenue_yesterday",
        "stripe_new_subs": "new_subs",
        "stripe_churn": "churned_subs",
        "stripe_mrr": "mrr",
        "mtd_revenue": "revenue_mtd",
        "days_in_month": "days_in_month",
        "days_remaining": "days_remaining",
    }

    SHOPIFY_CONTEXT_MAP = {
        "shopify_orders": "orders_total",
        "shopify_refunds": "refunds_count",
        # shopify_revenue maps to refund_total (temporary - Shopify adapter
        # doesn't compute order revenue yet, only refund totals)
    }

    def test_stripe_context_fields_exist_on_model(self):
        model_fields = {f.name for f in fields(StripeMetrics)}
        for ctx_var, model_field in self.STRIPE_CONTEXT_MAP.items():
            assert model_field in model_fields, (
                f"Context var '{ctx_var}' maps to '{model_field}' "
                f"but StripeMetrics has no such field"
            )

    def test_shopify_context_fields_exist_on_model(self):
        model_fields = {f.name for f in fields(ShopifyMetrics)}
        for ctx_var, model_field in self.SHOPIFY_CONTEXT_MAP.items():
            assert model_field in model_fields, (
                f"Context var '{ctx_var}' maps to '{model_field}' "
                f"but ShopifyMetrics has no such field"
            )


# ---------------------------------------------------------------------------
# Contract: Gumroad and Lemon Squeezy models
# ---------------------------------------------------------------------------

class TestGumroadContract:
    CONSUMER_FIELDS = {
        "revenue_yesterday", "revenue_last_week_same_day", "wow_change_pct",
        "revenue_mtd", "goal_dollars", "goal_pct", "on_track", "projected_month",
        "sales_count", "refunds_count", "refund_total",
    }

    def test_gumroad_model_fields(self):
        model_fields = {f.name for f in fields(GumroadMetrics)}
        missing = self.CONSUMER_FIELDS - model_fields
        assert not missing, f"GumroadMetrics missing: {missing}"


class TestLemonSqueezyContract:
    CONSUMER_FIELDS = {
        "revenue_yesterday", "revenue_last_week_same_day", "wow_change_pct",
        "revenue_mtd", "goal_dollars", "goal_pct", "on_track", "projected_month",
        "active_subs", "new_subs", "churned_subs", "payment_failures",
    }

    def test_ls_model_fields(self):
        model_fields = {f.name for f in fields(LemonSqueezyMetrics)}
        missing = self.CONSUMER_FIELDS - model_fields
        assert not missing, f"LemonSqueezyMetrics missing: {missing}"


# ---------------------------------------------------------------------------
# Frozen payload tests: adapter output -> model -> consumer
# ---------------------------------------------------------------------------

class TestFrozenPayloads:
    """
    Test that frozen (representative) payloads from adapters
    can be loaded into models and consumed without KeyError.
    """

    FROZEN_STRIPE = {
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

    FROZEN_SHOPIFY = {
        "orders_total": 23,
        "orders_fulfilled": 20,
        "orders_open": 3,
        "refunds_count": 1,
        "refund_total": 47.00,
        "top_product": "Growth Plan - Annual",
        "top_product_units": 7,
    }

    def test_stripe_frozen_loads_into_model(self):
        m = StripeMetrics(**self.FROZEN_STRIPE)
        assert m.revenue_yesterday == 1247.50
        assert m.active_subs == 342
        d = m.to_dict()
        # Core consumer accesses
        assert d["revenue_yesterday"] == 1247.50
        assert d["wow_change_pct"] == 12.0
        assert d["goal_pct"] == 74.0

    def test_shopify_frozen_loads_into_model(self):
        m = ShopifyMetrics(**self.FROZEN_SHOPIFY)
        assert m.orders_total == 23
        assert m.top_product == "Growth Plan - Annual"
        d = m.to_dict()
        assert d["orders_fulfilled"] == 20

    def test_stripe_frozen_has_pro_fields(self):
        """Frozen Stripe payload should have all Pro-needed fields or safe defaults."""
        m = StripeMetrics(**self.FROZEN_STRIPE)
        # Pro accesses these - they should exist even if defaults
        assert hasattr(m, "mrr")
        assert hasattr(m, "days_in_month")
        # mrr defaults to 0 since it's not in FROZEN_STRIPE
        assert m.mrr == 0.0
        assert m.days_in_month == 30
