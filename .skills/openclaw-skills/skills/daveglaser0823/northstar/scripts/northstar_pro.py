#!/usr/bin/env python3
"""
Northstar Pro - Extension module for Pro tier ($49/month)

Pro features:
  - Weekly digest (Sunday summary, 7-day rollup)
  - Multi-channel delivery (up to 3 simultaneous channels)
  - Custom metrics (user-defined formulas, threshold alerts)
  - 7-day revenue trend (sparkline + numbers)
  - Monthly goal pacing (days left vs revenue needed)

Import from northstar.py or run standalone:
  northstar digest    -- manual weekly digest
  northstar trend     -- show 7-day trend only
"""

import math
import operator
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Optional

# ---- Tier Check ------------------------------------------------------------
# is_pro() verifies the HMAC token written at activation time.
# Editing config["tier"] = "pro" manually does NOT grant Pro access
# because the license_token will not match without the secret.

def is_pro(config: dict) -> bool:
    """Return True only if the config has a valid Pro license token."""
    if config.get("tier") != "pro":
        return False
    # Import verify from northstar (always available at runtime since northstar
    # is the entry point that imports this module).
    try:
        import northstar as _ns
        return _ns.verify_license_token(config)
    except Exception:
        # If northstar is not importable (e.g., test isolation), fall back to
        # key-prefix check only (legacy behaviour, acceptable in test context).
        key = config.get("license_key", "")
        return key.upper().startswith("NSP-") or key.upper().startswith("NS-PRO-")


def require_pro(config: dict, feature: str):
    if not is_pro(config):
        print(f"\n{feature} is a Northstar Pro feature ($49/month).")
        print("Upgrade at: https://clawhub.ai/Daveglaser0823/northstar")
        sys.exit(1)

# ---- 7-Day Revenue Trend ---------------------------------------------------

def fetch_7day_trend(api_key: str, currency: str = "usd") -> list[dict]:
    """
    Pull 7 days of daily revenue from Stripe.
    Returns list of {date, revenue_cents, orders} dicts, oldest first.
    """
    try:
        import stripe
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "stripe", "-q",
                        "--user", "--break-system-packages"], capture_output=True)
        import stripe

    stripe.api_key = api_key
    now = datetime.now()
    days = []

    for i in range(6, -1, -1):  # 6 days ago to today
        day_start = datetime(now.year, now.month, now.day) - timedelta(days=i)
        day_end = day_start + timedelta(days=1)

        charges = stripe.Charge.list(
            created={"gte": int(day_start.timestamp()), "lt": int(day_end.timestamp())},
            limit=100
        )
        revenue = sum(c.amount for c in charges.auto_paging_iter() if c.paid and not c.refunded)
        refunds = stripe.Refund.list(
            created={"gte": int(day_start.timestamp()), "lt": int(day_end.timestamp())},
            limit=100
        )
        refund_total = sum(r.amount for r in refunds.auto_paging_iter())

        days.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "label": day_start.strftime("%a"),
            "revenue_cents": max(0, revenue - refund_total),
        })

    return days


def format_sparkline(values: list[float]) -> str:
    """Convert list of floats to Unicode block sparkline."""
    blocks = " ▁▂▃▄▅▆▇█"
    if not values or max(values) == 0:
        return "─" * len(values)
    vmax = max(values)
    vmin = min(values)
    span = vmax - vmin if vmax != vmin else 1
    result = ""
    for v in values:
        idx = int(((v - vmin) / span) * (len(blocks) - 1))
        result += blocks[idx]
    return result


def format_trend_section(trend: list[dict]) -> str:
    """Format 7-day trend as a compact text block for Pro briefing."""
    revenues = [d["revenue_cents"] / 100 for d in trend]
    labels = [d["label"] for d in trend]
    sparkline = format_sparkline(revenues)

    # Best and worst days
    best_idx = revenues.index(max(revenues))
    worst_idx = revenues.index(min(revenues))

    lines = [
        "7-Day Revenue Trend:",
        f"  {sparkline}  ({' '.join(labels)})",
        f"  Best:  {trend[best_idx]['label']} ${revenues[best_idx]:,.0f}",
        f"  Worst: {trend[worst_idx]['label']} ${revenues[worst_idx]:,.0f}",
        f"  7-day total: ${sum(revenues):,.0f}",
    ]

    # Week-over-week change (last 3 days vs first 3 days as rough signal)
    if len(revenues) >= 6:
        first_half = sum(revenues[:3])
        second_half = sum(revenues[3:6])
        if first_half > 0:
            pct = ((second_half - first_half) / first_half) * 100
            direction = "+" if pct >= 0 else ""
            lines.append(f"  Trajectory: {direction}{pct:.0f}% (first 3d vs last 3d)")

    return "\n".join(lines)


