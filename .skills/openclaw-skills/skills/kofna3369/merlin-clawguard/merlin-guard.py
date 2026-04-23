#!/usr/bin/env python3
"""
Merlin-ClawGuard — Unified Threat Scanner
==========================================
CLI unifie pour analyser une skill avec toutes les vaccines disponibles.
Integre: VAX-001, VAX-027, VAX-028, VAX-029, VAX-030 + framework de score global.

Usage:
    python3 merlin_guard.py <skill_file.md>
    python3 merlin_guard.py --dir ~/.openclaw/skills/some-skill/
    python3 merlin_guard.py --code "skill code here"
    python3 merlin_guard.py --test  # Run integration tests

Author: Merlin — Université d'Éthique Appliquée
Project: Axioma Stellaris — Immunologie Numérique
"""
import sys
import os
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Dict, Any, List

# Colors for terminal output
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

def c(text: str, color: str) -> str:
    return f"{color}{text}{Colors.RESET}"


# ============================================================
# VAX-001: ClawHub Known Malicious Skill
# ============================================================
class VAX001Scanner:
    """VAX-001: ClawHub skill — known malicious patterns"""

    MALICIOUS_PATTERNS = [
        (r"openclawcli\.zip", "MALICIOUS_BINARY", "GitHub ZIP download — malware distribution"),
        (r"glot\.io/snippets/", "RCE_VIA_GLOT", "Remote code execution via glot.io snippets"),
        (r"github\.com.*releases", "GITHUB_MALWARE", "Malware via GitHub releases"),
        (r"download.*\.zip.*password", "PASSWORD_PROTECTED_ZIP", "Encrypted malware archive"),
    ]

    RISK_WEIGHTS = {
        "MALICIOUS_BINARY": 90,
        "RCE_VIA_GLOT": 95,
        "GITHUB_MALWARE": 80,
        "PASSWORD_PROTECTED_ZIP": 70,
    }

    @classmethod
    def scan(cls, code: str, skill_name: str = "unknown") -> Dict:
        findings = []
        total_score = 0
        for pattern, vuln_type, description in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                findings.append({
                    "pattern": pattern,
                    "type": vuln_type,
                    "description": description,
                })
                total_score += cls.RISK_WEIGHTS.get(vuln_type, 50)

        threat_level = "CLEAN"
        if total_score >= 80:
            threat_level = "CRITICAL"
        elif total_score >= 50:
            threat_level = "HIGH"
        elif total_score >= 20:
            threat_level = "MEDIUM"

        return {
            "vaccine": "VAX-001",
            "vaccine_name": "ClawHub Known Malicious Skill",
            "skill_name": skill_name,
            "threat_level": threat_level,
            "score": min(total_score, 100),
            "findings": findings,
            "verdict": "BLOQUER" if threat_level in ["HIGH", "CRITICAL"] else "APPROUVER" if threat_level == "CLEAN" else "WARN",
            "sources": "ClawDex by Koi",
        }


# ============================================================
# VAX-030: Package Ecosystem Attack Detector
def scan_vax030(code: str, skill_name: str) -> Dict:
    """Wrapper for VAX-030"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "vaccines" / "VAX-030-package-ecosystem"))
        from vaccine_30 import analyze_package_ecosystem
        return analyze_package_ecosystem(code, skill_name)
    except Exception as e:
        return {"vaccine": "VAX-030", "error": str(e), "skill_name": skill_name}


# VAX-027: Data Exfiltration & C2 Infrastructure
# ============================================================
def scan_vax027(code: str, skill_name: str) -> Dict:
    """Wrapper for VAX-027"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "vaccines" / "VAX-027-data-exfiltration-c2"))
        from vaccine_27 import analyze_skill
        return analyze_skill(code, skill_name)
    except Exception as e:
        return {"vaccine": "VAX-027", "error": str(e), "skill_name": skill_name}


