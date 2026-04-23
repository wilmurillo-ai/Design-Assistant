"""
Create a TBS scene after explicit user confirmation.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from tbs_client import TBSClient, extract_data, resolve_ids_for_scene


STEP = "tbs-scene-create"
DEFAULT_BASE_URL = "https://sg-al-cwork-web.mediportal.com.cn/tbs-admin"


def emit_success(payload: dict[str, Any]) -> None:
    payload = {"success": True, **payload}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def emit_error(error: str, exit_code: int = 1, **extra: Any) -> None:
    payload = {"success": False, "step": STEP, "error": error, **extra}
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    sys.exit(exit_code)


def read_payload(input_path: str | None, params_file: str | None) -> dict[str, Any]:
    path = params_file or input_path
    if path and path != "-":
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    raw = sys.stdin.read()
    return json.loads(raw or "{}")


def require_confirmation(payload: dict[str, Any]) -> str:
    value = str(payload.get("userConfirmation") or "").strip()
    if not value:
        raise RuntimeError("缺少 userConfirmation，必须为 确认 或 取消")
    if value not in {"确认", "取消"}:
        raise RuntimeError("userConfirmation 仅允许为 确认 或 取消")
    return value


def persist_result(
    draft_path: str | None,
    scene: dict[str, Any],
    validation_report: dict[str, Any],
    scene_id: str,
    resolved_ids: dict[str, Any],
    resolution_report: dict[str, dict[str, Any]],
) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    payload = {
        "scene": scene,
        "validationReport": validation_report,
        "persistResult": {
            "sceneId": scene_id,
            "resolvedIds": resolved_ids,
            "resolutionReport": resolution_report,
            "updatedAt": datetime.now(timezone.utc).isoformat(),
        },
        "meta": {
            "updatedAt": datetime.now(timezone.utc).isoformat(),
            "lastStep": STEP,
        },
    }
    with open(draft_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="-", help="JSON file path, or '-' for stdin")
    parser.add_argument("--params-file", default=None, help="Read params from UTF-8 JSON file")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--access-token", required=True)
    args = parser.parse_args()

    payload = read_payload(args.input, args.params_file)
    try:
        confirmation = require_confirmation(payload)
    except RuntimeError as exc:
        emit_error(str(exc), exit_code=2)
    if confirmation == "取消":
        emit_error("user_cancelled", exit_code=0, hint="用户已取消，本次不执行创建。")

    access_token = str(args.access_token or "").strip()
    if not access_token:
        emit_error("缺少 access-token", exit_code=2)

    scene = payload.get("scene") if isinstance(payload.get("scene"), dict) else {}
    validation_report = (
        payload.get("validationReport") if isinstance(payload.get("validationReport"), dict) else {}
    )
    draft_path = payload.get("draftPath")
    if not scene and (args.params_file or (args.input and args.input != "-")):
        draft_path = args.params_file or args.input
        loaded = read_payload(draft_path, None)
        scene = loaded.get("scene") if isinstance(loaded.get("scene"), dict) else {}
        validation_report = (
            loaded.get("validationReport") if isinstance(loaded.get("validationReport"), dict) else {}
        )
    if not scene:
        emit_error("缺少 scene", exit_code=2)
    if validation_report.get("passed") is not True:
        emit_error(
            "validation_not_passed",
            exit_code=2,
            hint="必须先完成 tbs-scene-validate.py 且 validationReport.passed=true",
        )

    # Use sceneBackground as canonical background text for persistence/display.
    canonical_background = str(scene.get("sceneBackground") or scene.get("background") or "").strip()
    if canonical_background:
        scene["sceneBackground"] = canonical_background
        scene["background"] = canonical_background
        scene["repBriefing"] = canonical_background

    client = TBSClient(base_url=args.base_url, access_token=access_token)
    try:
        resolved_ids, resolution_report = resolve_ids_for_scene(client, scene)
        if resolved_ids.get("personaIds"):
            scene["personaIds"] = resolved_ids.get("personaIds") or []
        if resolved_ids.get("knowledgeIds"):
            scene["knowledgeIds"] = [str(item) for item in resolved_ids.get("knowledgeIds") or []]
        body = {
            "title": scene["title"],
            "businessDomainId": resolved_ids["businessDomainId"],
            "departmentId": resolved_ids["departmentId"],
            "drugId": resolved_ids["drugId"],
            "location": scene["location"],
            "doctorOnlyContext": scene["doctorOnlyContext"],
            "coachOnlyContext": scene["coachOnlyContext"],
            "repBriefing": scene["repBriefing"],
            "personaIds": resolved_ids.get("personaIds") or [],
            "knowledgeIds": resolved_ids.get("knowledgeIds") or [],
            "status": 1,
        }
        created = extract_data(client.request_json("POST", "/scene/createScene", body))
        scene_id = str(created.get("id") if isinstance(created, dict) else created)
        if not scene_id:
            raise RuntimeError("createScene 返回中缺少 sceneId")
    except Exception as exc:  # noqa: BLE001
        emit_error(str(exc), exit_code=1)

    if isinstance(draft_path, str) and draft_path.strip():
        persist_result(
            draft_path=draft_path.strip(),
            scene=scene,
            validation_report=validation_report,
            scene_id=scene_id,
            resolved_ids=resolved_ids,
            resolution_report=resolution_report,
        )

    emit_success(
        {
            "step": STEP,
            "sceneId": scene_id,
            "resolvedIds": resolved_ids,
            "resolutionReport": resolution_report,
            "personaIds": resolved_ids.get("personaIds") or [],
            "knowledgeIds": resolved_ids.get("knowledgeIds") or [],
            "message": "场景创建成功",
        }
    )


if __name__ == "__main__":
    main()
