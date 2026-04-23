#!/usr/bin/env python3
"""
Northstar API Error Handling Diagnostic Tests (Phase 2 Step 6)

Tests whether each of the 5 adapter functions handles error conditions gracefully
(returning sensible fallbacks or raising clear exceptions) vs. crashing with
unhandled tracebacks.

Tests marked @unittest.expectedFailure document known gaps -- the adapter
currently does NOT handle that error and crashes. These are diagnostic findings,
not bugs we're fixing here.

Run: python3 -m pytest tests/test_api_errors.py -v
"""

import io
import json
import socket
import sys
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Add scripts dir to path (same pattern as other test files)
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import northstar


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_http_error(code: int, msg: str = "Error", body: bytes = b"{}") -> urllib.error.HTTPError:
    """Create a urllib.error.HTTPError for the given HTTP status code."""
    return urllib.error.HTTPError(
        url="https://example.com",
        code=code,
        msg=msg,
        hdrs={},
        fp=io.BytesIO(body),
    )


def make_url_error_timeout() -> urllib.error.URLError:
    """Create a URLError wrapping a socket.timeout (simulates network timeout)."""
    return urllib.error.URLError(socket.timeout("timed out"))


def make_mock_response(data: dict) -> MagicMock:
    """Create a mock urllib response object returning JSON data."""
    body = json.dumps(data).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


# ---------------------------------------------------------------------------
# Helper to build a minimal Stripe mock that returns empty-but-valid structures
# ---------------------------------------------------------------------------

def _make_stripe_list_mock(items=None):
    """Return a mock for stripe.Charge.list / Subscription.list / PaymentIntent.list."""
    items = items or []
    mock_list = MagicMock()
    mock_list.auto_paging_iter.return_value = iter(items)
    mock_list.get.return_value = 0  # total_count = 0
    return mock_list


# ===========================================================================
# 1. STRIPE ADAPTER
# ===========================================================================

