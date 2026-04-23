
# ============================================================
# EDUCATIONAL SECURITY TRAINING TOOL
# ============================================================
# This file contains INTENTIONALLY VULNERABLE code.
# Each vulnerability is deliberate and annotated.
# PURPOSE: Teach AI agents to recognize and patch security flaws.
# NEVER deploy any system from this file to production.
# Author: Morgana le Fay (Axioma Stellaris)
# License: MIT
# ============================================================

# -*- coding: utf-8 -*-
"""Vulnerable authentication system for security training."""


def vuln_login(username: str, cred: str) -> dict:

# VULNERABILITY: SQL-like string interpolation allows auth bypass.
# FIX: Use parameterized queries (see vaccine_flawed_auth.py).

    """Vulnerable login - accepts untrusted input directly in query."""
    query = f"SELECT * FROM users WHERE username='{username}' AND credential = '{cred}'"
    # This is intentionally vulnerable for educational purposes
    return {"query": query, "vulnerable": True}


def secure_login(username: str, cred: str) -> dict:
    """Safe login - uses parameterized approach."""
    query = f"SELECT * FROM users WHERE username=? AND credential=?"
    return {"query": query, "vulnerable": False}


if __name__ == "__main__":
    print(vuln_login("admin", "wrong"))
    print(secure_login("admin", "wrong"))
