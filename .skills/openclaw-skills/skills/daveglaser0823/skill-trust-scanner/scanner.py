#!/usr/bin/env python3
"""
Skill Trust Scanner v1.0.0
Security scanner for OpenClaw and ClawHub skills.

Scans skill directories for malware, data exfiltration, crypto-miners,
obfuscated code, and supply-chain risks. Returns a Trust Score (0-100).

Usage:
    python scanner.py <path-to-skill>
    python scanner.py <path-to-skill> --json
    python scanner.py <path-to-skill> -o report.md
    python scanner.py --batch <skills-directory>

No external dependencies required - pure Python 3.7+ stdlib.

Author: Eli Labs (eli.labs.ceo@gmail.com)
License: MIT
"""

import os
import re
import sys
import json
import math
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple


# ── Severity & Verdict ────────────────────────────────────────────────────────

class Severity:
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Verdict:
    TRUSTED = "TRUSTED"
    CAUTION = "CAUTION"
    SUSPICIOUS = "SUSPICIOUS"
    REJECT = "REJECT"


# ── Data Classes ──────────────────────────────────────────────────────────────

@dataclass
class Finding:
    category: str
    severity: str
    file_path: str
    line_number: int
    line_content: str
    description: str
    recommendation: str
    pattern_name: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class SkillMeta:
    name: str = "unknown"
    version: str = "unknown"
    description: str = ""
    author: str = "unknown"
    has_skill_md: bool = False
    has_readme: bool = False
    has_tests: bool = False
    has_examples: bool = False
    file_count: int = 0
    script_count: int = 0
    total_lines: int = 0
    last_modified: str = ""


@dataclass
class TrustReport:
    skill_path: str
    scan_timestamp: str
    metadata: SkillMeta
    findings: List[Finding] = field(default_factory=list)
    trust_score: int = 70
    verdict: str = Verdict.TRUSTED
    verdict_reason: str = ""
    files_scanned: List[str] = field(default_factory=list)
    score_breakdown: Dict[str, int] = field(default_factory=dict)

    def to_dict(self):
        return {
            "skill_path": self.skill_path,
            "scan_timestamp": self.scan_timestamp,
            "trust_score": self.trust_score,
            "verdict": self.verdict,
            "verdict_reason": self.verdict_reason,
            "metadata": asdict(self.metadata),
            "findings_summary": {
                "critical": len([f for f in self.findings if f.severity == Severity.CRITICAL]),
                "high": len([f for f in self.findings if f.severity == Severity.HIGH]),
                "medium": len([f for f in self.findings if f.severity == Severity.MEDIUM]),
                "low": len([f for f in self.findings if f.severity == Severity.LOW]),
            },
            "findings": [f.to_dict() for f in self.findings],
            "score_breakdown": self.score_breakdown,
            "files_scanned": self.files_scanned,
        }


# ── Threat Patterns ──────────────────────────────────────────────────────────

