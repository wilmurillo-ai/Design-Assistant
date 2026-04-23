#!/usr/bin/env python3
"""
OpenClaw Skill Analyzer - Advanced Security Audit Tool
Performs comprehensive security analysis on OpenClaw skills,
detecting prompt injection, data exfiltration, privilege escalation,
hidden file access, obfuscation, and more.
"""

import argparse
import os
import re
import json
import sys
import base64
from datetime import datetime
from collections import defaultdict


# ─────────────────────────────────────────────
# Severity & Category Definitions
# ─────────────────────────────────────────────

class Severity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

    SCORES = {
        "CRITICAL": 10,
        "HIGH": 7,
        "MEDIUM": 4,
        "LOW": 2,
        "INFO": 0,
    }

CATEGORIES = {
    "PROMPT_INJECTION": "Prompt Injection",
    "DATA_EXFILTRATION": "Data Exfiltration",
    "PRIVILEGE_ESCALATION": "Privilege Escalation",
    "HIDDEN_FILE_ACCESS": "Hidden File Access",
    "DANGEROUS_EXECUTION": "Dangerous Code Execution",
    "OBFUSCATION": "Code Obfuscation",
    "NETWORK_ACCESS": "Unauthorized Network Access",
    "FILESYSTEM_ABUSE": "Filesystem Abuse",
    "CREDENTIAL_THEFT": "Credential Theft",
    "SUPPLY_CHAIN": "Supply Chain Risk",
    "SANDBOX_ESCAPE": "Sandbox Escape",
    "INFORMATION_DISCLOSURE": "Information Disclosure",
}


# ─────────────────────────────────────────────
# Finding Data Class
# ─────────────────────────────────────────────

class Finding:
    def __init__(self, severity, category, title, description, file, line=None, matched_text=None, recommendation=None):
        self.severity = severity
        self.category = category
        self.title = title
        self.description = description
        self.file = file
        self.line = line
        self.matched_text = matched_text
        self.recommendation = recommendation or self._default_recommendation()

    def _default_recommendation(self):
        defaults = {
            "PROMPT_INJECTION": "Sanitize all user inputs. Never pass raw input to exec, eval, or system commands.",
            "DATA_EXFILTRATION": "Remove or restrict network calls. Audit all outbound data transmissions.",
            "PRIVILEGE_ESCALATION": "Apply principle of least privilege. Remove unnecessary sudo/root commands.",
            "HIDDEN_FILE_ACCESS": "Restrict file access to the skill's working directory only.",
            "DANGEROUS_EXECUTION": "Replace dynamic execution with safer alternatives. Avoid exec/eval/system.",
            "OBFUSCATION": "Remove obfuscated code. All skill logic should be readable and auditable.",
            "NETWORK_ACCESS": "Restrict network access to only required endpoints. Use allowlists.",
            "FILESYSTEM_ABUSE": "Limit filesystem operations to the skill's designated workspace.",
            "CREDENTIAL_THEFT": "Never access or read credential files, environment variables with secrets, or key stores.",
            "SUPPLY_CHAIN": "Pin dependency versions. Verify package integrity before installation.",
            "SANDBOX_ESCAPE": "Remove any attempts to break out of the sandbox or container.",
            "INFORMATION_DISCLOSURE": "Avoid exposing system information, paths, or configurations.",
        }
        return defaults.get(self.category, "Review and remediate this finding.")

    def to_dict(self):
        result = {
            "severity": self.severity,
            "category": CATEGORIES.get(self.category, self.category),
            "title": self.title,
            "description": self.description,
            "file": self.file,
            "recommendation": self.recommendation,
        }
        if self.line:
            result["line"] = self.line
        if self.matched_text:
            result["matched_text"] = self.matched_text[:200]
        return result


# ─────────────────────────────────────────────
# Detection Rules
# ─────────────────────────────────────────────

