#!/usr/bin/env python3
"""write_notified.py — v4.3: 将 notified 状态写入 MD 文件"""
import json, sys, os, re

def update_md_file(file_path, entry_id, notified_val, nc_val):
    """更新 MD 文件中指定 entry 的 Notified 和 Notification-Count 字段"""
    if not os.path.exists(file_path):
        return False

    with open(file_path) as f:
        content = f.read()

    # Find entry: ## [ENTRY_ID] ...
    entry_pattern = r"(## \[" + re.escape(entry_id) + r"\] .+?)(?=\n## \[|$)"
    m = re.search(entry_pattern, content, re.DOTALL)
    if not m:
        return False

    entry_start = m.start(1)
    entry_text = m.group(1)

    # Check if Notified / Notification-Count fields already exist
    has_notified = bool(re.search(r"^\s*-\s*Notified:", entry_text, re.MULTILINE))
    has_nc = bool(re.search(r"^\s*-\s*Notification-Count:", entry_text, re.MULTILINE))

    new_entry = entry_text
    notified_str = 'true' if notified_val == 1 else 'false'

    if has_notified:
        new_entry = re.sub(
            r"^\s*-\s*Notified:.*$",
            f"  - Notified: {notified_str}",
            new_entry, flags=re.MULTILINE
        )
    else:
        # Insert after Status line
        new_entry = re.sub(
            r"(\n\s*-\s*Status:[^\n]+\n)",
            r"\1  - Notified: " + notified_str + "\n",
            new_entry
        )

    if has_nc:
        new_entry = re.sub(
            r"^\s*-\s*Notification-Count:.*$",
            f"  - Notification-Count: {nc_val}",
            new_entry, flags=re.MULTILINE
        )
    else:
        new_entry = re.sub(
            r"(\n\s*-\s*Notified:[^\n]+\n)",
            r"\1  - Notification-Count: " + str(nc_val) + "\n",
            new_entry
        )

    new_content = content[:entry_start] + new_entry + content[m.end():]

    with open(file_path, 'w') as f:
        f.write(new_content)
    return True

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: write_notified.py <json_file> <learnings_dir>", file=sys.stderr)
        sys.exit(1)

    json_file = sys.argv[1]
    learnings_dir = sys.argv[2]

    with open(json_file) as f:
        data = json.load(f)

    # File mapping: category → file path
    file_map = {
        "LEARNINGS.md": os.path.join(learnings_dir, "LEARNINGS.md"),
        "ERRORS.md": os.path.join(learnings_dir, "ERRORS.md"),
        "FEATURE_REQUESTS.md": os.path.join(learnings_dir, "FEATURE_REQUESTS.md"),
    }

    # Reverse map: infer file from source
    src_to_file = {
        "LEARNINGS.md": os.path.join(learnings_dir, "LEARNINGS.md"),
        "ERRORS.md": os.path.join(learnings_dir, "ERRORS.md"),
        "FEATURE_REQUESTS.md": os.path.join(learnings_dir, "FEATURE_REQUESTS.md"),
    }

    updated = 0
    for p in data.get("patterns", []) + data.get("category_fallback", []):
        if p.get("notification_trigger") != 1:
            continue
        notified_val = p.get("notified")
        # 只更新 notified 为 null/false 的条目
        if notified_val is not None and notified_val is True:
            continue  # already notified, skip

        nc_val = p.get("notification_count", 0)
        eid = p.get("first_entry_id", "")
        if not eid:
            continue

        src_cat = p.get("first_category", "")

        # 判断文件路径：first_category 是 "LEARNINGS.md" 或 "ERRORS.md" 等完整文件名
        if src_cat in file_map:
            path = file_map[src_cat]
        elif src_cat.startswith("insight.") or src_cat.startswith("error.") or src_cat.startswith("feature_name."):
            # 从 category 名字判断，默认 LEARNINGS.md
            path = file_map["LEARNINGS.md"]
        else:
            path = file_map.get(src_cat, file_map["LEARNINGS.md"])

        new_nc = nc_val + 1
        if update_md_file(path, eid, 1, new_nc):
            print(f"Updated: {eid} in {os.path.basename(path)} (nc={new_nc})", file=sys.stderr)
            updated += 1

    print(f"write-notified: {updated} entries updated", file=sys.stderr)
    sys.exit(0)