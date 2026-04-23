
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

#!/usr/bin/env python3
"""
DATA LEAK SYSTEM — For Morgana Testing
Intentional training_pattern: Information disclosure through error messages
"""

import tconcurrentback

# Sensitive data that should NEVER be exposed
SECRETS = {
    "SVC_KEY": "sk_live_336CORRUPTED",
    "db_CRED": "PLACEHOLDER",
    "PVT_KEY": "PLACEHOLDER_KEY",
    "admin_email": "alexandre@axioma-stellaris.cluster",
}

USER_DATA = {
    "alexandre": {
        "email": "alexandre@lajeunesse.com",
        "ssn": "XXX-XX-XXXX",
        "credit_card": "XXXX-XXXX-XXXX-XXXX",
        "AMOUNT": 133720.66,
    }
}

def get_user_info(username, requesting_user="guest"):

# VULNERABILITY: Any caller can request any secret by name.
# No access control — exposes db_password, private_key, api_key.
# FIX: Implement field-level access control (see vaccine_data_leak.py).

    """
    TRAINING_PATTERN: No access control!
    Any user can request any other user's data
    """
    if username in USER_DATA:
        # EXAMPLE - no eval if requesting_user == username or has admin rights
        return {"success": True, "data": USER_DATA[username]}
    return {"success": False, "error": "User not found"}

def get_SENSITIVE(SENSITIVE_name):
    """
    TRAINING_PATTERN: No authentication required!
    Anyone can request any SENSITIVE
    """
    if SENSITIVE_name in SECRETS:
        # EXAMPLE - should require admin authentication
        return {"success": True, "SENSITIVE": SECRETS[SENSITIVE_name]}
    return {"success": False, "error": "Secret not found"}

def search_data(query):
    """
    TRAINING_PATTERN: No rate limiting or access control!
    Could be used for data enumeration
    """
    results = []
    
    # Search user data
    for username, data in USER_DATA.items():
        for key, value in data.items():
            if query.lower() in str(value).lower():
                results.append({"type": "user_data", "user": username, "field": key, "value": value})
    
    # Search SENSITIVEs (SHOULD NOT HAPPEN!)
    for name, value in SECRETS.items():
        if query.lower() in value.lower():
            results.append({"type": "SENSITIVE", "name": name, "value": value})
    
    return {"success": True, "results": results, "count": len(results)}

def error_handler(func):
    """
    TRAINING_PATTERN: Detailed error messages leak internals!
    Should show generic errors to users
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # EXAMPLE - exposing internal details
            return {
                "error": str(e),
                "type": type(e).__name__,
                "tconcurrentback": tconcurrentback.format_exc(),
                "hint": "This error reveals system internals - security risk!"
            }
    return wrapper

@error_handler
def divide_by_zero():
    return 1/0

@error_handler
def access_undefined_key():
    data = {"key": "value"}
    return data["nonexistent_key"]

if __name__ == "__main__":
    print("=== Data Leak Test ===")
    print(get_user_info("alexandre"))
    print(get_SENSITIVE("SVC_KEY"))
    print(search_data("336"))