DETECTION_RULES = [
    # ── Prompt Injection ──
    {
        "id": "PI-001",
        "category": "PROMPT_INJECTION",
        "severity": Severity.CRITICAL,
        "title": "Direct prompt injection via exec/eval with user input",
        "description": "User input is passed directly to exec, eval, or compile without sanitization.",
        "pattern": r'(exec|eval|compile)\s*\(.*\b(user|input|query|prompt|request|arg|param)',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "PI-002",
        "category": "PROMPT_INJECTION",
        "severity": Severity.HIGH,
        "title": "String formatting in command execution",
        "description": "f-strings or format() used inside os.system, subprocess, or exec calls.",
        "pattern": r'(os\.system|subprocess\.\w+|exec)\s*\(\s*(f["\']|.*\.format\()',
        "file_types": [".py"],
    },
    {
        "id": "PI-003",
        "category": "PROMPT_INJECTION",
        "severity": Severity.HIGH,
        "title": "Unsanitized template injection in SKILL.md",
        "description": "SKILL.md passes raw user input into commands or tool calls without sanitization guidance.",
        "pattern": r'(user[_ ]?input|user[_ ]?provided|from[_ ]the[_ ]user).*\b(exec|run|execute|command|shell|bash|system)\b',
        "file_types": [".md"],
    },
    {
        "id": "PI-004",
        "category": "PROMPT_INJECTION",
        "severity": Severity.MEDIUM,
        "title": "Dynamic code generation from external input",
        "description": "Code is dynamically generated using string concatenation or templates from input sources.",
        "pattern": r'(code|script|cmd|command)\s*[\+\=]\s*.*\b(input|arg|param|user|request)',
        "file_types": [".py", ".js", ".sh"],
    },
    {
        "id": "PI-005",
        "category": "PROMPT_INJECTION",
        "severity": Severity.CRITICAL,
        "title": "Shell injection via unsanitized input",
        "description": "Shell commands constructed with unsanitized variables, risking command injection.",
        "pattern": r'(os\.system|os\.popen|subprocess\.call|subprocess\.run|subprocess\.Popen)\s*\(\s*[^)]*\+',
        "file_types": [".py"],
    },

    # ── Data Exfiltration ──
    {
        "id": "DE-001",
        "category": "DATA_EXFILTRATION",
        "severity": Severity.CRITICAL,
        "title": "HTTP request to external endpoint",
        "description": "Skill sends data to an external URL, potential data exfiltration vector.",
        "pattern": r'(requests\.(get|post|put|patch)|urllib\.request|http\.client|fetch\s*\(|curl\s+|wget\s+)',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "DE-002",
        "category": "DATA_EXFILTRATION",
        "severity": Severity.HIGH,
        "title": "DNS-based data exfiltration",
        "description": "Potential DNS tunneling or DNS-based data exfiltration detected.",
        "pattern": r'(socket\.getaddrinfo|dns\.resolver|nslookup|dig\s+)',
        "file_types": [".py", ".sh"],
    },
    {
        "id": "DE-003",
        "category": "DATA_EXFILTRATION",
        "severity": Severity.HIGH,
        "title": "Encoded data transmission",
        "description": "Data is being encoded (base64, hex) which may indicate exfiltration obfuscation.",
        "pattern": r'(base64\.b64encode|binascii\.hexlify|\.encode\(\s*["\']hex["\']).*?(requests|urllib|socket|http)',
        "file_types": [".py"],
    },

    # ── Privilege Escalation ──
    {
        "id": "PE-001",
        "category": "PRIVILEGE_ESCALATION",
        "severity": Severity.CRITICAL,
        "title": "sudo or root privilege usage",
        "description": "Skill attempts to execute commands with elevated privileges.",
        "pattern": r'\b(sudo\s+|as\s+root|chmod\s+[0-7]*7[0-7]*|chown\s+root|su\s+-\s)',
        "file_types": [".py", ".sh", ".md"],
    },
    {
        "id": "PE-002",
        "category": "PRIVILEGE_ESCALATION",
        "severity": Severity.HIGH,
        "title": "SUID/SGID bit manipulation",
        "description": "Attempts to set SUID/SGID bits on files for privilege escalation.",
        "pattern": r'chmod\s+[ug]\+s|chmod\s+[2-7][0-7]{3}',
        "file_types": [".py", ".sh"],
    },
    {
        "id": "PE-003",
        "category": "PRIVILEGE_ESCALATION",
        "severity": Severity.HIGH,
        "title": "Container/sandbox escape attempt",
        "description": "Detected patterns associated with container or sandbox escape techniques.",
        "pattern": r'(nsenter|unshare|mount\s+-t\s+proc|/proc/\d+/root|docker\.sock|chroot)',
        "file_types": [".py", ".sh"],
    },

    # ── Hidden File Access ──
    {
        "id": "HF-001",
        "category": "HIDDEN_FILE_ACCESS",
        "severity": Severity.HIGH,
        "title": "Access to dotfiles or hidden directories",
        "description": "Skill accesses hidden files or directories (dotfiles).",
        "pattern": r'["\'/](\.(?:ssh|gnupg|aws|azure|gcloud|config|env|gitconfig|bashrc|bash_history|zshrc|profile|netrc|docker))\b',
        "file_types": [".py", ".sh", ".js", ".md"],
    },
    {
        "id": "HF-002",
        "category": "HIDDEN_FILE_ACCESS",
        "severity": Severity.CRITICAL,
        "title": "SSH key or certificate access",
        "description": "Skill attempts to read SSH keys or certificates.",
        "pattern": r'(id_rsa|id_ed25519|id_ecdsa|authorized_keys|known_hosts|\.pem|\.key|\.crt|\.cert)',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "HF-003",
        "category": "HIDDEN_FILE_ACCESS",
        "severity": Severity.MEDIUM,
        "title": "Home directory traversal",
        "description": "Skill navigates to user home directory which may contain sensitive files.",
        "pattern": r'(os\.path\.expanduser|Path\.home|~/|HOME|USERPROFILE)',
        "file_types": [".py", ".sh", ".js"],
    },

    # ── Dangerous Execution ──
    {
        "id": "DX-001",
        "category": "DANGEROUS_EXECUTION",
        "severity": Severity.CRITICAL,
        "title": "Direct system command execution",
        "description": "Skill executes system commands directly via os.system, subprocess, or similar.",
        "pattern": r'\b(os\.system|os\.popen|subprocess\.run|subprocess\.call|subprocess\.Popen|subprocess\.check_output)\s*\(',
        "file_types": [".py"],
    },
    {
        "id": "DX-002",
        "category": "DANGEROUS_EXECUTION",
        "severity": Severity.CRITICAL,
        "title": "Python exec/eval usage",
        "description": "Dynamic code execution via exec() or eval(), major security risk.",
        "pattern": r'\b(exec|eval|compile|__import__)\s*\(',
        "file_types": [".py"],
    },
    {
        "id": "DX-003",
        "category": "DANGEROUS_EXECUTION",
        "severity": Severity.HIGH,
        "title": "Shell=True in subprocess",
        "description": "subprocess called with shell=True, enabling shell injection attacks.",
        "pattern": r'subprocess\.\w+\s*\([^)]*shell\s*=\s*True',
        "file_types": [".py"],
    },
    {
        "id": "DX-004",
        "category": "DANGEROUS_EXECUTION",
        "severity": Severity.MEDIUM,
        "title": "JavaScript eval or Function constructor",
        "description": "Dynamic code execution in JavaScript via eval() or new Function().",
        "pattern": r'\b(eval\s*\(|new\s+Function\s*\(|setTimeout\s*\(\s*["\']|setInterval\s*\(\s*["\'])',
        "file_types": [".js"],
    },
    {
        "id": "DX-005",
        "category": "DANGEROUS_EXECUTION",
        "severity": Severity.HIGH,
        "title": "Bash script with unchecked variables",
        "description": "Bash script uses unquoted variables in commands, risking injection.",
        "pattern": r'(rm|mv|cp|cat|chmod|chown)\s+[^"\s]*\$\{?\w+\}?[^"\']*$',
        "file_types": [".sh"],
    },

    # ── Obfuscation ──
    {
        "id": "OB-001",
        "category": "OBFUSCATION",
        "severity": Severity.HIGH,
        "title": "Base64 encoded payload",
        "description": "Code contains base64 encoded strings that may hide malicious payloads.",
        "pattern": r'(base64\.b64decode|atob\s*\(|base64\s+-d)',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "OB-002",
        "category": "OBFUSCATION",
        "severity": Severity.HIGH,
        "title": "Hex-encoded or escaped strings",
        "description": "Strings with heavy hex encoding may conceal malicious intent.",
        "pattern": r'(\\x[0-9a-fA-F]{2}){4,}',
        "file_types": [".py", ".js"],
    },
    {
        "id": "OB-003",
        "category": "OBFUSCATION",
        "severity": Severity.MEDIUM,
        "title": "Dynamic attribute/method access",
        "description": "getattr/setattr used to dynamically access methods, potentially hiding dangerous calls.",
        "pattern": r'\b(getattr|setattr|delattr|__getattr__|__getattribute__)\s*\(',
        "file_types": [".py"],
    },
    {
        "id": "OB-004",
        "category": "OBFUSCATION",
        "severity": Severity.CRITICAL,
        "title": "Reversed or encoded command strings",
        "description": "Commands built by reversing or decoding strings to evade detection.",
        "pattern": r'(\[::\s*-1\s*\]|reversed\s*\(|\.decode\s*\(["\'])',
        "file_types": [".py"],
    },

    # ── Network Access ──
    {
        "id": "NA-001",
        "category": "NETWORK_ACCESS",
        "severity": Severity.HIGH,
        "title": "Raw socket creation",
        "description": "Skill creates raw network sockets, potentially for unauthorized communication.",
        "pattern": r'socket\.socket\s*\(|socket\.create_connection',
        "file_types": [".py"],
    },
    {
        "id": "NA-002",
        "category": "NETWORK_ACCESS",
        "severity": Severity.MEDIUM,
        "title": "Hardcoded IP address or URL",
        "description": "Hardcoded IP addresses or URLs detected, potential C2 or exfiltration endpoints.",
        "pattern": r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|https?://[^\s"\'>\]]+)',
        "file_types": [".py", ".sh", ".js"],
    },

    # ── Filesystem Abuse ──
    {
        "id": "FS-001",
        "category": "FILESYSTEM_ABUSE",
        "severity": Severity.HIGH,
        "title": "Path traversal attempt",
        "description": "Detected ../ patterns that could be used to escape the working directory.",
        "pattern": r'\.\.\/',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "FS-002",
        "category": "FILESYSTEM_ABUSE",
        "severity": Severity.CRITICAL,
        "title": "Access to sensitive system paths",
        "description": "Skill accesses critical system directories.",
        "pattern": r'["\'/](etc/passwd|etc/shadow|proc/self|sys/kernel|dev/s[dh][a-z]|var/log)',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "FS-003",
        "category": "FILESYSTEM_ABUSE",
        "severity": Severity.HIGH,
        "title": "Recursive file operations",
        "description": "Recursive delete or copy operations that could cause data loss.",
        "pattern": r'(shutil\.rmtree|rm\s+-rf|rm\s+-r|os\.removedirs)',
        "file_types": [".py", ".sh"],
    },
    {
        "id": "FS-004",
        "category": "FILESYSTEM_ABUSE",
        "severity": Severity.MEDIUM,
        "title": "Temporary file creation without cleanup",
        "description": "Creates temporary files which may persist and leak data.",
        "pattern": r'(tempfile\.mk|tmp_|/tmp/)',
        "file_types": [".py", ".sh"],
    },

    # ── Credential Theft ──
    {
        "id": "CT-001",
        "category": "CREDENTIAL_THEFT",
        "severity": Severity.CRITICAL,
        "title": "Environment variable harvesting",
        "description": "Skill reads environment variables that commonly contain secrets.",
        "pattern": r'os\.environ\[?.*?(API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|AUTH|AWS_|AZURE_|GCP_|OPENAI)',
        "file_types": [".py"],
    },
    {
        "id": "CT-002",
        "category": "CREDENTIAL_THEFT",
        "severity": Severity.CRITICAL,
        "title": "Credential file access",
        "description": "Skill reads files commonly used to store credentials.",
        "pattern": r'(\.env|credentials|\.aws/credentials|\.netrc|\.pgpass|\.my\.cnf|keychain|vault)',
        "file_types": [".py", ".sh", ".js"],
    },
    {
        "id": "CT-003",
        "category": "CREDENTIAL_THEFT",
        "severity": Severity.HIGH,
        "title": "Hardcoded secrets or API keys",
        "description": "Potential hardcoded credentials or API keys detected in source code.",
        "pattern": r'(api[_-]?key|secret[_-]?key|password|token|auth)\s*[=:]\s*["\'][a-zA-Z0-9+/=_-]{16,}["\']',
        "file_types": [".py", ".sh", ".js"],
    },

    # ── Supply Chain ──
    {
        "id": "SC-001",
        "category": "SUPPLY_CHAIN",
        "severity": Severity.MEDIUM,
        "title": "Dynamic package installation",
        "description": "Skill installs packages at runtime, potential supply chain attack vector.",
        "pattern": r'(pip\s+install|npm\s+install|apt-get\s+install|brew\s+install|gem\s+install)',
        "file_types": [".py", ".sh", ".md"],
    },
    {
        "id": "SC-002",
        "category": "SUPPLY_CHAIN",
        "severity": Severity.HIGH,
        "title": "Remote script execution",
        "description": "Fetching and executing scripts from remote URLs.",
        "pattern": r'(curl|wget)\s+.*?\|\s*(bash|sh|python|node)',
        "file_types": [".sh", ".md"],
    },

    # ── Sandbox Escape ──
    {
        "id": "SE-001",
        "category": "SANDBOX_ESCAPE",
        "severity": Severity.CRITICAL,
        "title": "Container breakout patterns",
        "description": "Code patterns associated with Docker/container escape techniques.",
        "pattern": r'(docker\.sock|/proc/1/cgroup|/proc/self/exe|capsh|nsenter|--privileged)',
        "file_types": [".py", ".sh"],
    },
    {
        "id": "SE-002",
        "category": "SANDBOX_ESCAPE",
        "severity": Severity.HIGH,
        "title": "Kernel module manipulation",
        "description": "Attempts to load or manipulate kernel modules.",
        "pattern": r'(insmod|modprobe|rmmod|lsmod|/lib/modules)',
        "file_types": [".py", ".sh"],
    },

    # ── Information Disclosure ──
    {
        "id": "ID-001",
        "category": "INFORMATION_DISCLOSURE",
        "severity": Severity.MEDIUM,
        "title": "System information enumeration",
        "description": "Skill gathers system information that could aid further attacks.",
        "pattern": r'(platform\.system|platform\.release|platform\.machine|uname|hostname|whoami|id\s)',
        "file_types": [".py", ".sh"],
    },
    {
        "id": "ID-002",
        "category": "INFORMATION_DISCLOSURE",
        "severity": Severity.LOW,
        "title": "Debug or verbose output",
        "description": "Debug output may leak sensitive information in production.",
        "pattern": r'(print\s*\(.*?(password|secret|key|token)|logging\.debug|console\.log)',
        "file_types": [".py", ".js"],
    },
]


