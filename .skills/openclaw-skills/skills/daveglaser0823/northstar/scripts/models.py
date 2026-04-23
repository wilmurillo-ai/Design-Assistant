"""
Northstar Data Models - Canonical contracts for all module boundaries.

Every adapter (Stripe, Shopify, etc.) returns one of these models.
Every renderer/formatter consumes these models.
No raw dicts cross module boundaries.

Created: March 24, 2026 (Phase 1, Architecture Fix)
"""

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class StripeMetrics:
    """Canonical Stripe metrics returned by fetch_stripe_metrics()."""
    # Yesterday
    revenue_yesterday: float = 0.0
    revenue_last_week_same_day: float = 0.0
    wow_change_pct: Optional[float] = None

    # Month-to-date
    revenue_mtd: float = 0.0
    goal_dollars: float = 0.0
    goal_pct: Optional[float] = None
    days_remaining: int = 0
    days_in_month: int = 30
    on_track: Optional[bool] = None
    projected_month: float = 0.0

    # Subscribers
    active_subs: int = 0
    new_subs: int = 0
    churned_subs: int = 0

    # Payment health
    payment_failures: int = 0
    retries_pending: int = 0

    # Derived (computed from active subs, not stored in Stripe directly)
    mrr: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ShopifyMetrics:
    """Canonical Shopify metrics returned by fetch_shopify_metrics()."""
    orders_total: int = 0
    orders_fulfilled: int = 0
    orders_open: int = 0
    refunds_count: int = 0
    refund_total: float = 0.0
    top_product: Optional[str] = None
    top_product_units: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GumroadMetrics:
    """Canonical Gumroad metrics returned by fetch_gumroad_metrics()."""
    source: str = "gumroad"
    revenue_yesterday: float = 0.0
    revenue_last_week_same_day: float = 0.0
    wow_change_pct: Optional[float] = None
    revenue_mtd: float = 0.0
    goal_dollars: float = 0.0
    goal_pct: Optional[float] = None
    days_remaining: int = 0
    on_track: Optional[bool] = None
    projected_month: float = 0.0
    sales_count: int = 0
    refunds_count: int = 0
    refund_total: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LemonSqueezyMetrics:
    """Canonical Lemon Squeezy metrics returned by fetch_lemon_squeezy_metrics()."""
    source: str = "lemonsqueezy"
    revenue_yesterday: float = 0.0
    revenue_last_week_same_day: float = 0.0
    wow_change_pct: Optional[float] = None
    revenue_mtd: float = 0.0
    goal_dollars: float = 0.0
    goal_pct: Optional[float] = None
    days_remaining: int = 0
    on_track: Optional[bool] = None
    projected_month: float = 0.0
    active_subs: int = 0
    new_subs: int = 0
    churned_subs: int = 0
    payment_failures: int = 0
    retries_pending: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DeliveryConfig:
    """
    Canonical delivery configuration. One source of truth for all delivery paths.
    Both core and Pro delivery use this model.
    """
    channel: str = "none"
    channels: list = field(default_factory=list)  # Pro multi-channel
    recipient: str = ""  # Canonical recipient (phone number, email, etc.)
    slack_webhook: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    email_to: str = ""
    email_from: str = ""
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587

    @classmethod
    def from_config(cls, config: dict) -> "DeliveryConfig":
        """
        Build DeliveryConfig from raw config dict.
        Handles legacy key names (imessage_recipient -> recipient).
        """
        delivery = config.get("delivery", {})
        # Canonical recipient: prefer 'recipient', fall back to 'imessage_recipient'
        recipient = delivery.get("recipient", "") or delivery.get("imessage_recipient", "")
        return cls(
            channel=delivery.get("channel", "none"),
            channels=delivery.get("channels", []),
            recipient=recipient,
            slack_webhook=delivery.get("slack_webhook", ""),
            telegram_bot_token=delivery.get("telegram_bot_token", ""),
            telegram_chat_id=delivery.get("telegram_chat_id", ""),
            email_to=delivery.get("email_to", ""),
            email_from=delivery.get("email_from", ""),
            smtp_user=delivery.get("smtp_user", ""),
            smtp_password=delivery.get("smtp_password", ""),
            smtp_host=delivery.get("smtp_host", "smtp.gmail.com"),
            smtp_port=int(delivery.get("smtp_port", 587)),
        )

    def get_channels(self, max_channels: int = 1) -> list:
        """Return the list of channels to deliver to, respecting tier limits."""
        if self.channels:
            return self.channels[:max_channels]
        return [self.channel]
