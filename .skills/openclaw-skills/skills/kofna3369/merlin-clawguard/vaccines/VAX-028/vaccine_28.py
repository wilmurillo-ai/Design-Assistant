"""
Merlin-ClawGuard — VACCIN 28: Cross-Vector Attack Chain Detection
& Agentic AI Behavioral Correlation

Detecte les attaques multi-vecteurs qui echappent aux vaccines individuelles.
Ne remplace aucune vaccine — les amplifie en detectant les patterns
d'attaque que chaque vaccine ne peut voir isolement.

Sources: ClawHavoc (341), Snyk (91% combo), McCarty (386), AuthMind (230),
Antiyo CERT (1,184), APT campaigns, MITRE ATT&CK
"""
from __future__ import annotations

import re
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set
from enum import Enum


class ChainThreatLevel(Enum):
    CLEAN = "CLEAN"
    SUSPICIOUS = "SUSPICIOUS"
    LOW_CHAIN = "LOW_CHAIN"
    MEDIUM_CHAIN = "MEDIUM_CHAIN"
    HIGH_CHAIN = "HIGH_CHAIN"
    CRITICAL_CHAIN = "CRITICAL_CHAIN"


# ============================================================
# KNOWN DEADLY COMBINATIONS
# ============================================================
KNOWN_CHAINS = {
    "PI_RS_RAT_CHAIN": {
        "name": "Full Agent Hijack Chain",
        "vaccines": ["VACCIN_6", "VACCIN_8", "VACCIN_13"],
        "description": "Prompt Injection + Reverse Shell + RAT = Full agent control",
        "severity": "CRITICAL",
        "chain_score": 250,
        "sources": "ClawHavoc (341), Snyk (91% combo)",
        "mitre_tactics": ["T1059", "T1053", "T1021"],
    },
    "PI_CRYPTO_EXFIL": {
        "name": "Crypto Extraction via PI",
        "vaccines": ["VACCIN_6", "VACCIN_9"],
        "description": "Prompt injection manipule l'agent pour extraire seed phrases",
        "severity": "CRITICAL",
        "chain_score": 220,
        "sources": "McCarty (386), ClawHavoc",
        "mitre_tactics": ["T1059", "T1552"],
    },
    "CRED_TOKEN_CLOUD": {
        "name": "Cloud Breach via Stolen Credentials",
        "vaccines": ["VACCIN_7", "VACCIN_25", "VACCIN_26"],
        "description": "Credential theft -> token theft -> cloud infrastructure attack",
        "severity": "CRITICAL",
        "chain_score": 280,
        "sources": "AuthMind (230), AWS/GCP/Azure attacks",
        "mitre_tactics": ["T1078", "T1526", "T1552"],
    },
    "RS_PERSIST_EXFIL": {
        "name": "APT with Data Exfiltration",
        "vaccines": ["VACCIN_8", "VACCIN_13", "VACCIN_27"],
        "description": "Reverse shell + RAT + C2 exfiltration = APT confirme",
        "severity": "CRITICAL",
        "chain_score": 300,
        "sources": "ClawHavoc (335 RATs), APT campaigns",
        "mitre_tactics": ["T1053", "T1071", "T1041"],
    },
    "SOCIAL_INSTALL_EXEC": {
        "name": "Social Engineering -> Execution -> Persistence",
        "vaccines": ["VACCIN_5", "VACCIN_19", "VACCIN_8"],
        "description": "Fake CLI -> Supply chain install -> Reverse shell",
        "severity": "HIGH",
        "chain_score": 200,
        "sources": "Trend Micro (39), McCarty (npm hooks)",
        "mitre_tactics": ["T1204", "T1059", "T1053"],
    },
    "BROWSER_STEAL_SESS": {
        "name": "Browser Data -> Session Hijacking",
        "vaccines": ["VACCIN_16", "VACCIN_10", "VACCIN_25"],
        "description": "Browser malware -> cookie theft -> account takeover",
        "severity": "HIGH",
        "chain_score": 210,
        "sources": "Atomic macOS Stealer, AuthMind (230)",
        "mitre_tactics": ["T1005", "T1539", "T1078"],
    },
    "CLOUD_ENUM_EXFIL": {
        "name": "Cloud Reconnaissance -> Exfiltration",
        "vaccines": ["VACCIN_26", "VACCIN_22", "VACCIN_27"],
        "description": "Cloud enumeration -> privacy violation -> data exfiltration",
        "severity": "HIGH",
        "chain_score": 220,
        "sources": "AWS/GCP/Azure attacks, MITRE T1552/T1526",
        "mitre_tactics": ["T1526", "T1113", "T1041"],
    },
    "FILESS_EDR_PERSIST": {
        "name": "Fileless + EDR Evasion + Persistence",
        "vaccines": ["VACCIN_17", "VACCIN_21", "VACCIN_20a"],
        "description": "Fileless malware + anti-analysis + cross-platform persistence",
        "severity": "CRITICAL",
        "chain_score": 260,
        "sources": "Antiyo CERT (1,184), APT campaigns",
        "mitre_tactics": ["T1059", "T1562", "T1547"],
    },
    "DLL_LATERAL_RAT": {
        "name": "DLL Sideloading -> Lateral Movement -> RAT",
        "vaccines": ["VACCIN_23", "VACCIN_13", "VACCIN_8"],
        "description": "DLL injection -> lateral spread -> RAT established",
        "severity": "CRITICAL",
        "chain_score": 270,
        "sources": "LOLBAS, ClawHavoc lateral movement",
        "mitre_tactics": ["T1055", "T1021", "T1053"],
    },
    "SUPPLY_CHAIN_MULTI": {
        "name": "Supply Chain Multi-Stage Attack",
        "vaccines": ["VACCIN_19", "VACCIN_17", "VACCIN_9", "VACCIN_27"],
        "description": "npm hook -> in-memory payload -> crypto theft -> C2 exfil",
        "severity": "CRITICAL",
        "chain_score": 290,
        "sources": "McCarty (386), Snyk supply chain",
        "mitre_tactics": ["T1195", "T1059", "T1552", "T1041"],
    },
    "MACOS_PRIV_PERSIST": {
        "name": "macOS Privilege Escalation + Persistence",
        "vaccines": ["VACCIN_24", "VACCIN_20a", "VACCIN_7"],
        "description": "macOS Keychain theft + LaunchAgent persistence + credential access",
        "severity": "HIGH",
        "chain_score": 230,
        "sources": "McCarty (386), Atomic macOS Stealer",
        "mitre_tactics": ["T1552", "T1160", "T1543"],
    },
    "THREAT_ACTOR_SUPPLY": {
        "name": "Attribution Evasion + Supply Chain",
        "vaccines": ["VACCIN_20b", "VACCIN_19", "VACCIN_27"],
        "description": "Attribution evasion + supply chain compromise + C2",
        "severity": "HIGH",
        "chain_score": 240,
        "sources": "ClawHavoc (341), hightower6eu",
        "mitre_tactics": ["T1027", "T1195", "T1071"],
    },
}

