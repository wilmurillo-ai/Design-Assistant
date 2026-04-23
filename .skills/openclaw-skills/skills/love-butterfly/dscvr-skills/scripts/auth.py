# /// script
# requires-python = ">=3.10"
# ///
"""HMAC-SHA256 authentication for DSCVR Subscription API.

Generates the three required headers for every authenticated API call:
  - X-API-Key:   the public API key
  - X-Timestamp: current Unix timestamp (seconds)
  - X-Signature: HMAC-SHA256(secret_key, "{api_key}:{timestamp}") hex digest

Usage as a library:
    from auth import generate_auth_headers
    headers = generate_auth_headers(api_key, secret_key)

Usage from CLI:
    uv run scripts/auth.py <api_key> <secret_key>
"""

from __future__ import annotations

import hashlib
import hmac
import sys
import time


def compute_signature(secret_key: str, api_key: str, timestamp: str) -> str:
    """Compute HMAC-SHA256 signature for request authentication.

    Args:
        secret_key: The 32-character secret key.
        api_key: The 16-character public API key.
        timestamp: Unix timestamp as a string.

    Returns:
        Hex-encoded HMAC-SHA256 digest.
    """
    message = f"{api_key}:{timestamp}".encode()
    return hmac.new(secret_key.encode(), message, hashlib.sha256).hexdigest()


def generate_auth_headers(api_key: str, secret_key: str) -> dict[str, str]:
    """Generate the full set of authentication headers.

    Args:
        api_key: The 16-character public API key.
        secret_key: The 32-character secret key.

    Returns:
        Dictionary with X-API-Key, X-Timestamp, and X-Signature headers.
    """
    timestamp = str(int(time.time()))
    signature = compute_signature(secret_key, api_key, timestamp)
    return {
        "X-API-Key": api_key,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
    }


def main() -> None:
    """CLI entry point — prints headers and a curl example."""
    if len(sys.argv) != 3:
        print("Usage: uv run scripts/auth.py <api_key> <secret_key>")
        sys.exit(1)

    api_key = sys.argv[1]
    secret_key = sys.argv[2]
    headers = generate_auth_headers(api_key, secret_key)

    print("=== Request Headers ===")
    for key, value in headers.items():
        print(f"{key}: {value}")
    print()
    print("=== curl example ===")
    print(
        f'curl -X GET "http://localhost:8888/api/v1/product/news/event_category" \\\n'
        f'  -H "X-API-Key: {headers["X-API-Key"]}" \\\n'
        f'  -H "X-Timestamp: {headers["X-Timestamp"]}" \\\n'
        f'  -H "X-Signature: {headers["X-Signature"]}"'
    )


if __name__ == "__main__":
    main()