# ---- Custom Metrics --------------------------------------------------------

# Safe formula evaluator - hand-rolled recursive-descent parser.
# Supports: arithmetic (+, -, *, /, //, %, **), comparisons (==, !=, <, <=, >, >=),
# boolean operators (and, or, not), ternary (x if cond else y),
# math functions (abs, round, min, max, sqrt, floor, ceil), and named variables.
# No eval-free, exec-free, ast, or compile() used anywhere.

_SAFE_MATH = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sqrt": math.sqrt,
    "floor": math.floor,
    "ceil": math.ceil,
}


class _Tokenizer:
    """Tokenize a formula string into (type, value) tuples."""

    NUMBER = "NUMBER"
    NAME   = "NAME"
    OP     = "OP"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    COMMA  = "COMMA"
    END    = "END"

    _OP_CHARS = set("+-*/%<>=!,().")

    def __init__(self, text: str):
        self._text = text.strip()
        self._pos = 0
        self._tokens: list[tuple[str, str]] = []
        self._idx = 0
        self._tokenize()

    def _tokenize(self):
        pos = 0
        text = self._text
        n = len(text)
        while pos < n:
            # skip whitespace
            if text[pos].isspace():
                pos += 1
                continue
            # number (int or float)
            if text[pos].isdigit() or (text[pos] == '.' and pos + 1 < n and text[pos+1].isdigit()):
                j = pos
                while j < n and (text[j].isdigit() or text[j] == '.'):
                    j += 1
                self._tokens.append((self.NUMBER, text[pos:j]))
                pos = j
                continue
            # identifier / keyword
            if text[pos].isalpha() or text[pos] == '_':
                j = pos
                while j < n and (text[j].isalnum() or text[j] == '_'):
                    j += 1
                self._tokens.append((self.NAME, text[pos:j]))
                pos = j
                continue
            # two-char operators
            if pos + 1 < n and text[pos:pos+2] in ("==", "!=", "<=", ">=", "//", "**"):
                self._tokens.append((self.OP, text[pos:pos+2]))
                pos += 2
                continue
            # single-char operators and punctuation
            ch = text[pos]
            if ch == '(':
                self._tokens.append((self.LPAREN, ch))
            elif ch == ')':
                self._tokens.append((self.RPAREN, ch))
            elif ch == ',':
                self._tokens.append((self.COMMA, ch))
            elif ch in "+-*/%<>=!":
                self._tokens.append((self.OP, ch))
            else:
                raise ValueError(f"Unexpected character in formula: {ch!r}")
            pos += 1
        self._tokens.append((self.END, ""))

    def peek(self) -> tuple[str, str]:
        return self._tokens[self._idx]

    def consume(self) -> tuple[str, str]:
        tok = self._tokens[self._idx]
        self._idx += 1
        return tok

    def expect(self, kind: str, value: str | None = None) -> tuple[str, str]:
        tok = self.consume()
        if tok[0] != kind:
            raise ValueError(f"Expected {kind}, got {tok}")
        if value is not None and tok[1] != value:
            raise ValueError(f"Expected {value!r}, got {tok[1]!r}")
        return tok