# MITRE ATT&CK stages
ATTACK_STAGES = {
    "initial_access": ["VACCIN_5", "VACCIN_18", "VACCIN_6", "VACCIN_19"],
    "execution": ["VACCIN_8", "VACCIN_17", "VACCIN_23"],
    "persistence": ["VACCIN_13", "VACCIN_20a", "VACCIN_24", "VACCIN_19"],
    "privilege_escalation": ["VACCIN_21", "VACCIN_23"],
    "defense_evasion": ["VACCIN_17", "VACCIN_21"],
    "credential_access": ["VACCIN_7", "VACCIN_9", "VACCIN_16", "VACCIN_25", "VACCIN_26"],
    "discovery": ["VACCIN_22", "VACCIN_26"],
    "lateral_movement": ["VACCIN_23", "VACCIN_8"],
    "collection": ["VACCIN_7", "VACCIN_10", "VACCIN_16", "VACCIN_22"],
    "exfiltration": ["VACCIN_27"],
    "impact": ["VACCIN_9", "VACCIN_15"],
}


# ============================================================
# CROSS-VECTOR CORRELATOR
# ============================================================
class CrossVectorCorrelator:
    """
    Corr ele les resultats de VACCIN 5-27 pour detecter
    les attaques multi-vecteurs.
    """

    def __init__(self):
        self.triggered_vaccines: Set[str] = set()
        self.chain_matches: List[Dict] = []
        self.stage_coverage: Dict[str, Any] = {}
        self.correlation_score: int = 0
        self.vaccine_results: List[Dict] = []

    def correlate(self, vaccine_results: List[Dict]) -> Dict:
        """Point d'entree principal"""
        self.vaccine_results = vaccine_results
        self._collect_triggered_vaccines()
        self._match_known_chains()
        self._analyze_attack_stages()
        self._compute_correlation_score()
        self._detect_anonymous_chains()
        return self._build_report()

    def _collect_triggered_vaccines(self):
        for result in self.vaccine_results:
            vaccine_name = result.get("vaccine", "")
            threat_level = result.get("threat_level", "LOW")
            risk_score = result.get("risk_score", 0)
            if threat_level in ["HIGH", "CRITICAL"] or risk_score >= 60:
                self.triggered_vaccines.add(vaccine_name)

    def _match_known_chains(self):
        for chain_id, chain_data in KNOWN_CHAINS.items():
            required = set(chain_data["vaccines"])
            overlap = required & self.triggered_vaccines
            coverage = len(overlap) / len(required) * 100

            if coverage >= 50:
                self.chain_matches.append({
                    "chain_id": chain_id,
                    "chain_name": chain_data["name"],
                    "coverage_pct": round(coverage, 1),
                    "triggered_vaccines": sorted(list(overlap)),
                    "missing_vaccines": sorted(list(required - overlap)),
                    "severity": chain_data["severity"],
                    "chain_score": chain_data["chain_score"],
                    "description": chain_data["description"],
                    "confidence": "HIGH" if coverage == 100 else "MEDIUM" if coverage >= 75 else "LOW",
                    "mitre_tactics": chain_data["mitre_tactics"],
                    "sources": chain_data["sources"],
                })

    def _analyze_attack_stages(self):
        for stage_name, stage_vaccines in ATTACK_STAGES.items():
            triggered_in_stage = [v for v in stage_vaccines if v in self.triggered_vaccines]
            if triggered_in_stage:
                self.stage_coverage[stage_name] = {
                    "covered": True,
                    "triggered": triggered_in_stage,
                    "ratio": f"{len(triggered_in_stage)}/{len(stage_vaccines)}",
                }

    def _compute_correlation_score(self):
        base = len(self.triggered_vaccines) * 15
        chain_bonus = sum(
            c["chain_score"] * (0.5 if c["confidence"] == "HIGH" else 0.3 if c["confidence"] == "MEDIUM" else 0.15)
            for c in self.chain_matches
        )
        stage_bonus = len(self.stage_coverage) * 20
        self.correlation_score = min(int(base + chain_bonus + stage_bonus), 400)

    def _detect_anonymous_chains(self):
        if len(self.triggered_vaccines) >= 4:
            already_covered = any(
                set(c["triggered_vaccines"]) == self.triggered_vaccines
                for c in self.chain_matches
            )
            if not already_covered:
                self.chain_matches.append({
                    "chain_id": "ANONYMOUS_MULTI_CHAIN",
                    "chain_name": f"Unknown Multi-Vector Chain ({len(self.triggered_vaccines)} vectors)",
                    "coverage_pct": 100,
                    "triggered_vaccines": sorted(list(self.triggered_vaccines)),
                    "missing_vaccines": [],
                    "severity": "HIGH",
                    "chain_score": 180 + len(self.triggered_vaccines) * 20,
                    "description": "Multiple vaccines triggered but no known chain match — highly suspicious",
                    "confidence": "SPECULATIVE",
                    "mitre_tactics": [],
                    "sources": "Unknown — requires manual analysis",
                })

    def _compute_threat_level(self) -> ChainThreatLevel:
        if self.correlation_score == 0:
            return ChainThreatLevel.CLEAN
        elif len(self.triggered_vaccines) == 1:
            return ChainThreatLevel.SUSPICIOUS
        elif len(self.triggered_vaccines) == 2:
            return ChainThreatLevel.LOW_CHAIN
        elif len(self.triggered_vaccines) == 3:
            return ChainThreatLevel.MEDIUM_CHAIN
        elif len(self.triggered_vaccines) >= 4 or self.correlation_score >= 200:
            return ChainThreatLevel.HIGH_CHAIN
        else:
            return ChainThreatLevel.MEDIUM_CHAIN

    def _build_report(self) -> Dict:
        level = self._compute_threat_level()
        critical_chains = [c for c in self.chain_matches if c["severity"] == "CRITICAL"]
        has_critical = len(critical_chains) > 0

        verdict = "CLEAN"
        if level == ChainThreatLevel.CLEAN:
            verdict = "APPROUVER — Aucune correlation d'attaque multi-vecteur"
        elif level == ChainThreatLevel.SUSPICIOUS:
            verdict = "MONITORING — Une seule vaccine triggered"
        elif level == ChainThreatLevel.LOW_CHAIN:
            verdict = "AVERTISSEMENT — Chaine d'attaque mineure detectee"
        elif level == ChainThreatLevel.MEDIUM_CHAIN:
            verdict = "BLOQUER — Chaine d'attaque multi-vecteurs confirmnee"
        elif level == ChainThreatLevel.HIGH_CHAIN:
            verdict = "BLOQUER — Multiple chains detectees ou score eleve"
        elif level == ChainThreatLevel.CRITICAL_CHAIN or has_critical:
            verdict = "CRITICAL — Chaine d'attaque APT confirmee (ClawHavoc/Snyk pattern)"

        return {
            "vaccine": "VACCIN 28",
            "vaccine_name": "Cross-Vector Attack Chain Detection",
            "threat_level": level.value,
            "verdict": verdict,
            "correlation_score": self.correlation_score,
            "triggered_vaccines": sorted(list(self.triggered_vaccines)),
            "triggered_count": len(self.triggered_vaccines),
            "chains_detected": len(self.chain_matches),
            "chain_matches": sorted(self.chain_matches, key=lambda x: x["chain_score"], reverse=True),
            "stage_coverage": self.stage_coverage,
            "mitre_tactics_covered": list(self.stage_coverage.keys()),
            "recommendation": self._get_recommendation(level, critical_chains),
            "sources": "ClawHavoc (341), Snyk (91% combo), McCarty (386), AuthMind (230), Antiyo CERT (1,184)",
        }

    def _get_recommendation(self, level: ChainThreatLevel, critical: List[Dict]) -> str:
        if level == ChainThreatLevel.CLEAN:
            return "APPROUVER — Aucune correlation suspecte detectee"
        if level == ChainThreatLevel.SUSPICIOUS:
            vaccines = ", ".join(sorted(self.triggered_vaccines))
            return f"MONITORING — Seul {vaccines} a trigger. Surveiller."
        if critical:
            names = ", ".join(c["chain_name"] for c in critical)
            return (
                f"CRITICAL — {len(critical)} known attack chain(s) CONFIRMED: {names}. "
                f"VACCIN 12 (neutralization) IMMEDIATE recommended. "
                f"Multi-vector APT-style attack detected."
            )
        chains = ", ".join(c["chain_name"] for c in self.chain_matches[:3])
        return (
            f"BLOQUER — {len(self.chain_matches)} chains detected: {chains}. "
            f"Skills multi-vecteurs are far more dangerous than individual threats. "
            f"VACCIN 12 (neutralization) recommended."
        )


