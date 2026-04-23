#!/usr/bin/env python3
"""
Skill Analyzer — Automated best-practices review for CodeBuddy skills.

Reads a skill directory (or a single SKILL.md file) and produces a
categorized report of findings at three severity levels:
  CRITICAL, RECOMMENDED, OPTIONAL

Usage:
    python3 analyze_skill.py <path-to-skill-directory-or-SKILL.md>

Exit codes:
    0  — No critical findings
    1  — One or more critical findings
    2  — Input error (path not found, missing SKILL.md, etc.)
"""

import os
import re
import sys
import yaml
from pathlib import Path


# ── Constants ──────────────────────────────────────────────────────────────
RESERVED_WORDS = {"anthropic", "claude"}
NAME_MAX_LEN = 64
DESC_MAX_LEN = 1024
SKILL_BODY_MAX_LINES = 500
LONG_REF_THRESHOLD = 100  # lines before a TOC is recommended
VERBOSE_PATTERNS = [
    (r"(?i)\bPDF\s*\(Portable Document Format\)", "Unnecessary expansion of well-known acronym"),
    (r"(?i)\bthere are many (?:libraries|tools|ways)", "Generic filler — be specific or omit"),
    (r"(?i)\bfirst,?\s+you(?:'ll| will) need to", "Step-by-step hand-holding Claude does not need"),
]
SECOND_PERSON_RE = re.compile(
    r"\b(?:you\s+(?:should|can|need|must|will|could|might|may|are)|"
    r"your\s+(?!skill|Skill))\b",
    re.IGNORECASE,
)
XML_TAG_RE = re.compile(r"<\/?[a-zA-Z][^>]*>")
WINDOWS_PATH_RE = re.compile(r"(?<!\w)\\(?=[a-zA-Z_])")  # backslash before letter


# ── Helpers ────────────────────────────────────────────────────────────────
class Finding:
    """One discrete issue found during analysis."""

    def __init__(self, severity: str, category: str, message: str, location: str = ""):
        self.severity = severity  # CRITICAL | RECOMMENDED | OPTIONAL
        self.category = category
        self.message = message
        self.location = location  # e.g. "SKILL.md:12" or "scripts/rotate.py"

    def __str__(self):
        loc = f" ({self.location})" if self.location else ""
        return f"[{self.severity}] {self.category}{loc}: {self.message}"


def parse_frontmatter(text: str):
    """Return (metadata_dict, body_text) from SKILL.md content."""
    if not text.startswith("---"):
        return None, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text
    try:
        meta = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None, text
    return meta or {}, parts[2]


def count_lines(text: str) -> int:
    return len(text.strip().splitlines())


# ── Checks ─────────────────────────────────────────────────────────────────
def check_metadata(meta, findings: list):
    """Validate YAML frontmatter fields."""
    if meta is None:
        findings.append(Finding("CRITICAL", "Metadata", "Missing YAML frontmatter"))
        return

    # -- name --
    name = meta.get("name", "")
    if not name:
        findings.append(Finding("CRITICAL", "Metadata", "Missing 'name' field"))
    else:
        if len(name) > NAME_MAX_LEN:
            findings.append(
                Finding("CRITICAL", "Metadata", f"Name exceeds {NAME_MAX_LEN} chars (got {len(name)})")
            )
        if not re.match(r"^[a-z0-9][a-z0-9-]*$", name):
            findings.append(
                Finding("CRITICAL", "Metadata", "Name must be lowercase letters, digits, and hyphens only")
            )
        for rw in RESERVED_WORDS:
            if rw in name:
                findings.append(
                    Finding("CRITICAL", "Metadata", f"Name contains reserved word '{rw}'")
                )
        if XML_TAG_RE.search(name):
            findings.append(Finding("CRITICAL", "Metadata", "Name contains XML tags"))

    # -- description --
    desc = meta.get("description", "")
    if not desc:
        findings.append(Finding("CRITICAL", "Metadata", "Missing or empty 'description' field"))
    else:
        if len(desc) > DESC_MAX_LEN:
            findings.append(
                Finding("CRITICAL", "Metadata", f"Description exceeds {DESC_MAX_LEN} chars (got {len(desc)})")
            )
        if XML_TAG_RE.search(desc):
            findings.append(Finding("CRITICAL", "Metadata", "Description contains XML tags"))
        # Check third-person
        if re.match(r"(?i)^(I |You |We )", desc.strip()):
            findings.append(
                Finding("RECOMMENDED", "Description", "Use third person ('Processes...' not 'I help...')")
            )
        # Check trigger terms presence
        trigger_keywords = {"when", "use", "trigger", "for", "if"}
        desc_lower = desc.lower()
        has_trigger = any(kw in desc_lower for kw in trigger_keywords)
        if not has_trigger:
            findings.append(
                Finding(
                    "RECOMMENDED",
                    "Description",
                    "Include when to use the skill (e.g. 'Use when...')",
                )
            )