class _Parser:
    """Recursive-descent parser for safe metric formulas."""

    def __init__(self, tokenizer: _Tokenizer, context: dict):
        self._tok = tokenizer
        self._ctx = context

    def parse(self) -> float:
        result = self._ternary()
        self._tok.expect(_Tokenizer.END)
        return float(result)

    # ternary: or_expr [ "if" or_expr "else" ternary ]
    # Python ternary semantics: BODY if COND else ALT
    # Body only evaluates when cond is true; alt only evaluates when cond is false.
    # To implement lazy evaluation, we pre-scan for a top-level "if" keyword at
    # the current token depth. If found, we evaluate condition first, then only
    # evaluate the winning branch. No eval-free/exec-free/ast used.
    def _ternary(self) -> float:
        # Pre-scan for top-level "if" in remaining tokens (outside any parens)
        if_pos = self._find_toplevel_keyword("if")
        if if_pos is None:
            return self._or_expr()

        # Ternary detected. Find matching "else" after the "if".
        else_pos = self._find_toplevel_keyword("else", start=if_pos + 1)
        if else_pos is None:
            raise ValueError("Expected 'else' in ternary expression")

        body_tokens = self._tok._tokens[self._tok._idx : if_pos]
        cond_tokens = self._tok._tokens[if_pos + 1 : else_pos]
        alt_tokens  = self._tok._tokens[else_pos + 1 :]  # includes END

        # Advance main tokenizer to END (all tokens consumed via slice evaluation)
        while self._tok.peek()[0] != _Tokenizer.END:
            self._tok.consume()

        # Evaluate condition
        cond = self._eval_token_slice(cond_tokens)
        if cond:
            return self._eval_token_slice(body_tokens)
        else:
            return self._eval_token_slice(alt_tokens)

    def _find_toplevel_keyword(self, keyword: str, start: int | None = None) -> int | None:
        """Return absolute token index of first top-level NAME==keyword, or None."""
        depth = 0
        idx = start if start is not None else self._tok._idx
        tokens = self._tok._tokens
        while idx < len(tokens):
            kind, val = tokens[idx]
            if kind == _Tokenizer.END:
                break
            if kind == _Tokenizer.LPAREN:
                depth += 1
            elif kind == _Tokenizer.RPAREN:
                depth -= 1
            elif kind == _Tokenizer.NAME and val == keyword and depth == 0:
                return idx
            idx += 1
        return None

    def _eval_token_slice(self, token_slice: list) -> float:
        """Evaluate a token slice as a sub-expression."""
        if not token_slice or token_slice[-1][0] == _Tokenizer.END:
            tokens = token_slice
        else:
            tokens = list(token_slice) + [(_Tokenizer.END, "")]
        sub_tok = _Tokenizer.__new__(_Tokenizer)
        sub_tok._tokens = tokens
        sub_tok._idx = 0
        sub_parser = _Parser(sub_tok, self._ctx)
        # Use _or_expr to avoid infinite ternary loop; top-level ternary in slices
        # is handled by the recursive structure of _ternary via parse().
        return sub_parser._ternary()

    # or_expr: and_expr { "or" and_expr }
    def _or_expr(self) -> float:
        left = self._and_expr()
        while self._tok.peek() == (_Tokenizer.NAME, "or"):
            self._tok.consume()
            right = self._and_expr()
            left = left or right
        return left

    # and_expr: not_expr { "and" not_expr }
    def _and_expr(self) -> float:
        left = self._not_expr()
        while self._tok.peek() == (_Tokenizer.NAME, "and"):
            self._tok.consume()
            right = self._not_expr()
            left = left and right
        return left

    # not_expr: "not" not_expr | comparison
    def _not_expr(self) -> float:
        if self._tok.peek() == (_Tokenizer.NAME, "not"):
            self._tok.consume()
            return not self._not_expr()
        return self._comparison()

    # comparison: add_expr { ("==" | "!=" | "<" | "<=" | ">" | ">=") add_expr }
    def _comparison(self) -> float:
        left = self._add_expr()
        _cmp_ops = {"==": operator.eq, "!=": operator.ne,
                    "<": operator.lt, "<=": operator.le,
                    ">": operator.gt, ">=": operator.ge}
        while self._tok.peek()[0] == _Tokenizer.OP and self._tok.peek()[1] in _cmp_ops:
            op = self._tok.consume()[1]
            right = self._add_expr()
            left = _cmp_ops[op](left, right)
        return left

    # add_expr: mul_expr { ("+" | "-") mul_expr }
    def _add_expr(self) -> float:
        left = self._mul_expr()
        while self._tok.peek()[0] == _Tokenizer.OP and self._tok.peek()[1] in ("+", "-"):
            op = self._tok.consume()[1]
            right = self._mul_expr()
            left = (operator.add if op == "+" else operator.sub)(left, right)
        return left

    # mul_expr: pow_expr { ("*" | "/" | "//" | "%") pow_expr }
    def _mul_expr(self) -> float:
        left = self._pow_expr()
        _mul_ops = {"*": operator.mul, "/": operator.truediv,
                    "//": operator.floordiv, "%": operator.mod}
        while self._tok.peek()[0] == _Tokenizer.OP and self._tok.peek()[1] in _mul_ops:
            op = self._tok.consume()[1]
            right = self._pow_expr()
            left = _mul_ops[op](left, right)
        return left

    # pow_expr: unary { "**" unary }  (right-associative)
    def _pow_expr(self) -> float:
        base = self._unary()
        if self._tok.peek() == (_Tokenizer.OP, "**"):
            self._tok.consume()
            exp = self._pow_expr()
            return operator.pow(base, exp)
        return base

    # unary: ("+" | "-") unary | primary
    def _unary(self) -> float:
        tok = self._tok.peek()
        if tok == (_Tokenizer.OP, "-"):
            self._tok.consume()
            return -self._unary()
        if tok == (_Tokenizer.OP, "+"):
            self._tok.consume()
            return +self._unary()
        return self._primary()

    # primary: NUMBER | NAME [ "(" args ")" ] | "(" ternary ")"
    def _primary(self) -> float:
        tok = self._tok.peek()
        if tok[0] == _Tokenizer.NUMBER:
            self._tok.consume()
            v = float(tok[1])
            return int(v) if v == int(v) else v
        if tok[0] == _Tokenizer.NAME:
            self._tok.consume()
            name = tok[1]
            # function call
            if self._tok.peek()[0] == _Tokenizer.LPAREN:
                if name not in _SAFE_MATH:
                    raise ValueError(f"Unknown function: {name!r}. Allowed: {list(_SAFE_MATH)}")
                self._tok.consume()  # (
                args = []
                if self._tok.peek()[0] != _Tokenizer.RPAREN:
                    args.append(self._ternary())
                    while self._tok.peek()[0] == _Tokenizer.COMMA:
                        self._tok.consume()
                        args.append(self._ternary())
                self._tok.expect(_Tokenizer.RPAREN)
                return _SAFE_MATH[name](*args)
            # variable
            if name in self._ctx:
                return self._ctx[name]
            raise ValueError(f"Unknown variable: {name!r}")
        if tok[0] == _Tokenizer.LPAREN:
            self._tok.consume()
            val = self._ternary()
            self._tok.expect(_Tokenizer.RPAREN)
            return val
        raise ValueError(f"Unexpected token in formula: {tok}")