CRITICAL_PATTERNS = [
    {
        "name": "reverse_shell",
        "pattern": r"/dev/tcp/|nc\s+-[el]|ncat\s+-[el]|bash\s+-i\s+>&|python.*pty\.spawn|mkfifo.*\bnc\b|socat.*exec",
        "description": "Reverse shell / backdoor pattern",
        "recommendation": "REJECT immediately. Report skill to ClawHub.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts", ".rb", ".pl"},
    },
    {
        "name": "download_execute",
        "pattern": r"curl\s+[^|]*\|\s*(ba)?sh|wget\s+[^|]*\|\s*(ba)?sh|requests\.get\([^)]+\)\.(text|content).*\bexec\b|urllib.*urlopen.*\bexec\b",
        "description": "Downloads and executes remote code",
        "recommendation": "REJECT. Classic malware delivery pattern.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts"},
    },
    {
        "name": "crypto_miner",
        "pattern": r"\bxmrig\b|\bethminer\b|stratum\+tcp://|\bcpuminer\b|\bcgminer\b|mining[_\s]*pool|cryptonight|monero.*miner",
        "description": "Cryptocurrency mining indicators",
        "recommendation": "REJECT. Cryptojacking malware.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts", ".json", ".md", ".yml", ".yaml"},
    },
    {
        "name": "base64_decode_exec",
        "pattern": r"base64\.b64decode\s*\([^)]*\).*\bexec\b|atob\s*\([^)]*\).*\beval\b|Buffer\.from\s*\([^)]*,\s*['\"]base64['\"]\s*\).*\beval\b",
        "description": "Decodes and executes obfuscated payload",
        "recommendation": "REJECT. Hides malicious code in encoded form.",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "credential_harvest",
        "pattern": r"(?:open|read|cat|glob)\s*\(?.*(?:~|/home/\w+)/\.(?:ssh|aws|gnupg|config/gcloud)|/etc/shadow|\.kube/config",
        "description": "Reads sensitive credential files",
        "recommendation": "REJECT unless the skill is explicitly a credential manager.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts", ".rb"},
    },
    {
        "name": "system_service",
        "pattern": r"systemctl\s+(?:enable|start)|launchctl\s+load|/etc/systemd/system/|sc\s+create|chkconfig.*--add|update-rc\.d",
        "description": "Creates persistent system services",
        "recommendation": "REJECT. Skills should not install system services.",
        "file_types": {".py", ".sh", ".bash", ".js"},
    },
    {
        "name": "destructive_command",
        "pattern": r"rm\s+-rf\s+[/~](?!\S*tmp)|rm\s+-rf\s+\*\s*$|mkfs\b|dd\s+if=/dev/zero\s+of=/dev/|wipefs",
        "description": "Destructive command that could delete user data or format disks",
        "recommendation": "REJECT. This could destroy the system.",
        "file_types": {".py", ".sh", ".bash"},
    },
]

HIGH_PATTERNS = [
    {
        "name": "eval_exec",
        "pattern": r"(?<!\w)\beval\s*\(|(?<!\w)\bexec\s*\((?!ut)|new\s+Function\s*\(",
        "description": "Dynamic code execution",
        "recommendation": "Review: verify input is not user-controlled or from network.",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "bulk_env_access",
        "pattern": r"os\.environ\.copy\(\)|dict\(os\.environ\)|JSON\.stringify\(process\.env\)|for\s+\w+\s+in\s+os\.environ",
        "description": "Bulk access to all environment variables",
        "recommendation": "Suspicious. Legitimate tools read specific vars, not all.",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "crontab_modify",
        "pattern": r"crontab\s+-[elr]|/etc/cron\.[dw]|schtasks\s+/create",
        "description": "Modifies system scheduled tasks",
        "recommendation": "Skills should use OpenClaw cron, not system crontab.",
        "file_types": {".py", ".sh", ".bash", ".js"},
    },
    {
        "name": "network_listener",
        "pattern": r"socket\.bind\s*\(|\.listen\s*\(\s*\d|http\.createServer|net\.createServer|TCPServer|HTTPServer",
        "description": "Opens network listener/server",
        "recommendation": "Verify: is this skill supposed to run a server?",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "filesystem_write_outside",
        "pattern": r"open\s*\(\s*['\"](?:/etc/|/tmp/|/var/|/usr/)|write.*(?:/etc/|/usr/local/bin)",
        "description": "Writes files outside skill directory",
        "recommendation": "Review file paths. Skills should write within their own directory.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts"},
    },
    {
        "name": "process_spawn",
        "pattern": r"subprocess\.(?:Popen|call|run|check_output)|child_process\.exec(?:Sync)?|os\.system\s*\(|os\.popen\s*\(",
        "description": "Spawns external processes",
        "recommendation": "Review: what commands are being run? Is input sanitized?",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "runtime_install",
        "pattern": r"pip\s+install(?!\s+--help)|npm\s+install(?!\s+--help)|apt(?:-get)?\s+install|brew\s+install|gem\s+install",
        "description": "Installs packages at runtime",
        "recommendation": "Supply chain risk. Packages should be declared, not auto-installed.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts", ".md"},
    },
]

