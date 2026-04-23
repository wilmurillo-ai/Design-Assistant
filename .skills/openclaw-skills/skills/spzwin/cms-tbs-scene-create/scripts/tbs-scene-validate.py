"""
Validate whether the current scene draft is ready for user confirmation.
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


STEP = "tbs-scene-validate"
FIELD_LABELS = {
    "title": "场景标题",
    "businessDomainName": "业务领域",
    "departmentName": "科室",
    "drugName": "产品",
    "location": "地点",
    "doctorConcerns": "医生顾虑",
    "repGoal": "代表目标",
    "sceneBackground": "场景背景",
    "productKnowledgeNeeds": "产品知识需求",
    "repBriefing": "场景背景叙述",
    "doctorOnlyContext": "对练对象侧上下文",
    "coachOnlyContext": "教练侧上下文",
    "actorProfile": "对练对象档案",
    "productEvidenceStatus": "产品证据完备状态",
    "productEvidenceSource": "产品证据来源",
    "needsEvidenceConfirmation": "证据是否需用户确认",
}
CONFIRM_DISPLAY_FIELDS = [
    "title",
    "sceneBackground",
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
    "productKnowledgeNeeds",
    "productEvidenceStatus",
    "productEvidenceSource",
    "actorProfile",
]
ALLOWED_BUSINESS_DOMAINS = {"临床推广", "院外零售", "学术合作", "通用能力"}
ALLOWED_EVIDENCE_STATUS = {"NOT_PROVIDED", "PARTIAL", "READY"}
EVIDENCE_STATUS_LABELS = {"NOT_PROVIDED": "未提供", "PARTIAL": "部分提供", "READY": "已齐备"}
WARNING_ISSUE_CODES = {
    "scene.repBriefing_too_long",
    "scene.repBriefing_placeholder",
    "scene.repBriefing_label_style",
    "scene.repBriefing_pronoun",
    "scene.repBriefing_anchor_missing",
}
REQUIRED_FIELDS = [
    "title",
    "businessDomainName",
    "departmentName",
    "drugName",
    "location",
    "doctorConcerns",
    "repGoal",
    "sceneBackground",
    "productKnowledgeNeeds",
    "repBriefing",
    "doctorOnlyContext",
    "coachOnlyContext",
    "actorProfile",
    "productEvidenceStatus",
    "productEvidenceSource",
    "needsEvidenceConfirmation",
]
DOCTOR_REQUIRED_HEADERS = [
    "## 已知背景",
    "## 核心顾虑",
    "## 今日状态",
    "## 终止条件",
    "## 输出要求",
    "## 对话结束规则（强制）",
]
COACH_REQUIRED_HEADERS = [
    "## 期望代表行为",
    "## 评分重点",
    "## 终止条件",
    "## 最佳实践",
    "## 输出要求",
]
DOCTOR_ENDING_RULES_TEMPLATE = [
    "- 只有对练对象角色可结束：仅在本轮末尾追加 [对话结束]，且必须放在全文最后。",
    "- 允许结束：已触发终止条件，或系统明确要求本轮结束（最后一轮/轮次已满）。",
    "- 互斥（执行检查）：若本轮出现问号或疑问词，则必须删除 [对话结束]。",
    "- 互斥（执行检查）：若本轮要输出 [对话结束]，则全文不得出现任何问号或疑问词，且不得出现提问意图。",
    "- 结束语边界：结束语必须是纯陈述句，不得提问，也不得安排任何后续动作或要求。",
]
DOCTOR_OUTPUT_REQUIREMENTS_TEMPLATE = [
    "- 输出长度控制：每次回复控制在30-50字左右，保持真实医生沟通的自然简洁；每轮最多聚焦1个核心点。",
    "- 单问原则：每轮最多提出1个核心问题（问号≤1）。如果想到第二个问题，必须留到下一轮再问。",
    "- 语言要求：以中文自然对话为主；允许必要的医学缩写/单位/符号，但不得滥用英文；严禁出现与医学沟通无关的英文单词。",
    "- 纯文本要求（强制）：只输出纯文本对话，不要使用任何加粗/斜体/标题/代码符号等格式化写法。",
    "- 提问后必须等待代表回答：提问后必须收住，不得在同一轮连续追问，更不得在提问后追加结束标记。",
    "- 避免臆造数据（强制）：不得凭空编造背景之外的具体数值/比例/研究结论；不确定就说明需回去核对资料。",
]
_BRIEFING_LABEL_PATTERN = re.compile(r"(场景背景|人物关系|训练目的|开场建议|AI角色对象的顾虑)\s*[：:]")
_SINGLE_PRONOUN_PATTERN = re.compile(
    r"(^|[，。；：、“”（）\s\d])"
    r"([你我他她它咱])"
    r"(?=$|[，。；：、“”（）\s\d]|[的了吗呢吧啊呀])"
)


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


def _stringify_value(value: Any, field: str = "") -> str:
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
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        parts = [str(item).strip() for item in value if str(item).strip()]
        return "、".join(parts)
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def _issue_code_to_hint(code: str) -> str:
    if code.startswith("scene.") and code.endswith("_missing"):
        field = code[len("scene.") : -len("_missing")]
        label = FIELD_LABELS.get(field, "该字段")
        return f"「{label}」未填写或为空"
    static = {
        "scene.businessDomainName_invalid": "「业务领域」不在允许范围内，请从：临床推广、院外零售、学术合作、通用能力 中选择",
        "scene.repBriefing_invalid": "「场景背景叙述」未通过检查（长度、格式、人称或需包含科室、产品、地点等关键信息）",
        "scene.repBriefing_too_long": "「场景背景叙述」长度超过 180 字，建议精简",
        "scene.repBriefing_placeholder": "「场景背景叙述」含占位符或非常规符号（如【】/待补充），建议改写为自然叙述",
        "scene.repBriefing_label_style": "「场景背景叙述」含标签化前缀（如“场景背景：”），建议改成自然叙述",
        "scene.repBriefing_pronoun": "「场景背景叙述」包含第一/第二人称代词（如你/我），建议改为角色称谓叙述",
        "scene.repBriefing_anchor_missing": "「场景背景叙述」未完整覆盖科室/产品/地点锚点信息",
        "scene.doctorOnlyContext_invalid": "「对练对象侧上下文」的 Markdown 结构或固定模板句未通过检查",
        "scene.coachOnlyContext_invalid": "「教练侧上下文」的 Markdown 结构未通过检查",
        "scene.actorProfile_invalid": "「对练对象档案」不完整（需包含角色姓名等）",
        "scene.productEvidenceStatus_invalid": "「产品证据完备状态」无效",
        "scene.productEvidenceSource_invalid": "「产品证据来源」未填写或格式无效",
        "scene.needsEvidenceConfirmation_invalid": "「证据是否需用户确认」标记格式无效",
        "scene.needsEvidenceConfirmation_inconsistent": "证据完备状态与「是否需用户确认证据」不一致，请核对后修改",
    }
    return static.get(code, "存在未通过的校验项，请根据草稿核对后重新校验")


def build_confirmation_items(scene: dict[str, Any], fields: list[str]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for field in fields:
        items.append(
            {
                "label": FIELD_LABELS.get(field, field),
                "value": _stringify_value(scene.get(field), field),
            }
        )
    return items


def issues_to_hints(issues: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for code in issues:
        hint = _issue_code_to_hint(code)
        if hint not in seen:
            seen.add(hint)
            out.append(hint)
    return out


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, list):
        return not any(isinstance(item, str) and item.strip() for item in value)
    return False


def normalize_scene(scene: dict[str, Any]) -> dict[str, Any]:
    out = dict(scene)
    if "needsEvidenceConfirmation" not in out and isinstance(
        out.get("needEvidenceConfirmation"), bool
    ):
        out["needsEvidenceConfirmation"] = out.pop("needEvidenceConfirmation")
    background = out.get("sceneBackground") or out.get("background")
    if isinstance(background, str) and background.strip():
        out["sceneBackground"] = background.strip()
        out["background"] = background.strip()
        # Use sceneBackground as the single source of truth.
        out["repBriefing"] = background.strip()
    pk_needs = out.get("productKnowledgeNeeds")
    if isinstance(pk_needs, str) and pk_needs.strip():
        out["productKnowledgeNeeds"] = [pk_needs.strip()]
    elif isinstance(pk_needs, list):
        out["productKnowledgeNeeds"] = [
            item.strip() for item in pk_needs if isinstance(item, str) and item.strip()
        ]
    evidence_sources = out.get("productEvidenceSource")
    if isinstance(evidence_sources, str) and evidence_sources.strip():
        out["productEvidenceSource"] = [evidence_sources.strip()]
    elif isinstance(evidence_sources, list):
        out["productEvidenceSource"] = [
            item.strip() for item in evidence_sources if isinstance(item, str) and item.strip()
        ]

    evidence_status = str(out.get("productEvidenceStatus") or "").strip().upper()
    if evidence_status == "NOT_PROVIDED":
        if not isinstance(out.get("needsEvidenceConfirmation"), bool):
            out["needsEvidenceConfirmation"] = True
        filled = out.get("productEvidenceSource")
        if not isinstance(filled, list) or not any(
            isinstance(item, str) and item.strip() for item in filled
        ):
            out["productEvidenceSource"] = ["用户确认暂无书面证据资料"]

    doc_ctx = out.get("doctorOnlyContext")
    if isinstance(doc_ctx, str) and doc_ctx.strip():
        fixed_doc, changed = sanitize_doctor_core_concerns_to_two_bullets(doc_ctx)
        if changed:
            out["doctorOnlyContext"] = fixed_doc
            out["__validateAutoNormalizedDoctorContext"] = True

    rep_briefing = out.get("repBriefing")
    if isinstance(rep_briefing, str) and rep_briefing.strip():
        fixed_briefing, briefing_changes = sanitize_rep_briefing(rep_briefing, out)
        if briefing_changes:
            out["repBriefing"] = fixed_briefing
            out["sceneBackground"] = fixed_briefing
            out["background"] = fixed_briefing
            out["__validateAutoNormalizedRepBriefing"] = briefing_changes

    return out


def _contains_personal_name_or_pronoun(text: str) -> bool:
    if any(token in text for token in ("你们", "我们", "他们", "她们", "咱们")):
        return True
    return bool(_SINGLE_PRONOUN_PATTERN.search(text))


def _primary_drug_anchor(drug_name: str) -> str:
    name = drug_name.strip()
    if not name:
        return ""
    head = re.split(r"[（(]", name, maxsplit=1)[0].strip()
    head = re.split(r"[、，,/|]", head, maxsplit=1)[0].strip()
    return head


def _anchor_in_briefing(text: str, field: str, value: str) -> bool:
    needle = value.strip()
    if not needle:
        return True
    if needle in text:
        return True
    if field == "drugName":
        primary = _primary_drug_anchor(needle)
        if len(primary) >= 2 and primary in text:
            return True
    return False


def _extract_md_section_lines(text: str, header: str) -> list[str]:
    if not isinstance(text, str) or not text.strip():
        return []
    match = re.search(rf"(?ms)^({re.escape(header)})\s*$\n(.*?)(?=^##\s+|\Z)", text)
    if not match:
        return []
    body = match.group(2)
    return [line.strip() for line in body.splitlines() if line.strip()]


def _rep_briefing_valid(scene: dict[str, Any]) -> bool:
    return len(_rep_briefing_issue_codes(scene)) == 0


def _rep_briefing_issue_codes(scene: dict[str, Any]) -> list[str]:
    text = str(scene.get("repBriefing") or "").strip()
    if not text:
        return []
    issues: list[str] = []
    if len(text) > 180:
        issues.append("scene.repBriefing_too_long")
    if "【" in text or "】" in text or "待补充" in text:
        issues.append("scene.repBriefing_placeholder")
    if _BRIEFING_LABEL_PATTERN.search(text):
        issues.append("scene.repBriefing_label_style")
    if _contains_personal_name_or_pronoun(text):
        issues.append("scene.repBriefing_pronoun")
    missing_anchor = False
    for anchor in ("departmentName", "drugName", "location"):
        value = str(scene.get(anchor) or "").strip()
        if value and not _anchor_in_briefing(text, anchor, value):
            missing_anchor = True
    if missing_anchor:
        issues.append("scene.repBriefing_anchor_missing")
    return issues


def sanitize_rep_briefing(text: str, scene: dict[str, Any]) -> tuple[str, list[str]]:
    fixed = str(text or "").strip()
    changes: list[str] = []
    if not fixed:
        return fixed, changes

    if "【" in fixed or "】" in fixed:
        fixed = fixed.replace("【", "").replace("】", "")
        changes.append("repBriefing：移除了【】样式符号")
    if "待补充" in fixed:
        fixed = fixed.replace("待补充", "")
        changes.append("repBriefing：移除了“待补充”占位词")
    if _BRIEFING_LABEL_PATTERN.search(fixed):
        fixed = _BRIEFING_LABEL_PATTERN.sub("", fixed)
        changes.append("repBriefing：移除了标签化前缀写法")

    fixed = re.sub(r"\s+", " ", fixed).strip("，,。；; ")
    missing_tokens: list[str] = []
    for anchor in ("departmentName", "drugName", "location"):
        value = str(scene.get(anchor) or "").strip()
        if value and not _anchor_in_briefing(fixed, anchor, value):
            missing_tokens.append(_primary_drug_anchor(value) if anchor == "drugName" else value)

    if missing_tokens:
        suffix = "，涉及" + "、".join(token for token in missing_tokens if token) + "。"
        if len(fixed) + len(suffix) <= 180:
            fixed = fixed + suffix
        else:
            keep_len = max(0, 180 - len(suffix))
            fixed = fixed[:keep_len].rstrip("，,。；; ") + suffix
        changes.append("repBriefing：自动补齐了科室/产品/地点锚点信息")

    if len(fixed) > 180:
        fixed = fixed[:180].rstrip("，,。；; ")
        changes.append("repBriefing：长度已裁剪至 180 字以内")

    return fixed, changes


def _doctor_only_context_valid(scene: dict[str, Any]) -> bool:
    text = str(scene.get("doctorOnlyContext") or "").strip()
    if not text:
        return False
    headers = re.findall(r"(?m)^##\s+[^\n]+", text)
    filtered = [header for header in headers if header in DOCTOR_REQUIRED_HEADERS]
    if filtered != DOCTOR_REQUIRED_HEADERS:
        return False
    concern_lines = _extract_md_section_lines(text, "## 核心顾虑")
    concern_bullets = [line for line in concern_lines if line.startswith("-")]
    if not (1 <= len(concern_bullets) <= 2):
        return False
    output_lines = _extract_md_section_lines(text, "## 输出要求")
    ending_lines = _extract_md_section_lines(text, "## 对话结束规则（强制）")
    if output_lines != DOCTOR_OUTPUT_REQUIREMENTS_TEMPLATE:
        return False
    if ending_lines != DOCTOR_ENDING_RULES_TEMPLATE:
        return False
    return True


def _coach_only_context_valid(scene: dict[str, Any]) -> bool:
    text = str(scene.get("coachOnlyContext") or "").strip()
    if not text or "[对话结束]" in text:
        return False
    return all(header in text for header in COACH_REQUIRED_HEADERS)


def _actor_profile_valid(scene: dict[str, Any]) -> bool:
    actor_profile = scene.get("actorProfile")
    if not isinstance(actor_profile, dict):
        return False
    name = actor_profile.get("name")
    return isinstance(name, str) and bool(name.strip())


def build_issues(scene: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    for field in REQUIRED_FIELDS:
        if is_empty(scene.get(field)):
            issues.append(f"scene.{field}_missing")
    if not is_empty(scene.get("businessDomainName")) and scene.get("businessDomainName") not in ALLOWED_BUSINESS_DOMAINS:
        issues.append("scene.businessDomainName_invalid")
    issues.extend(_rep_briefing_issue_codes(scene))
    if not _doctor_only_context_valid(scene):
        issues.append("scene.doctorOnlyContext_invalid")
    if not _coach_only_context_valid(scene):
        issues.append("scene.coachOnlyContext_invalid")
    if not _actor_profile_valid(scene):
        issues.append("scene.actorProfile_invalid")
    evidence_status = scene.get("productEvidenceStatus")
    if evidence_status not in ALLOWED_EVIDENCE_STATUS:
        issues.append("scene.productEvidenceStatus_invalid")
    evidence_sources = scene.get("productEvidenceSource")
    if not isinstance(evidence_sources, list) or not evidence_sources:
        issues.append("scene.productEvidenceSource_invalid")
    needs_confirmation = scene.get("needsEvidenceConfirmation")
    if not isinstance(needs_confirmation, bool):
        issues.append("scene.needsEvidenceConfirmation_invalid")
    elif evidence_status == "READY" and needs_confirmation is not False:
        issues.append("scene.needsEvidenceConfirmation_inconsistent")
    elif evidence_status in {"NOT_PROVIDED", "PARTIAL"} and needs_confirmation is not True:
        issues.append("scene.needsEvidenceConfirmation_inconsistent")
    return issues


def split_issue_buckets(issues: list[str]) -> tuple[list[str], list[str]]:
    blocking: list[str] = []
    warning: list[str] = []
    for code in issues:
        if code in WARNING_ISSUE_CODES:
            warning.append(code)
        else:
            blocking.append(code)
    return blocking, warning


def maybe_write_draft(
    draft_path: str | None,
    scene: dict[str, Any],
    validation_report: dict[str, Any],
) -> None:
    if not draft_path:
        return
    parent = os.path.dirname(draft_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    payload = {
        "scene": scene,
        "validationReport": validation_report,
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
    draft_path = None
    scene: dict[str, Any] = {}
    if isinstance(payload.get("scene"), dict):
        scene = payload["scene"]
        draft_path = payload.get("draftPath")
    elif isinstance(payload, dict):
        scene = payload
    if not scene and (args.params_file or (args.input and args.input != "-")):
        draft_path = args.params_file or args.input
        loaded = read_payload(draft_path, None)
        if isinstance(loaded.get("scene"), dict):
            scene = loaded["scene"]
    scene = normalize_scene(scene)
    auto_normalized_doc = bool(scene.pop("__validateAutoNormalizedDoctorContext", False))
    auto_normalized_briefing = scene.pop("__validateAutoNormalizedRepBriefing", [])
    if not scene:
        emit_error("缺少 scene", exit_code=2)

    all_issues = build_issues(scene)
    blocking_issues, warning_issues = split_issue_buckets(all_issues)
    passed = len(blocking_issues) == 0
    confirmed_fields = {
        "title": scene.get("title"),
        "sceneBackground": scene.get("sceneBackground"),
        "businessDomainName": scene.get("businessDomainName"),
        "departmentName": scene.get("departmentName"),
        "drugName": scene.get("drugName"),
        "location": scene.get("location"),
        "doctorConcerns": scene.get("doctorConcerns"),
        "repGoal": scene.get("repGoal"),
        "productKnowledgeNeeds": scene.get("productKnowledgeNeeds"),
        "productEvidenceStatus": scene.get("productEvidenceStatus"),
        "productEvidenceSource": scene.get("productEvidenceSource"),
        "actorProfile": scene.get("actorProfile"),
    }
    validation_report: dict[str, Any] = {
        "passed": passed,
        "issues": blocking_issues,
        "blockingIssues": blocking_issues,
        "warningIssues": warning_issues,
        "allIssues": all_issues,
    }
    if auto_normalized_doc:
        validation_report["autoNormalized"] = [
            "doctorOnlyContext：## 核心顾虑 已自动合并为至多 2 条 bullet，以满足创建前固定结构校验"
        ]
    if auto_normalized_briefing:
        existing = validation_report.get("autoNormalized")
        if not isinstance(existing, list):
            existing = []
        validation_report["autoNormalized"] = existing + auto_normalized_briefing
    result = {
        "step": STEP,
        "scene": scene,
        "passed": passed,
        "validationReport": validation_report,
        "confirmedFields": confirmed_fields,
        "userOutputTemplate": {
            "stage": "READY_TO_CONFIRM" if passed else "GAP_ASKING",
            "stageLabel": "可发起最终确认" if passed else "待补齐后再校验",
            "confirmationItems": build_confirmation_items(scene, CONFIRM_DISPLAY_FIELDS),
            "issueHints": issues_to_hints(blocking_issues),
            "warningHints": issues_to_hints(warning_issues),
            "nextAction": (
                "可直接回复【确认】或【取消】；也可先按提示优化后再确认"
                if passed and warning_issues
                else "请回复【确认】或【取消】"
                if passed
                else "请根据提示补齐或修正后重新校验"
            ),
        },
    }

    if isinstance(draft_path, str) and draft_path.strip():
        maybe_write_draft(draft_path.strip(), scene, validation_report)
        result["draftPath"] = draft_path.strip()

    emit_success(result)


if __name__ == "__main__":
    main()