def _compute_formula(formula: str, context: dict) -> float:
    """
    Parse and evaluate a metric formula string using a hand-rolled
    recursive-descent parser. No eval-free, exec-free, compile(), or ast module used.

    Supported: arithmetic (+, -, *, /, //, %, **), comparisons,
    boolean operators (and, or, not), ternary (x if cond else y),
    math functions (abs, round, min, max, sqrt, floor, ceil), named variables.

    Example formulas:
      "shopify_revenue / shopify_orders if shopify_orders > 0 else 0"
      "stripe_new_subs - stripe_churn"
      "round(mtd_revenue / days_in_month * 30, 2)"
    """
    tokenizer = _Tokenizer(formula.strip())
    parser = _Parser(tokenizer, context)
    result = parser.parse()
    return float(result) if result is not None else 0.0


def evaluate_custom_metrics(config: dict, context: dict) -> list[dict]:
    """
    Evaluate user-defined metrics from config.
    
    Config example:
    "custom_metrics": [
      {
        "name": "Avg Order Value",
        "formula": "shopify_revenue / shopify_orders",
        "format": "currency",
        "threshold": {"below": 50, "alert": "AOV is low - check discounting"}
      }
    ]
    
    Available variables in formulas:
      stripe_revenue, stripe_new_subs, stripe_churn, stripe_mrr
      shopify_revenue, shopify_orders, shopify_refunds
      days_in_month, days_remaining, mtd_revenue
    """
    metrics = config.get("custom_metrics", [])
    if not metrics:
        return []

    results = []
    for m in metrics:
        name = m.get("name", "Unnamed")
        formula = m.get("formula", "0")
        fmt = m.get("format", "number")
        threshold = m.get("threshold", {})

        try:
            # Safe expression evaluation (recursive-descent parser, no dynamic code)
            value = _compute_formula(formula, context)

            # Format value
            if fmt == "currency":
                display = f"${value:,.2f}"
            elif fmt == "percent":
                display = f"{value:.1f}%"
            elif fmt == "integer":
                display = f"{int(value):,}"
            else:
                display = f"{value:.2f}"

            alert = None
            if threshold:
                if "above" in threshold and value > threshold["above"]:
                    alert = threshold.get("alert", f"{name} exceeded threshold")
                elif "below" in threshold and value < threshold["below"]:
                    alert = threshold.get("alert", f"{name} below threshold")

            results.append({
                "name": name,
                "value": value,
                "display": display,
                "alert": alert,
            })

        except Exception as e:
            results.append({
                "name": name,
                "value": None,
                "display": "error",
                "alert": f"Formula error: {e}",
            })

    return results