MEDIUM_PATTERNS = [
    {
        "name": "http_post_external",
        "pattern": r"requests\.post\s*\(|httpx\.post\s*\(|fetch\s*\([^)]*,\s*\{[^}]*method:\s*['\"]POST['\"]|urllib\.request\.urlopen.*data=",
        "description": "HTTP POST to external endpoint",
        "recommendation": "Verify destination URL is expected and documented.",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "env_read",
        "pattern": r"os\.getenv\s*\(|os\.environ\[|process\.env\.\w+",
        "description": "Reads specific environment variables",
        "recommendation": "Check which variables and whether they contain secrets.",
        "file_types": {".py", ".js", ".ts"},
    },
    {
        "name": "sensitive_file_read",
        "pattern": r"\.env\b|\.credentials\b|\.netrc\b|\.pgpass\b",
        "description": "References sensitive configuration files",
        "recommendation": "Verify the skill needs this access.",
        "file_types": {".py", ".sh", ".bash", ".js", ".ts", ".md"},
    },
    {
        "name": "encoded_payload",
        "pattern": r"[A-Za-z0-9+/]{80,}={0,2}|\\x[0-9a-fA-F]{2}(?:\\x[0-9a-fA-F]{2}){20,}",
        "description": "Long encoded string (potential obfuscated payload)",
        "recommendation": "Decode and inspect. Legitimate uses include embedded assets.",
        "file_types": {".py", ".js", ".ts", ".sh"},
    },
    {
        "name": "minified_code",
        "pattern": None,  # Handled by line-length check
        "description": "Minified/obfuscated code (lines >500 chars)",
        "recommendation": "Minified code hides intent. Request readable source.",
        "file_types": {".py", ".js", ".ts"},
    },
]

LOW_PATTERNS = [
    {
        "name": "hardcoded_url",
        "pattern": r"https?://(?!localhost|127\.0\.0\.1|example\.com|github\.com|clawhub\.com)\S+",
        "description": "Hardcoded external URL",
        "recommendation": "Informational. Document where URLs point.",
        "file_types": {".py", ".js", ".ts", ".sh", ".md"},
    },
    {
        "name": "api_key_pattern",
        "pattern": r"(?:sk|pk|key|token|secret|api[_-]?key)\s*[:=]\s*['\"][A-Za-z0-9_\-]{20,}['\"]",
        "description": "Potential hardcoded API key or secret",
        "recommendation": "Verify this is a placeholder, not a real key.",
        "file_types": {".py", ".js", ".ts", ".json", ".yml", ".yaml", ".env"},
    },
    {
        "name": "todo_fixme",
        "pattern": r"(?:#|//|/\*)\s*(?:TODO|FIXME|HACK|XXX)\b",
        "description": "Incomplete code marker",
        "recommendation": "Informational. Indicates code may be unfinished.",
        "file_types": {".py", ".js", ".ts", ".sh"},
    },
    {
        "name": "bare_except",
        "pattern": r"except\s*:|catch\s*\(\s*\)\s*\{|catch\s*\{",
        "description": "Bare exception handler (swallows all errors)",
        "recommendation": "Poor practice but not a security threat.",
        "file_types": {".py", ".js", ".ts"},
    },
]


# ── Scanner ───────────────────────────────────────────────────────────────────

