#!/usr/bin/env python3
"""
Prisma SASE API Authentication Helper

Handles OAuth2 client credentials flow with automatic token caching and renewal.
Credentials are loaded securely from .env files — no hardcoded secrets required.

Credential lookup order:
  1. Environment variables (already exported in shell)
  2. .env file in the current working directory
  3. ~/.sase/.env (global config)

Usage:
    from sase_auth import SASEAuth

    # Auto-discovers credentials from .env files
    auth = SASEAuth()

    # Or explicitly specify credentials
    auth = SASEAuth(
        client_id="your_client_id",
        client_secret="your_client_secret",
        tsg_id="your_tsg_id"
    )

    # Get a valid token (auto-refreshes if expired)
    token = auth.get_token()

    # Get headers ready for API calls
    headers = auth.get_headers()

    # For endpoints requiring regional header
    headers = auth.get_headers(region="americas")
"""

import os
import sys
import time
import base64
import json
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library is required. Install it with: pip install requests")
    sys.exit(1)


AUTH_URL = "https://auth.apps.paloaltonetworks.com/oauth2/access_token"
API_BASE = "https://api.sase.paloaltonetworks.com"

# Refresh token 60 seconds before actual expiry to avoid edge-case failures
TOKEN_REFRESH_BUFFER_SECONDS = 60

# .env file search paths (in priority order)
ENV_FILE_SEARCH_PATHS = [
    Path.cwd() / ".env",             # Current working directory
    Path.home() / ".sase" / ".env",  # Global SASE config
]

# Required credential keys
CREDENTIAL_KEYS = {
    "PRISMA_CLIENT_ID": "client_id",
    "PRISMA_CLIENT_SECRET": "client_secret",
    "PRISMA_TSG_ID": "tsg_id",
}


def _parse_env_file(filepath):
    """
    Parse a .env file and return a dict of key-value pairs.
    Supports: KEY=VALUE, KEY="VALUE", KEY='VALUE', comments (#), blank lines.
    """
    env_vars = {}
    filepath = Path(filepath)
    if not filepath.is_file():
        return env_vars

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Skip lines without =
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env_vars[key] = value

    return env_vars


def _discover_credentials():
    """
    Discover SASE credentials from environment variables and .env files.
    Returns a dict with client_id, client_secret, tsg_id (values may be None).
    """
    creds = {"client_id": None, "client_secret": None, "tsg_id": None}

    # Step 1: Check environment variables first
    for env_key, cred_key in CREDENTIAL_KEYS.items():
        val = os.environ.get(env_key)
        if val:
            creds[cred_key] = val

    # Step 2: Fill in missing values from .env files
    if not all(creds.values()):
        for env_path in ENV_FILE_SEARCH_PATHS:
            if all(creds.values()):
                break
            env_vars = _parse_env_file(env_path)
            for env_key, cred_key in CREDENTIAL_KEYS.items():
                if creds[cred_key] is None and env_key in env_vars:
                    creds[cred_key] = env_vars[env_key]

    return creds


def _get_env_setup_instructions():
    """Return user-friendly instructions for setting up credentials."""
    global_env_path = Path.home() / ".sase" / ".env"
    return (
        "\nTo configure credentials, create a .env file in one of these locations:\n"
        f"  Option 1: .env (in your current working directory)\n"
        f"  Option 2: {global_env_path}\n"
        "\nFile contents:\n"
        "  PRISMA_CLIENT_ID=your_client_id@your_tsg.iam.panserviceaccount.com\n"
        "  PRISMA_CLIENT_SECRET=your_client_secret\n"
        "  PRISMA_TSG_ID=your_tsg_id\n"
        "\nAlternatively, export them as environment variables in your shell.\n"
    )


class SASEAuth:
    """Handles OAuth2 authentication for Prisma SASE API."""

    def __init__(self, client_id=None, client_secret=None, tsg_id=None, env_file=None):
        """
        Initialize with credentials.

        Credential resolution order:
          1. Explicit arguments (client_id, client_secret, tsg_id)
          2. Custom env_file path (if provided)
          3. Auto-discovery: environment variables → ./.env → ~/.sase/.env
        """
        # If a specific env_file is provided, load it first
        if env_file:
            env_vars = _parse_env_file(env_file)
            for env_key, cred_key in CREDENTIAL_KEYS.items():
                if env_key in env_vars:
                    if cred_key == "client_id" and client_id is None:
                        client_id = env_vars[env_key]
                    elif cred_key == "client_secret" and client_secret is None:
                        client_secret = env_vars[env_key]
                    elif cred_key == "tsg_id" and tsg_id is None:
                        tsg_id = env_vars[env_key]

        # Auto-discover any still-missing credentials
        discovered = _discover_credentials()

        self.client_id = client_id or discovered["client_id"]
        self.client_secret = client_secret or discovered["client_secret"]
        self.tsg_id = tsg_id or discovered["tsg_id"]

        if not all([self.client_id, self.client_secret, self.tsg_id]):
            missing = []
            if not self.client_id:
                missing.append("PRISMA_CLIENT_ID")
            if not self.client_secret:
                missing.append("PRISMA_CLIENT_SECRET")
            if not self.tsg_id:
                missing.append("PRISMA_TSG_ID")
            raise ValueError(
                f"Missing credentials: {', '.join(missing)}\n"
                + _get_env_setup_instructions()
            )

        self._token = None
        self._token_expiry = 0

    def _request_token(self):
        """Request a new access token from the auth endpoint."""
        auth_string = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_string}",
        }

        data = {
            "grant_type": "client_credentials",
            "scope": f"tsg_id:{self.tsg_id}",
        }

        response = requests.post(AUTH_URL, headers=headers, data=data)

        if response.status_code != 200:
            raise RuntimeError(
                f"Authentication failed ({response.status_code}): {response.text}"
            )

        result = response.json()
        self._token = result["access_token"]
        self._token_expiry = time.time() + result.get("expires_in", 899)

        return self._token

    def get_token(self):
        """Get a valid access token. Automatically refreshes if expired or near expiry."""
        if (
            self._token is None
            or time.time() >= self._token_expiry - TOKEN_REFRESH_BUFFER_SECONDS
        ):
            self._request_token()
        return self._token

    def get_headers(self, region=None):
        """
        Get headers dict ready for API calls.

        Args:
            region: Optional region code for endpoints that require x-panw-region.
                    Valid values: americas, au, ca, de, europe, in, jp, sg, uk
        """
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/json",
        }
        if region:
            headers["x-panw-region"] = region
        return headers

    def api_get(self, path, region=None, params=None):
        """Make an authenticated GET request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.get(url, headers=self.get_headers(region), params=params)
        response.raise_for_status()
        return response.json()

    def api_post(self, path, data, region=None, params=None):
        """Make an authenticated POST request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.post(
            url, headers=self.get_headers(region), json=data, params=params
        )
        response.raise_for_status()
        return response.json()

    def api_put(self, path, data, region=None, params=None):
        """Make an authenticated PUT request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.put(
            url, headers=self.get_headers(region), json=data, params=params
        )
        response.raise_for_status()
        return response.json()

    def api_delete(self, path, region=None, params=None):
        """Make an authenticated DELETE request to the SASE API."""
        url = f"{API_BASE}{path}"
        response = requests.delete(
            url, headers=self.get_headers(region), params=params
        )
        response.raise_for_status()
        if response.content:
            return response.json()
        return None


def main():
    """CLI usage: python sase_auth.py — prints a fresh token to stdout."""
    try:
        auth = SASEAuth()
        print(auth.get_token())
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