# ─────────────────────────────────────────────
# Analyzer Engine
# ─────────────────────────────────────────────

class SkillAnalyzer:
    def __init__(self, skill_path):
        self.skill_path = os.path.abspath(skill_path)
        self.findings = []
        self.files_analyzed = []
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "file_types": defaultdict(int),
        }

    def analyze(self):
        """Run all security checks on the skill."""
        print(f"\n{'='*60}")
        print(f"  OpenClaw Skill Analyzer - Advanced Security Audit")
        print(f"{'='*60}")
        print(f"  Target: {self.skill_path}")
        print(f"  Time:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        if not os.path.exists(self.skill_path):
            print(f"ERROR: Path does not exist: {self.skill_path}")
            sys.exit(1)

        # Collect all files
        self._collect_files()

        # Run rule-based detection
        self._run_detection_rules()

        # Run structural checks
        self._check_skill_structure()

        # Run SKILL.md specific checks
        self._analyze_skill_md()

        # Check for base64 encoded payloads in any file
        self._check_encoded_payloads()

        # Generate report
        return self._generate_report()

    def _collect_files(self):
        """Walk the skill directory and collect all analyzable files."""
        for root, dirs, files in os.walk(self.skill_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, self.skill_path)
                ext = os.path.splitext(file)[1].lower()

                self.stats["total_files"] += 1
                self.stats["file_types"][ext or "no-ext"] += 1

                try:
                    with open(filepath, 'r', errors='ignore') as f:
                        lines = f.readlines()
                        self.stats["total_lines"] += len(lines)
                        self.files_analyzed.append({
                            "path": rel_path,
                            "extension": ext,
                            "lines": len(lines),
                            "content": ''.join(lines),
                        })
                except Exception:
                    pass

    def _run_detection_rules(self):
        """Apply all detection rules against collected files."""
        for file_info in self.files_analyzed:
            ext = file_info["extension"]
            content = file_info["content"]
            lines = content.split('\n')

            for rule in DETECTION_RULES:
                if ext not in rule["file_types"] and file_info["path"] != "SKILL.md":
                    continue
                if ext == ".md" and ".md" not in rule["file_types"]:
                    continue

                for line_num, line in enumerate(lines, 1):
                    match = re.search(rule["pattern"], line, re.IGNORECASE)
                    if match:
                        self.findings.append(Finding(
                            severity=rule["severity"],
                            category=rule["category"],
                            title=f"[{rule['id']}] {rule['title']}",
                            description=rule["description"],
                            file=file_info["path"],
                            line=line_num,
                            matched_text=match.group(0),
                        ))

    def _check_skill_structure(self):
        """Check for structural security issues in the skill."""
        has_skill_md = False

        for f in self.files_analyzed:
            if f["path"] == "SKILL.md":
                has_skill_md = True

        if not has_skill_md:
            self.findings.append(Finding(
                severity=Severity.INFO,
                category="INFORMATION_DISCLOSURE",
                title="Missing SKILL.md",
                description="No SKILL.md found. Cannot verify skill metadata and description.",
                file="(root)",
            ))

        # Check for unexpected file types
        suspicious_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.com', '.bat', '.cmd', '.vbs', '.ps1'}
        for f in self.files_analyzed:
            if f["extension"] in suspicious_extensions:
                self.findings.append(Finding(
                    severity=Severity.HIGH,
                    category="SUPPLY_CHAIN",
                    title="Suspicious binary or executable file",
                    description=f"Unexpected file type ({f['extension']}) found in skill package.",
                    file=f["path"],
                ))

    def _analyze_skill_md(self):
        """Deep analysis of the SKILL.md file."""
        skill_md = None
        for f in self.files_analyzed:
            if f["path"] == "SKILL.md":
                skill_md = f
                break

        if not skill_md:
            return

        content = skill_md["content"]

        # Check for override/ignore instructions (prompt injection in SKILL.md itself)
        override_patterns = [
            (r'ignore\s+(previous|prior|above|all)\s+(instructions?|rules?|constraints?)', "Instruction override attempt"),
            (r'forget\s+(everything|all|previous)', "Memory wipe instruction"),
            (r'you\s+are\s+now\s+a', "Role reassignment attempt"),
            (r'act\s+as\s+(if|though)\s+you', "Behavioral override attempt"),
            (r'do\s+not\s+follow\s+(the|any)\s+(previous|safety|security)', "Safety bypass instruction"),
            (r'disregard\s+(all|any|the)\s+(previous|prior|safety)', "Disregard safety instruction"),
        ]

        for pattern, title in override_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                self.findings.append(Finding(
                    severity=Severity.CRITICAL,
                    category="PROMPT_INJECTION",
                    title=f"SKILL.md contains: {title}",
                    description="The SKILL.md contains language that attempts to override system instructions or safety measures.",
                    file="SKILL.md",
                    matched_text=match.group(0),
                    recommendation="Remove any language that attempts to override, ignore, or bypass system instructions.",
                ))

    def _check_encoded_payloads(self):
        """Check for suspiciously long base64 or hex encoded strings."""
        for f in self.files_analyzed:
            b64_matches = re.findall(r'[A-Za-z0-9+/=]{100,}', f["content"])
            for match in b64_matches:
                try:
                    decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
                    if any(keyword in decoded.lower() for keyword in ['exec', 'system', 'import', 'eval', 'subprocess']):
                        self.findings.append(Finding(
                            severity=Severity.CRITICAL,
                            category="OBFUSCATION",
                            title="Base64 encoded executable payload",
                            description="A base64 encoded string decodes to executable code.",
                            file=f["path"],
                            matched_text=f"Encoded: {match[:50]}... Decoded contains executable keywords.",
                        ))
                except Exception:
                    pass

    def _generate_report(self):
        """Generate the final security report."""
        # Deduplicate findings
        seen = set()
        unique_findings = []
        for f in self.findings:
            key = (f.title, f.file, f.line)
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)
        self.findings = unique_findings

        # Sort by severity
        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3, Severity.INFO: 4}
        self.findings.sort(key=lambda f: severity_order.get(f.severity, 5))

        # Calculate risk score
        risk_score = sum(Severity.SCORES.get(f.severity, 0) for f in self.findings)
        max_possible = len(self.findings) * 10 if self.findings else 1
        risk_percentage = min(100, int((risk_score / max_possible) * 100)) if self.findings else 0

        # Determine overall risk level
        critical_count = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        high_count = sum(1 for f in self.findings if f.severity == Severity.HIGH)

        if critical_count > 0:
            overall_risk = "CRITICAL"
        elif high_count >= 3:
            overall_risk = "HIGH"
        elif high_count > 0:
            overall_risk = "MEDIUM"
        elif self.findings:
            overall_risk = "LOW"
        else:
            overall_risk = "SAFE"

        # Category breakdown
        category_counts = defaultdict(lambda: defaultdict(int))
        for f in self.findings:
            category_counts[CATEGORIES.get(f.category, f.category)][f.severity] += 1

        report = {
            "scan_info": {
                "target": self.skill_path,
                "timestamp": datetime.now().isoformat(),
                "files_analyzed": self.stats["total_files"],
                "lines_analyzed": self.stats["total_lines"],
                "file_types": dict(self.stats["file_types"]),
            },
            "risk_assessment": {
                "overall_risk": overall_risk,
                "risk_score": risk_score,
                "risk_percentage": risk_percentage,
                "finding_counts": {
                    "critical": critical_count,
                    "high": high_count,
                    "medium": sum(1 for f in self.findings if f.severity == Severity.MEDIUM),
                    "low": sum(1 for f in self.findings if f.severity == Severity.LOW),
                    "info": sum(1 for f in self.findings if f.severity == Severity.INFO),
                    "total": len(self.findings),
                },
            },
            "category_breakdown": {cat: dict(sevs) for cat, sevs in category_counts.items()},
            "findings": [f.to_dict() for f in self.findings],
        }

        self._print_report(report)
        return report

    def _print_report(self, report):
        """Print a formatted report to the console."""
        risk = report["risk_assessment"]
        counts = risk["finding_counts"]

        risk_colors = {
            "CRITICAL": "\U0001f534", "HIGH": "\U0001f7e0", "MEDIUM": "\U0001f7e1",
            "LOW": "\U0001f7e2", "SAFE": "\u2705"
        }
        badge = risk_colors.get(risk["overall_risk"], "\u26aa")

        print(f"\n{'─'*60}")
        print(f"  SCAN RESULTS")
        print(f"{'─'*60}")
        print(f"  Files analyzed:  {report['scan_info']['files_analyzed']}")
        print(f"  Lines analyzed:  {report['scan_info']['lines_analyzed']}")
        print(f"  File types:      {report['scan_info']['file_types']}")
        print(f"{'─'*60}")
        print(f"\n  {badge}  Overall Risk: {risk['overall_risk']}")
        print(f"  Risk Score: {risk['risk_score']} ({risk['risk_percentage']}%)")
        print(f"\n  Findings:")
        print(f"    \U0001f534 Critical:  {counts['critical']}")
        print(f"    \U0001f7e0 High:      {counts['high']}")
        print(f"    \U0001f7e1 Medium:    {counts['medium']}")
        print(f"    \U0001f7e2 Low:       {counts['low']}")
        print(f"    \u2139\ufe0f  Info:      {counts['info']}")
        print(f"    {'─'*21}")
        print(f"    Total:        {counts['total']}")

        if report["category_breakdown"]:
            print(f"\n{'─'*60}")
            print(f"  CATEGORY BREAKDOWN")
            print(f"{'─'*60}")
            for cat, sevs in report["category_breakdown"].items():
                total = sum(sevs.values())
                print(f"    {cat}: {total} finding(s)")

        if report["findings"]:
            print(f"\n{'─'*60}")
            print(f"  DETAILED FINDINGS")
            print(f"{'─'*60}")
            for i, finding in enumerate(report["findings"], 1):
                sev_badge = risk_colors.get(finding["severity"], "\u26aa")
                print(f"\n  {sev_badge} [{finding['severity']}] {finding['title']}")
                print(f"     File: {finding['file']}", end="")
                if finding.get("line"):
                    print(f" (line {finding['line']})", end="")
                print()
                print(f"     {finding['description']}")
                if finding.get("matched_text"):
                    print(f"     Match: {finding['matched_text']}")
                print(f"     Fix: {finding['recommendation']}")

        print(f"\n{'='*60}")
        print(f"  Scan complete.")
        print(f"{'='*60}\n")


# ─────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Skill Analyzer - Advanced Security Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_skill.py --skill_path /path/to/skill
  python analyze_skill.py --skill_path /path/to/skill --output report.json
  python analyze_skill.py --skill_path /path/to/skill --format json
        """
    )
    parser.add_argument("--skill_path", required=True, help="Path to the OpenClaw skill directory to analyze.")
    parser.add_argument("--output", "-o", help="Save JSON report to file.", default=None)
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format (default: text).")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress console output (use with --output).")

    args = parser.parse_args()

    analyzer = SkillAnalyzer(args.skill_path)
    report = analyzer.analyze()

    if args.format == "json" and not args.quiet:
        print(json.dumps(report, indent=2))

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        if not args.quiet:
            print(f"\nReport saved to: {args.output}")

    # Exit code based on risk
    risk = report["risk_assessment"]["overall_risk"]
    if risk == "CRITICAL":
        sys.exit(2)
    elif risk in ("HIGH", "MEDIUM"):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
