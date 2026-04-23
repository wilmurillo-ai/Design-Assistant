"""
Parse TBS scene input and output staged confirmation guidance.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

from tbs_md_sanitize import sanitize_doctor_core_concerns_to_two_bullets


STEP = "tbs-scene-parse"
FIELD_LABELS = {
    "title": "场景标题",
    "businessDomainName": "业务领域",
    "departmentName": "科室",
    "drugName": "产品名称",
    "location": "地点",
    "doctorConcerns": "医生顾虑",
    "repGoal": "代表目标",
    "sceneBackground": "场景背景",
    "productKnowledgeNeeds": "产品知识需求",
    "knowledge": "产品知识补充内容",
    "repBriefing": "场景背景叙述",
    "doctorOnlyContext": "对练对象侧上下文",
    "coachOnlyContext": "教练侧上下文",
    "actorProfile": "对练对象角色",
    "productEvidenceStatus": "产品证据状态",
    "productEvidenceSource": "产品证据资料",
    "needsEvidenceConfirmation": "是否仍需补充证据资料",
    "generationNotes": "待确认说明",
}
EVIDENCE_STATUS_LABELS = {
    "NOT_PROVIDED": "未提供",
    "PARTIAL": "部分提供",
    "READY": "已齐备",
}
BASE_CONFIRM_FIELDS = [
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
]
KNOWLEDGE_CONFIRM_FIELDS = [
    "productKnowledgeNeeds",
]
KNOWLEDGE_GATE_FIELDS = [
    "productEvidenceStatus",
    "productEvidenceSource",
]
GENERATED_CONFIRM_FIELDS = [
    "title",
    "sceneBackground",
    "actorProfile",
]
GENERATED_GATE_FIELDS = [
    "repBriefing",
]
INTERNAL_GENERATED_FIELDS = [
    "doctorOnlyContext",
    "coachOnlyContext",
]
FINAL_REQUIRED_FIELDS = (
    BASE_CONFIRM_FIELDS
    + KNOWLEDGE_CONFIRM_FIELDS
    + KNOWLEDGE_GATE_FIELDS
    + ["needsEvidenceConfirmation"]
    + GENERATED_CONFIRM_FIELDS
    + GENERATED_GATE_FIELDS
    + INTERNAL_GENERATED_FIELDS
)
STAGE_BASE_INFO_CONFIRM = "BASE_INFO_CONFIRM"
STAGE_KNOWLEDGE_CONFIRM = "KNOWLEDGE_CONFIRM"
STAGE_READY_FOR_SCENE_GENERATION = "READY_FOR_SCENE_GENERATION"
STAGE_READY_FOR_VALIDATE = "READY_FOR_VALIDATE"
STAGE_CONFIRM_FIELDS = {
    STAGE_BASE_INFO_CONFIRM: BASE_CONFIRM_FIELDS,
    STAGE_KNOWLEDGE_CONFIRM: BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS,
    STAGE_READY_FOR_SCENE_GENERATION: BASE_CONFIRM_FIELDS
    + KNOWLEDGE_CONFIRM_FIELDS
    + GENERATED_CONFIRM_FIELDS,
    STAGE_READY_FOR_VALIDATE: BASE_CONFIRM_FIELDS
    + KNOWLEDGE_CONFIRM_FIELDS
    + GENERATED_CONFIRM_FIELDS,
}

# 用户明确表示不提供书面证据时，由脚本落库一条说明，避免再向用户索要「待提供」类占位话术。
DEFAULT_NOT_PROVIDED_EVIDENCE_SOURCE = "用户确认暂无书面证据资料"
# 用户明确表示不补充产品知识主题时，写入占位主题以满足阶段门禁，避免再追问「知识需求」。
DEFAULT_DECLINED_PRODUCT_KNOWLEDGE_TOPIC = "用户确认暂不补充产品知识主题"
DEFAULT_PARTIAL_EVIDENCE_SOURCE = "用户已确认场景所需产品知识主题，书面证据待补充"
DEFAULT_READY_EVIDENCE_SOURCE = "用户已提供可用证据资料"


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


def _user_text_declines_product_knowledge(user_text: str) -> bool:
    s = (user_text or "").strip()
    if not s:
        return False
    if "产品知识暂无" in s:
        return True
    if "没有产品知识" in s or "无需产品知识" in s or "不提供产品知识" in s:
        return True
    if "不要产品知识" in s:
        return True
    if "不提供" in s and ("产品知识" in s or "知识主题" in s):
        return True
    if "不提供" in s and ("资料" in s or "证据" in s) and ("产品" in s or "书面" in s):
        return True
    if "暂不补充" in s and ("知识" in s or "资料" in s):
        return True
    return False


def _should_auto_decline_product_knowledge(
    user_text: str, scene: dict[str, Any], payload: dict[str, Any]
) -> bool:
    if payload.get("declineProductKnowledge") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("declineProductKnowledge") is True:
        return True
    if scene.get("declineProductKnowledge") is True:
        return True
    return _user_text_declines_product_knowledge(user_text)


def _has_knowledge_content(value: Any) -> bool:
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict) and str(item.get("content") or "").strip():
                return True
            if isinstance(item, str) and item.strip():
                return True
    if isinstance(value, dict):
        if str(value.get("content") or "").strip():
            return True
        items = value.get("items")
        if isinstance(items, list):
            return _has_knowledge_content(items)
    if isinstance(value, str):
        return bool(value.strip())
    return False


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        texts = [item for item in value if isinstance(item, str) and item.strip()]
        return len(texts) == 0
    return False


def normalize_scene(
    scene: dict[str, Any], user_text: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    out = dict(scene)
    payload = payload if isinstance(payload, dict) else {}
    if "needsEvidenceConfirmation" not in out and isinstance(
        out.get("needEvidenceConfirmation"), bool
    ):
        out["needsEvidenceConfirmation"] = out.pop("needEvidenceConfirmation")

    background = out.get("sceneBackground") or out.get("background") or ""
    if isinstance(background, str) and background.strip():
        out["sceneBackground"] = background.strip()
        out["background"] = background.strip()

    doctor_concerns = out.get("doctorConcerns")
    if isinstance(doctor_concerns, list):
        out["doctorConcerns"] = [
            item.strip() for item in doctor_concerns if isinstance(item, str) and item.strip()
        ]
    elif isinstance(doctor_concerns, str) and doctor_concerns.strip():
        out["doctorConcerns"] = doctor_concerns.strip()

    product_knowledge_needs = out.get("productKnowledgeNeeds")
    if isinstance(product_knowledge_needs, str) and product_knowledge_needs.strip():
        out["productKnowledgeNeeds"] = [product_knowledge_needs.strip()]
    elif isinstance(product_knowledge_needs, list):
        out["productKnowledgeNeeds"] = [
            item.strip()
            for item in product_knowledge_needs
            if isinstance(item, str) and item.strip()
        ]

    current_evidence_status = str(out.get("productEvidenceStatus") or "").strip().upper()
    if _should_auto_decline_product_knowledge(user_text, out, payload):
        if current_evidence_status not in {"PARTIAL", "READY"}:
            out["productEvidenceStatus"] = "NOT_PROVIDED"
            if is_empty(out.get("productKnowledgeNeeds")):
                out["productKnowledgeNeeds"] = [DEFAULT_DECLINED_PRODUCT_KNOWLEDGE_TOPIC]
            out["needsEvidenceConfirmation"] = True

    evidence_sources = out.get("productEvidenceSource")
    if isinstance(evidence_sources, str) and evidence_sources.strip():
        out["productEvidenceSource"] = [evidence_sources.strip()]
    elif isinstance(evidence_sources, list):
        out["productEvidenceSource"] = [
            item.strip() for item in evidence_sources if isinstance(item, str) and item.strip()
        ]

    evidence_status = str(out.get("productEvidenceStatus") or "").strip().upper()
    has_topics = not is_empty(out.get("productKnowledgeNeeds"))
    has_sources = not is_empty(out.get("productEvidenceSource"))
    has_knowledge_content = _has_knowledge_content(out.get("knowledge"))

    if evidence_status not in {"NOT_PROVIDED", "PARTIAL", "READY"}:
        if has_topics and (has_sources or has_knowledge_content):
            evidence_status = "PARTIAL"
        elif has_topics:
            evidence_status = "PARTIAL"
        else:
            evidence_status = "NOT_PROVIDED"
        out["productEvidenceStatus"] = evidence_status

    if evidence_status == "READY":
        if not isinstance(out.get("needsEvidenceConfirmation"), bool):
            out["needsEvidenceConfirmation"] = False
        filled = out.get("productEvidenceSource")
        if not isinstance(filled, list) or not any(
            isinstance(item, str) and item.strip() for item in filled
        ):
            out["productEvidenceSource"] = [DEFAULT_READY_EVIDENCE_SOURCE]
    elif evidence_status == "PARTIAL":
        if not isinstance(out.get("needsEvidenceConfirmation"), bool):
            out["needsEvidenceConfirmation"] = True
        filled = out.get("productEvidenceSource")
        if not isinstance(filled, list) or not any(
            isinstance(item, str) and item.strip() for item in filled
        ):
            out["productEvidenceSource"] = [DEFAULT_PARTIAL_EVIDENCE_SOURCE]
    elif evidence_status == "NOT_PROVIDED":
        if not isinstance(out.get("needsEvidenceConfirmation"), bool):
            out["needsEvidenceConfirmation"] = True
        filled = out.get("productEvidenceSource")
        if not isinstance(filled, list) or not any(
            isinstance(item, str) and item.strip() for item in filled
        ):
            out["productEvidenceSource"] = [DEFAULT_NOT_PROVIDED_EVIDENCE_SOURCE]

    if user_text.strip() and not str(out.get("sourceUserText") or "").strip():
        out["sourceUserText"] = user_text.strip()

    doc_ctx = out.get("doctorOnlyContext")
    if isinstance(doc_ctx, str) and doc_ctx.strip():
        fixed_doc, _ = sanitize_doctor_core_concerns_to_two_bullets(doc_ctx)
        out["doctorOnlyContext"] = fixed_doc

    return out


def _base_info_acknowledged(scene: dict[str, Any], payload: dict[str, Any]) -> bool:
    if payload.get("baseInfoAcknowledged") is True:
        return True
    if scene.get("baseInfoAcknowledged") is True:
        return True
    meta = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    if meta.get("baseInfoAcknowledged") is True:
        return True
    return False


def _confirmation_status_for_field(
    field: str,
    value: Any,
    *,
    stage: str,
    base_acknowledged: bool,
) -> str:
    if field == "needsEvidenceConfirmation":
        return "待补充" if _missing_bool(value) else "请确认"
    if is_empty(value):
        return "待补充"
    if field in BASE_CONFIRM_FIELDS and stage in {
        STAGE_KNOWLEDGE_CONFIRM,
        STAGE_READY_FOR_SCENE_GENERATION,
        STAGE_READY_FOR_VALIDATE,
    }:
        return "请确认" if base_acknowledged else "待确认"
    return "请确认"


def _has_placeholder_evidence(scene: dict[str, Any]) -> bool:
    sources = scene.get("productEvidenceSource")
    if not isinstance(sources, list):
        return False
    return any(str(item).strip().startswith("待补充") for item in sources)


def _missing_fields(scene: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if is_empty(scene.get(field))]


def _missing_bool(value: Any) -> bool:
    return not isinstance(value, bool)


def _normalize_incoming_patch(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    return {key: item for key, item in value.items() if key in FIELD_LABELS}


def _collect_scene_patch(payload: dict[str, Any]) -> dict[str, Any]:
    patch: dict[str, Any] = {}
    for key in (
        "parsedFields",
        "userUpdates",
        "userConfirmedFields",
        "userProvidedFields",
    ):
        patch.update(_normalize_incoming_patch(payload.get(key)))
    return patch


def _clean_user_short_text(user_text: str) -> str:
    text = (user_text or "").strip()
    if not text:
        return ""
    text = text.strip("。！？；;，,：:、 \t\r\n")
    if len(text) >= 2 and ((text[0] == text[-1]) and text[0] in {'"', "'"}):
        text = text[1:-1].strip()
    return text


def _is_non_value_reply(text: str) -> bool:
    lowered = text.lower()
    blocked_phrases = {
        "确认",
        "是",
        "不是",
        "对",
        "不对",
        "好的",
        "ok",
        "yes",
        "no",
        "暂无",
        "没有",
        "不清楚",
    }
    return lowered in blocked_phrases


def infer_user_reply_patch(user_text: str, missing_base_fields: list[str]) -> dict[str, Any]:
    if len(missing_base_fields) != 1:
        return {}
    field = missing_base_fields[0]
    if field != "drugName":
        return {}
    candidate = _clean_user_short_text(user_text)
    if not candidate or len(candidate) > 40:
        return {}
    if any(sep in candidate for sep in ("\n", "，", ",", "。", "；", ";", "：", ":")):
        return {}
    if _is_non_value_reply(candidate):
        return {}
    return {"drugName": candidate}


def _stringify_value(field: str, value: Any) -> str:
    if value is None:
        return ""
    if field == "productEvidenceStatus":
        return EVIDENCE_STATUS_LABELS.get(str(value).strip(), str(value).strip())
    if field == "needsEvidenceConfirmation":
        if value is True:
            return "需要补充"
        if value is False:
            return "无需补充"
        return ""
    if field == "actorProfile" and isinstance(value, dict):
        parts = [
            str(value.get("title") or "").strip(),
            str(value.get("name") or "").strip(),
            str(value.get("description") or "").strip(),
        ]
        return "；".join(part for part in parts if part)
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "、".join(parts)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _humanize_generation_notes(text: str) -> str:
    note = (text or "").strip()
    if not note:
        return ""
    # 优先替换 markdown 代码态字段名，避免用户看到英文字段键。
    for field, label in sorted(FIELD_LABELS.items(), key=lambda item: len(item[0]), reverse=True):
        note = note.replace(f"`{field}`", label)
    keys = [re.escape(field) for field in FIELD_LABELS]
    if not keys:
        return note
    pattern = re.compile(r"\b(" + "|".join(keys) + r")\b")
    return pattern.sub(lambda m: FIELD_LABELS.get(m.group(1), m.group(1)), note)


def build_confirmation_items(
    scene: dict[str, Any],
    fields: list[str],
    *,
    stage: str,
    base_acknowledged: bool,
) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for field in fields:
        value = scene.get(field)
        items.append(
            {
                "label": FIELD_LABELS.get(field, field),
                "status": _confirmation_status_for_field(
                    field, value, stage=stage, base_acknowledged=base_acknowledged
                ),
                "value": _stringify_value(field, value),
            }
        )
    return items


def _section_status(missing_fields: list[str], items: list[dict[str, str]]) -> str:
    if not missing_fields:
        return "已具备"
    if any(item["value"] for item in items):
        return "待补充"
    return "待开始"


def determine_stage(
    scene: dict[str, Any],
    *,
    base_acknowledged: bool,
) -> tuple[str, list[str], list[str], list[str], list[str], bool]:
    missing_base_fields = _missing_fields(scene, BASE_CONFIRM_FIELDS)
    missing_knowledge_fields = _missing_fields(
        scene, KNOWLEDGE_CONFIRM_FIELDS + KNOWLEDGE_GATE_FIELDS
    )
    missing_generated_fields = _missing_fields(scene, GENERATED_CONFIRM_FIELDS + GENERATED_GATE_FIELDS)
    missing_internal_fields = _missing_fields(scene, INTERNAL_GENERATED_FIELDS)
    missing_needs_evidence_confirmation = _missing_bool(scene.get("needsEvidenceConfirmation"))

    if missing_base_fields:
        return (
            STAGE_BASE_INFO_CONFIRM,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    if (
        missing_knowledge_fields
        or missing_needs_evidence_confirmation
        or not base_acknowledged
    ):
        return (
            STAGE_KNOWLEDGE_CONFIRM,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    if missing_generated_fields or missing_internal_fields:
        return (
            STAGE_READY_FOR_SCENE_GENERATION,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        )
    return (
        STAGE_READY_FOR_VALIDATE,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        missing_needs_evidence_confirmation,
    )


def build_phase_sections(
    scene: dict[str, Any],
    missing_base_fields: list[str],
    missing_knowledge_fields: list[str],
    missing_generated_fields: list[str],
    missing_internal_fields: list[str],
    *,
    stage: str,
    base_acknowledged: bool,
    missing_needs_evidence_confirmation: bool,
) -> list[dict[str, Any]]:
    base_items = build_confirmation_items(
        scene, BASE_CONFIRM_FIELDS, stage=stage, base_acknowledged=base_acknowledged
    )
    knowledge_items = build_confirmation_items(
        scene, KNOWLEDGE_CONFIRM_FIELDS, stage=stage, base_acknowledged=base_acknowledged
    )
    generated_items = build_confirmation_items(
        scene, GENERATED_CONFIRM_FIELDS, stage=stage, base_acknowledged=base_acknowledged
    )
    base_section_status = _section_status(missing_base_fields, base_items)
    if not missing_base_fields and not base_acknowledged:
        base_section_status = "待确认"

    knowledge_section_status = "已具备"
    if not base_acknowledged:
        knowledge_section_status = "待确认"
    elif missing_needs_evidence_confirmation or missing_knowledge_fields:
        knowledge_section_status = _section_status(missing_knowledge_fields, knowledge_items)

    return [
        {
            "stage": STAGE_BASE_INFO_CONFIRM,
            "title": "基础信息确认",
            "status": base_section_status,
            "items": base_items,
        },
        {
            "stage": STAGE_KNOWLEDGE_CONFIRM,
            "title": "产品知识与资料确认",
            "status": knowledge_section_status,
            "items": knowledge_items,
        },
        {
            "stage": STAGE_READY_FOR_SCENE_GENERATION,
            "title": "场景内容生成",
            "status": _section_status(missing_generated_fields + missing_internal_fields, generated_items),
            "items": generated_items,
        },
    ]


def build_pending_confirm_notes(
    scene: dict[str, Any], stage: str, *, base_acknowledged: bool
) -> list[str]:
    notes: list[str] = []
    generation_notes = str(scene.get("generationNotes") or "").strip()
    if generation_notes:
        notes.append(_humanize_generation_notes(generation_notes))
    if _has_placeholder_evidence(scene):
        notes.append("当前产品证据资料仍含待补充占位，请确认是否已有可提供的说明书、集采政策或其他证据材料。")
    if stage == STAGE_BASE_INFO_CONFIRM:
        notes.append("当前先确认业务领域、科室、产品、地点、医生顾虑、代表目标；标题、场景背景和上下文稍后统一生成。")
    elif stage == STAGE_KNOWLEDGE_CONFIRM:
        if base_acknowledged:
            notes.append("基础信息已由用户确认，接下来先确认产品知识需求和资料情况，再统一生成标题、场景背景与上下文。")
        else:
            notes.append("基础信息字段已识别，但仍需用户核对是否准确；核对无误后请由 Agent 在下一轮解析请求中携带 baseInfoAcknowledged=true，再进入场景内容生成。")
        notes.append("产品知识正文补充是可选的：可以只确认知识主题关键词，也可以额外补充知识正文/资料来源供创建前解析。")
    elif stage == STAGE_READY_FOR_SCENE_GENERATION:
        notes.append("基础信息与产品知识/资料已具备；此时应在内部执行场景内容生成，再进入校验。")
    return notes


def build_base_questions(missing_fields: list[str]) -> list[str]:
    question_map = {
        "businessDomainName": "这是哪个业务领域？请从临床推广、院外零售、学术合作、通用能力中选择一个。",
        "departmentName": "这次主要对应哪个科室？",
        "drugName": "这次对应的具体产品或品种是什么？",
        "location": "这个场景发生在什么地点？",
        "doctorConcerns": "医生当前最核心的顾虑是什么？",
        "repGoal": "代表本次沟通最想达成的目标是什么？",
    }
    return [question_map[field] for field in missing_fields if field in question_map]


def build_knowledge_questions(
    scene: dict[str, Any],
    missing_fields: list[str],
    missing_needs_evidence_confirmation: bool,
    base_acknowledged: bool,
) -> list[str]:
    background_hint = "已确认的业务背景" if base_acknowledged else "当前识别出的业务背景（请同时核对上方基础信息是否准确）"
    need_one_shot = bool(missing_fields) or missing_needs_evidence_confirmation
    questions: list[str] = []
    if need_one_shot:
        questions.append(
            f"基于{background_hint}，请确认“场景所需产品知识主题”（可给关键词；若暂无可写“暂无”）。"
        )
    questions.append("产品证据状态与证据来源由系统根据你提供的知识主题/资料自动判断，无需你单独填写。")
    questions.append("如有现成产品知识正文或政策解读内容，也可以一并补充；若暂时没有，可只确认知识主题关键词后继续。")
    if not base_acknowledged:
        questions.append("请先明确确认上方基础信息是否全部准确；确认后由 Agent 在下一轮 tbs-scene-parse 请求中设置 baseInfoAcknowledged=true。")
    return questions


def build_content_generation_questions(
    missing_generated_fields: list[str],
    missing_internal_fields: list[str],
    *,
    has_user_updates: bool,
    updated_labels: list[str],
) -> list[str]:
    questions: list[str] = []
    if has_user_updates and updated_labels:
        labels = "、".join(updated_labels)
        questions.append(f"本轮用户已更新：{labels}。请先向用户回显更新后的确认清单并请其确认。")
    if "title" in missing_generated_fields or "sceneBackground" in missing_generated_fields:
        questions.append("请在内部生成场景标题与场景背景。")
    if "actorProfile" in missing_generated_fields:
        questions.append("请在内部补齐对练对象角色画像（至少包含 name）。")
    if "repBriefing" in missing_generated_fields:
        questions.append("请在内部生成场景背景叙述（repBriefing）。")
    if missing_internal_fields:
        questions.append("请在内部生成对练对象侧上下文与教练侧上下文，用户无需逐段确认正文。")
    return questions


def build_clarify_questions(
    stage: str,
    scene: dict[str, Any],
    missing_base_fields: list[str],
    missing_knowledge_fields: list[str],
    missing_generated_fields: list[str],
    missing_internal_fields: list[str],
    missing_needs_evidence_confirmation: bool,
    base_acknowledged: bool,
    has_user_updates: bool,
    updated_labels: list[str],
) -> list[str]:
    if stage == STAGE_BASE_INFO_CONFIRM:
        return build_base_questions(missing_base_fields)
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        return build_knowledge_questions(
            scene,
            missing_knowledge_fields,
            missing_needs_evidence_confirmation,
            base_acknowledged,
        )
    if stage == STAGE_READY_FOR_SCENE_GENERATION:
        return build_content_generation_questions(
            missing_generated_fields,
            missing_internal_fields,
            has_user_updates=has_user_updates,
            updated_labels=updated_labels,
        )
    return []


def build_next_action(
    stage: str,
    *,
    base_acknowledged: bool,
    has_user_updates: bool,
    updated_labels: list[str],
) -> str:
    if stage == STAGE_BASE_INFO_CONFIRM:
        return "请先补充并确认基础信息；确认后再分析产品知识需求与资料情况。"
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        if not base_acknowledged:
            return "请先引导用户核对基础信息是否准确；用户明确确认后，在下一轮解析请求 JSON 顶层设置 baseInfoAcknowledged=true，再继续确认产品知识/资料并进入内部生成。"
        return "请引导用户一次性确认产品知识主题、证据状态与证据来源；产品知识正文补充可选。确认后再在内部生成标题、场景背景与上下文。"
    if stage == STAGE_READY_FOR_SCENE_GENERATION:
        if has_user_updates and updated_labels:
            labels = "、".join(updated_labels)
            return f"请先向用户回显更新后的确认清单（重点：{labels}），确认无误后再内部生成场景内容；生成完成后重新运行本脚本并进入场景校验。"
        return "请在内部执行场景内容生成；生成完成后重新运行本脚本，再进入场景校验。"
    if stage == STAGE_READY_FOR_VALIDATE and has_user_updates and updated_labels:
        labels = "、".join(updated_labels)
        return f"用户本轮已更新（{labels}），请先回显最新确认清单并确认无误，再执行场景校验。"
    return "请确认上述关键信息；如无误，可以继续执行场景校验。"


def build_system_action_hint(
    stage: str,
    *,
    base_acknowledged: bool,
    has_user_updates: bool,
    updated_labels: list[str],
) -> str:
    if stage == STAGE_BASE_INFO_CONFIRM:
        return "先与用户确认基础信息；此阶段不要提前执行 scenario-json-parse 全量生成。"
    if stage == STAGE_KNOWLEDGE_CONFIRM:
        if not base_acknowledged:
            return "先引导用户核对基础信息；未携带 baseInfoAcknowledged=true 前，不要进入 scenario-json-parse 全量生成。"
        return "基于用户已确认的基础信息分析产品知识需求，并以关键词形式给用户确认；若用户补充知识正文，则保存在 scene.knowledge，后续创建前再解析/创建 knowledgeIds。"
    if stage == STAGE_READY_FOR_SCENE_GENERATION:
        if has_user_updates and updated_labels:
            labels = "、".join(updated_labels)
            return f"检测到用户本轮更新字段（{labels}）；先向用户回显更新后的确认清单，再内部读取 references/scenario-json-parse.md + prompts/*.json 生成内容。"
        return "现在再内部读取 references/scenario-json-parse.md + prompts/*.json，生成 title、sceneBackground、repBriefing、actorProfile、doctorOnlyContext、coachOnlyContext。"
    if stage == STAGE_READY_FOR_VALIDATE and has_user_updates and updated_labels:
        labels = "、".join(updated_labels)
        return f"检测到用户本轮更新字段（{labels}）；先回显更新后的确认清单，再执行 tbs-scene-validate.py。"
    return "执行 tbs-scene-validate.py，确认是否达到最终创建前门禁。"


def maybe_write_draft(draft_path: str | None, scene: dict[str, Any], parse_result: dict[str, Any]) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    payload = {
        "scene": scene,
        "parseResult": parse_result,
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
    args = parser.parse_args()

    payload = read_payload(args.input, args.params_file)
    user_text = str(payload.get("userText") or "").strip()
    base_scene = payload.get("scene") if isinstance(payload.get("scene"), dict) else {}
    scene_patch = _collect_scene_patch(payload)
    draft_path = payload.get("draftPath")
    if not user_text and not base_scene and not scene_patch:
        emit_error("缺少 userText 或结构化 scene", exit_code=2)

    scene = dict(base_scene)
    scene.update(scene_patch)
    scene = normalize_scene(scene, user_text, payload)
    base_acknowledged = _base_info_acknowledged(scene, payload)
    if base_acknowledged:
        scene["baseInfoAcknowledged"] = True

    (
        stage,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        missing_needs_evidence_confirmation,
    ) = determine_stage(scene, base_acknowledged=base_acknowledged)

    inferred_reply_patch = infer_user_reply_patch(user_text, missing_base_fields)
    if inferred_reply_patch:
        scene.update(inferred_reply_patch)
        scene = normalize_scene(scene, user_text, payload)
        (
            stage,
            missing_base_fields,
            missing_knowledge_fields,
            missing_generated_fields,
            missing_internal_fields,
            missing_needs_evidence_confirmation,
        ) = determine_stage(scene, base_acknowledged=base_acknowledged)

    applied_user_patch = {**scene_patch, **inferred_reply_patch}
    confirm_fields = BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS + GENERATED_CONFIRM_FIELDS
    updated_confirm_fields = [field for field in confirm_fields if field in applied_user_patch]
    updated_labels = [FIELD_LABELS.get(field, field) for field in updated_confirm_fields]
    has_user_updates = len(updated_labels) > 0

    phase_sections = build_phase_sections(
        scene,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        stage=stage,
        base_acknowledged=base_acknowledged,
        missing_needs_evidence_confirmation=missing_needs_evidence_confirmation,
    )
    stage_items_map = {
        stage_name: build_confirmation_items(
            scene,
            fields,
            stage=stage,
            base_acknowledged=base_acknowledged,
        )
        for stage_name, fields in STAGE_CONFIRM_FIELDS.items()
    }
    confirm_view = {
        field: scene.get(field)
        for field in (BASE_CONFIRM_FIELDS + KNOWLEDGE_CONFIRM_FIELDS + GENERATED_CONFIRM_FIELDS)
    }
    all_missing_fields = _missing_fields(scene, FINAL_REQUIRED_FIELDS)
    if missing_needs_evidence_confirmation and "needsEvidenceConfirmation" not in all_missing_fields:
        all_missing_fields.append("needsEvidenceConfirmation")
    missing_knowledge_confirm_fields = _missing_fields(scene, KNOWLEDGE_CONFIRM_FIELDS)
    user_facing_missing_fields = (
        missing_base_fields + missing_knowledge_confirm_fields + missing_generated_fields
    )
    pending_confirm_notes = build_pending_confirm_notes(scene, stage, base_acknowledged=base_acknowledged)
    clarify_questions = build_clarify_questions(
        stage,
        scene,
        missing_base_fields,
        missing_knowledge_fields,
        missing_generated_fields,
        missing_internal_fields,
        missing_needs_evidence_confirmation,
        base_acknowledged,
        has_user_updates,
        updated_labels,
    )
    result = {
        "step": STEP,
        "stage": stage,
        "scene": scene,
        "confirmedFields": confirm_view,
        "missingFields": user_facing_missing_fields,
        "baseMissingFields": missing_base_fields,
        "knowledgeMissingFields": missing_knowledge_fields,
        "contentMissingFields": missing_generated_fields,
        "createGateMissingFields": all_missing_fields,
        "internalGeneratedMissingFields": missing_internal_fields,
        "readyForScenarioJsonParse": stage == STAGE_READY_FOR_SCENE_GENERATION,
        "readyForValidate": stage == STAGE_READY_FOR_VALIDATE,
        "baseInfoAcknowledged": base_acknowledged,
        "appliedUserPatch": applied_user_patch,
        "updatedFieldLabels": updated_labels,
        "mustEchoUpdatedConfirmation": has_user_updates,
        "clarifyQuestions": clarify_questions,
        "userOutputTemplate": {
            "stage": stage,
            "stageLabel": {
                STAGE_BASE_INFO_CONFIRM: "先确认基础信息",
                STAGE_KNOWLEDGE_CONFIRM: "再确认产品知识与资料",
                STAGE_READY_FOR_SCENE_GENERATION: "已可内部生成场景内容",
                STAGE_READY_FOR_VALIDATE: "已可执行场景校验",
            }[stage],
            "confirmationItems": stage_items_map[stage],
            "updatedConfirmationItems": stage_items_map[
                STAGE_KNOWLEDGE_CONFIRM if stage in {STAGE_READY_FOR_SCENE_GENERATION, STAGE_READY_FOR_VALIDATE} else stage
            ],
            "mustEchoUpdatedConfirmation": has_user_updates,
            "updatedFieldLabels": updated_labels,
            "baseInfoAcknowledged": base_acknowledged,
            "phaseSections": phase_sections,
            "missingLabels": [FIELD_LABELS.get(field, field) for field in user_facing_missing_fields],
            "createGateMissingLabels": [
                FIELD_LABELS.get(field, field) for field in all_missing_fields
            ],
            "internalGeneratedMissingLabels": [
                FIELD_LABELS.get(field, field) for field in missing_internal_fields
            ],
            "pendingConfirmNotes": pending_confirm_notes,
            "clarifyQuestions": clarify_questions,
            "nextAction": build_next_action(
                stage,
                base_acknowledged=base_acknowledged,
                has_user_updates=has_user_updates,
                updated_labels=updated_labels,
            ),
            "systemActionHint": build_system_action_hint(
                stage,
                base_acknowledged=base_acknowledged,
                has_user_updates=has_user_updates,
                updated_labels=updated_labels,
            ),
        },
    }

    if isinstance(draft_path, str) and draft_path.strip():
        maybe_write_draft(draft_path.strip(), scene, result)
        result["draftPath"] = draft_path.strip()

    emit_success(result)


if __name__ == "__main__":
    main()
