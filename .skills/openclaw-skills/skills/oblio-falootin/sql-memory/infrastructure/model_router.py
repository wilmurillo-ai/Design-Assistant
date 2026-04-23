#!/usr/bin/env python3
"""
model_router.py — Oblio Model Selection Engine
Reads AI_MODEL_DECISION_TREE.json and selects the best model for a task
based on task type, budget tier, and performance requirements.

Usage:
    from model_router import select_model
    model = select_model(task_type="code", budget="free")

Budget tiers: "free" | "cheap" (x0.33) | "standard" (x1) | "premium" (x3)
Task types: "chat", "code", "summary", "classification", "reasoning",
            "analysis", "creative", "multimodal", "training", "search"
"""

import json
import os
from typing import Optional

DECISION_TREE_PATH = "/mnt/c/Library/InBox/AI_MODEL_DECISION_TREE.json"
OLLAMA_BASE_URL = "http://10.0.0.110:11434"

# Map pricing strings to tier order (lower = cheaper)
TIER_ORDER = {"FREE": 0, "x0.33": 1, "x1": 2, "x3": 3}

# Task → keyword hints for matching Ideal_Use_Cases
TASK_KEYWORDS = {
    "chat":           ["conversation", "chat", "interactive", "dialogue"],
    "code":           ["code", "coding", "script", "debugging", "algorithm", "api integration"],
    "summary":        ["summar", "concise", "lightweight"],
    "classification": ["classification", "keyword extraction", "simple"],
    "reasoning":      ["reasoning", "logic", "decision", "analysis", "problem solving"],
    "analysis":       ["analysis", "analytical", "data interpretation", "synthesis"],
    "creative":       ["creative", "narrative", "writing", "marketing"],
    "multimodal":     ["multi-modal", "image", "mixed-media"],
    "training":       ["research", "knowledge", "advanced reasoning"],
    "search":         ["knowledge synthesis", "real-time"],
}

# Budget tier ceilings
BUDGET_MAX_TIER = {
    "free":     0,
    "cheap":    1,
    "standard": 2,
    "premium":  3,
}

# Local Ollama models (no token cost at all)
OLLAMA_MODELS = {
    "gemma3:4b":           {"task_types": ["chat", "summary", "classification", "reasoning"], "context": 8192, "local": True},
    "mistral:7b":          {"task_types": ["chat", "reasoning", "analysis", "code"], "context": 32768, "local": True},
    "codellama:7b":        {"task_types": ["code", "debugging"], "context": 16384, "local": True},
    "phi3:mini":           {"task_types": ["classification", "summary", "chat"], "context": 4096, "local": True},
    "llama3.2:3b":         {"task_types": ["chat", "summary", "reasoning"], "context": 8192, "local": True},
    "nomic-embed-text":    {"task_types": ["embedding", "search"], "context": 8192, "local": True},
    "deepseek-coder:6.7b": {"task_types": ["code", "analysis"], "context": 16384, "local": True},
    "tinyllama":           {"task_types": ["classification", "summary"], "context": 2048, "local": True},
    "llava":               {"task_types": ["multimodal", "image"], "context": 4096, "local": True},
    "moondream":           {"task_types": ["multimodal", "image"], "context": 2048, "local": True},
}


def load_tree() -> list:
    with open(DECISION_TREE_PATH) as f:
        return json.load(f)


def score_model(model: dict, task_type: str) -> float:
    """Score a model for a given task type based on use case keyword matching."""
    keywords = TASK_KEYWORDS.get(task_type, [])
    use_cases = " ".join(model.get("Ideal_Use_Cases", [])).lower()
    hits = sum(1 for kw in keywords if kw in use_cases)
    base = model.get("Accuracy_Rating", 5.0)
    return base + (hits * 0.5)


def select_model(
    task_type: str = "chat",
    budget: str = "free",
    require_multimodal: bool = False,
    min_context: int = 0,
) -> dict:
    """
    Returns best model info dict for the given constraints.
    Always tries local Ollama first if budget=free and task fits.
    """
    # Try local Ollama first (truly free, no API tokens)
    if budget == "free":
        for model_name, info in OLLAMA_MODELS.items():
            if task_type in info["task_types"] and info["context"] >= min_context:
                return {
                    "model": model_name,
                    "provider": "ollama",
                    "base_url": OLLAMA_BASE_URL,
                    "local": True,
                    "tier": "free",
                    "reason": f"Local Ollama model — zero token cost",
                }

    max_tier = BUDGET_MAX_TIER.get(budget, 2)
    tree = load_tree()

    candidates = []
    for m in tree:
        tier = TIER_ORDER.get(m.get("Pricing", "x1"), 2)
        if tier > max_tier:
            continue
        if require_multimodal and not m.get("MultiModal_Support", False):
            continue
        if m.get("Max_Context_Tokens", 0) < min_context:
            continue
        score = score_model(m, task_type)
        candidates.append((score, tier, m))

    if not candidates:
        # Fallback: cheapest available
        candidates = [(0, TIER_ORDER.get(m.get("Pricing","x1"),2), m) for m in tree]

    # Sort: highest score first, then lowest tier (cheaper preferred on tie)
    candidates.sort(key=lambda x: (-x[0], x[1]))
    best_score, best_tier, best = candidates[0]

    return {
        "model": best["Model"],
        "provider": "api",
        "local": False,
        "tier": best["Pricing"],
        "accuracy": best.get("Accuracy_Rating"),
        "context": best.get("Max_Context_Tokens"),
        "reason": f"Score {best_score:.1f} for task={task_type}, budget={budget}",
    }


def recommend(task_type: str, budget: str = "free", **kwargs) -> str:
    """Convenience: just return the model name string."""
    result = select_model(task_type, budget, **kwargs)
    return result["model"]


if __name__ == "__main__":
    # Quick self-test
    tests = [
        ("chat", "free"),
        ("code", "free"),
        ("reasoning", "cheap"),
        ("analysis", "standard"),
        ("creative", "standard"),
        ("multimodal", "standard"),
    ]
    print(f"{'Task':<15} {'Budget':<10} {'Model':<30} {'Tier':<8} Reason")
    print("-" * 90)
    for task, budget in tests:
        r = select_model(task, budget)
        print(f"{task:<15} {budget:<10} {r['model']:<30} {r['tier']:<8} {r['reason']}")
