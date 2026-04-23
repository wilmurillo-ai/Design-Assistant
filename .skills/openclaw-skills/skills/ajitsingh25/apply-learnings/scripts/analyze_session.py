#!/usr/bin/env python3
"""
Analyze Claude Code session transcripts to extract learnings that would have
been helpful if provided earlier. Covers code patterns, architectural preferences,
tool usage, and missing context.
"""

import json
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
from datetime import datetime


@dataclass
class Learning:
    """Represents a learning extracted from the session."""
    category: str  # 'code_pattern', 'architecture', 'tool_usage', 'missing_context'
    subcategory: str  # More specific classification
    summary: str  # Short description
    detail: str  # Full context/explanation
    source_session: str  # Session summary
    confidence: float = 0.5  # How confident we are this is a real learning


@dataclass
class ToolFailure:
    """Represents a failed tool call and any user correction."""
    session_id: str
    session_summary: str
    timestamp: str
    tool_name: str
    tool_input: dict
    error_type: str
    error_message: str
    user_correction: Optional[str] = None
    successful_retry: Optional[dict] = None
    project: str = ""


# Patterns that indicate user is teaching something
# Format: (regex_pattern, category, subcategory, min_text_length)
TEACHING_PATTERNS = [
    # Code patterns - require more context
    (r"(?:we|you should|always|never|prefer to)\s+use\s+\w+\s+(?:from|instead of|rather than)\s+", "code_pattern", "preference"),
    (r"the (?:convention|pattern|idiom) (?:is|here is)\s+", "code_pattern", "convention"),
    (r"in (?:this|our) (?:codebase|repo|project),?\s+(?:we|you)\s+(?:should|always|never|prefer)", "code_pattern", "convention"),
    (r"(?:glue|uber)\s+(?:framework|convention|pattern):\s+", "code_pattern", "framework"),
    (r"use\s+(?:ctx\.Logger|context\.Logger)\s+(?:instead|rather|not)", "code_pattern", "logger"),
    (r"(?:don't|do not|never)\s+(?:inject|DI|dependency inject)\s+(?:the\s+)?logger", "code_pattern", "logger"),

    # Architecture patterns - require specific keywords
    (r"(?:validate|validation)\s+(?:should be|belongs|goes)\s+(?:at|in)\s+(?:the\s+)?(?:handler|edge|boundary|mapper)", "architecture", "validation"),
    (r"(?:controller|handler|gateway|repository|mapper)\s+should(?:n't| not| never)\s+(?:do|have|contain|perform)\s+", "architecture", "layer_responsibility"),
    (r"(?:business logic|validation|error handling)\s+(?:should|belongs|goes)\s+(?:in|at)\s+(?:the\s+)?(\w+)\s+layer", "architecture", "layer_responsibility"),
    (r"at the (?:edge|boundary|handler layer)", "architecture", "edge_validation"),
    (r"mappers?\s+should(?:n't| not| only)\s+", "architecture", "mapper_responsibility"),

    # Git patterns
    (r"(?:use|always use)\s+git\s+push\s+-u", "tool_usage", "git"),
    (r"git\s+rebase\s+(?:conflict|resolution)", "tool_usage", "git"),

    # Bazel patterns
    (r"(?:run|use)\s+gazelle\s+(?:after|before|when)", "tool_usage", "bazel"),
    (r"(?:never|don't)\s+run\s+bazel\s+(?:build|test)\s+//\.\.\.", "tool_usage", "bazel"),

    # Missing context signals - user providing unrequested info
    (r"(?:actually|fyi|btw|note that),?\s+(?:in this|we|the)\s+(?:codebase|repo|project)", "missing_context", "correction"),
    (r"you (?:need|have|must) to\s+(?:also|first|always)\s+", "missing_context", "requirement"),
]

# Keywords that boost confidence
CONFIDENCE_BOOSTERS = [
    ("always", 0.2),
    ("never", 0.2),
    ("must", 0.15),
    ("should", 0.1),
    ("prefer", 0.1),
    ("convention", 0.15),
    ("pattern", 0.1),
    ("instead of", 0.15),
    ("rather than", 0.15),
]


def extract_user_messages(messages: list) -> list[tuple[str, str]]:
    """Extract user text messages with session context."""
    user_texts = []
    for msg in messages:
        if msg.get('type') != 'user':
            continue
        content = msg.get('message', {}).get('content', '')
        if isinstance(content, str) and len(content) > 20:
            user_texts.append((content, msg.get('sessionId', '')))
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text = item.get('text', '')
                    if len(text) > 20:
                        user_texts.append((text, msg.get('sessionId', '')))
    return user_texts