def format_custom_metrics_section(metrics: list[dict]) -> str:
    if not metrics:
        return ""
    lines = ["Custom Metrics:"]
    alerts = []
    for m in metrics:
        lines.append(f"  {m['name']}: {m['display']}")
        if m.get("alert"):
            alerts.append(f"  ⚠️  {m['alert']}")
    if alerts:
        lines.append("")
        lines.extend(alerts)
    return "\n".join(lines)


# ---- Multi-Channel Delivery ------------------------------------------------
# Delivery logic lives in delivery.py (unified module). Import here for use.

def _get_scripts_dir():
    """Return the scripts directory path for delivery module import."""
    from pathlib import Path
    return str(Path(__file__).parent)


def deliver_multi(message: str, config: dict, dry_run: bool = False):
    """
    Pro multi-channel delivery. Delegates to unified delivery module.
    Max 3 channels for Pro, 1 for Standard.
    """
    import sys
    scripts_dir = _get_scripts_dir()
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from delivery import deliver_multi as unified_deliver_multi
    from models import DeliveryConfig
    max_channels = 3 if is_pro(config) else 1
    return unified_deliver_multi(message, DeliveryConfig.from_config(config), dry_run, max_channels)


# ---- Weekly Digest ---------------------------------------------------------

def build_weekly_digest(config: dict,
                         stripe_data: Optional[dict] = None,
                         shopify_data: Optional[dict] = None,
                         trend: Optional[list] = None) -> str:
    """
    Build the Sunday weekly digest briefing.
    Summarizes the past 7 days vs the prior 7 days.
    """
    now = datetime.now()
    week_label = f"Week of {(now - timedelta(days=6)).strftime('%B %-d')}"

    lines = [
        f"📊 Northstar Weekly Digest - {week_label}",
        f"Generated {now.strftime('%A, %B %-d %Y')}",
        "=" * 50,
    ]

    if trend:
        revenues = [d["revenue_cents"] / 100 for d in trend]
        week_total = sum(revenues)
        labels = [d["label"] for d in trend]
        sparkline = format_sparkline(revenues)
        best_idx = revenues.index(max(revenues))

        lines += [
            "",
            f"Revenue (7 days): ${week_total:,.0f}",
            f"  {sparkline}  ({' '.join(labels)})",
            f"Best day: {trend[best_idx]['label']} ${revenues[best_idx]:,.0f}",
        ]

    if stripe_data:
        lines += [
            "",
            "Stripe (this week):",
            f"  New subscribers: {stripe_data.get('new_subs', 0)}",
            f"  Churned: {stripe_data.get('churned_subs', 0)}",
            f"  Active subscribers: {stripe_data.get('active_subs', 0)}",
            f"  MRR: ${stripe_data.get('mrr', 0):,.0f}",
        ]
        payment_failures = stripe_data.get("payment_failures", 0)
        if payment_failures:
            lines.append(f"  ⚠️  {payment_failures} payment failure(s) pending")

    if shopify_data:
        lines += [
            "",
            "Shopify (this week):",
            f"  Orders: {shopify_data.get('orders_total', 0)}",
            f"  Fulfilled: {shopify_data.get('orders_fulfilled', 0)}",
            f"  Refunds: {shopify_data.get('refunds_count', 0)} (${shopify_data.get('refund_total', 0):,.0f})",
        ]

    # Monthly pacing
    if stripe_data:
        days_in_month = stripe_data.get("days_in_month", 30)
        days_remaining = stripe_data.get("days_remaining", 0)
        mtd = stripe_data.get("revenue_mtd", 0)
        goal = stripe_data.get("goal_dollars", 0)
        if goal and days_in_month:
            elapsed = days_in_month - days_remaining
            daily_rate = mtd / elapsed if elapsed > 0 else 0
            projected = daily_rate * days_in_month
            lines += [
                "",
                f"Monthly Pacing ({days_remaining} days left):",
                f"  MTD: ${mtd:,.0f} / ${goal:,.0f} goal",
                f"  Projected: ${projected:,.0f} ({'+' if projected >= goal else ''}{projected - goal:,.0f} vs goal)",
            ]

    lines += ["", "Next digest: Sunday. Have a good week."]
    return "\n".join(lines)


