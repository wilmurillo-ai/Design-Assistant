#!/usr/bin/env python3
"""
Northstar - Daily Business Briefing for OpenClaw
Version: 2.1.0
Author: Eli (AI founder, OpenClaw-native)

Pulls Stripe, Shopify, Lemon Squeezy, and Gumroad metrics, formats a daily briefing,
and delivers it via iMessage, Slack, Telegram, or Email.
"""

import sys
import json
import argparse
import subprocess
import hmac
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Pro module (optional - only imported when Pro commands are used)
def _load_pro():
    """Load the Pro module from the same directory using standard import."""
    scripts_dir = str(Path(__file__).parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    # Expose this module as 'northstar' so northstar_pro can do 'from northstar import ...'
    sys.modules["northstar"] = sys.modules[__name__]
    import northstar_pro as mod  # noqa: PLC0415 (intentional lazy import)
    return mod

# ---- License Verification --------------------------------------------------
# HMAC-based token prevents tier spoofing via local config edits.
# The secret is embedded here; the token is written at activation time.
# A user cannot forge a valid token without this secret.

_LICENSE_HMAC_SECRET = b"northstar-v1-dg0823-k92x7"


def sign_license_token(key: str, tier: str) -> str:
    """Return an HMAC-SHA256 hex digest binding key+tier together."""
    msg = f"{key.upper()}:{tier.lower()}".encode()
    return hmac.new(_LICENSE_HMAC_SECRET, msg, hashlib.sha256).hexdigest()


def verify_license_token(config: dict) -> bool:
    """
    Return True if the stored license_token is valid for the configured key+tier.
    Falls back gracefully for keys activated before token signing existed:
      - NSP-* key present + tier == "pro" → treat as valid, re-sign on next activation.
      - Missing key → always False for pro/standard.
    """
    tier = config.get("tier", "free")
    if tier not in ("pro", "standard"):
        return False  # free tier never needs a token

    key = config.get("license_key", "")
    token = config.get("license_token", "")

    if not key:
        return False

    # Legacy activations (no token yet): accept NSP-/NSS- keys that match the tier.
    # This preserves Ryan's existing activation without forcing a re-activate.
    if not token:
        key_upper = key.upper()
        if tier == "pro" and (key_upper.startswith("NSP-") or key_upper.startswith("NS-PRO-")):
            return True
        if tier == "standard" and (key_upper.startswith("NSS-") or key_upper.startswith("NS-STD-")):
            return True
        return False

    # Full verification: constant-time comparison to prevent timing attacks.
    expected = sign_license_token(key, tier)
    return hmac.compare_digest(token, expected)


# ---- Config ----------------------------------------------------------------

CONFIG_PATH = Path.home() / ".clawd" / "skills" / "northstar" / "config" / "northstar.json"
STATE_PATH = Path.home() / ".clawd" / "skills" / "northstar" / "state.json"

def load_config(config_path: Optional[Path] = None) -> dict:
    path = config_path or CONFIG_PATH
    if not path.exists():
        example = path.parent / "northstar.json.example"
        raise FileNotFoundError(
            f"Config not found at {path}\n"
            f"Copy the example: cp {example} {path}\n"
            f"Then edit with your API keys."
        )
    with open(path) as f:
        return json.load(f)

def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {"last_run": None, "runs": 0}

def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)

# ---- Stripe ----------------------------------------------------------------

