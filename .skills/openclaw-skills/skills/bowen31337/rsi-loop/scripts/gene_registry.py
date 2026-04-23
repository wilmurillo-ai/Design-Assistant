#!/usr/bin/env python3
"""
Gene Registry — CRUD operations for genes.json and capsules.json.
Part of RSI Loop v2.0 Gene Registry (Phase 1).
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SKILL_DIR = Path(__file__).parent.parent
DATA_DIR = SKILL_DIR / "data"
GENES_FILE = DATA_DIR / "genes.json"
CAPSULES_FILE = DATA_DIR / "capsules.json"

REQUIRED_GENE_FIELDS = [
    "gene_id",
    "schema_version",
    "meta",
    "trigger",
    "mutation_type",
    "blast_radius",
    "implementation",
    "validation",
    "expected_improvement",
]

VALID_MUTATION_TYPES = {"repair", "optimize", "innovate"}


# ---------------------------------------------------------------------------
# Asset ID integrity
# ---------------------------------------------------------------------------

def compute_asset_id(gene: dict) -> str:
    """Compute SHA-256 asset_id from canonical gene JSON (excluding asset_id field)."""
    clean = {k: v for k, v in gene.items() if k != "asset_id"}
    canonical = json.dumps(clean, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Genes I/O
# ---------------------------------------------------------------------------

def load_genes() -> list:
    """Load all genes from genes.json. Returns list of gene dicts."""
    if not GENES_FILE.exists():
        return []
    with open(GENES_FILE) as f:
        data = json.load(f)
    return data.get("genes", [])


def save_genes(genes: list) -> None:
    """Save genes list to genes.json (creates file if missing)."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": "1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "genes": genes,
    }
    with open(GENES_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Capsules I/O
# ---------------------------------------------------------------------------

def load_capsules() -> list:
    """Load all capsules from capsules.json. Returns list of capsule dicts."""
    if not CAPSULES_FILE.exists():
        return []
    with open(CAPSULES_FILE) as f:
        data = json.load(f)
    return data.get("capsules", [])


def save_capsules(capsules: list) -> None:
    """Save capsules list to capsules.json."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": "1.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "capsules": capsules,
    }
    with open(CAPSULES_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# Gene CRUD
# ---------------------------------------------------------------------------

def _validate_gene(gene: dict) -> None:
    """Raise ValueError if gene is missing required fields or has invalid values."""
    missing = [f for f in REQUIRED_GENE_FIELDS if f not in gene]
    if missing:
        raise ValueError(f"Gene missing required fields: {missing}")

    mt = gene.get("mutation_type")
    if mt not in VALID_MUTATION_TYPES:
        raise ValueError(f"Invalid mutation_type '{mt}'. Must be one of {VALID_MUTATION_TYPES}")

    meta = gene.get("meta", {})
    for mf in ("title", "description", "created_at"):
        if mf not in meta:
            raise ValueError(f"Gene meta missing field: '{mf}'")


def add_gene(gene: dict) -> dict:
    """
    Validate schema, compute asset_id, and append gene to registry.
    Returns the gene with asset_id set.
    Raises ValueError on schema violations or duplicate gene_id.
    """
    _validate_gene(gene)

    genes = load_genes()

    # Check for duplicate
    gene_id = gene["gene_id"]
    if any(g["gene_id"] == gene_id for g in genes):
        raise ValueError(f"Gene '{gene_id}' already exists")

    # Compute and set asset_id
    gene = dict(gene)  # don't mutate caller's dict
    gene["asset_id"] = compute_asset_id(gene)

    genes.append(gene)
    save_genes(genes)
    return gene


def get_gene(gene_id: str) -> dict | None:
    """Look up a gene by gene_id. Returns None if not found."""
    for g in load_genes():
        if g["gene_id"] == gene_id:
            return g
    return None


def update_gene_stats(gene_id: str, success: bool) -> bool:
    """
    Update times_applied, success_rate, and last_applied for a gene.
    Returns True if found and updated, False if gene_id not found.
    """
    genes = load_genes()
    for g in genes:
        if g["gene_id"] != gene_id:
            continue

        meta = g.setdefault("meta", {})
        times = meta.get("times_applied", 0) + 1
        prev_rate = meta.get("success_rate", 0.0)

        # Incremental success rate: ((prev_rate * (n-1)) + new) / n
        if times == 1:
            new_rate = 1.0 if success else 0.0
        else:
            prev_successes = prev_rate * (times - 1)
            new_rate = (prev_successes + (1 if success else 0)) / times

        meta["times_applied"] = times
        meta["success_rate"] = round(new_rate, 4)
        meta["last_applied"] = datetime.now(timezone.utc).isoformat()
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Recompute asset_id after stats update
        g["asset_id"] = compute_asset_id(g)

        save_genes(genes)
        return True

    return False


def list_genes(filter_mutation_type: str = None) -> list:
    """
    List all genes, optionally filtered by mutation_type.
    """
    genes = load_genes()
    if filter_mutation_type:
        genes = [g for g in genes if g.get("mutation_type") == filter_mutation_type]
    return genes
