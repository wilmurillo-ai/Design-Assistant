"""
conftest.py — RSI Loop test suite configuration.
Adds the scripts directory to sys.path so tests can import rsi-loop modules.
"""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