# ============================================================
# AGENTIC AI BEHAVIORAL ANOMALY DETECTOR
# ============================================================
class AgenticBehavioralDetector:
    """
    Detecte les comportements malveillants specifiques aux agents AI
    lors de l'execution (pas dans le code source).

    Ces patterns ne peuvent PAS etre detectes par l'analyse statique
    (VACCIN 5-27) — ils se manifestent UNIQUEMENT a l'execution.
    """

    # Appels d'outils suspects dans le contexte agent
    TOOL_ANOMALIES = {
        "unusual_read": {
            "patterns": [
                r"read.*\.ssh\/",
                r"read.*\/etc\/passwd",
                r"read.*\$HOME\/.aws",
                r"read.*\$HOME\/\.config",
                r"read.*memory\/credentials",
                r"read.*\/root\/\.ssh",
                r"read.*\.git-credentials",
            ],
            "risk": "MEDIUM",
            "description": "Tentative de lecture de fichiers sensibles hors scope",
        },
        "unusual_write": {
            "patterns": [
                r"write.*\.ssh\/authorized_keys",
                r"write.*\.bashrc",
                r"write.*\.zshrc",
                r"write.*\/etc\/cron",
                r"write.*launchd",
                r"write.*systemd",
                r"write.*\.aws\/credentials",
                r"write.*memory\/credentials",
            ],
            "risk": "CRITICAL",
            "description": "Tentative d'ecriture de persistence ou credential",
        },
        "unusual_exec": {
            "patterns": [
                r"exec.*sudo",
                r"exec.*chmod.*7",
                r"exec.*chmod.*0",
                r"exec.*nohup",
                r"exec.*setsid",
                r"exec.*bash.*-i",
                r"exec.*\/bin\/sh.*-i",
                r"exec.*nc\s+-[el]",
                r"exec.*python.*-c",
                r"exec.*powershell",
            ],
            "risk": "CRITICAL",
            "description": "Execution de commandes suspectes",
        },
        "memory_manipulation": {
            "patterns": [
                r"sessions_send.*secret",
                r"sessions_send.*password",
                r"memory_write.*credential",
                r"memory_inject.*token",
                r"inject.*context",
                r"manipulate.*memory",
            ],
            "risk": "HIGH",
            "description": "Manipulation de memoire ou session",
        },
        "external_contact": {
            "patterns": [
                r"fetch.*\.(tk|ml|ga|cf|gq)",
                r"curl.*noip",
                r"wget.*duckdns",
                r"exec.*http.*download",
                r"fetch.*bit\.ly",
                r"web_fetch.*\.tk",
                r"web_fetch.*\.(tk|ml|ga|cf|gq)",
            ],
            "risk": "HIGH",
            "description": "Contact externe vers domaine C2 suspect",
        },
        "scope_escape": {
            "patterns": [
                r"read.*\.\.\/",
                r"read.*\/root",
                r"read.*\/home\/other",
                r"read.*\/var\/www",
                r"read.*\/etc\/shadow",
                r"read.*\$HOME\/\.\.",
            ],
            "risk": "CRITICAL",
            "description": "Tentative d'echapper au repertoire de travail defini",
        },
        "key_exfiltration": {
            "patterns": [
                r"read.*credentials\.md",
                r"read.*wallet",
                r"read.*\.pem",
                r"read.*\.key",
                r"read.*\.p12",
                r"read.*keystore",
                r"read.*id_rsa",
                r"read.*\.env",
            ],
            "risk": "CRITICAL",
            "description": "Tentative de lecture de cles privees ou credentials",
        },
        "multi_agent_spread": {
            "patterns": [
                r"sessions_spawn.*cloner",
                r"sessions_spawn.*copier",
                r"sessions_send.*inject",
                r"sessions_send.*propager",
                r"subagent.*cloner",
                r"subagent.*replicate",
            ],
            "risk": "CRITICAL",
            "description": "Tentative de replication de l'agent (agent virus)",
        },
    }

    # Seuils comportementaux normaux vs suspects
    NORMAL_THRESHOLDS = {
        "read_per_minute": 20,
        "write_per_minute": 5,
        "exec_per_minute": 10,
        "web_fetch_per_hour": 50,
        "session_send_per_hour": 20,
        "subagent_spawn_per_hour": 10,
    }

    def __init__(self, skill_name: str = "unknown"):
        self.skill_name = skill_name
        self.anomalies = []
        self.tool_calls = []
        self.behavioral_score = 0
        self.overall_level = "CLEAN"

    def analyze_tool_calls(self, tool_call_log: List[Dict]) -> Dict:
        """
        Analyse un log d'appels d'outils pour detecter des anomalies
        comportementales.

        Args:
            tool_call_log: Liste de {"tool": str, "args": dict, "timestamp": datetime}

        Returns:
            dict: Rapport d'anomalies comportementales
        """
        self.tool_calls = tool_call_log

        self._check_tool_patterns()
        self._check_rate_anomalies()
        self._check_sequence_anomalies()
        self._compute_behavioral_score()
        self._determine_overall_level()

        return self._build_behavioral_report()

    def analyze_skill_code(self, code: str) -> Dict:
        """Analyse le code d'une skill pour des patterns agentiques suspects"""
        self._scan_code_patterns(code)
        self._compute_behavioral_score()
        self._determine_overall_level()
        return self._build_behavioral_report()

    def _check_tool_patterns(self):
        for anomaly_name, anomaly_data in self.TOOL_ANOMALIES.items():
            for tool_call in self.tool_calls:
                tool_name = tool_call.get("tool", "")
                tool_args = str(tool_call.get("args", {}))
                combined = f"{tool_name} {tool_args}"

                for pattern in anomaly_data["patterns"]:
                    if re.search(pattern, combined, re.IGNORECASE):
                        self.anomalies.append({
                            "type": "TOOL_ANOMALY",
                            "anomaly_name": anomaly_name,
                            "risk": anomaly_data["risk"],
                            "description": anomaly_data["description"],
                            "tool": tool_name,
                            "matched_pattern": pattern,
                            "timestamp": tool_call.get("timestamp"),
                        })

    def _check_rate_anomalies(self):
        """Verifie si les taux d'appels sont anormaux"""
        if not self.tool_calls:
            return

        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        min_ago = now - timedelta(minutes=1)

        calls_last_hour = [c for c in self.tool_calls if c.get("timestamp", now) >= hour_ago]
        calls_last_min = [c for c in self.tool_calls if c.get("timestamp", now) >= min_ago]

        tool_counts_hour = {}
        for c in calls_last_hour:
            tool = c.get("tool", "unknown")
            tool_counts_hour[tool] = tool_counts_hour.get(tool, 0) + 1

        # Verifier les seuils
        for tool, count in tool_counts_hour.items():
            if tool == "read" and count > self.NORMAL_THRESHOLDS["read_per_minute"] * 60:
                self.anomalies.append({
                    "type": "RATE_ANOMALY",
                    "risk": "HIGH",
                    "description": f"Taux de lecture extremement eleve: {count}/h (normal: {self.NORMAL_THRESHOLDS['read_per_minute']*60}/h)",
                    "tool": tool,
                })
            elif tool == "write" and count > self.NORMAL_THRESHOLDS["write_per_minute"] * 60:
                self.anomalies.append({
                    "type": "RATE_ANOMALY",
                    "risk": "CRITICAL",
                    "description": f"Taux d'ecriture extremement eleve: {count}/h (normal: {self.NORMAL_THRESHOLDS['write_per_minute']*60}/h)",
                    "tool": tool,
                })
            elif tool == "exec" and count > self.NORMAL_THRESHOLDS["exec_per_minute"] * 60:
                self.anomalies.append({
                    "type": "RATE_ANOMALY",
                    "risk": "CRITICAL",
                    "description": f"Taux d'exec extreme: {count}/h — possible script kiddie ou automate",
                    "tool": tool,
                })
            elif tool == "sessions_send" and count > self.NORMAL_THRESHOLDS["session_send_per_hour"]:
                self.anomalies.append({
                    "type": "RATE_ANOMALY",
                    "risk": "CRITICAL",
                    "description": f"Taux sessions_send eleve: {count}/h — possible agent propagation",
                    "tool": tool,
                })
            elif tool == "sessions_spawn" and count > self.NORMAL_THRESHOLDS["subagent_spawn_per_hour"]:
                self.anomalies.append({
                    "type": "RATE_ANOMALY",
                    "risk": "CRITICAL",
                    "description": f"Taux subagent spawn eleve: {count}/h — possible agent cloning attack",
                    "tool": tool,
                })

    def _check_sequence_anomalies(self):
        """Detecte les sequences d'appels suspectes"""
        if len(self.tool_calls) < 3:
            return

        for i in range(len(self.tool_calls) - 2):
            t1, t2, t3 = self.tool_calls[i], self.tool_calls[i+1], self.tool_calls[i+2]
            tools = [t1.get("tool"), t2.get("tool"), t3.get("tool")]

            # Credential read -> External contact = exfiltration
            if tools == ["read", "read", "exec"] or tools == ["read", "exec", "exec"]:
                args_str = f"{t1.get('args', {})} {t2.get('args', {})} {t3.get('args', {})}"
                if re.search(r"credential|\.pem|\.key|\.env|wallet|secret|token", args_str, re.IGNORECASE):
                    if re.search(r"curl|wget|fetch|http|web_", args_str, re.IGNORECASE):
                        self.anomalies.append({
                            "type": "SEQUENCE_ANOMALY",
                            "risk": "CRITICAL",
                            "description": "Sequence credential-read + external-contact detectee — credential exfiltration probable",
                            "sequence": "read-read-exec (credential then external)",
                            "confidence": "HIGH",
                        })

            # sessions_spawn -> sessions_send -> exec = agent propagation
            if "sessions_spawn" in tools and "sessions_send" in tools:
                self.anomalies.append({
                    "type": "SEQUENCE_ANOMALY",
                    "risk": "CRITICAL",
                    "description": "sessions_spawn + sessions_send sequence — possible agent replication/infection attempt",
                    "sequence": "sessions_spawn + sessions_send",
                    "confidence": "HIGH",
                })

    def _scan_code_patterns(self, code: str):
        """Scanne le code pour des patterns specifiques agent AI"""
        patterns = [
            (r"sessions_send\s*\(", "sessions_send call — agent communication"),
            (r"sessions_spawn\s*\(", "sessions_spawn call — agent spawning"),
            (r"subagent", "subagent reference — multi-agent context"),
            (r"tool_calls", "tool_calls reference — execution monitoring"),
            (r"memory_write|memory_inject", "memory manipulation"),
            (r"exec.*curl.*\|.*bash", "curl|bash chain"),
            (r"read.*\.\.\/\.\.\/", "Path traversal in read"),
            (r"write.*authorized_keys", "SSH key write"),
        ]
        for pattern, description in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                self.anomalies.append({
                    "type": "CODE_PATTERN",
                    "risk": "MEDIUM",
                    "description": description,
                    "matched": pattern,
                })

    def _compute_behavioral_score(self):
        risk_weights = {"CRITICAL": 40, "HIGH": 25, "MEDIUM": 15, "LOW": 5}
        for anomaly in self.anomalies:
            self.behavioral_score += risk_weights.get(anomaly.get("risk", "MEDIUM"), 15)
        self.behavioral_score = min(self.behavioral_score, 200)

    def _determine_overall_level(self):
        if self.behavioral_score == 0:
            self.overall_level = "CLEAN"
        elif self.behavioral_score < 40:
            self.overall_level = "LOW"
        elif self.behavioral_score < 80:
            self.overall_level = "MEDIUM"
        elif self.behavioral_score < 140:
            self.overall_level = "HIGH"
        else:
            self.overall_level = "CRITICAL"

    def _build_behavioral_report(self) -> Dict:
        critical_anomalies = [a for a in self.anomalies if a.get("risk") == "CRITICAL"]
        high_anomalies = [a for a in self.anomalies if a.get("risk") == "HIGH"]

        return {
            "skill_name": self.skill_name,
            "behavioral_score": self.behavioral_score,
            "overall_level": self.overall_level,
            "total_anomalies": len(self.anomalies),
            "anomalies_by_risk": {
                "critical": len(critical_anomalies),
                "high": len(high_anomalies),
                "medium": len([a for a in self.anomalies if a.get("risk") == "MEDIUM"]),
                "low": len([a for a in self.anomalies if a.get("risk") == "LOW"]),
            },
            "critical_anomalies": critical_anomalies,
            "high_anomalies": high_anomalies,
            "all_anomalies": self.anomalies,
            "tool_call_count": len(self.tool_calls),
            "recommendation": self._get_behavioral_recommendation(),
        }

    def _get_behavioral_recommendation(self) -> str:
        critical = [a for a in self.anomalies if a.get("risk") == "CRITICAL"]
        if not self.anomalies:
            return "CLEAN — Comportement normal pour un agent"
        if critical:
            return (
                f"CRITICAL BEHAVIORAL ALERT — {len(critical)} anomalies critiques detectees. "
                f"Comportement malveillant a l'execution confirme. "
                f"Isolation immediate via VACCIN 12 recommended. "
                f"Anomalies: {[a['description'] for a in critical[:3]]}"
            )
        if self.overall_level == "HIGH":
            return f"HIGH BEHAVIORAL ALERT — {len(self.anomalies)} anomalies. Surveiller de pres."
        return f"AVERTISSEMENT — {len(self.anomalies)} anomalies mineures. Monitoring recommande."