def extract_learnings_from_text(text: str, session_summary: str) -> list[Learning]:
    """Extract potential learnings from user text."""
    learnings = []
    text_lower = text.lower()

    # Skip if text is too short or looks like a system message / skill prompt
    if len(text) < 50:
        return learnings
    if text.startswith('Base directory for this skill:'):
        return learnings
    if 'SKILL.md' in text or '```bash' in text[:100]:
        return learnings

    for pattern, category, subcategory in TEACHING_PATTERNS:
        if re.search(pattern, text_lower):
            # Calculate confidence based on boosters
            confidence = 0.5
            for keyword, boost in CONFIDENCE_BOOSTERS:
                if keyword in text_lower:
                    confidence += boost
            confidence = min(confidence, 1.0)

            # Extract a summary (first sentence or up to 100 chars)
            # Find the matching portion for better context
            match = re.search(pattern, text_lower)
            if match:
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 80)
                summary = text[start:end].strip()
            else:
                summary = text[:100].split('.')[0].strip()

            if len(summary) < 20:
                summary = text[:100].strip()

            learning = Learning(
                category=category,
                subcategory=subcategory,
                summary=summary,
                detail=text[:500],
                source_session=session_summary,
                confidence=confidence
            )
            learnings.append(learning)
            break  # One learning per text block

    return learnings