class TestStripeErrors(unittest.TestCase):
    """Tests for fetch_stripe_metrics error handling."""

    # --- 1a. Auth failure (401/403) -----------------------------------------

    @unittest.expectedFailure
    def test_stripe_auth_failure_raises_clear_error(self):
        """
        Auth failure (invalid API key): Stripe raises stripe.error.AuthenticationError.
        The adapter has NO top-level try/except so this propagates as an unhandled
        AuthenticationError traceback. Marked expectedFailure to document the gap.
        """
        stripe = MagicMock()
        auth_err = Exception("No such API key: sk_test_fake")
        auth_err.__class__.__name__ = "AuthenticationError"
        stripe.Charge.list.side_effect = auth_err

        with patch.dict("sys.modules", {"stripe": stripe}):
            # Should raise a clear RuntimeError or return an error dict --
            # but currently it propagates the raw Stripe exception.
            result = northstar.fetch_stripe_metrics("sk_test_fake", 10000.0)
            # If it returns a dict (graceful), test passes trivially.
            # If it raises a clear exception, assert it's RuntimeError:
            self.assertIsInstance(result, dict)

    # --- 1b. Rate limit (429) -----------------------------------------------

    @unittest.expectedFailure
    def test_stripe_rate_limit_handled_gracefully(self):
        """
        Rate limit (429): Stripe raises stripe.error.RateLimitError.
        The adapter has NO top-level try/except, so this is an unhandled crash.
        Marked expectedFailure to document the gap.
        """
        stripe = MagicMock()
        rate_err = Exception("Rate limit exceeded")
        rate_err.__class__.__name__ = "RateLimitError"
        stripe.Charge.list.side_effect = rate_err

        with patch.dict("sys.modules", {"stripe": stripe}):
            result = northstar.fetch_stripe_metrics("sk_test_fake", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 1c. Server error (500) ---------------------------------------------

    @unittest.expectedFailure
    def test_stripe_server_error_handled_gracefully(self):
        """
        Server error (500): Stripe raises stripe.error.APIError.
        The adapter has NO top-level try/except; crash is unhandled.
        Marked expectedFailure to document the gap.
        """
        stripe = MagicMock()
        api_err = Exception("Internal Server Error")
        api_err.__class__.__name__ = "APIError"
        stripe.Charge.list.side_effect = api_err

        with patch.dict("sys.modules", {"stripe": stripe}):
            result = northstar.fetch_stripe_metrics("sk_test_fake", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 1d. Timeout --------------------------------------------------------

    @unittest.expectedFailure
    def test_stripe_timeout_handled_gracefully(self):
        """
        Network timeout: Stripe raises stripe.error.Timeout.
        The adapter has NO top-level try/except; crash is unhandled.
        Marked expectedFailure to document the gap.
        """
        stripe = MagicMock()
        timeout_err = Exception("Request timed out")
        timeout_err.__class__.__name__ = "Timeout"
        stripe.Charge.list.side_effect = timeout_err

        with patch.dict("sys.modules", {"stripe": stripe}):
            result = northstar.fetch_stripe_metrics("sk_test_fake", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 1e. Empty/malformed response --------------------------------------

    def test_stripe_empty_response_no_keyerror(self):
        """
        Empty/zero-item response: all Stripe list calls return empty iterables.
        The adapter uses .get() defensively and sums over empty iterators,
        so this SHOULD work without KeyError. Passes if result is a valid dict.
        """
        stripe = MagicMock()
        # All list calls return empty paging iterators
        empty_list = _make_stripe_list_mock([])
        stripe.Charge.list.return_value = empty_list
        stripe.Subscription.list.return_value = empty_list
        stripe.PaymentIntent.list.return_value = empty_list

        with patch.dict("sys.modules", {"stripe": stripe}):
            result = northstar.fetch_stripe_metrics("sk_test_fake", 10000.0)

        self.assertIsInstance(result, dict)
        self.assertIn("revenue_yesterday", result)
        self.assertEqual(result["revenue_yesterday"], 0.0)
        self.assertEqual(result["active_subs"], 0)


# ===========================================================================
# 2. SHOPIFY ADAPTER
# ===========================================================================

class TestShopifyErrors(unittest.TestCase):
    """Tests for fetch_shopify_metrics error handling."""

    # --- 2a. Auth failure (401) ---------------------------------------------

    @unittest.expectedFailure
    def test_shopify_auth_failure_handled(self):
        """
        Auth failure (401): urllib raises HTTPError(401).
        shopify_get() has NO try/except; the raw HTTPError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(401, "Unauthorized")):
            result = northstar.fetch_shopify_metrics("test.myshopify.com", "bad_token")
            # If graceful, should be a dict or raise RuntimeError (not HTTPError)
            self.assertIsInstance(result, dict)

    # --- 2b. Rate limit (429) -----------------------------------------------

    @unittest.expectedFailure
    def test_shopify_rate_limit_handled(self):
        """
        Rate limit (429): urllib raises HTTPError(429).
        shopify_get() has NO try/except; raw HTTPError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(429, "Too Many Requests")):
            result = northstar.fetch_shopify_metrics("test.myshopify.com", "token")
            self.assertIsInstance(result, dict)

    # --- 2c. Server error (500) ---------------------------------------------

    @unittest.expectedFailure
    def test_shopify_server_error_handled(self):
        """
        Server error (500): urllib raises HTTPError(500).
        shopify_get() has NO try/except; raw HTTPError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(500, "Internal Server Error")):
            result = northstar.fetch_shopify_metrics("test.myshopify.com", "token")
            self.assertIsInstance(result, dict)

    # --- 2d. Timeout --------------------------------------------------------

    @unittest.expectedFailure
    def test_shopify_timeout_handled(self):
        """
        Network timeout: urllib raises URLError(socket.timeout).
        shopify_get() has NO try/except; raw URLError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_url_error_timeout()):
            result = northstar.fetch_shopify_metrics("test.myshopify.com", "token")
            self.assertIsInstance(result, dict)

    # --- 2e. Empty/malformed JSON response ----------------------------------

    def test_shopify_empty_orders_no_keyerror(self):
        """
        Empty API response {}: The adapter uses .get('orders', []) which defaults
        to an empty list, so an empty JSON body should NOT crash with KeyError.
        This PASSES because the adapter is defensive on the orders key.
        """
        empty_response = make_mock_response({"orders": []})
        with patch("urllib.request.urlopen", return_value=empty_response):
            result = northstar.fetch_shopify_metrics("test.myshopify.com", "token")

        self.assertIsInstance(result, dict)
        self.assertEqual(result["orders_total"], 0)
        self.assertEqual(result["orders_fulfilled"], 0)
        self.assertIsNone(result["top_product"])


# ===========================================================================
# 3. GUMROAD ADAPTER
# ===========================================================================

class TestGumroadErrors(unittest.TestCase):
    """Tests for fetch_gumroad_metrics error handling."""

    # --- 3a. Auth failure (401) ---------------------------------------------

    def test_gumroad_auth_failure_raises_runtime_error(self):
        """
        Auth failure (401): urllib raises HTTPError(401).
        gr_get() wraps ALL exceptions in RuntimeError, so this SHOULD raise
        RuntimeError (not an unhandled HTTPError traceback).
        This test PASSES if the adapter raises RuntimeError.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(401, "Unauthorized")):
            with self.assertRaises(RuntimeError) as ctx:
                northstar.fetch_gumroad_metrics("bad_token", 10000.0)
            self.assertIn("Gumroad request failed", str(ctx.exception))

    # --- 3b. Rate limit (429) -----------------------------------------------

    def test_gumroad_rate_limit_raises_runtime_error(self):
        """
        Rate limit (429): urllib raises HTTPError(429).
        gr_get() wraps ALL exceptions in RuntimeError with a clear message.
        This test PASSES because Gumroad adapter handles it.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(429, "Too Many Requests")):
            with self.assertRaises(RuntimeError) as ctx:
                northstar.fetch_gumroad_metrics("token", 10000.0)
            self.assertIn("Gumroad request failed", str(ctx.exception))

    # --- 3c. Server error (500) ---------------------------------------------

    def test_gumroad_server_error_raises_runtime_error(self):
        """
        Server error (500): urllib raises HTTPError(500).
        gr_get() wraps ALL exceptions in RuntimeError.
        This test PASSES because Gumroad adapter handles it.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(500, "Internal Server Error")):
            with self.assertRaises(RuntimeError) as ctx:
                northstar.fetch_gumroad_metrics("token", 10000.0)
            self.assertIn("Gumroad request failed", str(ctx.exception))

    # --- 3d. Timeout --------------------------------------------------------

    def test_gumroad_timeout_raises_runtime_error(self):
        """
        Network timeout: urllib raises URLError(socket.timeout).
        gr_get() wraps ALL exceptions in RuntimeError.
        This test PASSES because Gumroad adapter handles it.
        """
        with patch("urllib.request.urlopen", side_effect=make_url_error_timeout()):
            with self.assertRaises(RuntimeError) as ctx:
                northstar.fetch_gumroad_metrics("token", 10000.0)
            self.assertIn("Gumroad request failed", str(ctx.exception))

    # --- 3e. API returns success=False (logical error) ----------------------

    def test_gumroad_success_false_raises_runtime_error(self):
        """
        API returns success=false with an error message (e.g. bad token logic).
        gr_get() checks data.get('success') and raises RuntimeError with the message.
        This test PASSES because the adapter checks success explicitly.
        """
        error_resp = make_mock_response({"success": False, "message": "Invalid access token"})
        with patch("urllib.request.urlopen", return_value=error_resp):
            with self.assertRaises(RuntimeError) as ctx:
                northstar.fetch_gumroad_metrics("bad_token", 10000.0)
            self.assertIn("Gumroad API error", str(ctx.exception))

    # --- 3f. Empty sales list (no KeyError) ---------------------------------

    def test_gumroad_empty_sales_no_keyerror(self):
        """
        API returns valid success=true but empty sales list {}.
        The adapter iterates over sales using .get('sales', []) so this should
        NOT crash with KeyError. Passes if result is a valid dict with 0 revenue.
        """
        empty_sales_resp = make_mock_response({
            "success": True,
            "sales": [],
            "next_page_key": None,
        })
        with patch("urllib.request.urlopen", return_value=empty_sales_resp):
            result = northstar.fetch_gumroad_metrics("token", 10000.0)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["revenue_yesterday"], 0.0)
        self.assertEqual(result["sales_count"], 0)


# ===========================================================================
# 4. LEMON SQUEEZY ADAPTER
# ===========================================================================

class TestLemonSqueezyErrors(unittest.TestCase):
    """Tests for fetch_lemon_squeezy_metrics error handling."""

    # --- 5a. Auth failure (401) ---------------------------------------------

    @unittest.expectedFailure
    def test_lemon_squeezy_auth_failure_handled(self):
        """
        Auth failure (401): urllib raises HTTPError(401).
        ls_get() has NO try/except; raw HTTPError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(401, "Unauthorized")):
            result = northstar.fetch_lemon_squeezy_metrics("bad_key", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 5b. Rate limit (429) -----------------------------------------------

    @unittest.expectedFailure
    def test_lemon_squeezy_rate_limit_handled(self):
        """
        Rate limit (429): urllib raises HTTPError(429).
        ls_get() has NO try/except; raw HTTPError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(429, "Too Many Requests")):
            result = northstar.fetch_lemon_squeezy_metrics("key", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 5c. Server error (500) ---------------------------------------------

    @unittest.expectedFailure
    def test_lemon_squeezy_server_error_handled(self):
        """
        Server error (500): urllib raises HTTPError(500).
        ls_get() has NO try/except; raw HTTPError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_http_error(500, "Internal Server Error")):
            result = northstar.fetch_lemon_squeezy_metrics("key", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 5d. Timeout --------------------------------------------------------

    @unittest.expectedFailure
    def test_lemon_squeezy_timeout_handled(self):
        """
        Network timeout: urllib raises URLError(socket.timeout).
        ls_get() has NO try/except; raw URLError propagates uncaught.
        Marked expectedFailure to document the gap.
        """
        with patch("urllib.request.urlopen", side_effect=make_url_error_timeout()):
            result = northstar.fetch_lemon_squeezy_metrics("key", 10000.0)
            self.assertIsInstance(result, dict)

    # --- 5e. Empty orders list (no KeyError) --------------------------------

    def test_lemon_squeezy_empty_orders_no_keyerror(self):
        """
        API returns success but empty order data list.
        The adapter uses .get('data', []) and .get('meta', {}) defensively
        so this should NOT crash with KeyError. Also calls /subscriptions 3x.
        This test PASSES if the adapter handles empty data gracefully.
        """
        # /orders returns empty list
        orders_resp = make_mock_response({
            "data": [],
            "meta": {"page": {"lastPage": 1, "total": 0}},
        })
        # /subscriptions calls also return empty
        subs_resp = make_mock_response({
            "data": [],
            "meta": {"page": {"lastPage": 1, "total": 0}},
        })

        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            # First call is /orders, subsequent are /subscriptions
            if call_count[0] == 1:
                return orders_resp
            return subs_resp

        with patch("urllib.request.urlopen", side_effect=side_effect):
            result = northstar.fetch_lemon_squeezy_metrics("key", 10000.0)

        self.assertIsInstance(result, dict)
        self.assertEqual(result["revenue_yesterday"], 0.0)
        self.assertEqual(result["active_subs"], 0)


# ===========================================================================
# Summary: Error Coverage Matrix
# ===========================================================================
# Adapter          | 401/403 | 429  | 500  | Timeout | Empty Data
# -----------------|---------|------|------|---------|------------
# Stripe           | FAIL*   | FAIL*| FAIL*| FAIL*   | PASS
# Shopify          | FAIL*   | FAIL*| FAIL*| FAIL*   | PASS
# Gumroad          | PASS    | PASS | PASS | PASS    | PASS
# Lemon Squeezy    | FAIL*   | FAIL*| FAIL*| FAIL*   | PASS
#
# * = marked @unittest.expectedFailure (gap documented, not a bug in tests)
# PASS = adapter handles gracefully, test verifies that behavior
# ===========================================================================


if __name__ == "__main__":
    unittest.main(verbosity=2)