def check_body(body: str, findings: list):
    """Analyze the SKILL.md body for common issues."""
    lines = body.strip().splitlines()
    line_count = len(lines)

    # -- Length --
    if line_count > SKILL_BODY_MAX_LINES:
        findings.append(
            Finding(
                "CRITICAL",
                "Length",
                f"SKILL.md body is {line_count} lines (max {SKILL_BODY_MAX_LINES}). "
                "Split detail into references/ files.",
                "SKILL.md",
            )
        )
    elif line_count > SKILL_BODY_MAX_LINES * 0.8:
        findings.append(
            Finding(
                "RECOMMENDED",
                "Length",
                f"SKILL.md body is {line_count} lines — approaching the 500-line limit. "
                "Consider moving some content to references/.",
                "SKILL.md",
            )
        )

    # -- Second-person language --
    for i, line in enumerate(lines, 1):
        if SECOND_PERSON_RE.search(line):
            findings.append(
                Finding(
                    "RECOMMENDED",
                    "Writing Style",
                    f"Second-person language detected: \"{line.strip()[:80]}...\"",
                    f"SKILL.md:{i}",
                )
            )
            break  # report once then stop

    # -- Verbose patterns --
    full_text = "\n".join(lines)
    for pattern, msg in VERBOSE_PATTERNS:
        if re.search(pattern, full_text):
            findings.append(Finding("RECOMMENDED", "Conciseness", msg, "SKILL.md"))

    # -- Windows paths --
    for i, line in enumerate(lines, 1):
        if WINDOWS_PATH_RE.search(line):
            findings.append(
                Finding("OPTIONAL", "Paths", "Windows-style backslash path detected", f"SKILL.md:{i}")
            )
            break


def check_references(skill_dir: Path, body: str, findings: list):
    """Check reference files and their linking from SKILL.md."""
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return

    for ref_file in sorted(refs_dir.iterdir()):
        if ref_file.is_file() and ref_file.suffix in (".md", ".txt"):
            content = ref_file.read_text(errors="replace")
            lc = count_lines(content)
            if lc > LONG_REF_THRESHOLD:
                # check for TOC
                has_toc = bool(
                    re.search(r"(?i)(table of contents|## toc|## contents|\[.*\]\(#)", content[:500])
                )
                if not has_toc:
                    findings.append(
                        Finding(
                            "OPTIONAL",
                            "References",
                            f"Reference file is {lc} lines but has no table of contents",
                            f"references/{ref_file.name}",
                        )
                    )

            # Check for nested references (references pointing to other references)
            nested_links = re.findall(r"\[.*?\]\((?:\.\./)?references/", content)
            if nested_links:
                findings.append(
                    Finding(
                        "RECOMMENDED",
                        "References",
                        "Nested reference detected — keep references one level deep from SKILL.md",
                        f"references/{ref_file.name}",
                    )
                )


