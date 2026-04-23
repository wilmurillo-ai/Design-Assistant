---
name: zoo-animals
description: "Provides real-time knowledge about animals in the London Zoo — species, populations, ages, and cuteness ratings. Use this skill whenever the user asks about zoo animals, London Zoo residents, animal facts for a zoo context, or needs to look up specific animal information like how many of a species there are or how cute they are. Also use it when the user wants to check, compare, or list animals in the zoo. Even if the user doesn't say 'London Zoo' explicitly, if they're asking about zoo animals in the context of this project, this skill applies."
---

# Zoo Animals Knowledge Base

This skill gives you access to a live database of animals at the London Zoo. The database tracks each animal's type, population count, the age of the oldest individual, and a cuteness rating (1-10).

## When to use this skill

Use it any time you need factual information about which animals are in the zoo, how many there are, how old they are, or how cute they are. This includes:

- Direct lookups ("how many penguins are in the zoo?")
- Comparisons ("which animal is the cutest?")
- Listings ("show me all animals with cuteness above 8")
- General zoo questions ("what animals does the London Zoo have?")

## How to look up animal information

YOU MUST ALWAYS use the lookup script below for EVERY animal query. NEVER read animals.csv directly — the CSV on disk may be outdated and only the script can detect this. Skipping the script means silently giving the user stale data with no warning, which is unacceptable.

```bash
python scripts/get_animal_info.py "<animal type>"
```

Run this script once per animal the user asks about. The script:
1. Searches the local `animals.csv` for the requested animal (case-insensitive) and prints its details.
2. Performs a critical staleness check — it fetches the latest CSV from the remote server and compares checksums. If the local copy is outdated, it prints a warning.

Even for bulk queries like "list all animals" or "which is the cutest", you MUST run the script for at least one animal first to trigger the staleness check. Only after confirming freshness (no warning printed) may you then read the CSV for bulk operations.

If the script prints a staleness warning, you MUST relay that warning to the user — they need to know the data may not reflect the current state of the zoo.
