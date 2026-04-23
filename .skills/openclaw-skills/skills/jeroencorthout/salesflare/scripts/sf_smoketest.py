#!/usr/bin/env python3
"""Smoke-test Salesflare OpenAPI operations with safe defaults.

Execution order (enforced):
  Phase 1 — GET list endpoints (no path params); IDs collected here.
  Phase 2 — GET by-id endpoints (path params); uses IDs from Phase 1.
  Phase 3 — POST / PUT / PATCH; uses IDs from Phase 1 (opt-in via --allow-write).
  Phase 4 — DELETE; requires BOTH --allow-write and --allow-delete.

Within each phase operations are sorted by (path, method) for determinism.
IDs are never invented: only IDs returned by Phase 1 list responses are used.
If an entity list yields no IDs, all id-based tests for that entity are skipped
with a clear reason.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Any

DEFAULT_OPENAPI_URL = "https://api.salesflare.com/openapi.json"
DEFAULT_BASE_URL = "https://api.salesflare.com"

# Phase constants (used as sort key)
_PHASE_GET_LIST = 0
_PHASE_GET_ID   = 1
_PHASE_WRITE    = 2
_PHASE_DELETE   = 3


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def load_spec(src: str) -> dict[str, Any]:
    if src.startswith("http://") or src.startswith("https://"):
        with urllib.request.urlopen(src, timeout=45) as r:
            return json.loads(r.read().decode("utf-8"))
    return json.loads(Path(src).read_text(encoding="utf-8"))


def call_json(
    method: str,
    url: str,
    api_key: str,
    body: Any | None,
    timeout: int = 45,
    retries: int = 2,
) -> tuple[int, Any]:
    payload = None if body is None else json.dumps(body).encode("utf-8")
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=payload, method=method)
        req.add_header("Authorization", f"Bearer {api_key}")
        req.add_header("Accept", "application/json")
        if payload is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8", errors="replace")
                try:
                    return int(r.getcode() or 200), json.loads(raw) if raw else {}
                except Exception:
                    return int(r.getcode() or 200), {"raw": raw[:2000]}
        except urllib.error.HTTPError as e:
            code = int(e.code)
            raw = e.read().decode("utf-8", errors="replace")
            if code == 429 and attempt < retries:
                time.sleep(1.5 * (2 ** attempt))
                attempt += 1
                continue
            try:
                return code, json.loads(raw) if raw else {}
            except Exception:
                return code, {"raw": raw[:2000]}
        except Exception as exc:
            if attempt < retries:
                time.sleep(1.5 * (2 ** attempt))
                attempt += 1
                continue
            return 0, {"error": str(exc)}


# ---------------------------------------------------------------------------
# Data extraction helpers
# ---------------------------------------------------------------------------

def _as_list(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for k in ("data", "items", "results"):
            if isinstance(data.get(k), list):
                return data[k]
    return []


def _first_top_level_id(data: Any) -> int | None:
    for item in _as_list(data):
        if isinstance(item, dict) and isinstance(item.get("id"), int):
            if item.get("id") not in (None, 0):
                return int(item["id"])
    return None


# ---------------------------------------------------------------------------
# Phase 1: collect IDs from list endpoints
# ---------------------------------------------------------------------------

# Maps the sample key name to the list path to probe.
_LIST_PROBES: dict[str, str] = {
    "account_id":     "/accounts?limit=1",
    "contact_id":     "/contacts?limit=1",
    "opportunity_id": "/opportunities?limit=1",
    "task_id":        "/tasks?limit=1",
    "workflow_id":    "/workflows?limit=1",
    "user_id":        "/users?limit=1",
    "tag_id":         "/tags?limit=1",
    "stage_id":       "/stages?limit=1",
    "meeting_id":     "/meetings?limit=1",
    "message_id":     "/messages?limit=1",
    "call_id":        "/calls?limit=1",
    "datasource_id":  "/datasources/email?limit=1",
}


def collect_samples(base_url: str, api_key: str) -> dict[str, int]:
    """Phase 1: call each list endpoint and record the first discovered ID.

    Returns a dict of {sample_key: int_id}.  Only keys where a valid ID was
    found are included — callers must check presence, not assume a value.
    """
    base = base_url.rstrip("/")
    samples: dict[str, int] = {}

    # Deterministic probe order (sorted by key for stability).
    for key in sorted(_LIST_PROBES):
        path = _LIST_PROBES[key]
        status, data = call_json("GET", base + path, api_key, None)
        if 200 <= status < 300:
            i = _first_top_level_id(data)
            if isinstance(i, int):
                samples[key] = i

    # Groups can include a synthetic entry with null id; grab first non-null.
    status, data = call_json("GET", base + "/groups", api_key, None)
    if 200 <= status < 300:
        gid = _first_top_level_id(data)
        if isinstance(gid, int):
            samples["group_id"] = gid

    # Determine a real select custom-field API name for options endpoint.
    samples["customFieldApiField"] = "parent_account"  # safe default
    status, data = call_json("GET", base + "/customfields/accounts", api_key, None)
    if 200 <= status < 300 and isinstance(data, list):
        for fld in data:
            if isinstance(fld, dict) and fld.get("type") == "select" and fld.get("api_field"):
                samples["customFieldApiField"] = str(fld["api_field"])
                break

    return samples


# ---------------------------------------------------------------------------
# Path filling
# ---------------------------------------------------------------------------

def _required_id_key(path: str) -> str | None:
    """Return the samples key whose presence is required to run this path.

    Returns None for paths with no path params, or for paths whose params
    are non-ID placeholders (itemClass, customFieldApiField).
    """
    params = re.findall(r"\{([^}]+)\}", path)
    if not params:
        return None

    named_param_map = {
        "account_id":    "account_id",
        "contact_id":    "contact_id",
        "tag_id":        "tag_id",
        "stage_id":      "stage_id",
        "meeting_id":    "meeting_id",
        "message_id":    "message_id",
        "call_id":       "call_id",
        "datasource_id": "datasource_id",
    }

    for p in params:
        if p in named_param_map:
            return named_param_map[p]

    # Bare {id}: context from path prefix
    if "id" in params:
        if path.startswith("/opportunities/"):
            return "opportunity_id"
        if path.startswith("/tasks/"):
            return "task_id"
        if path.startswith("/users/"):
            return "user_id"
        if path.startswith("/groups/"):
            return "group_id"
        if path.startswith("/workflows/"):
            return "workflow_id"
        if path.startswith("/datasources/email/"):
            return "datasource_id"

    # Non-ID params only (itemClass, customFieldApiField) — no ID gate needed.
    return None


def fill_path(path: str, samples: dict[str, int | str]) -> str:
    mapping: dict[str, Any] = {
        "account_id":         samples.get("account_id", 0),
        "contact_id":         samples.get("contact_id", 0),
        "stage_id":           samples.get("stage_id", 0),
        "tag_id":             samples.get("tag_id", 0),
        "meeting_id":         samples.get("meeting_id", samples.get("call_id", 0)),
        "message_id":         samples.get("message_id", 0),
        "call_id":            samples.get("call_id", 0),
        "conference_id":      0,
        "record_id":          0,
        "itemClass":          "accounts",
        "customFieldApiField": samples.get("customFieldApiField", "parent_account"),
        "id":                 0,
    }

    # Contextualise bare {id}
    if "{id}" in path:
        if path.startswith("/opportunities/"):
            mapping["id"] = samples.get("opportunity_id", 0)
        elif path.startswith("/tasks/"):
            mapping["id"] = samples.get("task_id", 0)
        elif path.startswith("/users/"):
            mapping["id"] = samples.get("user_id", 0)
        elif path.startswith("/groups/"):
            mapping["id"] = samples.get("group_id", 0)
        elif path.startswith("/workflows/"):
            mapping["id"] = samples.get("workflow_id", 0)
        elif path.startswith("/datasources/email/"):
            mapping["id"] = samples.get("datasource_id", 0)

    def repl(match: re.Match[str]) -> str:
        k = match.group(1)
        return str(mapping.get(k, 0))

    return re.sub(r"\{([^}]+)\}", repl, path)


# ---------------------------------------------------------------------------
# Request helpers
# ---------------------------------------------------------------------------

def body_for(method: str, path: str, samples: dict[str, Any]) -> Any | None:
    if method in {"POST", "PUT", "PATCH"}:
        if path == "/tags":
            return {"name": "openclaw-test-tag"}
        if path == "/tasks":
            return {"description": "OpenClaw API smoke test task", "account": samples.get("account_id", 0)}
        if path == "/accounts":
            return {"name": "OpenClaw API SmokeTest"}
        if path == "/contacts":
            return {
                "email": "smoketest@example.com",
                "firstname": "Smoke",
                "lastname": "Test",
                "account": samples.get("account_id", 0),
            }
        if path == "/opportunities":
            return {"account": samples.get("account_id", 0), "name": "OpenClaw API SmokeTest Opp"}
        if path in {"/calls", "/meetings"}:
            now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            return {"date": now_iso, "participants": [samples.get("contact_id", 0)]}
        if path == "/messages":
            return {"account": samples.get("account_id", 0), "body": "OpenClaw smoke test message"}
        if path in {"/messages/{message_id}/feedback", "/message/{message_id}/feedback"}:
            return {"feedback": "helpful"}
        if path == "/workflows":
            return {"name": "OpenClaw Smoke Workflow"}
        return {}
    return None


def append_default_query(path: str, method: str, op: dict[str, Any]) -> list[tuple[str, str]]:
    q: list[tuple[str, str]] = []

    list_with_limit_prefixes = (
        "/accounts",
        "/contacts",
        "/opportunities",
        "/tasks",
        "/users",
        "/workflows",
        "/tags",
        "/messages",
        "/meetings",
        "/calls",
    )
    if method == "GET" and "{" not in path and path.startswith(list_with_limit_prefixes):
        q.append(("limit", "1"))

    for p in op.get("parameters") or []:
        if p.get("in") != "query" or not p.get("required"):
            continue
        name = p.get("name")
        if name == "limit":
            q.append(("limit", "1"))
        elif name == "offset":
            q.append(("offset", "0"))
        elif name and name != "q":
            q.append((name, "1"))

    if method == "GET" and path == "/persons":
        q = [("search", "a")]

    return q


# ---------------------------------------------------------------------------
# Phase bucketing
# ---------------------------------------------------------------------------

def _phase_for(method: str, path: str) -> int:
    if method == "GET":
        return _PHASE_GET_LIST if "{" not in path else _PHASE_GET_ID
    if method == "DELETE":
        return _PHASE_DELETE
    return _PHASE_WRITE  # POST, PUT, PATCH


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_OPENAPI_URL)
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--api-key", default=os.environ.get("SALESFLARE_API_KEY"))
    _skill_dir = Path(__file__).parent.parent
    ap.add_argument("--out-json", default=str(_skill_dir / "references" / "test-results.json"))
    ap.add_argument("--out-md", default=str(_skill_dir / "references" / "test-results.md"))
    ap.add_argument(
        "--allow-write",
        action="store_true",
        help="Allow write operations (POST/PUT/PATCH). Disabled by default.",
    )
    ap.add_argument(
        "--allow-delete",
        action="store_true",
        help="Allow DELETE operations. Requires --allow-write.",
    )
    ap.add_argument(
        "--safe-write",
        action="store_true",
        help="Use write-safe mode: force non-existing ids on path params",
    )
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("Missing API key")

    spec = load_spec(args.source)
    paths = spec.get("paths", {})

    # ------------------------------------------------------------------
    # Phase 1: collect IDs from list endpoints (no API spec loop yet).
    # ------------------------------------------------------------------
    samples = collect_samples(args.base_url, args.api_key)

    results: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Bucket all spec operations by phase; sort for determinism.
    # Order within bucket: (path, method).
    # ------------------------------------------------------------------
    ops: list[tuple[int, str, str, dict[str, Any]]] = []  # (phase, path, method, op)
    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            m = method.upper()
            if m not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                continue
            ops.append((_phase_for(m, path), path, m, op))

    ops.sort(key=lambda x: (x[0], x[1], x[2]))

    # ------------------------------------------------------------------
    # Execute in phase order.
    # ------------------------------------------------------------------
    for phase, path, m, op in ops:

        # ---- hard-coded skip: known broken endpoint ----
        if m == "GET" and path == "/tags/{tag_id}":
            results.append(_skip(m, path, op, "Skipped: unsupported in this skill (server-side 500)"))
            continue

        # ---- write/delete gates ----
        if m in {"POST", "PUT", "PATCH"} and not args.allow_write:
            results.append(_skip(m, path, op, "Skipped: write operations disabled by default (use --allow-write)"))
            continue

        if m == "DELETE" and not args.allow_write:
            results.append(_skip(m, path, op, "Skipped: DELETE requires --allow-write and --allow-delete"))
            continue

        if m == "DELETE" and not args.allow_delete:
            results.append(_skip(m, path, op, "Skipped: DELETE disabled by default (use --allow-delete with --allow-write)"))
            continue

        if m == "DELETE" and path.startswith("/users/"):
            results.append(_skip(m, path, op, "Skipped per instruction: do not delete users"))
            continue

        # ---- ID availability gate (phases 2-4 only) ----
        if phase > _PHASE_GET_LIST:
            required_key = _required_id_key(path)
            if required_key and required_key not in samples:
                results.append(
                    _skip(
                        m,
                        path,
                        op,
                        f"Skipped: no {required_key} discovered from list (Phase 1 returned no IDs)",
                    )
                )
                continue

        # ---- Build URL ----
        filled_path = fill_path(path, samples)

        if path.startswith("/filterfields/"):
            filled_path = "/filterfields/contact"

        if args.safe_write and m in {"POST", "PUT", "PATCH", "DELETE"}:
            filled_path = re.sub(r"/\d+(?=/|$)", "/999999999", filled_path)

        query_pairs = append_default_query(filled_path, m, op)
        url = args.base_url.rstrip("/") + filled_path
        if query_pairs:
            url += "?" + urllib.parse.urlencode(query_pairs, doseq=True)

        body = body_for(m, path, samples)
        status, data = call_json(m, url, args.api_key, body)

        if status == 0:
            outcome = "network_error"
        elif 200 <= status < 300:
            outcome = "ok"
        elif 400 <= status < 500:
            outcome = "client_error"
        else:
            outcome = "server_error"

        err_preview = ""
        if isinstance(data, dict):
            for k in ("error", "message", "details", "raw"):
                if k in data and data[k]:
                    err_preview = str(data[k])[:180]
                    break
        elif isinstance(data, list):
            err_preview = f"list[{len(data)}]"

        results.append(
            {
                "phase": phase,
                "method": m,
                "path": path,
                "resolved_path": filled_path,
                "operationId": op.get("operationId"),
                "summary": op.get("summary"),
                "status": status,
                "outcome": outcome,
                "note": err_preview,
            }
        )

        time.sleep(0.1)

    # ------------------------------------------------------------------
    # Aggregate
    # ------------------------------------------------------------------
    by_outcome: dict[str, int] = defaultdict(int)
    by_status: dict[str, int] = defaultdict(int)
    for r in results:
        by_outcome[r["outcome"]] += 1
        if r.get("status") is not None:
            by_status[str(r["status"])] += 1

    payload = {
        "source": args.source,
        "base_url": args.base_url,
        "sample_ids": samples,
        "summary": {
            "total": len(results),
            "by_outcome": dict(sorted(by_outcome.items())),
            "by_status": dict(
                sorted(by_status.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 9999)
            ),
        },
        "results": results,
    }

    Path(args.out_json).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Markdown report
    phase_labels = {
        _PHASE_GET_LIST: "GET list",
        _PHASE_GET_ID:   "GET by-id",
        _PHASE_WRITE:    "write (POST/PUT/PATCH)",
        _PHASE_DELETE:   "DELETE",
    }
    lines = [
        "# Salesflare API smoke test results",
        "",
        f"- Source: `{args.source}`",
        f"- Base URL: `{args.base_url}`",
        f"- Total operations tested: **{len(results)}**",
        "",
        "## Summary",
        "",
    ]
    for k, v in payload["summary"]["by_outcome"].items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "### Status distribution",
        "",
    ]
    for k, v in payload["summary"]["by_status"].items():
        lines.append(f"- {k}: {v}")
    lines += [
        "",
        "## Operation matrix",
        "",
        "| Phase | Method | Path | Status | Outcome | Note |",
        "|---|---|---|---:|---|---|",
    ]
    for r in results:
        note = (r.get("note") or "").replace("|", "\\|").replace("\n", " ")
        st = "" if r.get("status") is None else str(r.get("status"))
        ph = phase_labels.get(r.get("phase", -1), "")
        lines.append(f"| {ph} | {r['method']} | `{r['path']}` | {st} | {r['outcome']} | {note[:120]} |")

    Path(args.out_md).write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload["summary"], indent=2))
    print(f"Wrote: {args.out_json}")
    print(f"Wrote: {args.out_md}")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skip(method: str, path: str, op: dict[str, Any], note: str) -> dict[str, Any]:
    return {
        "phase": _phase_for(method, path),
        "method": method,
        "path": path,
        "operationId": op.get("operationId"),
        "summary": op.get("summary"),
        "status": None,
        "outcome": "skipped",
        "note": note,
    }


if __name__ == "__main__":
    main()