def check_scripts(skill_dir: Path, findings: list):
    """Check script quality."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return

    for script_file in sorted(scripts_dir.iterdir()):
        if not script_file.is_file():
            continue
        if script_file.suffix not in (".py", ".sh", ".bash"):
            continue

        content = script_file.read_text(errors="replace")
        rel = f"scripts/{script_file.name}"

        # -- Bare except / punt to Claude --
        if "except:" in content and "except Exception" not in content:
            findings.append(
                Finding("RECOMMENDED", "Scripts", "Bare 'except:' — handle errors explicitly", rel)
            )

        if re.search(r"raise\s+(Exception|RuntimeError)\s*\(", content):
            # Not necessarily bad, but check for helpful messages
            pass

        # -- sys.exit without message --
        if re.search(r"sys\.exit\(\s*1\s*\)", content) and "print" not in content:
            findings.append(
                Finding(
                    "RECOMMENDED",
                    "Scripts",
                    "sys.exit(1) without printing an error message — solve, don't punt",
                    rel,
                )
            )

        # -- Magic numbers --
        magic_numbers = re.findall(r"(?<![\"'\w])(\d{3,})(?![\"'\w])", content)
        # Exclude common benign values
        benign = {"100", "200", "404", "500", "1000", "1024", "2048", "4096", "8192", "65535"}
        suspicious = [n for n in magic_numbers if n not in benign]
        if suspicious:
            findings.append(
                Finding(
                    "OPTIONAL",
                    "Scripts",
                    f"Possible magic numbers without explanation: {', '.join(suspicious[:5])}",
                    rel,
                )
            )

        # -- Windows paths in scripts --
        if WINDOWS_PATH_RE.search(content):
            findings.append(Finding("OPTIONAL", "Paths", "Windows-style backslash path in script", rel))

        # -- Missing docstring --
        if script_file.suffix == ".py" and '"""' not in content and "'''" not in content:
            findings.append(
                Finding("OPTIONAL", "Scripts", "Python script has no docstring", rel)
            )


def check_consistency(body: str, meta: dict, skill_dir: Path, findings: list):
    """Check terminology consistency and naming conventions."""
    name = meta.get("name", "")
    if name:
        # Naming convention check
        words = name.split("-")
        if len(words) >= 2 and not any(w.endswith("ing") for w in words):
            findings.append(
                Finding(
                    "OPTIONAL",
                    "Naming",
                    f"Consider gerund form for skill name (e.g. 'improving-skills' instead of '{name}')",
                )
            )

    # Check directory name matches metadata name
    dir_name = skill_dir.name
    if name and dir_name != name:
        findings.append(
            Finding(
                "CRITICAL",
                "Metadata",
                f"Directory name '{dir_name}' does not match metadata name '{name}'",
            )
        )


# ── Main ───────────────────────────────────────────────────────────────────
def analyze(path_str: str) -> list:
    """Run all checks on a skill and return list of Finding objects."""
    path = Path(path_str).resolve()
    findings: list[Finding] = []

    # Determine skill directory and SKILL.md path
    if path.is_file() and path.name == "SKILL.md":
        skill_md = path
        skill_dir = path.parent
    elif path.is_dir():
        skill_md = path / "SKILL.md"
        skill_dir = path
    else:
        print(f"Error: {path} is not a directory or SKILL.md file", file=sys.stderr)
        sys.exit(2)

    if not skill_md.exists():
        print(f"Error: SKILL.md not found at {skill_md}", file=sys.stderr)
        sys.exit(2)

    raw = skill_md.read_text(errors="replace")
    meta, body = parse_frontmatter(raw)

    check_metadata(meta, findings)
    check_body(body, findings)
    check_references(skill_dir, body, findings)
    check_scripts(skill_dir, findings)
    if meta:
        check_consistency(body, meta, skill_dir, findings)

    return findings


def main():
    if len(sys.argv) < 2:
        print("Usage: analyze_skill.py <path-to-skill-directory-or-SKILL.md>")
        sys.exit(2)

    findings = analyze(sys.argv[1])

    if not findings:
        print("✅ No issues found — skill looks great!")
        sys.exit(0)

    # Group by severity
    severity_order = ["CRITICAL", "RECOMMENDED", "OPTIONAL"]
    grouped: dict[str, list[Finding]] = {s: [] for s in severity_order}
    for f in findings:
        grouped[f.severity].append(f)

    total = len(findings)
    crit = len(grouped["CRITICAL"])

    print(f"\n{'='*60}")
    print(f" Skill Analysis Report — {total} finding(s)")
    print(f"{'='*60}\n")

    for sev in severity_order:
        items = grouped[sev]
        if not items:
            continue
        icons = {"CRITICAL": "🔴", "RECOMMENDED": "🟡", "OPTIONAL": "🔵"}
        print(f"{icons[sev]} {sev} ({len(items)})")
        print("-" * 40)
        for f in items:
            loc = f"  [{f.location}]" if f.location else ""
            print(f"  • {f.category}{loc}")
            print(f"    {f.message}")
        print()

    if crit > 0:
        print(f"❌ {crit} critical issue(s) must be fixed.")
        sys.exit(1)
    else:
        print("✅ No critical issues. Review recommended/optional items for polish.")
        sys.exit(0)


if __name__ == "__main__":
    main()