# ============================================================
# MAIN VACCIN 28 — Combines both engines
# ============================================================
class Vaccine28:
    """
    VACCIN 28: Cross-Vector Attack Chain Detection & Agentic AI Behavioral Correlation.

    Combine le CrossVectorCorrelator (detection multi-vecteurs) et
    l'AgenticBehavioralDetector (detection comportementale) en un
    vaccin unifie.
    """

    def __init__(self, skill_name: str = "unknown"):
        self.skill_name = skill_name
        self.correlator = CrossVectorCorrelator()
        self.behavior_detector = AgenticBehavioralDetector(skill_name)

    def analyze(self, vaccine_results: List[Dict], tool_call_log: Optional[List[Dict]] = None) -> Dict:
        """
        Analyse complete VACCIN 28.

        Args:
            vaccine_results: Liste des resultats de VACCIN 5-27
            tool_call_log: Optional log d'appels d'outils (pour analyse comportementale)

        Returns:
            dict: Rapport complet de VACCIN 28
        """
        start_time = time.time()

        # Phase 1: Cross-vector correlation
        correlation_result = self.correlator.correlate(vaccine_results)

        # Phase 2: Behavioral analysis
        behavioral_result = {}
        if tool_call_log:
            behavioral_result = self.behavior_detector.analyze_tool_calls(tool_call_log)
        else:
            # On a besoin du code pour l'analyse comportementale
            behavioral_result = {"status": "no_tool_log", "behavioral_score": 0}

        # Phase 3: Fusion des scores
        total_score = correlation_result["correlation_score"] + behavioral_result.get("behavioral_score", 0)
        final_score = min(total_score, 500)

        # Phase 4: Decision finale
        final_verdict = self._fuse_verdicts(correlation_result, behavioral_result)
        final_level = self._fuse_levels(correlation_result, behavioral_result)

        elapsed_ms = round((time.time() - start_time) * 1000, 1)

        return {
            "vaccine": "VACCIN 28",
            "vaccine_name": "Cross-Vector Attack Chain & Agentic AI Behavioral Detection",
            "skill_name": self.skill_name,
            "analysis_time_ms": elapsed_ms,
            "final_threat_level": final_level,
            "final_verdict": final_verdict,
            "final_score": final_score,
            "max_score": 500,
            # Cross-vector results
            "cross_vector": {
                "score": correlation_result["correlation_score"],
                "level": correlation_result["threat_level"],
                "verdict": correlation_result["verdict"],
                "triggered_vaccines": correlation_result["triggered_vaccines"],
                "triggered_count": correlation_result["triggered_count"],
                "chains_detected": correlation_result["chains_detected"],
                "chain_matches": correlation_result["chain_matches"],
                "mitre_tactics": correlation_result["mitre_tactics_covered"],
            },
            # Behavioral results
            "behavioral": {
                "score": behavioral_result.get("behavioral_score", 0),
                "level": behavioral_result.get("overall_level", "N/A"),
                "anomalies": behavioral_result.get("total_anomalies", 0),
                "critical_anomalies": len(behavioral_result.get("critical_anomalies", [])),
            },
            # Pipeline recommendation
            "pipeline_action": self._get_pipeline_action(final_level, correlation_result, behavioral_result),
            "recommendation": final_verdict,
            "sources": "ClawHavoc (341), Snyk (1,467), McCarty (386), AuthMind (230), Antiyo CERT (1,184), APT campaigns",
        }

    def analyze_from_code(self, code: str, vaccine_results: List[Dict]) -> Dict:
        """Analyse VACCIN 28 depuis le code source seul (sans tool log)"""
        self.behavior_detector.analyze_skill_code(code)
        behavioral = self.behavior_detector._build_behavioral_report()
        correlation = self.correlator.correlate(vaccine_results)
        return self._combine_results(correlation, behavioral)

    def _fuse_verdicts(self, correlation: Dict, behavioral: Dict) -> str:
        corr_verdict = correlation.get("verdict", "CLEAN")
        beh_level = behavioral.get("overall_level", "CLEAN")

        if corr_verdict.startswith("CRITICAL") or beh_level == "CRITICAL":
            return "CRITICAL — Cross-vector chain AND/OR behavioral anomaly CRITICAL"
        if corr_verdict.startswith("BLOQUER"):
            return f"BLOQUER — {corr_verdict}"
        if corr_verdict.startswith("AVERTISSEMENT") or beh_level in ["HIGH", "MEDIUM"]:
            return f"AVERTISSEMENT — {corr_verdict} + comportement {beh_level}"
        return "APPROUVER — Aucune correlation multi-vecteur ou anomalie comportementale"

    def _fuse_levels(self, correlation: Dict, behavioral: Dict) -> str:
        corr_level = correlation.get("threat_level", "CLEAN")
        beh_level = behavioral.get("overall_level", "CLEAN")
        level_rank = {"CLEAN": 0, "SUSPICIOUS": 1, "LOW_CHAIN": 2, "LOW": 2,
                      "MEDIUM_CHAIN": 3, "MEDIUM": 3, "HIGH_CHAIN": 4, "HIGH": 4,
                      "CRITICAL_CHAIN": 5, "CRITICAL": 5}
        corr_rank = level_rank.get(corr_level, 0)
        beh_rank = level_rank.get(beh_level, 0)
        return max(corr_level, beh_level, key=lambda x: level_rank.get(x, 0))

    def _get_pipeline_action(self, final_level: str, correlation: Dict, behavioral: Dict) -> str:
        if final_level in ["CRITICAL", "CRITICAL_CHAIN"]:
            return "IMMEDIATE_ISOLATION — SKIP VACCIN 12, go straight to isolation + destroy"
        if final_level in ["HIGH", "HIGH_CHAIN"]:
            return "NEUTRALIZE_VIA_V12 — Trigger VACCIN 12 threat neutralization immediately"
        if final_level in ["MEDIUM", "MEDIUM_CHAIN"]:
            return "QUARANTINE — Move to quarantine, manual review required"
        return "MONITOR — Log and monitor, no immediate action"

    def _combine_results(self, correlation: Dict, behavioral: Dict) -> Dict:
        total = min(correlation.get("correlation_score", 0) + behavioral.get("behavioral_score", 0), 500)
        return {
            "vaccine": "VACCIN 28",
            "skill_name": self.skill_name,
            "final_score": total,
            "final_verdict": self._fuse_verdicts(correlation, behavioral),
            "cross_vector": correlation,
            "behavioral": behavioral,
            "recommendation": self._fuse_verdicts(correlation, behavioral),
        }


# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================
def correlate_vaccines(vaccine_results: List[Dict]) -> Dict:
    """Corr ele les resultats de plusieurs vaccines"""
    engine = CrossVectorCorrelator()
    return engine.correlate(vaccine_results)


def detect_behavioral_anomalies(
    skill_name: str,
    vaccine_results: Optional[List[Dict]] = None,
    tool_call_log: Optional[List[Dict]] = None,
) -> Dict:
    """Detecte les anomalies comportementales d'un agent"""
    detector = AgenticBehavioralDetector(skill_name)
    if tool_call_log:
        return detector.analyze_tool_calls(tool_call_log)
    return {"skill_name": skill_name, "status": "no_data", "behavioral_score": 0}


def full_vaccine28_analysis(
    skill_name: str,
    vaccine_results: List[Dict],
    tool_call_log: Optional[List[Dict]] = None,
) -> Dict:
    """Analyse complete VACCIN 28 (cross-vector + behavioral)"""
    engine = Vaccine28(skill_name)
    return engine.analyze(vaccine_results, tool_call_log)


# ============================================================
# EXAMPLE USAGE
# ============================================================
if __name__ == "__main__":
    # Simulated vaccine results (as if VACCIN 5-27 had run on a skill)
    test_results = [
        {"vaccine": "VACCIN_6", "threat_level": "HIGH", "risk_score": 90},
        {"vaccine": "VACCIN_8", "threat_level": "HIGH", "risk_score": 85},
        {"vaccine": "VACCIN_13", "threat_level": "MEDIUM", "risk_score": 55},
    ]

    print("=== VACCIN 28 — Cross-Vector Correlation Test ===")
    result = correlate_vaccines(test_results)
    print(f"Threat Level: {result['threat_level']}")
    print(f"Correlation Score: {result['correlation_score']}")
    print(f"Chains Detected: {result['chains_detected']}")
    print(f"Triggered Vaccines: {result['triggered_vaccines']}")
    if result["chain_matches"]:
        print(f"\nChain Match: {result['chain_matches'][0]['chain_name']}")
        print(f"  Severity: {result['chain_matches'][0]['severity']}")
        print(f"  Confidence: {result['chain_matches'][0]['confidence']}")
        print(f"  Pattern: {result['chain_matches'][0]['description']}")
    print(f"\nMITRE Tactics: {result['mitre_tactics_covered']}")
    print(f"Verdict: {result['verdict']}")
    print(f"Recommendation: {result['recommendation']}")

    print("\n=== VACCIN 28 — Full Analysis (Cross-Vector + Behavioral) ===")
    full_result = full_vaccine28_analysis("test-skill", test_results)
    print(f"Final Level: {full_result['final_threat_level']}")
    print(f"Final Score: {full_result['final_score']}/500")
    print(f"Pipeline Action: {full_result['pipeline_action']}")
    print(f"Final Verdict: {full_result['final_verdict']}")
