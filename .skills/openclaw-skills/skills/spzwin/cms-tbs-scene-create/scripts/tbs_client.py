"""
TBS Admin API helper for cms-tbs-scene-create.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any

import requests


TIMEOUT = 60
MAX_RETRIES = 3
RETRY_INTERVAL = 1


def extract_data(payload: Any) -> Any:
    if isinstance(payload, dict):
        if "data" in payload:
            return payload["data"]
        if "result" in payload:
            return payload["result"]
    return payload


def guess_entity_id(item: dict) -> str | None:
    for key in (
        "id",
        "personaId",
        "persona_id",
        "rolePersonaId",
        "knowledgeId",
        "knowledge_id",
        "departmentId",
        "drugId",
        "businessDomainId",
    ):
        value = item.get(key)
        if isinstance(value, (str, int, float)) and not isinstance(value, bool):
            text = str(value).strip()
            if text:
                return text
    return None


def _scalar_entity_id(value: Any) -> str | None:
    """Coerce API-returned scalar ids; do not treat 0 as 'missing'."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return str(value).strip() or None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        text = value.strip()
        return text or None
    return None


def extract_create_persona_id(raw_response: Any) -> str | None:
    """
    TBS createRolePersona success body is often::
        {"resultCode": 1, "data": 3008}
    so extract_data returns an int. Some gateways instead return a dict or put id on the envelope.
    """
    inner = extract_data(raw_response) if isinstance(raw_response, dict) else raw_response

    sid = _scalar_entity_id(inner)
    if sid is not None:
        return sid

    if isinstance(inner, dict):
        for key in (
            "id",
            "personaId",
            "persona_id",
            "recordId",
            "rolePersonaId",
        ):
            sid = _scalar_entity_id(inner.get(key))
            if sid is not None:
                return sid
        for nested_key in ("persona", "rolePersona", "entity", "result"):
            nested = inner.get(nested_key)
            if isinstance(nested, dict):
                sid = guess_entity_id(nested)
                if sid:
                    return sid
            sid = _scalar_entity_id(nested)
            if sid is not None:
                return sid
        guessed = guess_entity_id(inner)
        if guessed:
            return guessed

    if isinstance(raw_response, dict):
        for key in ("personaId", "persona_id", "id", "recordId", "data"):
            sid = _scalar_entity_id(raw_response.get(key))
            if sid is not None:
                return sid
    return None


def guess_entity_name(item: dict) -> str | None:
    for key in (
        "name",
        "title",
        "departmentName",
        "drugName",
        "businessDomainName",
    ):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def normalize_name(value: str) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    table = str.maketrans(
        {
            "（": "(",
            "）": ")",
            "，": ",",
            "、": ",",
            "－": "-",
            "–": "-",
            "—": "-",
        }
    )
    return "".join(text.translate(table).split()).lower()


def exact_match_ids(items: list[dict], target_name: str) -> list[str]:
    target = normalize_name(target_name)
    if not target:
        return []
    matches: list[str] = []
    for item in items:
        item_name = guess_entity_name(item)
        item_id = guess_entity_id(item)
        if item_id and normalize_name(item_name or "") == target:
            matches.append(item_id)
    seen = set()
    ordered: list[str] = []
    for item_id in matches:
        if item_id not in seen:
            seen.add(item_id)
            ordered.append(item_id)
    return ordered


class TBSClient:
    def __init__(self, base_url: str, access_token: str, timeout: int = TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "accept": "application/json",
            "access-token": self.access_token,
        }

    def request_json(self, method: str, path: str, body: dict | None = None) -> Any:
        url = self.base_url + (path if path.startswith("/") else f"/{path}")
        payload_text = json.dumps(body or {}, ensure_ascii=False)
        last_error: Exception | None = None

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.request(
                    method=method.upper(),
                    url=url,
                    headers=self._headers(),
                    json=body,
                    timeout=self.timeout,
                    verify=False,
                )
                if response.status_code >= 400:
                    raise RuntimeError(
                        f"HTTP {response.status_code} {method.upper()} {url}: {response.text[:500]}"
                    )
                try:
                    return response.json()
                except ValueError as exc:
                    raise RuntimeError(f"响应不是合法 JSON: {response.text[:500]}") from exc
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt >= MAX_RETRIES:
                    break
                time.sleep(RETRY_INTERVAL)

        raise RuntimeError(
            f"请求失败: {method.upper()} {url}, body={payload_text[:500]}, error={last_error}"
        )


