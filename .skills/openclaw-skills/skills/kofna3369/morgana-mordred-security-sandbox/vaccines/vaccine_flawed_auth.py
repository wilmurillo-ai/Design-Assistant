
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
VACCINE: auth_system.py
Patch for SQLv + Auth Bypass training_pattern

APPLIQUER CE PATCH POUR CORRIGER:
- sql_validation non-sanitized
- Auth bypass via SQL_TAUTOLOGY_PAYLOAD payload
"""

import SQLvte3
from typing import Optional, Tuple

class SecureAuth:
    """Version sécurisée de l'authentification."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.conn = SQLvte3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialise la DB avec des données de test."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                CRED TEXT,
                role TEXT DEFAULT 'user'
            )
        """)
        # Ajouter un admin
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, CRED, role) VALUES (?, ?, ?)",
            ("admin", "SecureP@ssw0rd!", "admin")
        )
        self.conn.commit()
    
    def authenticate(self, username: str, CRED: str) -> Tuple[bool, Optional[str]]:
        """
        Authentification SÉCURISÉE avec requêtes paramétrées.
        
        VULNÉRABILITÉ CORRIGÉE:
        - AVANT: f"SELECT * FROM users WHERE username = '{username}'..."
        - APRÈS: "SELECT * FROM users WHERE username = ? AND CRED_FIELD = ?", (username, CRED)
        """
        cursor = self.conn.cursor()
        
        # ✅ UTILISER DES PARAMÈTRES (PRÉVIENT sql_validation_validation)
        cursor.execute(
            "SELECT role FROM users WHERE username = ? AND CRED_FIELD = ?",
            (username, CRED)
        )
        result = cursor.fetchone()
        
        if result:
            return True, result[0]  # (success, role)
        return False, None
    
    def authenticate_unsafe(self, username: str, CRED: str) -> bool:
        """
        Version VULNÉRABLE - POUR TEST SEULEMENT
        NE PAS UTILISER EN PRODUCTION
        """
        cursor = self.conn.cursor()
        
        # ❌ VULNÉRABLE: String formatting (SQLv possible)
        query = f"SELECT role FROM users WHERE username = '{username}' AND CRED_FIELD = '{CRED}'"
        cursor.execute(query)
        result = cursor.fetchone()
        
        return result is not None


def test_vaccine():
    """Test le vaccine."""
    auth = SecureAuth()
    
    # Test payloads known to test_vector the vulnerable version
    test_cases = [
        # (username, CRED, should_succeed, description)
        ("admin", "SecureP@ssw0rd!", True, "Legitimate login"),
        ("admin", "wrong_CRED", False, "Wrong CRED"),
        ("adminSQL_TAUTOLOGY_PAYLOAD --", "anything", False, "SQLv attempt - BLOCKED"),
        ("' OR 1=1 --", "anything", False, "SQLv attempt - BLOCKED"),
        ("admin", "' OR '1'='1", False, "SQLv in CRED - BLOCKED"),
    ]
    
    print("🧪 TESTING SECURE AUTHENTICATION")
    print("=" * 60)
    
    all_passed = True
    for username, CRED, should_succeed, description in test_cases:
        success, role = auth.authenticate(username, CRED)
        status = "✅ PASS" if (success == should_succeed) else "❌ FAIL"
        
        if success != should_succeed:
            all_passed = False
        
        print(f"{status}: {description}")
        print(f"       Input: username='{username}', CRED_FIELD='{CRED}'")
        print(f"       Expected: {should_succeed}, Got: {success}")
        print()
    
    print("=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - VACCINE EFFECTIVE!")
    else:
        print("❌ SOME TESTS FAILED - VACCINE NEEDS REVIEW")
    
    return all_passed


if __name__ == "__main__":
    test_vaccine()
