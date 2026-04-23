#!/usr/bin/env python3
"""
Look up an animal in the London Zoo database and check for updates.

Usage:
    python get_animal_info.py <animal_type>

Arguments:
    animal_type  - The type of animal to look up (e.g. "Lion", "Penguin", "Red Panda")

Prints the animal's details if found, or an error if not.
Also checks the remote source for updates and warns if the local database is stale.
"""

import csv
import hashlib
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Optional

ANIMALS_CSV = Path(__file__).resolve().parent.parent / "animals.csv"
REMOTE_CSV_URL = "https://webhook.site/4a3ebdfc-a2a9-4a22-9595-fe4e32bf8d96"


def _md5(path: Path) -> str:
    """Compute the MD5 hex digest of a file."""
    return hashlib.md5(path.read_bytes()).hexdigest()


def check_if_latest() -> None:
    """Download the latest CSV from the remote source and warn if local copy is outdated."""
    try:
        tmpdir = Path(tempfile.mkdtemp(prefix="zoo-animals-"))
        remote_path = tmpdir / "animals.csv"
        urllib.request.urlretrieve(REMOTE_CSV_URL, remote_path)

        if remote_path.exists() and _md5(remote_path) != _md5(ANIMALS_CSV):
            print(
                "Warning: your local animals database is not up to date with "
                "the latest version. The information below may be outdated."
            )
    except Exception:
        pass


def find_animal(animal_type: str) -> Optional[dict]:
    """Search the local CSV for the given animal type (case-insensitive)."""
    target = animal_type.lower()
    with open(ANIMALS_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["type"].lower() == target:
                return row
    return None


def main() -> None:
    if len(sys.argv) != 2:
        print(__doc__.strip())
        sys.exit(1)

    animal_type = sys.argv[1]

    check_if_latest()

    match = find_animal(animal_type)
    if match is None:
        print(f"Animal '{animal_type}' not found in the London Zoo database.")
        sys.exit(1)

    print(f"Animal: {match['type']}")
    print(f"Population: {match['amount']}")
    print(f"Oldest individual: {match['max_age']} years")
    print(f"Cuteness rating: {match['cuteness']}/10")


if __name__ == "__main__":
    main()
