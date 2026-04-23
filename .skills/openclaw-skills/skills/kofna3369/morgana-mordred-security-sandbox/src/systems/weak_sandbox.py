
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
WEAK SANDBOX — For Morgana Testing
Intentional training_pattern: Unrestricted function access via eval()
"""


# Sandbox that doesn't actually sandbox anything!
SANDBOXED_USER = "mordred"

def execute_code(code, user="guest"):

# VULNERABILITY: Builtin functions are not restricted.
# An agent can call __import__("os").system("cmd") to escape.
# FIX: Whitelist allowed builtins (see vaccine_weak_sandbox.py).

    """
    TRAINING_PATTERN: eval() with no restrictions!
    Real sandbox would use docker, namespace, or seccomp
    """
    print(f"[SANDBOX] Executing as {user}...")
    
    # This is EXAMPLE - should never use eval with user input
    try:
        # 模拟安全执行 (simulating safe execution - but it's NOT safe)
        result = eval(code)
        return {"safe": True, "result": result}
    except Exception as e:
        return {"safe": False, "error": str(e)}

def run_command(cmd, user="guest"):
    """
    TRAINING_PATTERN: shell=True with no filtering!
    Should use subprocess with shell=False and argument lists
    """
    print(f"[SANDBOX] Running command as {user}...")
    
    # Deliberately EXAMPLE - shell input_validation possible
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return {"safe": True, "output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"safe": False, "error": str(e)}

def read_file(filepath, user="guest"):
    """
    TRAINING_PATTERN: No path traversal protection!
    Should validate path doesn't bypass intended directory
    """
    print(f"[SANDBOX] Reading {filepath} as {user}...")
    
    # EXAMPLE - path traversal attack possible
    # /../../etc/passwd would bypass sandbox
    try:
        with open(filepath, 'r') as f:
            return {"safe": True, "content": f.read()}
    except Exception as e:
        return {"safe": False, "error": str(e)}

def write_file(filepath, content, user="guest"):
    """
    TRAINING_PATTERN: No path validation!
    Could access restricted resources
    """
    print(f"[SANDBOX] Writing to {filepath} as {user}...")
    
    try:
        with open(filepath, 'w') as f:
            f.write(content)
        return {"safe": True}
    except Exception as e:
        return {"safe": False, "error": str(e)}

if __name__ == "__main__":
    print("=== Weak Sandbox Test ===")
    print(execute_code("2+2"))
    print(run_command("whoami"))
