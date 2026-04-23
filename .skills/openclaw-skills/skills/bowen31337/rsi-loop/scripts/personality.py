#!/usr/bin/env python3
"""
RSI Loop - PersonalityState
Tracks adaptive bias based on what mutation types have been working.
Part of RSI Loop v2.0 Gene Registry (Phase 3).
"""

import json
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
PERSONALITY_FILE = DATA_DIR / "personality.json"


def _default_personality() -> dict:
    return {
        "schema_version": "1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "stats": {
            "repair_success_rate": 0.0,
            "repair_total": 0,
            "optimize_success_rate": 0.0,
            "optimize_total": 0,
            "innovate_success_rate": 0.0,
            "innovate_total": 0,
        },
        "current_bias": "balanced",
        "trait_scores": {"caution": 0.5, "creativity": 0.5, "speed": 0.5},
        "natural_selection": {
            "total_cycles": 0,
            "successful_repairs": 0,
            "successful_innovations": 0,
        },
    }


def load_personality() -> dict:
    """Load personality state from disk, creating default if missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PERSONALITY_FILE.exists():
        p = _default_personality()
        _save_personality(p)
        return p
    with open(PERSONALITY_FILE) as f:
        return json.load(f)


def _save_personality(p: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    p["updated_at"] = datetime.now(timezone.utc).isoformat()
    with open(PERSONALITY_FILE, "w") as f:
        json.dump(p, f, indent=2)


def _compute_bias(stats: dict) -> str:
    """
    Compute current_bias from success rate stats.
    Bias options: "repair_confident", "balanced", "innovate_hungry", "cautious"
    """
    repair_rate = stats.get("repair_success_rate", 0.0)
    repair_total = stats.get("repair_total", 0)
    innovate_rate = stats.get("innovate_success_rate", 0.0)
    innovate_total = stats.get("innovate_total", 0)
    optimize_rate = stats.get("optimize_success_rate", 0.0)

    # Not enough data — stay balanced
    if repair_total + innovate_total < 3:
        return "balanced"

    # High repair success, low innovate success → repair_confident
    if repair_rate >= 0.8 and (innovate_total == 0 or innovate_rate < 0.5):
        return "repair_confident"

    # High innovate success → innovate_hungry
    if innovate_total >= 2 and innovate_rate >= 0.7:
        return "innovate_hungry"

    # All rates low → cautious
    all_rates = [r for r in [repair_rate, optimize_rate, innovate_rate] if r > 0]
    if all_rates and max(all_rates) < 0.5:
        return "cautious"

    return "balanced"


def _compute_traits(stats: dict) -> dict:
    """Recompute trait scores from stats."""
    repair_rate = stats.get("repair_success_rate", 0.0)
    innovate_rate = stats.get("innovate_success_rate", 0.0)
    optimize_rate = stats.get("optimize_success_rate", 0.0)

    # caution: inversely proportional to innovate success
    caution = max(0.1, min(0.9, 0.8 - (innovate_rate * 0.4)))

    # creativity: proportional to innovate success + optimize success
    creativity = max(0.1, min(0.9, (innovate_rate * 0.6 + optimize_rate * 0.4)))

    # speed: proportional to repair success (fast, focused fixes)
    speed = max(0.1, min(0.9, 0.4 + repair_rate * 0.5))

    return {
        "caution": round(caution, 3),
        "creativity": round(creativity, 3),
        "speed": round(speed, 3),
    }


def update_personality(mutation_type: str, success: bool) -> dict:
    """
    Increment success/total counters and recompute bias.
    Returns updated personality dict.
    """
    p = load_personality()
    stats = p["stats"]
    ns = p["natural_selection"]

    # Update counters for this mutation_type
    key_total = f"{mutation_type}_total"
    key_rate = f"{mutation_type}_success_rate"

    if key_total in stats:
        old_total = stats[key_total]
        old_rate = stats[key_rate]
        new_total = old_total + 1
        if old_total == 0:
            new_rate = 1.0 if success else 0.0
        else:
            prev_successes = old_rate * old_total
            new_rate = (prev_successes + (1 if success else 0)) / new_total
        stats[key_total] = new_total
        stats[key_rate] = round(new_rate, 4)

    # Natural selection counters
    ns["total_cycles"] = ns.get("total_cycles", 0) + 1
    if success and mutation_type == "repair":
        ns["successful_repairs"] = ns.get("successful_repairs", 0) + 1
    if success and mutation_type == "innovate":
        ns["successful_innovations"] = ns.get("successful_innovations", 0) + 1

    # Recompute bias and traits
    p["current_bias"] = _compute_bias(stats)
    p["trait_scores"] = _compute_traits(stats)

    _save_personality(p)
    return p


def get_bias() -> str:
    """Return the current bias string."""
    p = load_personality()
    return p.get("current_bias", "balanced")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PersonalityState manager")
    parser.add_argument("--show", action="store_true", help="Show current personality")
    parser.add_argument("--update", choices=["repair", "optimize", "innovate"],
                        help="Record a mutation outcome")
    parser.add_argument("--success", action="store_true", default=True)
    parser.add_argument("--failure", dest="success", action="store_false")
    args = parser.parse_args()

    if args.update:
        p = update_personality(args.update, args.success)
        print(f"Updated personality: bias={p['current_bias']}")
        print(json.dumps(p, indent=2))
    else:
        p = load_personality()
        print(json.dumps(p, indent=2))