def parse_session_for_tool_failures(session_file: Path, session_meta: dict) -> list[ToolFailure]:
    """Parse a session file for tool failures (from original script)."""
    failures = []
    messages = []

    with open(session_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                messages.append(msg)
            except json.JSONDecodeError:
                continue

    uuid_to_msg = {m.get('uuid'): m for m in messages if m.get('uuid')}

    for i, msg in enumerate(messages):
        if msg.get('type') != 'user':
            continue

        content = msg.get('message', {}).get('content', [])
        if isinstance(content, str):
            continue

        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get('type') != 'tool_result':
                continue

            is_error = item.get('is_error', False)
            tool_use_result = msg.get('toolUseResult', '')

            error_type = None
            error_message = ""

            if isinstance(tool_use_result, str) and 'rejected' in tool_use_result.lower():
                error_type = 'rejected'
                error_message = tool_use_result
            elif is_error:
                error_type = 'error'
                error_message = item.get('content', '')[:500]
            elif 'interrupted' in str(content).lower():
                error_type = 'interrupted'
                error_message = 'User interrupted'

            if not error_type:
                continue

            parent_uuid = msg.get('sourceToolAssistantUUID') or msg.get('parentUuid')
            tool_call_msg = uuid_to_msg.get(parent_uuid)

            tool_name = "unknown"
            tool_input = {}

            if tool_call_msg:
                assistant_content = tool_call_msg.get('message', {}).get('content', [])
                if isinstance(assistant_content, list):
                    for ac in assistant_content:
                        if isinstance(ac, dict) and ac.get('type') == 'tool_use':
                            if ac.get('id') == item.get('tool_use_id'):
                                tool_name = ac.get('name', 'unknown')
                                tool_input = ac.get('input', {})
                                break

            user_correction = None
            successful_retry = None

            for j in range(i + 1, min(i + 10, len(messages))):
                next_msg = messages[j]
                if next_msg.get('type') == 'user':
                    next_content = next_msg.get('message', {}).get('content', '')
                    if isinstance(next_content, str) and len(next_content) > 10:
                        user_correction = next_content[:1000]
                        break
                    elif isinstance(next_content, list):
                        for nc in next_content:
                            if isinstance(nc, dict) and nc.get('type') == 'text':
                                text = nc.get('text', '')
                                if len(text) > 10:
                                    user_correction = text[:1000]
                                    break
                        if user_correction:
                            break
                elif next_msg.get('type') == 'assistant':
                    ass_content = next_msg.get('message', {}).get('content', [])
                    if isinstance(ass_content, list):
                        for ac in ass_content:
                            if isinstance(ac, dict) and ac.get('type') == 'tool_use':
                                if ac.get('name') == tool_name:
                                    successful_retry = ac.get('input', {})
                                    break

            failure = ToolFailure(
                session_id=msg.get('sessionId', ''),
                session_summary=session_meta.get('summary', ''),
                timestamp=msg.get('timestamp', ''),
                tool_name=tool_name,
                tool_input=tool_input,
                error_type=error_type,
                error_message=error_message,
                user_correction=user_correction,
                successful_retry=successful_retry,
                project=session_meta.get('projectPath', '')
            )
            failures.append(failure)

    return failures


def parse_session(session_file: Path, session_meta: dict) -> tuple[list[Learning], list[ToolFailure]]:
    """Parse a session for both learnings and tool failures."""
    messages = []

    with open(session_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                messages.append(msg)
            except json.JSONDecodeError:
                continue

    # Extract learnings from user messages
    learnings = []
    user_texts = extract_user_messages(messages)
    session_summary = session_meta.get('summary', 'Unknown session')

    for text, _ in user_texts:
        text_learnings = extract_learnings_from_text(text, session_summary)
        learnings.extend(text_learnings)

    # Extract tool failures
    failures = parse_session_for_tool_failures(session_file, session_meta)

    # Convert tool failures with corrections to learnings
    for failure in failures:
        if failure.user_correction:
            learning = Learning(
                category='tool_usage',
                subcategory=failure.tool_name,
                summary=f"{failure.tool_name}: {failure.error_type}",
                detail=failure.user_correction[:500],
                source_session=session_summary,
                confidence=0.7 if failure.successful_retry else 0.5
            )
            learnings.append(learning)

    return learnings, failures


def deduplicate_learnings(learnings: list[Learning]) -> list[Learning]:
    """Remove duplicate or very similar learnings."""
    seen_summaries = set()
    unique = []

    for learning in sorted(learnings, key=lambda x: -x.confidence):
        # Normalize summary for comparison
        normalized = learning.summary.lower()[:50]
        if normalized not in seen_summaries:
            seen_summaries.add(normalized)
            unique.append(learning)

    return unique


def generate_report(learnings: list[Learning], failures: list[ToolFailure]) -> str:
    """Generate a human-readable report."""
    lines = []
    lines.append("# Session Learnings Analysis")
    lines.append("")
    lines.append(f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # Deduplicate and filter
    learnings = deduplicate_learnings(learnings)
    high_confidence = [l for l in learnings if l.confidence >= 0.6]

    # Group by category
    by_category = defaultdict(list)
    for learning in high_confidence:
        by_category[learning.category].append(learning)

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Total learnings extracted:** {len(learnings)}")
    lines.append(f"- **High confidence learnings:** {len(high_confidence)}")
    lines.append(f"- **Tool failures with corrections:** {len([f for f in failures if f.user_correction])}")
    lines.append("")

    category_names = {
        'code_pattern': 'Code Patterns',
        'architecture': 'Architectural Preferences',
        'tool_usage': 'Tool Usage',
        'missing_context': 'Missing Context'
    }

    for category, display_name in category_names.items():
        cat_learnings = by_category.get(category, [])
        if not cat_learnings:
            continue

        lines.append(f"## {display_name}")
        lines.append("")

        # Group by subcategory
        by_sub = defaultdict(list)
        for l in cat_learnings:
            by_sub[l.subcategory].append(l)

        for subcategory, sub_learnings in by_sub.items():
            lines.append(f"### {subcategory.replace('_', ' ').title()}")
            lines.append("")
            for learning in sub_learnings[:5]:  # Limit per subcategory
                lines.append(f"**{learning.summary}**")
                lines.append(f"> {learning.detail[:200]}...")
                lines.append(f"*(from: {learning.source_session}, confidence: {learning.confidence:.0%})*")
                lines.append("")

    return "\n".join(lines)


def generate_claude_md_proposal(learnings: list[Learning]) -> str:
    """Generate proposed additions to CLAUDE.md."""
    lines = []
    lines.append("## Proposed CLAUDE.md Additions")
    lines.append("")
    lines.append("Add to `~/.claude/CLAUDE.md`:")
    lines.append("")
    lines.append("```markdown")
    lines.append("## Learnings")
    lines.append("")
    lines.append(f"*Auto-generated from session analysis on {datetime.now().strftime('%Y-%m-%d')}*")
    lines.append("")

    # Deduplicate and filter
    learnings = deduplicate_learnings(learnings)
    high_confidence = [l for l in learnings if l.confidence >= 0.6]

    by_category = defaultdict(list)
    for learning in high_confidence:
        by_category[learning.category].append(learning)

    category_names = {
        'code_pattern': 'Code Patterns',
        'architecture': 'Architectural Preferences',
        'tool_usage': 'Tool Usage Guidelines',
        'missing_context': 'Project Context'
    }

    for category, display_name in category_names.items():
        cat_learnings = by_category.get(category, [])
        if not cat_learnings:
            continue

        lines.append(f"### {display_name}")
        lines.append("")

        by_sub = defaultdict(list)
        for l in cat_learnings:
            by_sub[l.subcategory].append(l)

        for subcategory, sub_learnings in by_sub.items():
            lines.append(f"**{subcategory.replace('_', ' ').title()}:**")
            for learning in sub_learnings[:3]:
                # Extract actionable guidance
                detail = learning.detail[:150].strip()
                if not detail.endswith('.'):
                    detail += "..."
                lines.append(f"- {detail}")
            lines.append("")

    lines.append("```")

    return "\n".join(lines)


def get_sessions_to_analyze(scope: str, project_path: Optional[str] = None) -> list[tuple[Path, dict]]:
    """Get list of sessions to analyze based on scope."""
    projects_dir = Path.home() / '.claude' / 'projects'
    sessions = []

    if not projects_dir.exists():
        return sessions

    if scope == 'current':
        cwd = os.getcwd().replace('/', '-')
        if not cwd.startswith('-'):
            cwd = '-' + cwd
        project_dir = projects_dir / cwd
        if project_dir.exists():
            index_file = project_dir / 'sessions-index.json'
            if index_file.exists():
                with open(index_file) as f:
                    index = json.load(f)
                entries = sorted(index.get('entries', []), key=lambda x: x.get('modified', ''), reverse=True)
                if entries:
                    session_path = Path(entries[0]['fullPath'])
                    if session_path.exists():
                        sessions.append((session_path, entries[0]))

    elif scope == 'project':
        path = project_path or os.getcwd()
        cwd = path.replace('/', '-')
        if not cwd.startswith('-'):
            cwd = '-' + cwd
        project_dir = projects_dir / cwd
        if project_dir.exists():
            index_file = project_dir / 'sessions-index.json'
            if index_file.exists():
                with open(index_file) as f:
                    index = json.load(f)
                for entry in index.get('entries', []):
                    session_path = Path(entry['fullPath'])
                    if session_path.exists():
                        sessions.append((session_path, entry))

    else:  # all
        for project_dir in projects_dir.iterdir():
            if not project_dir.is_dir():
                continue
            index_file = project_dir / 'sessions-index.json'
            if index_file.exists():
                try:
                    with open(index_file) as f:
                        index = json.load(f)
                    for entry in index.get('entries', []):
                        session_path = Path(entry['fullPath'])
                        if session_path.exists():
                            sessions.append((session_path, entry))
                except (json.JSONDecodeError, KeyError):
                    continue

    return sessions


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Analyze Claude Code sessions for learnings')
    parser.add_argument('--scope', choices=['current', 'all', 'project'], default='current',
                       help='Scope of analysis')
    parser.add_argument('--project', type=str, help='Specific project path')
    parser.add_argument('--output', choices=['text', 'json'], default='text')
    parser.add_argument('--proposals', action='store_true', default=True,
                       help='Include CLAUDE.md proposals')
    args = parser.parse_args()

    sessions = get_sessions_to_analyze(args.scope, args.project)

    if not sessions:
        print("No sessions found to analyze.", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing {len(sessions)} sessions...", file=sys.stderr)

    all_learnings = []
    all_failures = []

    for session_path, session_meta in sessions:
        try:
            learnings, failures = parse_session(session_path, session_meta)
            all_learnings.extend(learnings)
            all_failures.extend(failures)
        except Exception as e:
            print(f"Error parsing {session_path}: {e}", file=sys.stderr)

    print(f"Found {len(all_learnings)} potential learnings.", file=sys.stderr)
    print(f"Found {len(all_failures)} tool failures.", file=sys.stderr)

    if args.output == 'json':
        result = {
            'learnings': [
                {
                    'category': l.category,
                    'subcategory': l.subcategory,
                    'summary': l.summary,
                    'detail': l.detail[:200],
                    'confidence': l.confidence
                }
                for l in deduplicate_learnings(all_learnings)[:50]
            ],
            'tool_failures': len(all_failures)
        }
        print(json.dumps(result, indent=2))
    else:
        report = generate_report(all_learnings, all_failures)
        print(report)

        if args.proposals and all_learnings:
            proposal = generate_claude_md_proposal(all_learnings)
            print("\n" + proposal)


if __name__ == '__main__':
    main()