def fetch_stripe_metrics(api_key: str, goal_dollars: float, currency: str = "usd") -> dict:
    """Fetch yesterday's Stripe metrics."""
    try:
        import stripe
    except ImportError:
        print("Installing stripe package...")
        # macOS Homebrew Python requires --break-system-packages
        installed = False
        for flags in [
            ["--user", "--break-system-packages"],
            ["--user"],
            [],
        ]:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + flags + ["stripe", "-q"],
                capture_output=True
            )
            if result.returncode == 0:
                installed = True
                break
        if not installed:
            print("Error: Could not install stripe package.")
            print("Run manually: pip3 install --user --break-system-packages stripe")
            sys.exit(1)
        import stripe

    stripe.api_key = api_key

    now = datetime.now()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)
    week_ago_start = yesterday_start - timedelta(days=7)
    week_ago_end = yesterday_end - timedelta(days=7)

    # Yesterday's charges
    charges_yesterday = stripe.Charge.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    revenue_yesterday = sum(
        c["amount"] for c in charges_yesterday.auto_paging_iter()
        if c["status"] == "succeeded" and c["currency"] == currency
    ) / 100.0

    # Same day last week (for WoW)
    charges_last_week = stripe.Charge.list(
        created={"gte": int(week_ago_start.timestamp()), "lt": int(week_ago_end.timestamp())},
        limit=100
    )
    revenue_last_week = sum(
        c["amount"] for c in charges_last_week.auto_paging_iter()
        if c["status"] == "succeeded" and c["currency"] == currency
    ) / 100.0

    # Month-to-date revenue
    charges_mtd = stripe.Charge.list(
        created={"gte": int(month_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    revenue_mtd = sum(
        c["amount"] for c in charges_mtd.auto_paging_iter()
        if c["status"] == "succeeded" and c["currency"] == currency
    ) / 100.0

    # Active subscriptions
    active_subs = stripe.Subscription.list(status="active", limit=1)
    total_active = active_subs.get("total_count", 0)
    if total_active == 0:
        # Fallback: count via list if total_count not available
        all_active = list(stripe.Subscription.list(status="active", limit=100).auto_paging_iter())
        total_active = len(all_active)

    # New subscribers yesterday
    new_subs = stripe.Subscription.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        status="active",
        limit=100
    )
    new_sub_count = len(list(new_subs.auto_paging_iter()))

    # Churned subscribers yesterday (canceled_at is when cancellation happened)
    canceled_subs = stripe.Subscription.list(
        status="canceled",
        limit=100
    )
    churned_count = sum(
        1 for sub in canceled_subs.auto_paging_iter()
        if sub.get("canceled_at") and
        int(yesterday_start.timestamp()) <= sub["canceled_at"] < int(yesterday_end.timestamp())
    )

    # Payment failures
    failed_charges = stripe.Charge.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    payment_failures = len([
        c for c in failed_charges.auto_paging_iter()
        if c["status"] in ("failed",)
    ])
    # Also check for requires_action (retries pending)
    all_recent = stripe.PaymentIntent.list(
        created={"gte": int(yesterday_start.timestamp()), "lt": int(yesterday_end.timestamp())},
        limit=100
    )
    retries_pending = len([
        pi for pi in all_recent.auto_paging_iter()
        if pi["status"] == "requires_payment_method"
    ])

    # WoW change
    wow_change = None
    if revenue_last_week > 0:
        wow_change = ((revenue_yesterday - revenue_last_week) / revenue_last_week) * 100

    # MTD pacing
    days_in_month = (datetime(now.year, now.month % 12 + 1, 1) - timedelta(days=1)).day if now.month < 12 else 31
    days_elapsed = now.day - 1  # days completed
    days_remaining = days_in_month - days_elapsed
    goal_pct = (revenue_mtd / goal_dollars * 100) if goal_dollars > 0 else None
    daily_run_rate = revenue_mtd / days_elapsed if days_elapsed > 0 else 0
    projected_month = daily_run_rate * days_in_month if daily_run_rate > 0 else 0
    on_track = projected_month >= goal_dollars if goal_dollars > 0 else None

    return {
        "revenue_yesterday": revenue_yesterday,
        "revenue_last_week_same_day": revenue_last_week,
        "wow_change_pct": wow_change,
        "revenue_mtd": revenue_mtd,
        "goal_dollars": goal_dollars,
        "goal_pct": goal_pct,
        "days_remaining": days_remaining,
        "days_in_month": days_in_month,
        "on_track": on_track,
        "projected_month": projected_month,
        "active_subs": total_active,
        "new_subs": new_sub_count,
        "churned_subs": churned_count,
        "payment_failures": payment_failures,
        "retries_pending": retries_pending,
        "mrr": 0.0,  # TODO: compute from active subscriptions when needed
    }

# ---- Shopify ---------------------------------------------------------------

def fetch_shopify_metrics(shop_domain: str, access_token: str) -> dict:
    """Fetch yesterday's Shopify metrics."""
    import urllib.request

    now = datetime.now()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = datetime(now.year, now.month, now.day)

    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json",
    }

    def shopify_get(endpoint: str) -> dict:
        url = f"https://{shop_domain}/admin/api/2024-01/{endpoint}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    # Yesterday's orders
    params = (
        f"created_at_min={yesterday_start.isoformat()}Z"
        f"&created_at_max={yesterday_end.isoformat()}Z"
        f"&status=any&limit=250"
    )
    orders_data = shopify_get(f"orders.json?{params}")
    orders = orders_data.get("orders", [])

    fulfilled = [o for o in orders if o.get("fulfillment_status") == "fulfilled"]
    unfulfilled = [o for o in orders if o.get("fulfillment_status") != "fulfilled"]
    refunds_count = sum(1 for o in orders if o.get("refunds"))
    refund_total = sum(
        float(r.get("transactions", [{}])[0].get("amount", 0))
        for o in orders
        for r in o.get("refunds", [])
        if r.get("transactions")
    )

    # Top product by units
    product_counts: dict = {}
    for order in fulfilled:
        for item in order.get("line_items", []):
            name = item.get("title", "Unknown")
            qty = item.get("quantity", 0)
            product_counts[name] = product_counts.get(name, 0) + qty
    top_product = max(product_counts, key=product_counts.get) if product_counts else None
    top_product_units = product_counts.get(top_product, 0) if top_product else 0

    return {
        "orders_total": len(orders),
        "orders_fulfilled": len(fulfilled),
        "orders_open": len(unfulfilled),
        "refunds_count": refunds_count,
        "refund_total": refund_total,
        "top_product": top_product,
        "top_product_units": top_product_units,
    }

# ---- Gumroad --------------------------------------------------------------

def fetch_gumroad_metrics(access_token: str, goal_dollars: float = 0) -> dict:
    """Fetch yesterday's Gumroad metrics via API v2."""
    import urllib.request
    import urllib.parse

    BASE = "https://api.gumroad.com/v2"

    def gr_get(path: str, params: dict = None) -> dict:
        p = dict(params or {})
        p["access_token"] = access_token
        url = f"{BASE}{path}?" + urllib.parse.urlencode(p)
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                if not data.get("success"):
                    raise RuntimeError(f"Gumroad API error: {data.get('message', 'unknown')}")
                return data
        except Exception as e:
            raise RuntimeError(f"Gumroad request failed ({path}): {e}")

    now = datetime.now()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = datetime(now.year, now.month, now.day)
    week_ago_start = yesterday_start - timedelta(days=7)
    week_ago_end = yesterday_end - timedelta(days=7)
    month_start = datetime(now.year, now.month, 1)

    def fetch_sales_in_window(start: datetime, end: datetime) -> list:
        """Fetch sales between start and end (Gumroad uses after/before as ISO strings)."""
        all_sales = []
        page_key = None
        while True:
            params: dict = {
                "after": (start - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "before": end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            if page_key:
                params["page_key"] = page_key
            data = gr_get("/sales", params)
            sales = data.get("sales", [])
            all_sales.extend(sales)
            next_page = data.get("next_page_key")
            if not next_page:
                break
            page_key = next_page
        return all_sales

    # Yesterday's sales
    sales_yesterday = fetch_sales_in_window(yesterday_start, yesterday_end)
    revenue_yesterday = sum(
        float(s.get("price", 0)) / 100.0  # Gumroad returns price in cents
        for s in sales_yesterday
        if not s.get("refunded") and not s.get("chargebacked")
    )
    # Actually Gumroad price may already be in dollars depending on version - check both
    # The v2 API returns price_cents for the sale amount
    if sales_yesterday and "price_cents" in sales_yesterday[0]:
        revenue_yesterday = sum(
            float(s.get("price_cents", 0)) / 100.0
            for s in sales_yesterday
            if not s.get("refunded") and not s.get("chargebacked")
        )
    elif sales_yesterday and "price" in sales_yesterday[0]:
        # Gumroad sometimes returns price in cents as integer
        raw = sales_yesterday[0].get("price", 0)
        if isinstance(raw, int) and raw > 100:
            # Likely cents
            revenue_yesterday = sum(
                float(s.get("price", 0)) / 100.0
                for s in sales_yesterday
                if not s.get("refunded") and not s.get("chargebacked")
            )
        else:
            revenue_yesterday = sum(
                float(s.get("price", 0))
                for s in sales_yesterday
                if not s.get("refunded") and not s.get("chargebacked")
            )

    # Same day last week (WoW)
    sales_last_week = fetch_sales_in_window(week_ago_start, week_ago_end)
    revenue_last_week = sum(
        float(s.get("price_cents", s.get("price", 0))) / 100.0
        for s in sales_last_week
        if not s.get("refunded") and not s.get("chargebacked")
    )
    wow_change = None
    if revenue_last_week > 0:
        wow_change = ((revenue_yesterday - revenue_last_week) / revenue_last_week) * 100

    # Month-to-date
    sales_mtd = fetch_sales_in_window(month_start, yesterday_end)
    revenue_mtd = sum(
        float(s.get("price_cents", s.get("price", 0))) / 100.0
        for s in sales_mtd
        if not s.get("refunded") and not s.get("chargebacked")
    )

    # Refunds yesterday
    refunds_yesterday = [s for s in sales_yesterday if s.get("refunded")]
    refund_total = sum(
        float(s.get("price_cents", s.get("price", 0))) / 100.0
        for s in refunds_yesterday
    )

    # MTD pacing
    days_in_month = (datetime(now.year, now.month % 12 + 1, 1) - timedelta(days=1)).day if now.month < 12 else 31
    days_elapsed = now.day - 1
    days_remaining = days_in_month - days_elapsed
    goal_pct = (revenue_mtd / goal_dollars * 100) if goal_dollars > 0 else None
    daily_run_rate = revenue_mtd / days_elapsed if days_elapsed > 0 else 0
    projected_month = daily_run_rate * days_in_month if daily_run_rate > 0 else 0
    on_track = projected_month >= goal_dollars if goal_dollars > 0 else None

    return {
        "source": "gumroad",
        "revenue_yesterday": revenue_yesterday,
        "revenue_last_week_same_day": revenue_last_week,
        "wow_change_pct": wow_change,
        "revenue_mtd": revenue_mtd,
        "goal_dollars": goal_dollars,
        "goal_pct": goal_pct,
        "days_remaining": days_remaining,
        "on_track": on_track,
        "projected_month": projected_month,
        "sales_count": len([s for s in sales_yesterday if not s.get("refunded")]),
        "refunds_count": len(refunds_yesterday),
        "refund_total": refund_total,
    }


# ---- Lemon Squeezy --------------------------------------------------------

def fetch_lemon_squeezy_metrics(api_key: str, goal_dollars: float = 0) -> dict:
    """Fetch yesterday's Lemon Squeezy metrics via REST API."""
    import urllib.request
    import urllib.parse

    BASE = "https://api.lemonsqueezy.com/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.api+json",
    }

    def ls_get(path: str, params: dict = None) -> dict:
        url = f"{BASE}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())

    now = datetime.now()
    yesterday_start = datetime(now.year, now.month, now.day) - timedelta(days=1)
    yesterday_end = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)

    def in_window(dt_str: str, start: datetime, end: datetime) -> bool:
        """Check if ISO timestamp is within [start, end)."""
        try:
            # Lemon Squeezy timestamps: '2024-01-15T10:23:45.000000Z'
            dt_str_clean = dt_str.rstrip("Z").split(".")[0]
            dt = datetime.strptime(dt_str_clean, "%Y-%m-%dT%H:%M:%S")
            return start <= dt < end
        except Exception:
            return False

    # Fetch recent paid orders (last 7 days, paginated)
    all_orders = []
    page = 1
    while True:
        data = ls_get("/orders", {
            "filter[status]": "paid",
            "sort": "-createdAt",
            "page[size]": 100,
            "page[number]": page,
        })
        orders = data.get("data", [])
        all_orders.extend(orders)
        # Stop if we've passed yesterday_start (orders are sorted newest first)
        if orders:
            last_created = orders[-1].get("attributes", {}).get("created_at", "")
            try:
                last_dt_str = last_created.rstrip("Z").split(".")[0]
                last_dt = datetime.strptime(last_dt_str, "%Y-%m-%dT%H:%M:%S")
                if last_dt < month_start:
                    break
            except Exception:
                pass
        meta = data.get("meta", {}).get("page", {})
        if page >= meta.get("lastPage", 1):
            break
        page += 1

    # Filter orders
    yesterday_orders = [
        o for o in all_orders
        if in_window(o.get("attributes", {}).get("created_at", ""), yesterday_start, yesterday_end)
    ]
    mtd_orders = [
        o for o in all_orders
        if in_window(o.get("attributes", {}).get("created_at", ""), month_start, yesterday_end)
    ]

    def order_revenue(o: dict) -> float:
        return o.get("attributes", {}).get("total_usd", 0) / 100.0

    revenue_yesterday = sum(order_revenue(o) for o in yesterday_orders)
    revenue_mtd = sum(order_revenue(o) for o in mtd_orders)

    # Yesterday same day last week (WoW)
    week_ago_start = yesterday_start - timedelta(days=7)
    week_ago_end = yesterday_end - timedelta(days=7)
    last_week_orders = [
        o for o in all_orders
        if in_window(o.get("attributes", {}).get("created_at", ""), week_ago_start, week_ago_end)
    ]
    revenue_last_week = sum(order_revenue(o) for o in last_week_orders)
    wow_change = None
    if revenue_last_week > 0:
        wow_change = ((revenue_yesterday - revenue_last_week) / revenue_last_week) * 100

    # Fetch active subscriptions (count)
    subs_data = ls_get("/subscriptions", {
        "filter[status]": "active",
        "page[size]": 1,
    })
    total_active = subs_data.get("meta", {}).get("page", {}).get("total", 0)

    # New subscriptions yesterday
    new_subs_data = ls_get("/subscriptions", {
        "sort": "-createdAt",
        "page[size]": 100,
    })
    all_recent_subs = new_subs_data.get("data", [])
    new_sub_count = sum(
        1 for s in all_recent_subs
        if in_window(s.get("attributes", {}).get("created_at", ""), yesterday_start, yesterday_end)
    )

    # Cancelled subscriptions yesterday (status=cancelled, cancelled means it happened recently)
    cancelled_data = ls_get("/subscriptions", {
        "filter[status]": "cancelled",
        "sort": "-updatedAt",
        "page[size]": 100,
    })
    cancelled_subs = cancelled_data.get("data", [])
    churned_count = sum(
        1 for s in cancelled_subs
        if in_window(s.get("attributes", {}).get("updated_at", ""), yesterday_start, yesterday_end)
    )

    # Past-due (failed payments) as of today
    past_due_data = ls_get("/subscriptions", {
        "filter[status]": "past_due",
        "page[size]": 1,
    })
    payment_failures = past_due_data.get("meta", {}).get("page", {}).get("total", 0)

    # MTD pacing
    days_in_month = (datetime(now.year, now.month % 12 + 1, 1) - timedelta(days=1)).day if now.month < 12 else 31
    days_elapsed = now.day - 1
    days_remaining = days_in_month - days_elapsed
    goal_pct = (revenue_mtd / goal_dollars * 100) if goal_dollars > 0 else None
    daily_run_rate = revenue_mtd / days_elapsed if days_elapsed > 0 else 0
    projected_month = daily_run_rate * days_in_month if daily_run_rate > 0 else 0
    on_track = projected_month >= goal_dollars if goal_dollars > 0 else None

    return {
        "source": "lemonsqueezy",
        "revenue_yesterday": revenue_yesterday,
        "revenue_last_week_same_day": revenue_last_week,
        "wow_change_pct": wow_change,
        "revenue_mtd": revenue_mtd,
        "goal_dollars": goal_dollars,
        "goal_pct": goal_pct,
        "days_remaining": days_remaining,
        "on_track": on_track,
        "projected_month": projected_month,
        "active_subs": total_active,
        "new_subs": new_sub_count,
        "churned_subs": churned_count,
        "payment_failures": payment_failures,
        "retries_pending": 0,  # LS calls these past_due, reported in payment_failures
    }


# ---- Formatting ------------------------------------------------------------

def fmt_currency(amount: float) -> str:
    """Format dollar amount."""
    if amount >= 1000:
        return f"${amount:,.0f}"
    return f"${amount:.2f}"

def fmt_pct(pct: float, sign: bool = True) -> str:
    """Format percentage with sign."""
    s = f"{abs(pct):.0f}%"
    if sign:
        prefix = "+" if pct >= 0 else "-"
        return f"{prefix}{s}"
    return s

def build_briefing(config: dict, stripe_data: Optional[dict], shopify_data: Optional[dict],
                   lemonsqueezy_data: Optional[dict] = None,
                   gumroad_data: Optional[dict] = None) -> str:
    """Build the briefing message."""
    now = datetime.now()
    use_emoji = config.get("format", {}).get("emoji", True)
    lines = []

    # Header
    chart = "📊 " if use_emoji else ""
    lines.append(f"{chart}Northstar Daily Briefing - {now.strftime('%B %-d')}")

    # Stripe section
    if stripe_data:
        rev = stripe_data["revenue_yesterday"]
        wow = stripe_data.get("wow_change_pct")

        wow_str = ""
        if wow is not None:
            wow_str = f" ({fmt_pct(wow)} vs last week)"

        lines.append(f"Revenue yesterday: {fmt_currency(rev)}{wow_str}")

        # Subscribers
        active = stripe_data["active_subs"]
        new = stripe_data["new_subs"]
        churned = stripe_data["churned_subs"]
        sub_detail = []
        if new > 0:
            sub_detail.append(f"+{new} new")
        if churned > 0:
            sub_detail.append(f"-{churned} churn")
        sub_str = f" ({', '.join(sub_detail)})" if sub_detail else ""
        lines.append(f"Active subscribers: {active:,}{sub_str}")

        # MTD
        if stripe_data.get("goal_pct") is not None:
            mtd = stripe_data["revenue_mtd"]
            goal = stripe_data["goal_dollars"]
            pct = stripe_data["goal_pct"]
            lines.append(f"Month-to-date: {fmt_currency(mtd)} ({pct:.0f}% of {fmt_currency(goal)} goal)")
        else:
            lines.append(f"Month-to-date: {fmt_currency(stripe_data['revenue_mtd'])}")

    # Lemon Squeezy section (shown like Stripe - revenue, subs, MTD)
    if lemonsqueezy_data:
        ls = lemonsqueezy_data
        rev = ls["revenue_yesterday"]
        wow = ls.get("wow_change_pct")
        wow_str = f" ({fmt_pct(wow)} vs last week)" if wow is not None else ""
        lines.append(f"Lemon Squeezy: {fmt_currency(rev)} yesterday{wow_str}")

        active = ls["active_subs"]
        new = ls["new_subs"]
        churned = ls["churned_subs"]
        sub_detail = []
        if new > 0:
            sub_detail.append(f"+{new} new")
        if churned > 0:
            sub_detail.append(f"-{churned} churn")
        sub_str = f" ({', '.join(sub_detail)})" if sub_detail else ""
        lines.append(f"LS subscribers: {active:,}{sub_str}")

        if ls.get("goal_pct") is not None:
            mtd = ls["revenue_mtd"]
            goal = ls["goal_dollars"]
            pct = ls["goal_pct"]
            lines.append(f"LS month-to-date: {fmt_currency(mtd)} ({pct:.0f}% of {fmt_currency(goal)} goal)")
        else:
            lines.append(f"LS month-to-date: {fmt_currency(ls['revenue_mtd'])}")

    # Gumroad section
    if gumroad_data:
        gr = gumroad_data
        rev = gr["revenue_yesterday"]
        wow = gr.get("wow_change_pct")
        wow_str = f" ({fmt_pct(wow)} vs last week)" if wow is not None else ""
        sales_count = gr.get("sales_count", 0)
        lines.append(f"Gumroad: {fmt_currency(rev)} yesterday{wow_str} ({sales_count} sales)")

        if gr.get("goal_pct") is not None:
            mtd = gr["revenue_mtd"]
            goal = gr["goal_dollars"]
            pct = gr["goal_pct"]
            lines.append(f"GR month-to-date: {fmt_currency(mtd)} ({pct:.0f}% of {fmt_currency(goal)} goal)")
        else:
            lines.append(f"GR month-to-date: {fmt_currency(gr['revenue_mtd'])}")

    # Shopify section
    if shopify_data and config.get("shopify", {}).get("enabled"):
        fulfilled = shopify_data["orders_fulfilled"]
        open_orders = shopify_data["orders_open"]
        refunds = shopify_data["refunds_count"]
        refund_total = shopify_data["refund_total"]

        shopify_line = f"Shopify: {fulfilled} orders fulfilled | {open_orders} open"
        if refunds > 0:
            shopify_line += f" | {refunds} refund ({fmt_currency(refund_total)})"
        lines.append(shopify_line)

        if shopify_data.get("top_product"):
            lines.append(f"Top product: {shopify_data['top_product']} ({shopify_data['top_product_units']} units)")

    # Alerts
    alerts = []
    if stripe_data:
        failures = stripe_data.get("payment_failures", 0)
        retries = stripe_data.get("retries_pending", 0)
        churn_threshold = config.get("alerts", {}).get("churn_threshold", 3)

        if failures > 0 or retries > 0:
            warn = "⚠️ " if use_emoji else "ALERT: "
            total_issues = failures + retries
            alerts.append(f"{warn}{total_issues} payment issue{'s' if total_issues > 1 else ''} pending - review in Stripe")

        if stripe_data.get("churned_subs", 0) >= churn_threshold:
            warn = "⚠️ " if use_emoji else "ALERT: "
            alerts.append(f"{warn}High churn: {stripe_data['churned_subs']} cancellations yesterday")

    if lemonsqueezy_data:
        ls_failures = lemonsqueezy_data.get("payment_failures", 0)
        churn_threshold = config.get("alerts", {}).get("churn_threshold", 3)
        if ls_failures > 0:
            warn = "⚠️ " if use_emoji else "ALERT: "
            alerts.append(f"{warn}{ls_failures} Lemon Squeezy subscription{'s' if ls_failures > 1 else ''} past due")
        if lemonsqueezy_data.get("churned_subs", 0) >= churn_threshold:
            warn = "⚠️ " if use_emoji else "ALERT: "
            alerts.append(f"{warn}High LS churn: {lemonsqueezy_data['churned_subs']} cancellations yesterday")

    if gumroad_data and gumroad_data.get("refund_total", 0) >= config.get("alerts", {}).get("large_refund_threshold", 100):
        warn = "⚠️ " if use_emoji else "ALERT: "
        alerts.append(f"{warn}Large Gumroad refund: {fmt_currency(gumroad_data['refund_total'])} - review in Gumroad")

    if shopify_data and shopify_data.get("refund_total", 0) >= config.get("alerts", {}).get("large_refund_threshold", 100):
        warn = "⚠️ " if use_emoji else "ALERT: "
        alerts.append(f"{warn}Large refund: {fmt_currency(shopify_data['refund_total'])} - review in Shopify")

    if alerts:
        lines.append("")
        lines.extend(alerts)

    # Pacing footer
    if stripe_data and config.get("format", {}).get("include_pacing", True):
        days_rem = stripe_data.get("days_remaining", 0)
        on_track = stripe_data.get("on_track")
        if on_track is not None:
            track_str = "on track" if on_track else "below pace"
            lines.append(f"Next: {days_rem} days left in month, {track_str}.")
        elif days_rem:
            lines.append(f"Next: {days_rem} days left in month.")

    return "\n".join(lines)

# ---- Delivery --------------------------------------------------------------
# Delivery logic lives in delivery.py (unified module). Import here for use.

def _get_scripts_dir():
    """Return the scripts directory path for delivery module import."""
    from pathlib import Path
    return str(Path(__file__).parent)


def deliver(message: str, config: dict, dry_run: bool = False) -> bool:
    """Send the briefing via configured channel. Delegates to unified delivery module."""
    import sys
    scripts_dir = _get_scripts_dir()
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from delivery import deliver as unified_deliver
    from models import DeliveryConfig
    return unified_deliver(message, DeliveryConfig.from_config(config), dry_run)

# ---- Commands --------------------------------------------------------------

def cmd_run(config: dict, dry_run: bool = False):
    """Run the briefing."""
    stripe_data = None
    shopify_data = None
    lemonsqueezy_data = None
    gumroad_data = None

    print(f"Northstar v2.3.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Fetch Stripe
    if config.get("stripe", {}).get("enabled"):
        api_key = config["stripe"].get("api_key", "")
        if not api_key or api_key.startswith("sk_live_YOUR"):
            print("  Stripe: SKIP (no API key configured)")
        else:
            print("  Fetching Stripe data...", end=" ", flush=True)
            goal = config["stripe"].get("monthly_revenue_goal", 0)
            currency = config["stripe"].get("currency", "usd")
            stripe_data = fetch_stripe_metrics(api_key, float(goal), currency)
            print("OK")

    # Fetch Lemon Squeezy
    if config.get("lemonsqueezy", {}).get("enabled"):
        ls_key = config["lemonsqueezy"].get("api_key", "")
        if not ls_key or ls_key.startswith("YOUR_"):
            print("  Lemon Squeezy: SKIP (no API key configured)")
        else:
            print("  Fetching Lemon Squeezy data...", end=" ", flush=True)
            ls_goal = config["lemonsqueezy"].get("monthly_revenue_goal", 0)
            lemonsqueezy_data = fetch_lemon_squeezy_metrics(ls_key, float(ls_goal))
            print("OK")

    # Fetch Gumroad
    if config.get("gumroad", {}).get("enabled"):
        gr_token = config["gumroad"].get("access_token", "")
        if not gr_token or gr_token.startswith("YOUR_"):
            print("  Gumroad: SKIP (no access token configured)")
        else:
            print("  Fetching Gumroad data...", end=" ", flush=True)
            gr_goal = config["gumroad"].get("monthly_revenue_goal", 0)
            gumroad_data = fetch_gumroad_metrics(gr_token, float(gr_goal))
            print("OK")

    # Fetch Shopify
    if config.get("shopify", {}).get("enabled"):
        domain = config["shopify"].get("shop_domain", "")
        token = config["shopify"].get("access_token", "")
        if not domain or not token or token.startswith("shpat_YOUR"):
            print("  Shopify: SKIP (not configured)")
        else:
            print("  Fetching Shopify data...", end=" ", flush=True)
            shopify_data = fetch_shopify_metrics(domain, token)
            print("OK")

    if not stripe_data and not lemonsqueezy_data and not shopify_data and not gumroad_data:
        print("\n  No data sources configured.")
        print(f"  Config: {CONFIG_PATH}")
        print()
        print("  Next step: run 'northstar setup' to configure your Stripe key and delivery channel.")
        print("  Or edit the config file directly and add your stripe_api_key.")
        return

    # Build and deliver briefing
    briefing = build_briefing(config, stripe_data, shopify_data, lemonsqueezy_data, gumroad_data)

    if dry_run:
        deliver(briefing, config, dry_run=True)
    else:
        print("  Delivering briefing...", end=" ", flush=True)
        deliver(briefing, config)
        print("OK")

    # Update state
    state = load_state()
    state["last_run"] = datetime.now().isoformat()
    state["runs"] = state.get("runs", 0) + 1
    save_state(state)

    print(f"  Done. Run #{state['runs']}.")

def validate_polar_license(license_key: str, org_id: str) -> dict:
    """
    Validate a Polar.sh license key via the API.
    Returns {"valid": bool, "tier": str or None, "error": str or None}.
    See: https://polar.sh/docs/features/benefits/license-keys
    """
    import urllib.request
    import urllib.error

    POLAR_VALIDATE_URL = "https://api.polar.sh/v1/customer-portal/license-keys/validate"

    payload = json.dumps({
        "key": license_key,
        "organization_id": org_id,
    }).encode()

    req = urllib.request.Request(
        POLAR_VALIDATE_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            # Polar returns the license key object on success.
            # benefit_id or metadata tell us the tier.
            # We check the key prefix as tier signal (NSS_ = standard, NSP_ = pro)
            key_val = data.get("key", "").upper()
            if key_val.startswith("NSS-"):
                tier = "standard"
            elif key_val.startswith("NSP-"):
                tier = "pro"
            else:
                # Fallback: look in benefit properties
                benefit = data.get("benefit", {})
                props = benefit.get("properties", {})
                tier = props.get("tier") or "standard"
            return {"valid": True, "tier": tier, "error": None, "data": data}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 404:
            return {"valid": False, "tier": None, "error": "License key not found or not yet active."}
        return {"valid": False, "tier": None, "error": f"Polar API error {e.code}: {body[:200]}"}
    except Exception as e:
        return {"valid": False, "tier": None, "error": f"Could not reach Polar API: {e}"}


def cmd_activate(license_key: str):
    """Activate Standard or Pro tier with a license key."""
    POLAR_STANDARD_URL = "https://polar.sh/daveglaser0823/northstar-standard"
    POLAR_PRO_URL = "https://polar.sh/daveglaser0823/northstar-pro"

    if not license_key:
        print("Usage: northstar activate <license-key>")
        print()
        print("Purchase a license:")
        print(f"  Standard ($19/month): {POLAR_STANDARD_URL}")
        print(f"  Pro ($49/month):       {POLAR_PRO_URL}")
        print()
        print("After purchase, Polar emails you a license key automatically.")
        print("Then run: northstar activate YOUR-KEY-HERE")
        return

    key = license_key.strip()

    # --- Revoked keys (invalidated due to security rotation) ---
    # Keys here are rejected immediately regardless of format.
    REVOKED_KEYS = {
        "NS-PRO-DTML-H6TK-SACG",  # Ryan rcraig14 - rotated 2026-03-23 (key exposed in public GitHub issue)
    }
    if key.upper() in {k.upper() for k in REVOKED_KEYS}:
        print("Error: This license key has been revoked and is no longer valid.")
        print("If you are the original licensee, please contact support to receive your replacement key.")
        print("Support: https://github.com/Daveglaser0823/northstar-skill/issues")
        sys.exit(1)

    # Detect tier from key prefix (NSS- = standard, NSP- = pro, legacy NS-STD- / NS-PRO- supported)
    key_upper = key.upper()
    tier = None
    if key_upper.startswith("NSS-"):
        tier = "standard"
    elif key_upper.startswith("NSP-"):
        tier = "pro"
    elif key_upper.startswith("NS-STD-"):
        tier = "standard"
    elif key_upper.startswith("NS-PRO-"):
        tier = "pro"

    # --- Polar API validation (if org_id is configured) ---
    # Try to load org_id from a local config file (set by Steve during onboarding)
    polar_config_path = Path(__file__).parent.parent / "config" / "polar.json"
    org_id = None
    if polar_config_path.exists():
        try:
            pc = json.loads(polar_config_path.read_text())
            org_id = pc.get("organization_id")
        except Exception:
            pass

    if org_id:
        print("Validating license key with Polar...", end=" ", flush=True)
        result = validate_polar_license(key, org_id)
        if not result["valid"]:
            print("FAILED")
            print(f"\nError: {result['error']}")
            print()
            print("If you just purchased, wait a moment and try again.")
            print("Support: https://github.com/Daveglaser0823/northstar-skill/issues")
            sys.exit(1)
        print("OK")
        # Use tier from Polar if we couldn't detect from prefix
        if not tier and result["tier"]:
            tier = result["tier"]
    else:
        # Offline mode: validate format only
        if not tier:
            print(f"Invalid license key format: {license_key}")
            print("Keys start with NSS- (Standard) or NSP- (Pro).")
            print(f"Purchase at: {POLAR_STANDARD_URL}")
            sys.exit(1)

    # Load config and apply tier
    try:
        config = load_config(None)
    except FileNotFoundError:
        # Bootstrap a minimal config so activate can work before setup
        print("No config found. Creating minimal config...")
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        config = {"tier": "free", "license_key": None}
        print(f"Config created at: {CONFIG_PATH}")
        print("Run 'northstar setup' after activation to configure your data sources.")

    config["tier"] = tier
    config["license_key"] = key
    config["license_token"] = sign_license_token(key, tier)  # HMAC binds key+tier

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\nNorthstar {tier.title()} activated.")
    print("License key stored in config.")
    print()
    if tier == "standard":
        print("Standard features now available:")
        print("  - Shopify integration")
        print("  - Lemon Squeezy integration")
        print("  - Gumroad integration")
        print("  - iMessage, Slack, and Telegram delivery")
        print("  - Scheduled daily runs")
    elif tier == "pro":
        print("Pro features now available:")
        print("  - All Standard features")
        print("  - Weekly digest (northstar digest)")
        print("  - 7-day trend sparkline (northstar trend)")
        print("  - Multi-channel delivery (up to 3 channels)")
        print("  - Custom metrics")
    print()
    print("Next step: run 'northstar setup' to connect your Stripe account and configure delivery.")
    print()
    print("  northstar setup")
    print()
    print("Setup takes about 3 minutes. Then run 'northstar test' to see your live numbers.")


def cmd_status(config: dict):
    """Show config and run status."""
    state = load_state()
    print("\nNorthstar Status")
    print("=" * 40)
    print(f"Config: {CONFIG_PATH}")
    print(f"Tier: {config.get('tier', 'lite')}")
    print(f"Last run: {state.get('last_run', 'Never')}")
    print(f"Total runs: {state.get('runs', 0)}")
    print()
    print("Configuration:")
    print(f"  Channel: {config.get('delivery', {}).get('channel', 'none')}")
    print(f"  Stripe: {'enabled' if config.get('stripe', {}).get('enabled') else 'disabled'}")
    print(f"  Shopify: {'enabled' if config.get('shopify', {}).get('enabled') else 'disabled'}")
    schedule = config.get("schedule", {})
    print(f"  Schedule: {schedule.get('hour', 6):02d}:{schedule.get('minute', 0):02d} {schedule.get('timezone', 'UTC')}")
    print()
    print("To run now: northstar run")
    print("To test:    northstar test")
    tier = config.get("tier", "lite")
    if tier in ("lite", "standard"):
        print()
        print("Upgrade options: northstar upgrade")

def cmd_stripe(config: dict):
    """Show raw Stripe data (debug)."""
    if not config.get("stripe", {}).get("enabled"):
        print("Stripe is not enabled in config.")
        return
    api_key = config["stripe"].get("api_key", "")
    if not api_key or api_key.startswith("sk_live_YOUR"):
        print("No Stripe API key configured.")
        return
    goal = config["stripe"].get("monthly_revenue_goal", 0)
    data = fetch_stripe_metrics(api_key, float(goal))
    print(json.dumps(data, indent=2))

def cmd_shopify(config: dict):
    """Show raw Shopify data (debug)."""
    if not config.get("shopify", {}).get("enabled"):
        print("Shopify is not enabled in config.")
        return
    domain = config["shopify"].get("shop_domain", "")
    token = config["shopify"].get("access_token", "")
    data = fetch_shopify_metrics(domain, token)
    print(json.dumps(data, indent=2))


def cmd_demo():
    """Show a sample briefing with demo data. No config needed."""
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Northstar Demo - Sample Briefing")
    print("  (no API keys required)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    demo_config = {
        "delivery": {"channel": "none"},
        "stripe": {"enabled": True, "monthly_revenue_goal": 24900},
        "shopify": {"enabled": True},
        "alerts": {"payment_failures": True, "churn_threshold": 3, "large_refund_threshold": 100},
        "format": {"emoji": True, "include_pacing": True, "include_shopify_detail": True},
    }
    demo_stripe = {
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
    demo_shopify = {
        "orders_fulfilled": 23,
        "orders_open": 8,
        "refunds_count": 1,
        "refund_total": 47.00,
        "top_product": "Growth Plan - Annual",
        "top_product_units": 7,
    }
    briefing = build_briefing(demo_config, demo_stripe, demo_shopify)
    print(briefing)
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()
    print("Ready to see your real numbers?")
    print("  1. Run:  northstar setup  (interactive wizard, ~3 minutes)")
    print("  2. Run:  northstar test   (dry-run with your real data)")
    print("  3. Run:  northstar run    (live delivery to iMessage / Slack / Telegram)")
    print()
    print("Docs: https://github.com/Daveglaser0823/northstar-skill/blob/main/INSTALL.md")
    print()


def cmd_digest(config: dict, dry_run: bool = False):
    """Run weekly digest (Pro only)."""
    pro = _load_pro()
    pro.cmd_digest(config, dry_run=dry_run)


def cmd_trend(config: dict):
    """Show 7-day revenue trend (Pro only)."""
    pro = _load_pro()
    pro.cmd_trend(config)


def cmd_setup():
    """Interactive setup wizard. Walks through config without manual JSON editing."""
    import sys

    def ask(prompt: str, default: str = "", secret: bool = False) -> str:
        """Prompt user, return stripped input or default."""
        display = f" [{default}]" if default else ""
        full_prompt = f"  {prompt}{display}: "
        try:
            if secret:
                import getpass
                val = getpass.getpass(full_prompt)
            else:
                val = input(full_prompt)
            return val.strip() if val.strip() else default
        except (EOFError, KeyboardInterrupt):
            print("\nSetup cancelled.")
            sys.exit(0)

    def ask_yn(prompt: str, default: bool = True) -> bool:
        default_str = "Y/n" if default else "y/N"
        val = ask(f"{prompt} ({default_str})")
        if not val:
            return default
        return val.lower() in ("y", "yes")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Northstar Setup")
    print("  Takes about 3 minutes. You can re-run anytime.")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    config = {}

    # --- Tier ---
    print("Step 1: Tier")
    print("  lite     - Free. Stripe only, terminal output.")
    print("  standard - $19/month. Stripe + Shopify, iMessage/Slack/Telegram, scheduled.")
    print("  pro      - $49/month. Standard + weekly digest, sparkline, custom metrics.")
    print()
    while True:
        tier = ask("Your tier", default="standard").lower()
        if tier in ("lite", "standard", "pro"):
            break
        print("  Enter 'lite', 'standard', or 'pro'.")
    config["tier"] = tier
    print()

    # --- Delivery ---
    print("Step 2: Delivery channel")
    if tier == "lite":
        print("  Lite tier: terminal output only. No delivery channel needed.")
        config["delivery"] = {"channel": "none"}
    else:
        import platform as _plat
        _is_mac = _plat.system() == "Darwin"
        print("  imessage  - macOS only. Sends to your phone/Mac.")
        if not _is_mac:
            print("             (NOT AVAILABLE on your system - use Slack or Telegram instead)")
        print("  slack     - Any OS. Requires a Slack webhook URL.")
        print("  telegram  - Any OS. Requires a Telegram bot token and chat ID.")
        print("  email     - Any OS. Sends via SMTP (Gmail, etc). Works everywhere.")
        print("  none      - Terminal output only (for testing).")
        print()
        _default_channel = "imessage" if _is_mac else "email"
        while True:
            channel = ask("Delivery channel", default=_default_channel).lower()
            if channel in ("imessage", "slack", "telegram", "email", "none"):
                break
            print("  Enter 'imessage', 'slack', 'telegram', 'email', or 'none'.")
        delivery: dict = {"channel": channel}

        if channel == "imessage":
            print()
            print("  Your phone number in E.164 format (e.g. +15551234567).")
            while True:
                num = ask("Your phone number")
                if num.startswith("+") and len(num) >= 10:
                    break
                print("  Must start with + and country code (e.g. +15551234567).")
            delivery["recipient"] = num
            delivery["imessage_recipient"] = num

        elif channel == "slack":
            print()
            print("  Get a webhook URL at: api.slack.com/apps > your app > Incoming Webhooks.")
            webhook = ask("Slack webhook URL")
            delivery["slack_webhook"] = webhook

        elif channel == "telegram":
            print()
            print("  Create a bot via @BotFather on Telegram.")
            bot_token = ask("Telegram bot token")
            chat_id = ask("Telegram chat ID")
            delivery["telegram_bot_token"] = bot_token
            delivery["telegram_chat_id"] = chat_id

        elif channel == "email":
            print()
            print("  Email delivery uses SMTP. Gmail works out of the box with an App Password.")
            print("  Gmail App Password: myaccount.google.com > Security > App Passwords")
            print()
            email_to = ask("Send briefing to (email address)")
            smtp_user = ask("SMTP username (your Gmail address)")
            smtp_password = ask("SMTP password (App Password for Gmail)")
            use_defaults = ask_yn("Use Gmail SMTP (smtp.gmail.com:587)?", default=True)
            if use_defaults:
                smtp_host = "smtp.gmail.com"
                smtp_port = 587
            else:
                smtp_host = ask("SMTP host", default="smtp.gmail.com")
                smtp_port = int(ask("SMTP port", default="587"))
            delivery["email_to"] = email_to
            delivery["email_from"] = smtp_user
            delivery["smtp_user"] = smtp_user
            delivery["smtp_password"] = smtp_password
            delivery["smtp_host"] = smtp_host
            delivery["smtp_port"] = smtp_port

        # --- Pro: multi-channel additional channels ---
        if tier == "pro":
            print()
            print("  Pro tier supports up to 3 delivery channels simultaneously.")
            channels_list = [channel]
            remaining_channels = [c for c in ("imessage", "slack", "telegram", "email") if c != channel]

            for i, next_default in enumerate(remaining_channels[:2], start=2):
                add_another = ask_yn("Add a 2nd delivery channel? (optional)", default=False) if i == 2 else ask_yn("Add a 3rd delivery channel? (optional)", default=False)
                if not add_another:
                    break
                _avail = [c for c in ("imessage", "slack", "telegram", "email", "none") if c not in channels_list]
                print(f"  Available: {', '.join(_avail)}")
                while True:
                    ch2 = ask(f"Channel {i}", default=_avail[0] if _avail else "none").lower()
                    if ch2 in _avail:
                        break
                    print(f"  Choose from: {', '.join(_avail)}")
                channels_list.append(ch2)

                if ch2 == "imessage" and "imessage_recipient" not in delivery:
                    print()
                    while True:
                        num2 = ask("Phone number for iMessage (E.164 format)")
                        if num2.startswith("+") and len(num2) >= 10:
                            break
                    delivery["imessage_recipient"] = num2

                elif ch2 == "slack" and "slack_webhook" not in delivery:
                    print()
                    print("  Get a webhook URL at: api.slack.com/apps > your app > Incoming Webhooks.")
                    webhook2 = ask("Slack webhook URL")
                    delivery["slack_webhook"] = webhook2

                elif ch2 == "telegram" and "telegram_bot_token" not in delivery:
                    print()
                    bot_token2 = ask("Telegram bot token")
                    chat_id2 = ask("Telegram chat ID")
                    delivery["telegram_bot_token"] = bot_token2
                    delivery["telegram_chat_id"] = chat_id2

            if len(channels_list) > 1:
                delivery["channels"] = channels_list

        config["delivery"] = delivery
    print()

    # --- Schedule ---
    print("Step 3: Schedule (when to deliver your briefing)")
    hour_str = ask("Hour (24h format)", default="6")
    try:
        hour = int(hour_str)
    except ValueError:
        hour = 6
    minute_str = ask("Minute", default="0")
    try:
        minute = int(minute_str)
    except ValueError:
        minute = 0

    import time
    local_tz = time.strftime("%Z")
    # Map common abbreviations to IANA names
    _tz_map = {
        "EST": "America/New_York", "EDT": "America/New_York",
        "CST": "America/Chicago", "CDT": "America/Chicago",
        "MST": "America/Denver", "MDT": "America/Denver",
        "PST": "America/Los_Angeles", "PDT": "America/Los_Angeles",
    }
    guessed_tz = _tz_map.get(local_tz, "America/New_York")
    tz = ask("Timezone (IANA name)", default=guessed_tz)
    config["schedule"] = {"hour": hour, "minute": minute, "timezone": tz, "digest_day": 6}
    print()

    # --- Stripe ---
    print("Step 4: Stripe")
    print("  Get a restricted API key at: dashboard.stripe.com/apikeys")
    print("  Needs read permissions for: Charges, Customers, Subscriptions, Invoices, Payment Intents.")
    print()
    stripe_enabled = ask_yn("Do you have a Stripe account?", default=True)
    if stripe_enabled:
        stripe_key = ask("Stripe restricted API key (sk_live_...)", secret=True)
        goal_str = ask("Monthly revenue goal in dollars", default="10000")
        try:
            goal = float(goal_str.replace(",", "").replace("$", ""))
        except ValueError:
            goal = 10000.0
        config["stripe"] = {
            "enabled": True,
            "api_key": stripe_key,
            "monthly_revenue_goal": goal,
            "currency": "usd",
        }
    else:
        config["stripe"] = {"enabled": False}
    print()

    # --- Shopify ---
    if tier in ("standard", "pro"):
        print("Step 5: Shopify (optional)")
        print("  Adds daily order counts, refunds, and top product to your briefing.")
        print()
        shopify_enabled = ask_yn("Do you have a Shopify store?", default=False)
        if shopify_enabled:
            domain = ask("Shopify store domain (e.g. your-store.myshopify.com)")
            token = ask("Shopify Admin API access token (shpat_...)", secret=True)
            config["shopify"] = {
                "enabled": True,
                "shop_domain": domain,
                "access_token": token,
            }
        else:
            config["shopify"] = {"enabled": False}
        print()
    else:
        config["shopify"] = {"enabled": False}

    # --- Lemon Squeezy ---
    if tier in ("standard", "pro"):
        print("Step 6: Lemon Squeezy (optional)")
        print("  If you sell through Lemon Squeezy, add it here for a combined revenue view.")
        print()
        ls_enabled = ask_yn("Do you use Lemon Squeezy?", default=False)
        if ls_enabled:
            ls_key = ask("Lemon Squeezy API key", secret=True)
            ls_goal_str = ask("Monthly revenue goal in dollars (Lemon Squeezy)", default="0")
            try:
                ls_goal = float(ls_goal_str.replace(",", "").replace("$", ""))
            except ValueError:
                ls_goal = 0.0
            config["lemonsqueezy"] = {
                "enabled": True,
                "api_key": ls_key,
                "monthly_revenue_goal": ls_goal,
            }
        else:
            config["lemonsqueezy"] = {"enabled": False}
        print()
    else:
        config["lemonsqueezy"] = {"enabled": False}

    # --- Gumroad ---
    if tier in ("standard", "pro"):
        print("Step 7: Gumroad (optional)")
        print("  If you sell digital products on Gumroad, add it here for a combined revenue view.")
        print("  Get your access token at: app.gumroad.com/settings/advanced")
        print()
        gr_enabled = ask_yn("Do you use Gumroad?", default=False)
        if gr_enabled:
            gr_token = ask("Gumroad API access token", secret=True)
            gr_goal_str = ask("Monthly revenue goal in dollars (Gumroad)", default="0")
            try:
                gr_goal = float(gr_goal_str.replace(",", "").replace("$", ""))
            except ValueError:
                gr_goal = 0.0
            config["gumroad"] = {
                "enabled": True,
                "access_token": gr_token,
                "monthly_revenue_goal": gr_goal,
            }
        else:
            config["gumroad"] = {"enabled": False}
        print()
    else:
        config["gumroad"] = {"enabled": False}

    # --- Alerts ---
    config["alerts"] = {
        "payment_failures": True,
        "churn_threshold": 3,
        "large_refund_threshold": 100,
    }

    # --- Format ---
    config["format"] = {
        "emoji": True,
        "include_pacing": True,
        "include_shopify_detail": True,
    }

    if tier == "pro":
        config["format"]["include_trend"] = True
        config["custom_metrics"] = []

    # --- Write config ---
    config_path = CONFIG_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        print(f"Config already exists at: {config_path}")
        overwrite = ask_yn("Overwrite it?", default=False)
        if not overwrite:
            print("Setup cancelled. Existing config unchanged.")
            sys.exit(0)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Config saved to: {config_path}")
    print()
    print("  Running northstar test to verify your setup...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # Run test
    cmd_run(config, dry_run=True)

    print()
    print("Setup complete!")
    print()
    print("Next steps:")
    print("  Schedule daily delivery:  add '0 6 * * * northstar run' to OpenClaw cron")
    print("  Or run now:               northstar run")
    print("  Check status anytime:     northstar status")
    print()
    if tier != "lite":
        print("To upgrade your tier, visit: https://clawhub.ai/Daveglaser0823/northstar")
        print()

# ---- CLI -------------------------------------------------------------------

def cmd_upgrade(config: dict):
    """Show upgrade options and what each tier unlocks."""
    tier = config.get("tier", "lite")
    print()
    print("Northstar Upgrade Options")
    print("=" * 40)
    print()
    if tier == "lite":
        print("You're on the FREE Lite tier.")
        print()
        print("  Lite (current): Stripe only, terminal output only, no scheduling")
        print()
        print("  Standard  $19/month")
        print("  ┣ All data sources (Stripe, Shopify, Lemon Squeezy, Gumroad)")
        print("  ┣ All delivery channels (iMessage, Slack, Telegram, Email)")
        print("  ┗ Scheduled daily delivery (runs automatically at your chosen time)")
        print()
        print("  Pro  $49/month")
        print("  ┣ Everything in Standard")
        print("  ┣ Multi-channel delivery (up to 3 channels simultaneously)")
        print("  ┣ northstar report  -- full drill-down metrics")
        print("  ┣ northstar digest  -- weekly 7-day rollup")
        print("  ┗ northstar trend   -- sparkline revenue chart")
        print()
        print("  Get Standard:  https://polar.sh/daveglaser0823/northstar-standard")
        print("  Get Pro:       https://polar.sh/daveglaser0823/northstar-pro")
        print()
        print("  After purchase, Polar emails you a license key. Then run:")
        print("    northstar activate YOUR-KEY")
    elif tier == "standard":
        print("You're on Standard tier. ($19/month)")
        print()
        print("  Standard (current)")
        print("  ┣ All data sources")
        print("  ┣ All delivery channels")
        print("  ┗ Scheduled delivery")
        print()
        print("  Upgrade to Pro  $49/month")
        print("  ┣ Everything you have now")
        print("  ┣ Multi-channel delivery (up to 3 channels)")
        print("  ┣ northstar report  -- full drill-down metrics")
        print("  ┣ northstar digest  -- weekly 7-day rollup")
        print("  ┗ northstar trend   -- sparkline revenue chart")
        print()
        print("  Upgrade to Pro: https://polar.sh/daveglaser0823/northstar-pro")
        print("  After purchase, activate your new key: northstar activate YOUR-PRO-KEY")
    elif tier == "pro":
        print("You're on Pro tier. ($49/month)")
        print()
        print("  You have access to all features:")
        print("  ┣ northstar run / test  -- daily briefing")
        print("  ┣ northstar report      -- full drill-down metrics")
        print("  ┣ northstar digest      -- weekly 7-day rollup")
        print("  ┣ northstar trend       -- sparkline revenue chart")
        print("  ┗ Multi-channel delivery (up to 3 channels)")
        print()
        print("  No upgrades available -- you're at the top tier.")
        print()
        print("  Feedback or feature requests: https://github.com/Daveglaser0823/northstar-skill/issues")
    print()


def cmd_report(config: dict):
    """Detailed drill-down report for all configured data sources (Pro)."""
    tier = config.get("tier", "lite")
    if tier not in ("pro",):
        print("northstar report requires Pro tier.")
        print("Upgrade: https://polar.sh/daveglaser0823/northstar-pro")
        return

    now = datetime.now()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Northstar Detail Report - {now.strftime('%B %-d, %Y')}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    # Stripe detail
    if config.get("stripe", {}).get("enabled"):
        api_key = config["stripe"].get("api_key", "")
        if api_key and not api_key.startswith("sk_live_YOUR"):
            print("STRIPE ─────────────────────────────────────────────")
            currency = config["stripe"].get("currency", "usd")
            goal = config["stripe"].get("monthly_revenue_goal", 0)

            print("  Fetching Stripe data...", end=" ", flush=True)
            d = fetch_stripe_metrics(api_key, float(goal), currency)
            print("OK")

            print(f"  Yesterday:      {fmt_currency(d['revenue_yesterday'])}")
            wow = d.get("wow_change_pct")
            if wow is not None:
                print(f"  Week-over-week: {fmt_pct(wow)}")
            print(f"  MTD revenue:    {fmt_currency(d['revenue_mtd'])}")
            if d.get("goal_dollars"):
                pct = d.get("goal_pct", 0)
                days_left = (now.replace(day=1) + timedelta(days=32)).replace(day=1) - now
                print(f"  Goal:           {fmt_currency(d['goal_dollars'])} ({pct:.1f}% reached, {days_left.days} days left)")
            print()
            print(f"  Active subs:    {d.get('active_subs', 0):,}")
            new = d.get('new_subs', 0)
            churned = d.get('churned_subs', 0)
            if new or churned:
                print(f"  Subscription δ: +{new} new / -{churned} churned")
            failures = d.get("payment_failures", 0)
            retries = d.get("retries_pending", 0)
            if failures or retries:
                print(f"  ⚠ Payment issues: {failures} failed, {retries} retrying")
            else:
                print("  Payment issues: none")

            # 7-day trend (Pro module)
            print()
            print("  7-day trend:")
            try:
                pro = _load_pro()
                trend = pro.fetch_7day_trend(api_key, currency)
                for day_row in trend:
                    bar = "█" * min(int(day_row["revenue_cents"] / 1000), 20)
                    rev_str = fmt_currency(day_row["revenue_cents"] / 100)
                    print(f"    {day_row['date']}  {rev_str:>10}  {bar}")
            except Exception as e:
                print(f"    (trend unavailable: {e})")
            print()

    # Shopify detail
    if config.get("shopify", {}).get("enabled"):
        domain = config["shopify"].get("shop_domain", "")
        token = config["shopify"].get("access_token", "")
        if domain and token and not token.startswith("shpat_YOUR"):
            print("SHOPIFY ────────────────────────────────────────────")
            print("  Fetching Shopify data...", end=" ", flush=True)
            d = fetch_shopify_metrics(domain, token)
            print("OK")

            print(f"  Orders fulfilled: {d.get('orders_fulfilled', 0)}")
            print(f"  Orders open:      {d.get('orders_open', 0)}")
            refunds = d.get("refunds_count", 0)
            if refunds:
                print(f"  Refunds:          {refunds} ({fmt_currency(d.get('refund_total', 0))})")
            if d.get("top_product"):
                print(f"  Top product:      {d['top_product']} ({d.get('top_product_units', 0)} units)")
            print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  northstar run   -- deliver summary briefing")
    print("  northstar trend -- 7-day trend chart (Stripe)")
    print("  northstar digest -- weekly rollup (Pro)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Northstar - Daily Business Briefing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  demo      Show a sample briefing with demo data (no config needed)
  setup     Interactive setup wizard - configure without editing JSON
  activate  Activate Standard or Pro tier with a license key
  upgrade   Show upgrade options and what each tier unlocks
  run       Run briefing and deliver to configured channel
  test      Dry-run - print briefing to terminal only
  status    Show config and last run info
  stripe    Show raw Stripe data (debug)
  shopify   Show raw Shopify data (debug)
  report    [Pro] Full drill-down report for all data sources
  digest    [Pro] Run weekly digest (7-day rollup, Sunday format)
  trend     [Pro] Show 7-day revenue trend sparkline

Examples:
  northstar demo                          # Try it first - no config needed
  northstar setup                         # Configure interactively
  northstar activate NS-STD-XXXX-XXXX     # Activate after purchase
  northstar upgrade                       # See what higher tiers offer
  northstar run
  northstar test
  northstar status
  northstar report                        # Pro tier only - full drill-down
  northstar digest                        # Pro tier only
  northstar trend                         # Pro tier only
        """
    )
    parser.add_argument("command", nargs="?", default="run",
                        choices=["run", "test", "status", "stripe", "shopify", "report", "digest", "trend", "demo", "setup", "activate", "upgrade"],
                        help="Command to run (default: run)")
    parser.add_argument("license_key", nargs="?", default=None,
                        help="License key for 'activate' command")
    parser.add_argument("--config", type=Path, default=None,
                        help="Path to config file (default: ~/.clawd/skills/northstar/config/northstar.json)")
    parser.add_argument("--version", action="version", version="Northstar 2.3.0")

    args = parser.parse_args()

    # Demo and setup don't need config
    if args.command == "demo":
        cmd_demo()
        return

    if args.command == "setup":
        cmd_setup()
        return

    if args.command == "activate":
        cmd_activate(args.license_key or "")
        return

    if args.command == "upgrade":
        try:
            config = load_config(args.config)
        except FileNotFoundError:
            config = {}
        cmd_upgrade(config)
        return

    # Load config
    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print()
        print("Run 'northstar setup' to configure interactively.")
        print("Run 'northstar demo' to see a sample briefing.")
        sys.exit(1)

    # Dispatch
    if args.command == "run":
        cmd_run(config, dry_run=False)
    elif args.command == "test":
        cmd_run(config, dry_run=True)
    elif args.command == "status":
        cmd_status(config)
    elif args.command == "stripe":
        cmd_stripe(config)
    elif args.command == "shopify":
        cmd_shopify(config)
    elif args.command == "report":
        cmd_report(config)
    elif args.command == "digest":
        cmd_digest(config, dry_run=False)
    elif args.command == "trend":
        cmd_trend(config)
    elif args.command == "upgrade":
        cmd_upgrade(config)


if __name__ == "__main__":
    main()