class TrustScanner:
    """Scans a skill directory and produces a TrustReport."""

    SCANNABLE_EXTENSIONS = {
        ".py", ".js", ".ts", ".sh", ".bash", ".rb", ".pl",
        ".md", ".json", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".env",
    }

    def __init__(self, skill_path: str):
        self.skill_path = Path(skill_path).resolve()
        self.report = TrustReport(
            skill_path=str(self.skill_path),
            scan_timestamp=datetime.now().isoformat(),
            metadata=SkillMeta(),
        )

    def scan(self) -> TrustReport:
        if not self.skill_path.exists():
            raise FileNotFoundError(f"Skill path not found: {self.skill_path}")
        if not self.skill_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.skill_path}")

        self._extract_metadata()
        self._scan_all_files()
        self._check_entropy()
        self._calculate_score()
        return self.report

    def _extract_metadata(self):
        meta = self.report.metadata
        skill_md = self.skill_path / "SKILL.md"
        if skill_md.exists():
            meta.has_skill_md = True
            content = skill_md.read_text(encoding="utf-8", errors="ignore")
            if content.startswith("---"):
                try:
                    end = content.index("---", 3)
                    frontmatter = content[3:end]
                    for line in frontmatter.split("\n"):
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip().lower()
                            value = value.strip().strip("\"'")
                            if key == "name":
                                meta.name = value
                            elif key == "version":
                                meta.version = value
                            elif key == "description" and value:
                                meta.description = value
                            elif key == "author":
                                meta.author = value
                except ValueError:
                    pass

        meta.has_readme = (self.skill_path / "README.md").exists()
        meta.has_tests = (self.skill_path / "tests").is_dir()
        meta.has_examples = (self.skill_path / "examples").is_dir()

        # Find latest modification time
        latest_mtime = 0
        script_exts = {".py", ".js", ".ts", ".sh", ".bash", ".rb", ".pl"}
        for f in self.skill_path.rglob("*"):
            if f.is_file():
                meta.file_count += 1
                if f.suffix in script_exts:
                    meta.script_count += 1
                mtime = f.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime

        if latest_mtime > 0:
            meta.last_modified = datetime.fromtimestamp(latest_mtime).isoformat()

    def _scan_all_files(self):
        for file_path in sorted(self.skill_path.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in self.SCANNABLE_EXTENSIONS:
                continue

            rel_path = str(file_path.relative_to(self.skill_path))
            self.report.files_scanned.append(rel_path)

            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = content.split("\n")
            self.report.metadata.total_lines += len(lines)
            suffix = file_path.suffix.lower()

            # Check all pattern categories
            self._match_patterns(CRITICAL_PATTERNS, Severity.CRITICAL, rel_path, lines, suffix)
            self._match_patterns(HIGH_PATTERNS, Severity.HIGH, rel_path, lines, suffix)
            self._match_patterns(MEDIUM_PATTERNS, Severity.MEDIUM, rel_path, lines, suffix)
            self._match_patterns(LOW_PATTERNS, Severity.LOW, rel_path, lines, suffix)

            # Check for minified code (lines > 500 chars in script files)
            if suffix in {".py", ".js", ".ts"}:
                for i, line in enumerate(lines, 1):
                    if len(line) > 500:
                        self.report.findings.append(Finding(
                            category="obfuscation",
                            severity=Severity.MEDIUM,
                            file_path=rel_path,
                            line_number=i,
                            line_content=line[:100] + "... [truncated]",
                            description="Minified/obfuscated code (line >500 chars)",
                            recommendation="Minified code hides intent. Request readable source.",
                            pattern_name="minified_code",
                        ))

    def _match_patterns(self, patterns: list, severity: str, rel_path: str,
                        lines: List[str], suffix: str):
        for pdef in patterns:
            if pdef.get("pattern") is None:
                continue
            if suffix not in pdef.get("file_types", set()):
                continue

            regex = re.compile(pdef["pattern"], re.IGNORECASE)
            for i, line in enumerate(lines, 1):
                if regex.search(line):
                    self.report.findings.append(Finding(
                        category=pdef["name"],
                        severity=severity,
                        file_path=rel_path,
                        line_number=i,
                        line_content=line.strip()[:200],
                        description=pdef["description"],
                        recommendation=pdef["recommendation"],
                        pattern_name=pdef["name"],
                    ))

    def _check_entropy(self):
        """Flag files with unusually high Shannon entropy (obfuscation signal)."""
        for file_path in sorted(self.skill_path.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in {".py", ".js", ".ts", ".sh"}:
                continue
            try:
                data = file_path.read_bytes()
            except Exception:
                continue

            if len(data) < 500:
                continue

            entropy = self._shannon_entropy(data)
            if entropy > 6.0:
                rel_path = str(file_path.relative_to(self.skill_path))
                self.report.findings.append(Finding(
                    category="obfuscation",
                    severity=Severity.MEDIUM,
                    file_path=rel_path,
                    line_number=0,
                    line_content=f"Shannon entropy: {entropy:.2f}/8.0",
                    description=f"High entropy ({entropy:.2f}) suggests obfuscated or compressed content",
                    recommendation="Inspect file contents manually. Normal source code is 4.0-5.5 entropy.",
                    pattern_name="high_entropy",
                ))

    @staticmethod
    def _shannon_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        freq = {}
        for byte in data:
            freq[byte] = freq.get(byte, 0) + 1
        length = len(data)
        entropy = 0.0
        for count in freq.values():
            p = count / length
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def _calculate_score(self):
        score = 70
        breakdown = {"baseline": 70}

        # Metadata bonuses/penalties
        meta = self.report.metadata
        meta_adj = 0
        if meta.has_skill_md:
            meta_adj += 5
        else:
            meta_adj -= 10
        if meta.has_readme:
            meta_adj += 3
        else:
            meta_adj -= 5
        if meta.has_tests:
            meta_adj += 5
        if meta.has_examples:
            meta_adj += 3
        if meta.description and len(meta.description) > 20:
            meta_adj += 2
        elif not meta.description or meta.description == "":
            meta_adj -= 5
        if meta.total_lines < 1000:
            meta_adj += 2
        elif meta.total_lines > 5000:
            meta_adj -= 5
        if meta.file_count > 50:
            meta_adj -= 5

        breakdown["metadata"] = meta_adj
        score += meta_adj

        # Finding penalties
        counts = {Severity.CRITICAL: 0, Severity.HIGH: 0, Severity.MEDIUM: 0, Severity.LOW: 0}
        # Deduplicate: count unique (pattern_name, file_path) pairs per severity
        seen = set()
        for f in self.report.findings:
            key = (f.pattern_name, f.file_path, f.severity)
            if key not in seen:
                seen.add(key)
                counts[f.severity] = counts.get(f.severity, 0) + 1

        crit_penalty = counts[Severity.CRITICAL] * 70
        high_penalty = counts[Severity.HIGH] * 20
        med_penalty = counts[Severity.MEDIUM] * 5
        low_penalty = counts[Severity.LOW] * 1

        if crit_penalty > 0:
            breakdown["critical_findings"] = -crit_penalty
        if high_penalty > 0:
            breakdown["high_findings"] = -high_penalty
        if med_penalty > 0:
            breakdown["medium_findings"] = -med_penalty
        if low_penalty > 0:
            breakdown["low_findings"] = -low_penalty

        score -= (crit_penalty + high_penalty + med_penalty + low_penalty)

        # Clamp
        score = max(0, min(100, score))
        self.report.trust_score = score
        self.report.score_breakdown = breakdown

        # Verdict
        if score >= 80:
            self.report.verdict = Verdict.TRUSTED
            self.report.verdict_reason = "No critical or high-severity issues detected."
        elif score >= 60:
            self.report.verdict = Verdict.CAUTION
            self.report.verdict_reason = "Some issues found. Review flagged items before installing."
        elif score >= 40:
            self.report.verdict = Verdict.SUSPICIOUS
            self.report.verdict_reason = "Multiple concerning patterns. Manual review required."
        else:
            self.report.verdict = Verdict.REJECT
            self.report.verdict_reason = "Critical security issues found. Do not install."


# ── Formatters ────────────────────────────────────────────────────────────────

def format_markdown(report: TrustReport) -> str:
    lines = []
    lines.append(f"# Skill Trust Report: {report.metadata.name}")
    lines.append("")
    lines.append(f"**Trust Score: {report.trust_score}/100 - {report.verdict}**")
    lines.append(f"**Scanned:** {report.scan_timestamp}")
    lines.append(f"**Path:** `{report.skill_path}`")
    lines.append("")

    # Metadata
    lines.append("## Metadata")
    lines.append("")
    m = report.metadata
    lines.append(f"- **Name:** {m.name}")
    lines.append(f"- **Version:** {m.version}")
    lines.append(f"- **Author:** {m.author}")
    lines.append(f"- **Files:** {m.file_count} ({m.script_count} scripts, {m.total_lines} lines)")
    lines.append(f"- **SKILL.md:** {'Yes' if m.has_skill_md else 'No'}")
    lines.append(f"- **README.md:** {'Yes' if m.has_readme else 'No'}")
    lines.append(f"- **Tests:** {'Yes' if m.has_tests else 'No'}")
    lines.append(f"- **Examples:** {'Yes' if m.has_examples else 'No'}")
    lines.append("")

    # Score Breakdown
    lines.append("## Score Breakdown")
    lines.append("")
    for key, val in report.score_breakdown.items():
        sign = "+" if val >= 0 else ""
        lines.append(f"- {key}: {sign}{val}")
    lines.append(f"- **Final: {report.trust_score}/100**")
    lines.append("")

    # Findings by severity
    for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        matches = [f for f in report.findings if f.severity == severity]
        label = severity.upper()
        lines.append(f"## {label} Findings ({len(matches)})")
        lines.append("")
        if not matches:
            lines.append("None found.")
            lines.append("")
            continue
        for f in matches:
            lines.append(f"### {f.pattern_name}")
            lines.append(f"- **File:** `{f.file_path}` line {f.line_number}")
            lines.append(f"- **Description:** {f.description}")
            lines.append(f"- **Recommendation:** {f.recommendation}")
            lines.append(f"- **Code:** `{f.line_content}`")
            lines.append("")

    # Files scanned
    lines.append("## Files Scanned")
    lines.append("")
    for f in report.files_scanned:
        lines.append(f"- `{f}`")
    lines.append("")

    # Verdict
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"**{report.verdict}** (Score: {report.trust_score}/100)")
    lines.append(f"{report.verdict_reason}")
    lines.append("")

    return "\n".join(lines)


def format_json(report: TrustReport) -> str:
    return json.dumps(report.to_dict(), indent=2)


def format_summary(report: TrustReport) -> str:
    """One-line summary for batch mode."""
    counts = {}
    for f in report.findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    parts = []
    for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        if counts.get(sev, 0) > 0:
            parts.append(f"{counts[sev]}{sev[0].upper()}")
    findings_str = " ".join(parts) if parts else "clean"
    return f"{report.trust_score:3d}/100  {report.verdict:<12s}  {findings_str:<20s}  {report.metadata.name}"


# ── Batch Scanner ─────────────────────────────────────────────────────────────

def scan_batch(skills_dir: str, output_format: str = "summary") -> List[TrustReport]:
    """Scan all subdirectories in a skills directory."""
    skills_path = Path(skills_dir).resolve()
    if not skills_path.is_dir():
        print(f"Error: {skills_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    reports = []
    subdirs = sorted([d for d in skills_path.iterdir() if d.is_dir()])
    if not subdirs:
        print(f"No skill directories found in {skills_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {len(subdirs)} skills in {skills_path}...\n")
    print(f"{'Score':>7s}  {'Verdict':<12s}  {'Findings':<20s}  {'Skill'}")
    print("-" * 70)

    for subdir in subdirs:
        try:
            scanner = TrustScanner(str(subdir))
            report = scanner.scan()
            reports.append(report)
            print(format_summary(report))
        except Exception as e:
            print(f"  ERROR  {'---':<12s}  {'---':<20s}  {subdir.name}: {e}")

    print("-" * 70)

    # Summary stats
    if reports:
        avg_score = sum(r.trust_score for r in reports) / len(reports)
        reject_count = sum(1 for r in reports if r.verdict == Verdict.REJECT)
        suspicious_count = sum(1 for r in reports if r.verdict == Verdict.SUSPICIOUS)
        print(f"\nAverage Trust Score: {avg_score:.0f}/100")
        if reject_count > 0:
            print(f"REJECT: {reject_count} skill(s) should NOT be installed")
        if suspicious_count > 0:
            print(f"SUSPICIOUS: {suspicious_count} skill(s) need manual review")

    return reports


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Skill Trust Scanner - Security audit for OpenClaw/ClawHub skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scanner.py ./my-skill               Scan a local skill
  python scanner.py ./my-skill --json        Output as JSON
  python scanner.py ./my-skill -o report.md  Save report to file
  python scanner.py --batch ~/.openclaw/skills/  Scan all installed skills
        """,
    )
    parser.add_argument("skill_path", nargs="?", help="Path to skill directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Write report to file")
    parser.add_argument("--batch", action="store_true", help="Scan all subdirs as separate skills")

    args = parser.parse_args()

    if not args.skill_path:
        parser.print_help()
        sys.exit(1)

    if args.batch:
        reports = scan_batch(args.skill_path)
        if args.json:
            output = json.dumps([r.to_dict() for r in reports], indent=2)
            if args.output:
                Path(args.output).write_text(output)
                print(f"\nJSON report written to {args.output}")
            else:
                print(output)
        sys.exit(0)

    try:
        scanner = TrustScanner(args.skill_path)
        report = scanner.scan()
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        output = format_json(report)
    else:
        output = format_markdown(report)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Exit code based on verdict
    if report.verdict == Verdict.REJECT:
        sys.exit(2)
    elif report.verdict in (Verdict.SUSPICIOUS, Verdict.CAUTION):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
