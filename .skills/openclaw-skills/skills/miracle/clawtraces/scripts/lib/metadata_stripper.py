# FILE_META
# INPUT:  raw user message text
# OUTPUT: cleaned message text
# POS:    skill lib — called by converter.py
# MISSION: Strip gateway-injected metadata (Sender JSON, operator policy, post-compaction
#          System blocks, Lark message_id / OpenID prefixes, timestamps) from user messages.

"""Strip metadata prefixes from OpenClaw user messages.

OpenClaw / gateway bridges prepend various metadata headers to user messages when
received via IM gateways (Telegram, Feishu/Lark, etc.). This module removes them
so the trajectory training data only contains the actual user content.

Handled prefix types (applied iteratively until the text stabilizes):

1. `(untrusted metadata):` JSON fenced blocks
   (e.g. `Sender (untrusted metadata):`, `Conversation info (untrusted metadata):`)
2. Operator-injected policy preamble:
       Skills store policy (operator configured):
       1. ...
       2. ...
3. Post-compaction context refresh block — consecutive `System: ...` lines:
       System: [2026-04-09 15:34:49 GMT+8] [Post-compaction context refresh]
       System: Session was just compacted...
       System: Current time: ...
4. Lark message_id marker line: `[message_id: om_xxx]`
5. Lark sender OpenID / UnionID prefix: `ou_xxx:` / `on_xxx:`
6. Weekday timestamp prefix: `[Thu 2026-03-12 18:39 GMT+8]`

Example input:
    Skills store policy (operator configured):
    1. For skills discovery...
    6. In the current session, reply directly.

    System: [2026-04-09 15:34:49 GMT+8] [Post-compaction context refresh]
    System: Current time: ...

    [message_id: om_x100b52bd8e58889cb3bfcffe6c154be]
    ou_8c006a2ac836565223ad0a01526ba191: 场景：构建自动化营销工作流系统

Expected output:
    场景：构建自动化营销工作流系统
"""

import re

# Generic pattern: matches ANY "(untrusted metadata):" block with JSON code fence.
# Covers Sender, Conversation info, and any future gateway metadata blocks
# (e.g. WeChat Work "Group info", Discord "Channel info", etc.)
_UNTRUSTED_METADATA_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z ]*\(untrusted metadata\):\s*\n"
    r"```json\s*\n"
    r"[\s\S]*?\n"
    r"```\s*\n*",
    re.MULTILINE,
)

# Operator-configured "Skills store policy" preamble block.
# Matches the title line plus all following non-empty lines, stopping at a blank line.
_SKILLS_POLICY_PATTERN = re.compile(
    r"^Skills store policy \(operator configured\):[ \t]*\n"
    r"(?:(?!\n).+\n)*",
    re.MULTILINE,
)

# Post-compaction context refresh: a run of lines starting with "System:".
# Also includes empty "System: " lines used as spacers.
_SYSTEM_PREFIX_BLOCK_PATTERN = re.compile(
    r"(?:^System:[^\n]*\n)+",
    re.MULTILINE,
)

# Lark message_id marker line: [message_id: om_xxx]
_MESSAGE_ID_PATTERN = re.compile(
    r"^\[message_id:\s*[^\]]+\]\s*\n?",
    re.MULTILINE,
)

# Lark sender OpenID / UnionID prefix appearing immediately before real content.
# Only stripped once and from the very beginning (not a global sub) so normal
# references to `ou_xxx:` inside the body aren't mangled.
_LARK_SENDER_PATTERN = re.compile(
    r"\A(?:ou|on)_[A-Za-z0-9]+:\s*",
)

# Pattern: Timestamp prefix like [Thu 2026-03-12 18:39 GMT+8]
_TIMESTAMP_PATTERN = re.compile(
    r"^\[(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+"
    r"\d{4}-\d{2}-\d{2}\s+"
    r"\d{2}:\d{2}\s+"
    r"GMT[+-]\d+\]\s*",
    re.MULTILINE,
)

# System startup message detection
_STARTUP_PATTERN = re.compile(
    r"^A new session was started",
    re.IGNORECASE,
)


def strip_metadata_prefix(text: str) -> str:
    """Remove all gateway-injected metadata prefixes from a user message.

    Applies every known prefix pattern repeatedly until the text stops changing,
    so stacked / reordered prefixes all get cleaned in a single call.
    """
    prev = None
    while prev != text:
        prev = text
        text = _UNTRUSTED_METADATA_PATTERN.sub("", text)
        text = _SKILLS_POLICY_PATTERN.sub("", text)
        text = _SYSTEM_PREFIX_BLOCK_PATTERN.sub("", text)
        text = _MESSAGE_ID_PATTERN.sub("", text)
        text = _TIMESTAMP_PATTERN.sub("", text)
        text = text.lstrip()
        text = _LARK_SENDER_PATTERN.sub("", text, count=1)
    return text.strip()


def is_system_startup_message(text: str) -> bool:
    """Check if a user message is a system startup instruction (should be excluded)."""
    cleaned = strip_metadata_prefix(text)
    return bool(_STARTUP_PATTERN.match(cleaned))