def list_entities(client: TBSClient, path: str, body: dict | None = None) -> list[dict]:
    data = extract_data(client.request_json("POST", path, body or {}))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("records", "list", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def list_entities_get(client: TBSClient, path: str) -> list[dict]:
    data = extract_data(client.request_json("GET", path))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("records", "list", "items", "data"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def _maybe_id(value: str) -> str | None:
    text = str(value or "").strip()
    if text.isdigit():
        return text
    return None


def fingerprint_sha256_of_text(text: str) -> str:
    return hashlib.sha256(str(text or "").strip().encode("utf-8")).hexdigest()


def _ensure_text(value: Any) -> str:
    return str(value or "").strip()


def _find_persona_by_name_and_title(
    items: list[dict[str, Any]], name: str, title: str, role_type: str = ""
) -> str | None:
    target_name = normalize_name(name)
    target_title = normalize_name(title)
    target_role_type = normalize_name(role_type)
    for item in items:
        item_id = guess_entity_id(item)
        if not item_id or not isinstance(item, dict):
            continue
        item_name = normalize_name(
            item.get("name") or item.get("personaName") or item.get("doctorName") or ""
        )
        item_title = normalize_name(item.get("title") or item.get("doctorTitle") or "")
        item_role_type = normalize_name(item.get("roleType") or item.get("type") or "")
        if item_name != target_name:
            continue
        if target_title and item_title and item_title != target_title:
            continue
        if target_role_type and item_role_type and item_role_type != target_role_type:
            continue
        return str(item_id)
    return None


def resolve_or_create_business_domain(
    client: TBSClient,
    business_domain_name: str,
    allow_create: bool = True,
) -> tuple[str, dict]:
    candidate_id = _maybe_id(business_domain_name)
    if candidate_id:
        return candidate_id, {"action": "matched_by_id", "input": business_domain_name}

    items = list_entities(
        client,
        "/businessDomain/listBusinessDomains",
        {"pageNo": 1, "pageSize": 200, "name": business_domain_name},
    )
    matches = exact_match_ids(items, business_domain_name)
    if len(matches) == 1:
        return matches[0], {"action": "matched", "input": business_domain_name}
    if len(matches) > 1:
        raise RuntimeError(f"业务领域名称匹配到多条记录，需人工确认：{business_domain_name}")
    if not allow_create:
        raise RuntimeError(f"业务领域不存在：{business_domain_name}")

    payload = {"name": business_domain_name}
    created = extract_data(client.request_json("POST", "/businessDomain/createBusinessDomain", payload))
    created_id = str(created.get("id") if isinstance(created, dict) else created)
    if not created_id:
        raise RuntimeError("创建业务领域失败：返回中缺少 id")
    return created_id, {"action": "created", "input": business_domain_name}


def resolve_or_create_department(
    client: TBSClient,
    department_name: str,
    business_domain_id: str,
    business_domain_name: str,
    allow_create: bool = True,
) -> tuple[str, dict]:
    candidate_id = _maybe_id(department_name)
    if candidate_id:
        return candidate_id, {"action": "matched_by_id", "input": department_name}

    items = list_entities(
        client,
        "/department/listDepartments",
        {
            "pageNo": 1,
            "pageSize": 200,
            "name": department_name,
            "businessDomainId": business_domain_id,
        },
    )
    matches = exact_match_ids(items, department_name)
    if len(matches) == 1:
        return matches[0], {"action": "matched", "input": department_name}
    if len(matches) > 1:
        raise RuntimeError(f"科室名称匹配到多条记录，需人工确认：{department_name}")
    if not allow_create:
        raise RuntimeError(f"科室不存在：{department_name}")

    payload = {
        "name": department_name,
        "businessDomainId": business_domain_id,
        "businessDomainName": business_domain_name,
    }
    created = extract_data(client.request_json("POST", "/department/createDepartment", payload))
    created_id = str(created.get("id") if isinstance(created, dict) else created)
    if not created_id:
        raise RuntimeError("创建科室失败：返回中缺少 id")
    return created_id, {"action": "created", "input": department_name}


def resolve_or_create_drug(
    client: TBSClient,
    drug_name: str,
    business_domain_id: str,
    business_domain_name: str,
    allow_create: bool = True,
) -> tuple[str, dict]:
    candidate_id = _maybe_id(drug_name)
    if candidate_id:
        return candidate_id, {"action": "matched_by_id", "input": drug_name}

    items = list_entities(
        client,
        "/drug/listDrugs",
        {
            "pageNo": 1,
            "pageSize": 200,
            "name": drug_name,
            "businessDomainId": business_domain_id,
        },
    )
    matches = exact_match_ids(items, drug_name)
    if len(matches) == 1:
        return matches[0], {"action": "matched", "input": drug_name}
    if len(matches) > 1:
        raise RuntimeError(f"品种名称匹配到多条记录，需人工确认：{drug_name}")
    if not allow_create:
        raise RuntimeError(f"品种不存在：{drug_name}")

    payload = {
        "name": drug_name,
        "businessDomainId": business_domain_id,
        "businessDomainName": business_domain_name,
    }
    created = extract_data(client.request_json("POST", "/drug/createDrug", payload))
    created_id = str(created.get("id") if isinstance(created, dict) else created)
    if not created_id:
        raise RuntimeError("创建品种失败：返回中缺少 id")
    return created_id, {"action": "created", "input": drug_name}


def resolve_or_create_persona(
    client: TBSClient, scene: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    actor_profile = scene.get("actorProfile") if isinstance(scene.get("actorProfile"), dict) else {}
    if not actor_profile and isinstance(scene.get("doctorProfile"), dict):
        actor_profile = scene.get("doctorProfile")
    if not actor_profile:
        return [], {"action": "skipped", "reason": "missing_actor_profile"}

    name = _ensure_text(
        actor_profile.get("name")
        or actor_profile.get("doctor_name")
        or actor_profile.get("persona_name")
    )
    title = _ensure_text(actor_profile.get("title") or actor_profile.get("doctor_title"))
    role_type = _ensure_text(actor_profile.get("roleType"))
    if not name:
        raise RuntimeError("actorProfile.name 必填，无法解析或创建画像。")

    items = list_entities_get(client, "/rolePersona/forResourceSelect")
    matched_id = _find_persona_by_name_and_title(items, name=name, title=title, role_type=role_type)
    if matched_id:
        persona_entry = {
            "personaId": str(matched_id),
            "difficulty": _ensure_text(actor_profile.get("difficulty")) or "medium",
            "isDefault": bool(actor_profile.get("isDefault", True)),
            "rounds": int(actor_profile.get("rounds") or 5),
        }
        return [persona_entry], {"action": "matched", "input": {"name": name, "title": title}}

    description = _ensure_text(
        actor_profile.get("description")
        or actor_profile.get("desc")
        or actor_profile.get("summary")
    )
    persona_config = actor_profile.get("personaConfig") or actor_profile.get("persona_config")
    payload: dict[str, Any] = {
        "name": name,
        "title": title,
        "description": description,
        "trustInitial": int(actor_profile.get("trustInitial") or actor_profile.get("trust_initial") or 80),
        "patienceInitial": int(actor_profile.get("patienceInitial") or actor_profile.get("patience_initial") or 80),
        "isPreset": False,
    }
    surname = _ensure_text(
        actor_profile.get("surname")
        or actor_profile.get("last_name")
        or actor_profile.get("family_name")
    )
    if surname:
        payload["surname"] = surname
    if persona_config:
        payload["personaConfig"] = (
            persona_config
            if isinstance(persona_config, str)
            else json.dumps(persona_config, ensure_ascii=False)
        )

    raw = client.request_json("POST", "/rolePersona/createRolePersona", body=payload)
    created_id = extract_create_persona_id(raw)
    if created_id is None:
        preview = raw
        if isinstance(raw, dict):
            preview = {k: raw.get(k) for k in list(raw.keys())[:12]}
        raise RuntimeError(
            "创建角色画像失败：响应中无法解析画像 ID（已兼容 data 为数值、id/personaId 及常见嵌套）。"
            f" 响应摘要: {json.dumps(preview, ensure_ascii=False)[:800]}"
        )

    persona_entry = {
        "personaId": str(created_id),
        "difficulty": _ensure_text(actor_profile.get("difficulty")) or "medium",
        "isDefault": bool(actor_profile.get("isDefault", True)),
        "rounds": int(actor_profile.get("rounds") or 5),
    }
    return [persona_entry], {"action": "created", "input": {"name": name, "title": title}}


def _knowledge_has_evidence(knowledge_draft: dict[str, Any]) -> bool:
    if knowledge_draft.get("evidenceReady") is True:
        return True
    if str(knowledge_draft.get("evidenceStatus") or "").upper() == "READY":
        return True
    for key in ("evidenceSource", "evidenceSources", "source", "sources", "productEvidenceSource"):
        value = knowledge_draft.get(key)
        if isinstance(value, str) and value.strip():
            return True
        if isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value):
            return True
    return False


def _fetch_existing_knowledge(
    client: TBSClient, drug_id: str, title: str = "", category: str = ""
) -> list[dict[str, Any]]:
    list_err: Exception | None = None
    body: dict[str, Any] = {"pageNo": 1, "pageSize": 200, "drugId": drug_id}
    if title:
        body["title"] = title
    if category:
        body["category"] = category
    try:
        payload = client.request_json("POST", "/knowledge/listProductKnowledge", body=body)
        data = extract_data(payload)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("records", "list", "items"):
                value = data.get(key)
                if isinstance(value, list):
                    return value
    except Exception as exc:  # noqa: BLE001
        list_err = exc

    try:
        payload = client.request_json("GET", f"/knowledge/forResourceSelect?drugId={drug_id}")
        data = extract_data(payload)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("records", "list", "items", "data"):
                value = data.get(key)
                if isinstance(value, list):
                    return value
    except Exception as exc:  # noqa: BLE001
        if list_err is not None:
            raise RuntimeError(
                f"产品知识查询失败：listProductKnowledge={list_err}; forResourceSelect={exc}"
            ) from exc
        raise RuntimeError(f"产品知识查询失败：forResourceSelect={exc}") from exc
    return []


def create_knowledge_if_needed_by_dedup(
    client: TBSClient, drug_id: str, knowledge_draft: dict[str, Any], category: str
) -> dict[str, str] | None:
    title = str(knowledge_draft.get("title") or "").strip()
    content = str(knowledge_draft.get("content") or "").strip()
    if not content:
        return None

    existing = _fetch_existing_knowledge(client, drug_id=drug_id, title=title, category=category)
    content_fp = fingerprint_sha256_of_text(content)

    for item in existing:
        item_id = guess_entity_id(item)
        item_title = ""
        if isinstance(item, dict):
            item_title = str(item.get("title") or item.get("name") or "").strip()
        if item_id and title and item_title == title:
            return {"id": str(item_id), "mode": "matched_by_title"}

    for item in existing:
        if not isinstance(item, dict):
            continue
        item_id = guess_entity_id(item)
        item_content = str(item.get("content") or item.get("text") or "").strip()
        if item_id and fingerprint_sha256_of_text(item_content) == content_fp:
            return {"id": str(item_id), "mode": "matched_by_content"}

    payload = {
        "drugId": drug_id,
        "category": category,
        "title": title,
        "content": content,
    }
    created = extract_data(client.request_json("POST", "/knowledge/createProductKnowledge", body=payload))
    created_id = None
    if isinstance(created, dict):
        created_id = (
            created.get("id")
            or created.get("knowledgeId")
            or created.get("knowledge_id")
            or guess_entity_id(created)
        )
    else:
        created_id = created
    if not created_id:
        raise RuntimeError("创建产品知识失败：返回中缺少 knowledgeId")
    return {"id": str(created_id), "mode": "created"}


def resolve_or_create_knowledge_for_scene(
    client: TBSClient, scene: dict[str, Any], drug_id: str
) -> tuple[list[str], dict[str, Any]]:
    knowledge_drafts = scene.get("knowledge") or scene.get("sceneKnowledge") or []
    if isinstance(knowledge_drafts, dict) and "items" in knowledge_drafts:
        knowledge_drafts = knowledge_drafts["items"]
    if not isinstance(knowledge_drafts, list):
        return [], {"action": "skipped", "reason": "knowledge_not_list"}

    evidence_status = str(scene.get("productEvidenceStatus") or "NOT_PROVIDED").upper()
    report: dict[str, Any] = {
        "action": "processed",
        "evidenceStatus": evidence_status,
        "totalDrafts": len(knowledge_drafts),
        "created": 0,
        "matchedByTitle": 0,
        "matchedByContent": 0,
        "skippedNoContent": 0,
        "skippedNoEvidence": 0,
        "skippedByEvidenceStatus": 0,
        "pendingEvidenceTasks": [],
    }
    knowledge_ids: list[str] = []

    if evidence_status == "NOT_PROVIDED":
        report["skippedByEvidenceStatus"] = len(knowledge_drafts)
        for draft in knowledge_drafts:
            if not isinstance(draft, dict):
                continue
            report["pendingEvidenceTasks"].append(
                {
                    "title": str(draft.get("title") or "").strip() or "(untitled)",
                    "reason": "NOT_PROVIDED: skip creation until evidence is ready",
                }
            )
        return knowledge_ids, report

    for draft in knowledge_drafts:
        if not isinstance(draft, dict):
            continue
        title = str(draft.get("title") or "").strip() or "(untitled)"
        content = str(draft.get("content") or "").strip()
        if not content:
            report["skippedNoContent"] += 1
            continue
        if evidence_status == "PARTIAL" and not _knowledge_has_evidence(draft):
            report["skippedNoEvidence"] += 1
            report["pendingEvidenceTasks"].append(
                {"title": title, "reason": "PARTIAL: item has no evidence source"}
            )
            continue
        category = str(draft.get("category") or draft.get("knowledge_category") or "").strip()
        result = create_knowledge_if_needed_by_dedup(
            client=client, drug_id=drug_id, knowledge_draft=draft, category=category
        )
        if result and result.get("id"):
            knowledge_ids.append(str(result["id"]))
            mode = result.get("mode")
            if mode == "created":
                report["created"] += 1
            elif mode == "matched_by_title":
                report["matchedByTitle"] += 1
            elif mode == "matched_by_content":
                report["matchedByContent"] += 1
    return knowledge_ids, report


def resolve_ids_for_scene(client: TBSClient, scene: dict) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    business_domain_name = str(scene.get("businessDomainName") or "").strip()
    department_name = str(scene.get("departmentName") or "").strip()
    drug_name = str(scene.get("drugName") or "").strip()
    if not business_domain_name:
        raise RuntimeError("缺少 businessDomainName")
    if not department_name:
        raise RuntimeError("缺少 departmentName")
    if not drug_name:
        raise RuntimeError("缺少 drugName")

    business_domain_id, business_domain_report = resolve_or_create_business_domain(
        client, business_domain_name
    )
    department_id, department_report = resolve_or_create_department(
        client, department_name, business_domain_id, business_domain_name
    )
    drug_id, drug_report = resolve_or_create_drug(
        client, drug_name, business_domain_id, business_domain_name
    )
    persona_ids, persona_report = resolve_or_create_persona(client, scene)
    knowledge_ids, knowledge_report = resolve_or_create_knowledge_for_scene(client, scene, drug_id)

    return (
        {
            "businessDomainId": business_domain_id,
            "departmentId": department_id,
            "drugId": drug_id,
            "personaIds": persona_ids,
            "knowledgeIds": knowledge_ids,
        },
        {
            "businessDomain": business_domain_report,
            "department": department_report,
            "drug": drug_report,
            "persona": persona_report,
            "knowledge": knowledge_report,
        },
    )
