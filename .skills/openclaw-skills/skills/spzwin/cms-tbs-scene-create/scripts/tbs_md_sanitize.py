"""
Shared Markdown tweaks for TBS scene drafts (used by parse + validate).
"""

from __future__ import annotations

import re


def sanitize_doctor_core_concerns_to_two_bullets(doctor_only_context: str) -> tuple[str, bool]:
    """
    `tbs-scene-validate` requires `## 核心顾虑` to have 1-2 lines starting with `-`.
    Models often emit 3+ bullets; merge extras into the second bullet so structure passes
    without losing wording.
    """
    text = doctor_only_context or ""
    if not text.strip():
        return text, False
    match = re.search(r"(?ms)^(## 核心顾虑)\s*$\n(.*?)(?=^##\s+|\Z)", text)
    if not match:
        return text, False
    header_line = match.group(1)
    body = match.group(2)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    bullets = [line for line in lines if line.startswith("-")]
    if len(bullets) <= 2:
        return text, False
    first = bullets[0]
    pieces: list[str] = []
    for b in bullets[1:]:
        piece = b[1:].strip() if b.startswith("-") else b.strip()
        if piece:
            pieces.append(piece)
    second = "- " + "；".join(pieces)
    new_section_body = first + "\n" + second + "\n"
    replacement = header_line + "\n" + new_section_body
    new_text = text[: match.start()] + replacement + text[match.end() :]
    return new_text, True
