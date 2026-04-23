import argparse
import csv
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Deduplicate CSV rows.")
    ap.add_argument("--input", required=True, help="Input CSV file")
    ap.add_argument("--output", required=True, help="Output CSV file")
    ap.add_argument("--keys", help="Comma-separated key columns. Default: entire row")
    ap.add_argument("--keep-last", action="store_true", help="Keep last occurrence instead of first")
    ap.add_argument("--case-insensitive", action="store_true", help="Lowercase key values")
    args = ap.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    with input_path.open(newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    keys = [k.strip() for k in args.keys.split(",")] if args.keys else None

    seen = {}
    for idx, row in enumerate(rows):
        if keys:
            key_vals = []
            for k in keys:
                if k not in row:
                    raise SystemExit(f"Key column not found: {k}")
                v = row.get(k, "")
                if args.case_insensitive:
                    v = v.lower()
                key_vals.append(v)
            key = tuple(key_vals)
        else:
            key = tuple(row.get(fn, "") for fn in fieldnames)

        if args.keep_last:
            seen[key] = idx
        else:
            if key not in seen:
                seen[key] = idx

    keep_indices = set(seen.values())
    deduped = [r for i, r in enumerate(rows) if i in keep_indices]

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(deduped)

    print(f"Input rows: {len(rows)}")
    print(f"Output rows: {len(deduped)}")


if __name__ == "__main__":
    main()