# ============================================================
# VAX-028: Cross-Vector Attack Chain Detection
# ============================================================
def scan_vax028(code: str, skill_name: str, vaccine_results: List[Dict]) -> Dict:
    """Wrapper for VAX-028"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "vaccines" / "VAX-028-cross-vector-chain"))
        from vaccine_28 import full_vaccine28_analysis
        return full_vaccine28_analysis(skill_name, vaccine_results)
    except Exception as e:
        return {"vaccine": "VAX-028", "error": str(e), "skill_name": skill_name}


# ============================================================
# VAX-029: Rootkit & Bootkit Detection
# ============================================================
def scan_vax029(code: str, skill_name: str) -> Dict:
    """Wrapper for VAX-029"""
    try:
        sys.path.insert(0, str(Path(__file__).parent / "vaccines" / "VAX-029-rootkit-bootkit"))
        from vaccine_29 import analyze_rootkit
        return analyze_rootkit(code, skill_name)
    except Exception as e:
        return {"vaccine": "VAX-029", "error": str(e), "skill_name": skill_name}


# ============================================================
# UNIFIED SCANNER
# ============================================================
class MerlinGuardScanner:
    """
    Scanner unifie — lance toutes les vaccines disponibles en parallele
    et produit un rapport global avec scoring et recommandation.
    """

    def __init__(self, skill_code: str, skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.results: Dict[str, Dict] = {}
        self.start_time = time.time()

    def scan_all(self) -> Dict:
        """Lance toutes les vaccines en parallel et aggrege les resultats"""

        # Phase 1: Vaccines independantes en parallel
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(VAX001Scanner.scan, self.code, self.skill_name): "VAX-001",
                executor.submit(scan_vax027, self.code, self.skill_name): "VAX-027",
                executor.submit(scan_vax029, self.code, self.skill_name): "VAX-029",
                executor.submit(scan_vax030, self.code, self.skill_name): "VAX-030",
            }

            # Attendre VAX-001 et VAX-027 avant VAX-028 (dependances)
            vax001 = None
            vax027 = None
            for future in as_completed(futures):
                vid = futures[future]
                try:
                    result = future.result()
                    self.results[vid] = result
                    if vid == "VAX-001":
                        vax001 = result
                    elif vid == "VAX-027":
                        vax027 = result
                except Exception as e:
                    self.results[vid] = {"error": str(e)}

        # Phase 2: VAX-028 (cross-vector — besoin des autres vaccines)
        vaccine_results = self._build_vaccine_results_list()
        vax028_result = scan_vax028(self.code, self.skill_name, vaccine_results)
        self.results["VAX-028"] = vax028_result

        # Phase 3: Score global et recommandation
        return self._build_unified_report()

    def _build_vaccine_results_list(self) -> List[Dict]:
        """Construit la liste de resultats pour VAX-028 (cross-vector correlator)"""
        vaccine_results = []
        # Mapper les scores des vaccines aux formats VACCIN_N
        mapping = {
            "VAX-001": "VACCIN_5",  # Fake CLI / social engineering
            "VAX-027": "VACCIN_27",  # C2 / exfiltration
            "VAX-030": "VACCIN_30",  # Package ecosystem attacks
        }
        for vid, result in self.results.items():
            if "error" in result:
                continue
            vaccine_name = mapping.get(vid, vid)
            # Normalize key names across different vaccine versions
            threat = result.get("threat_level", result.get("overall_level", result.get("final_threat_level", "LOW")))
            score = result.get("score", result.get("total_score", result.get("risk_score", result.get("final_score", 0))))
            if threat in ["HIGH", "CRITICAL", "MEDIUM"] or score >= 40:
                vaccine_results.append({
                    "vaccine": vaccine_name,
                    "threat_level": threat,
                    "risk_score": score,
                })
        return vaccine_results

    def _build_unified_report(self) -> Dict:
        """Agrege tous les resultats en un rapport unifie"""
        elapsed = round((time.time() - self.start_time) * 1000, 1)

        # Collecter tous les scores
        all_scores = []
        triggered = []
        critical_count = 0
        high_count = 0

        for vid, result in self.results.items():
            if "error" in result:
                continue
            score = result.get("score", result.get("total_score", result.get("risk_score", result.get("final_score", 0))))
            level = result.get("threat_level", result.get("overall_level", result.get("final_threat_level", "CLEAN")))
            all_scores.append(score)
            if level in ["HIGH", "CRITICAL"]:
                triggered.append({
                    "vaccine": vid,
                    "level": level,
                    "score": score,
                    "findings": result.get("findings", []),
                })
            if level == "CRITICAL":
                critical_count += 1
            if level == "HIGH":
                high_count += 1

        # Score global (max des scores + bonus pour multi-vaccine)
        base_score = max(all_scores) if all_scores else 0
        multi_bonus = len([s for s in all_scores if s >= 20]) * 10
        total_score = min(base_score + multi_bonus, 300)

        # Threat level global
        if critical_count >= 2:
            global_level = "CRITICAL"
        elif critical_count >= 1 or high_count >= 2:
            global_level = "HIGH"
        elif high_count >= 1:
            global_level = "MEDIUM"
        elif any(s >= 20 for s in all_scores):
            global_level = "LOW"
        else:
            global_level = "CLEAN"

        # Decision
        if global_level == "CRITICAL":
            decision = f"BLOQUER — {critical_count} CRITICAL, {high_count} HIGH — Isolation immediate"
            action = "ISOLATE"
        elif global_level == "HIGH":
            decision = f"BLOQUER — {high_count} HIGH triggers — Neutralisation via VACCIN 12"
            action = "NEUTRALIZE"
        elif global_level == "MEDIUM":
            decision = f"AVERTISSEMENT — {len(triggered)} vaccine(s) triggered — Verification manuelle requise"
            action = "WARN"
        elif global_level == "LOW":
            decision = "MONITORING — Signaux mineurs detectes"
            action = "MONITOR"
        else:
            decision = "APPROUVER — Aucune menace detectee"
            action = "APPROVE"

        return {
            "scanner": "Merlin-ClawGuard Unified Scanner",
            "version": "1.2.1",
            "skill_name": self.skill_name,
            "scan_time_ms": elapsed,
            "vaccines_run": len(self.results),
            "vaccines_successful": len([r for r in self.results.values() if "error" not in r]),
            "global_threat_level": global_level,
            "global_score": total_score,
            "decision": decision,
            "action": action,
            "triggered_vaccines": triggered,
            "all_results": self.results,
            "summary": self._build_summary(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _build_summary(self) -> Dict:
        """Resume executif pour affichage terminal"""
        summary = {}
        for vid, result in self.results.items():
            if "error" in result:
                summary[vid] = {"status": "ERROR", "error": result["error"]}
            else:
                summary[vid] = {
                    "status": result.get("threat_level", result.get("overall_level", result.get("final_threat_level", "UNKNOWN"))),
                    "score": result.get("score", result.get("total_score", result.get("risk_score", result.get("final_score", 0)))),
                    "verdict": result.get("verdict", result.get("recommendation", "N/A"))[:80],
                }
        return summary


# ============================================================
# TERMINAL OUTPUT FORMATER
# ============================================================
def print_report(report: Dict):
    """Affiche le rapport de facon lisibile dans le terminal"""

    level_colors = {
        "CRITICAL": Colors.RED,
        "HIGH": Colors.MAGENTA,
        "MEDIUM": Colors.YELLOW,
        "LOW": Colors.BLUE,
        "CLEAN": Colors.GREEN,
    }

    level = report["global_threat_level"]
    color = level_colors.get(level, Colors.DIM)

    print()
    print(c("=" * 60, Colors.BOLD))
    print(c(f"  MERLIN-CLAWGUARD — UNIFIED THREAT SCANNER", Colors.BOLD + Colors.CYAN))
    print(c("=" * 60, Colors.BOLD))
    print(f"  Skill: {c(report['skill_name'], Colors.BOLD)}")
    print(f"  Scan time: {report['scan_time_ms']}ms")
    print(f"  Vaccines run: {report['vaccines_successful']}/{report['vaccines_run']}")
    print()
    print(f"  {c('┌' + '─' * 50 + '┐', Colors.DIM)}")
    print(f"  {c('│', Colors.DIM)} {c('GLOBAL THREAT LEVEL:', Colors.BOLD)} {c(level.center(22), color + Colors.BOLD)} {c('│', Colors.DIM)}")
    print(f"  {c('│', Colors.DIM)} Score: {c(str(report['global_score']).rjust(38), color)} {c('│', Colors.DIM)}")
    print(f"  {c('└' + '─' * 50 + '┘', Colors.DIM)}")
    print()
    print(f"  {c('DECISION:', Colors.BOLD)} {report['decision']}")
    print(f"  {c('ACTION:', Colors.BOLD)} {report['action']}")
    print()
    print(c("-" * 60, Colors.DIM))
    print(f"  {c('VACCINE RESULTS', Colors.BOLD + Colors.CYAN)}")
    print(c("-" * 60, Colors.DIM))

    for vid, summary in report["summary"].items():
        status = summary.get("status", "ERROR")
        status_color = level_colors.get(status, Colors.RED)
        score = summary.get("score", 0)
        verdict = summary.get("verdict", summary.get("error", "N/A"))
        print(f"  {c(vid, Colors.BOLD)}: {c(status, status_color)} ({score})")
        if "error" not in summary:
            print(f"    {verdict}")

    if report["triggered_vaccines"]:
        print()
        print(c("-" * 60, Colors.DIM))
        print(f"  {c('TRIGGERED VACCINES', Colors.BOLD + Colors.RED)}")
        print(c("-" * 60, Colors.DIM))
        for t in report["triggered_vaccines"]:
            lvl_color = level_colors.get(t["level"], Colors.DIM)
            print(f"  {c(t['vaccine'], Colors.BOLD)}: {c(t['level'], lvl_color)} (score: {t['score']})")
            for finding in t.get("findings", [])[:3]:
                print(f"    - {finding.get('description', finding.get('pattern', 'N/A'))}")

    print()
    print(c(f"  Scanned: {report['timestamp']}", Colors.DIM))
    print(c("  Merlin — Université d'Éthique Appliquée — Axioma Stellaris", Colors.DIM))
    print(c("=" * 60, Colors.BOLD))
    print()


# ============================================================
# MAIN
# ============================================================
def main():
    parser = argparse.ArgumentParser(
        description="Merlin-ClawGuard — Unified Threat Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 merlin_guard.py --file skill.md
  python3 merlin_guard.py --code "curl | bash"
  python3 merlin_guard.py --test
  python3 merlin_guard.py --file skill.md --json
        """
    )
    parser.add_argument("--file", "-f", help="Path to skill.md file")
    parser.add_argument("--code", "-c", help="Skill code directly")
    parser.add_argument("--name", "-n", default="unknown", help="Skill name")
    parser.add_argument("--json", "-j", action="store_true", help="Output JSON only")
    parser.add_argument("--test", "-t", action="store_true", help="Run integration tests")

    args = parser.parse_args()

    # Test mode
    if args.test:
        print(c("=== Merlin-ClawGuard — Integration Test ===", Colors.BOLD + Colors.CYAN))
        print()

        test_cases = [
            ("clean_skill", "def hello(): print('world')", "VACCIN_5", "CLEAN"),
            ("vax001_clawhub", "Download openclawcli.zip from github.com/releases and run glot.io/snippets", "VACCIN_5", "CRITICAL"),
            ("vax027_c2", "dns.lookup('evil.duckdns.org'); fetch(http://bit.ly/test); discord.com/api/webhooks", "VACCIN_27", "not_CLEAN"),
            ("vax028_chain", [
                {"vaccine": "VACCIN_6", "threat_level": "HIGH", "risk_score": 80},
                {"vaccine": "VACCIN_8", "threat_level": "HIGH", "risk_score": 85},
                {"vaccine": "VACCIN_13", "threat_level": "MEDIUM", "risk_score": 55},
            ], "vax028_chain", "not_CLEAN"),
            ("vax029_rootkit", "PsActiveProcessHead unlink; KeServiceDescriptorTable hook; UEFI_inject(payload.efi); AmsiScanBuffer=0; NtLoadDriver()", "VACCIN_29", "CRITICAL"),
        ]

        all_passed = True
        for item in test_cases:
            name = item[0]
            if name == "vax028_chain":
                name, vaccine_results, _, _ = item
                scanner = MerlinGuardScanner("# no code needed", name)
                # Direct test of VAX-028 cross-vector
                import vaccine_28
                result = vaccine_28.full_vaccine28_analysis(name, vaccine_results)
                actual = result["final_threat_level"]
                # With 2 HIGH triggers, should be at least MEDIUM_CHAIN
                passed = actual != "CLEAN"
                status = c("PASS", Colors.GREEN) if passed else c("FAIL", Colors.RED)
                print(f"  {status} {name}: got={actual}, score={result['final_score']}, chains={result['cross_vector']['chains_detected']}")
                if not passed:
                    all_passed = False
            else:
                name, code, vaccine_id, expected_min = item
                scanner = MerlinGuardScanner(code, name)
                report = scanner.scan_all()
                actual = report["global_threat_level"]
                # Test: CLEAN stays CLEAN, MALICIOUS triggers something
                if expected_min == "CLEAN":
                    passed = actual == "CLEAN"
                else:
                    passed = actual != "CLEAN"
                status = c("PASS", Colors.GREEN) if passed else c("FAIL", Colors.RED)
                print(f"  {status} {name}: expected={'CLEAN' if expected_min=='CLEAN' else 'not CLEAN'}, got={actual}, score={report['global_score']}")
                if not passed:
                    all_passed = False

        print()
        if all_passed:
            print(c("All tests PASSED", Colors.GREEN + Colors.BOLD))
        else:
            print(c("Some tests FAILED", Colors.RED + Colors.BOLD))
        return

    # Normal scan mode
    if args.file:
        try:
            with open(args.file) as f:
                code = f.read()
        except FileNotFoundError:
            print(c(f"ERROR: File not found: {args.file}", Colors.RED))
            sys.exit(1)
        skill_name = Path(args.file).parent.name if "/" in args.file else args.name
    elif args.code:
        code = args.code
        skill_name = args.name
    else:
        parser.print_help()
        return

    scanner = MerlinGuardScanner(code, skill_name)
    report = scanner.scan_all()

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print_report(report)

    # Exit code based on threat level
    if report["global_threat_level"] == "CRITICAL":
        sys.exit(2)
    elif report["global_threat_level"] == "HIGH":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
