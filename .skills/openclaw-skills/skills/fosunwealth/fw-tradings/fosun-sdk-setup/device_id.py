import os
import uuid


def _resolve_workspace_root():
    return os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
    )


def _read_env_entries(env_path):
    entries = {}
    if not os.path.isfile(env_path):
        return entries
    with open(env_path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("#"):
            i += 1
            continue
        key, sep, value = line.partition("=")
        if not sep:
            i += 1
            continue
        key = key.strip()
        value = value.strip()
        if value.startswith("-----BEGIN "):
            pem_lines = [value]
            i += 1
            while i < len(lines):
                pem_line = lines[i].rstrip()
                pem_lines.append(pem_line)
                if pem_line.strip().startswith("-----END "):
                    i += 1
                    break
                i += 1
            value = "\n".join(pem_lines)
        else:
            i += 1
        entries[key] = value
    return entries


def _write_env_entries(env_path, entries):
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    with open(env_path, "w", encoding="utf-8") as f:
        for key in sorted(entries.keys()):
            value = entries.get(key, "")
            f.write(f"{key}={value}\n")


def get_or_create_device_id(env_path):
    entries = _read_env_entries(env_path)
    device_id = entries.get("FSOPENAPI_MAC_ID", "").strip()
    if device_id:
        return device_id

    device_id = uuid.uuid4().hex
    entries["FSOPENAPI_MAC_ID"] = device_id
    _write_env_entries(env_path, entries)
    return device_id


if __name__ == "__main__":
    workspace_root = _resolve_workspace_root()
    print(get_or_create_device_id(os.path.join(workspace_root, "fosun.env")))
