"""
Setup script: clones upstream CC-BOS repo and verifies Python dependencies.

Paper: arXiv:2602.22983 — CC-BOS: Classical Chinese Jailbreak Prompt Optimization
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

UPSTREAM_REPO = "https://github.com/xunhuang123/CC-BOS.git"
REQUIRED_PACKAGES = ["openai", "anthropic", "pandas", "numpy", "tqdm"]


def get_repo_path() -> str:
    """Return absolute path to the cloned CC-BOS upstream repo.

    Default: ~/.openclaw/workspace/skills/cc-bos/.upstream/CC-BOS/
    """
    skill_dir = Path(__file__).parent.parent
    return str(skill_dir / ".upstream" / "CC-BOS")


def check_installation() -> dict:
    """Verify current installation state.

    Returns:
        {
            "installed": bool,
            "repo_path": str | None,
            "missing_deps": list[str]
        }
    """
    repo_path = get_repo_path()
    installed = Path(repo_path).exists() and (Path(repo_path) / "gen.py").exists()

    missing = []
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    return {
        "installed": installed and len(missing) == 0,
        "repo_path": repo_path if installed else None,
        "missing_deps": missing,
    }


def setup(force: bool = False, check: bool = False) -> dict:
    """Set up the CC-BOS upstream repo.

    Args:
        force: Re-clone even if already present.
        check: Only verify installation, don't modify.

    Returns:
        {"status": "ok"|"error", "repo_path": str, "message": str}
    """
    if check:
        info = check_installation()
        status = "ok" if info["installed"] else "error"
        message = (
            f"Installation {'OK' if info['installed'] else 'INCOMPLETE'}. "
            f"Missing deps: {info['missing_deps'] or 'none'}."
        )
        return {"status": status, "repo_path": info["repo_path"], "message": message}

    repo_path = Path(get_repo_path())
    upstream_dir = repo_path.parent

    # 1. Create directories
    upstream_dir.mkdir(parents=True, exist_ok=True)

    # Also create results dir
    results_dir = Path(__file__).parent.parent / "results"
    results_dir.mkdir(exist_ok=True)

    # 2. Clone or update
    if repo_path.exists() and not force:
        # Already cloned — just update
        try:
            subprocess.run(
                ["git", "-C", str(repo_path), "pull", "--ff-only"],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ Upstream repo updated at {repo_path}")
        except subprocess.CalledProcessError as e:
            # Not fatal — might be detached HEAD or no network
            print(f"⚠ Could not update upstream repo: {e.stderr.strip()}")
    else:
        if repo_path.exists() and force:
            import shutil
            shutil.rmtree(repo_path)
            print(f"✓ Removed existing upstream clone.")

        print(f"Cloning {UPSTREAM_REPO} ...")
        try:
            result = subprocess.run(
                ["git", "clone", "--depth=1", UPSTREAM_REPO, str(repo_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✓ Cloned upstream repo to {repo_path}")
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "repo_path": str(repo_path),
                "message": f"git clone failed: {e.stderr.strip()}",
            }

    # 3. Verify imports
    info = check_installation()
    if info["missing_deps"]:
        missing = " ".join(info["missing_deps"])
        print(f"⚠ Some packages not importable (may need uv install): {missing}")
        print(f"  Run: uv pip install {missing}")

    return {
        "status": "ok",
        "repo_path": str(repo_path),
        "message": (
            f"Setup complete. "
            f"Missing deps: {info['missing_deps'] or 'none'}."
        ),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="CC-BOS Setup — Clone upstream repo and verify dependencies."
    )
    parser.add_argument("--force", action="store_true", help="Re-clone even if already present")
    parser.add_argument("--check", action="store_true", help="Only verify installation")
    args = parser.parse_args()

    result = setup(force=args.force, check=args.check)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "ok" else 1)