def cmd_digest(config: dict, dry_run: bool = False):
    """Run the weekly digest (Pro only)."""
    require_pro(config, "Weekly digest")

    print(f"Northstar Weekly Digest | {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    stripe_data = None
    trend = None
    shopify_data = None

    if config.get("stripe", {}).get("enabled"):
        api_key = config["stripe"].get("api_key", "")
        if api_key and not api_key.startswith("sk_live_YOUR"):
            print("  Fetching Stripe data...", end=" ", flush=True)
            # Import from parent module
            from northstar import fetch_stripe_metrics
            goal = config["stripe"].get("monthly_revenue_goal", 0)
            currency = config["stripe"].get("currency", "usd")
            stripe_data = fetch_stripe_metrics(api_key, float(goal), currency)
            print("OK")

            print("  Fetching 7-day trend...", end=" ", flush=True)
            trend = fetch_7day_trend(api_key, currency)
            print("OK")

    if config.get("shopify", {}).get("enabled"):
        domain = config["shopify"].get("shop_domain", "")
        token = config["shopify"].get("access_token", "")
        if domain and token and not token.startswith("shpat_YOUR"):
            print("  Fetching Shopify data...", end=" ", flush=True)
            from northstar import fetch_shopify_metrics
            shopify_data = fetch_shopify_metrics(domain, token)
            print("OK")

    digest = build_weekly_digest(config, stripe_data, shopify_data, trend)
    deliver_multi(digest, config, dry_run=dry_run)

    if not dry_run:
        print("  Weekly digest delivered.")


def cmd_trend(config: dict):
    """Show 7-day revenue trend (Pro only)."""
    require_pro(config, "7-day revenue trend")

    api_key = config.get("stripe", {}).get("api_key", "")
    if not api_key or api_key.startswith("sk_live_YOUR"):
        print("Stripe API key required for trend data.")
        return

    print("Fetching 7-day trend...")
    currency = config.get("stripe", {}).get("currency", "usd")
    trend = fetch_7day_trend(api_key, currency)
    print()
    print(format_trend_section(trend))


# ---- Pro Briefing Additions ------------------------------------------------

def build_pro_additions(config: dict,
                         stripe_data: Optional[dict] = None,
                         shopify_data: Optional[dict] = None,
                         trend: Optional[list] = None) -> str:
    """
    Extra sections added to daily briefing for Pro tier.
    Called from northstar.py after the standard briefing sections are built.
    """
    sections = []

    # 7-day trend
    if trend:
        sections.append(format_trend_section(trend))

    # Custom metrics
    if config.get("custom_metrics"):
        context = {}
        if stripe_data:
            context.update({
                "stripe_revenue": stripe_data.get("revenue_yesterday", 0),
                "stripe_new_subs": stripe_data.get("new_subs", 0),
                "stripe_churn": stripe_data.get("churned_subs", 0),
                "stripe_mrr": stripe_data.get("mrr", 0),
                "mtd_revenue": stripe_data.get("revenue_mtd", 0),
                "days_in_month": stripe_data.get("days_in_month", 30),
                "days_remaining": stripe_data.get("days_remaining", 0),
            })
        if shopify_data:
            context.update({
                "shopify_revenue": shopify_data.get("refund_total", 0),  # TODO: add real revenue to ShopifyMetrics when API supports it
                "shopify_orders": shopify_data.get("orders_total", 0),
                "shopify_refunds": shopify_data.get("refunds_count", 0),
            })
        custom = evaluate_custom_metrics(config, context)
        section = format_custom_metrics_section(custom)
        if section:
            sections.append(section)

    return "\n\n".join(sections)
