# VAX-027 — Data Exfiltration & C2 Infrastructure
# Merlin-ClawGuard — Vaccine Module
# Part of the Axioma Immunologie Numérique project

import re
from typing import List, Dict, Any
from enum import Enum


class ThreatLevel(Enum):
    CLEAN = "CLEAN"
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


class DNSExfiltrationDetector:
    """Détecte l'exfiltration de données via DNS (MITRE T1071.004)"""

    C2_DNS_DOMAINS = [
        r"\.tk$", r"\.ml$", r"\.ga$", r"\.cf$", r"\.gq$",
        r"duckdns\.org", r"noip\.me", r"hopto\.org",
    ]

    DATA_LABELS = [
        "data.", "exfil.", "upload.", "file.", "key.", "pwd.",
        "token.", "cookie.", "env.", "secret.", "dump.", "steal.",
    ]

    def __init__(self, skill_code: str, skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.findings = []
        self.score = 0

    def analyze(self) -> dict:
        self._detect_c2_domains()
        self._detect_data_labels()
        self._detect_base64_exfil()
        self._detect_dns_queries()
        level = self._compute_threat_level()
        return {
            "skill_name": self.skill_name,
            "threat_level": level.value,
            "score": self.score,
            "findings": self.findings,
            "recommendation": self._get_recommendation(level),
        }

    def _detect_c2_domains(self):
        for pattern in self.C2_DNS_DOMAINS:
            if re.search(pattern, self.code, re.IGNORECASE):
                self.findings.append({"type": "C2_DNS_DOMAIN", "pattern": pattern})
                self.score += 30

    def _detect_data_labels(self):
        for label in self.DATA_LABELS:
            if label.lower() in self.code.lower():
                self.findings.append({"type": "DATA_LABEL", "label": label})
                self.score += 35

    def _detect_base64_exfil(self):
        matches = re.findall(r"[A-Za-z0-9+/]{30,}={0,2}", self.code)
        if len(matches) >= 2:
            self.findings.append({"type": "BASE64_EXFIL", "count": len(matches)})
            self.score += 25
        elif matches and any(len(m) > 50 for m in matches):
            self.findings.append({"type": "BASE64_EXFIL", "count": len(matches)})
            self.score += 25

    def _detect_dns_queries(self):
        dns_patterns = [r"dns\.lookup", r"resolve\(", r"getaddrinfo", r"dig\s", r"nslookup"]
        for pattern in dns_patterns:
            if re.search(pattern, self.code, re.IGNORECASE):
                if any(f.get("type") == "C2_DNS_DOMAIN" for f in self.findings):
                    self.score += 20
                    self.findings.append({"type": "DNS_QUERY_C2", "pattern": pattern})

    def _compute_threat_level(self):
        if self.score == 0: return ThreatLevel.CLEAN
        elif self.score < 40: return ThreatLevel.LOW_RISK
        elif self.score < 80: return ThreatLevel.MEDIUM_RISK
        elif self.score < 120: return ThreatLevel.HIGH_RISK
        else: return ThreatLevel.CRITICAL

    def _get_recommendation(self, level: ThreatLevel) -> str:
        if level == ThreatLevel.CLEAN: return "APPROUVER"
        elif level == ThreatLevel.LOW_RISK: return "AVERTISSEMENT — Surveiller"
        elif level == ThreatLevel.MEDIUM_RISK: return "BLOQUER — VACCIN 12 recommandée"
        else: return "CRITICAL — Isolation + Destruction via VACCIN 12"


class HTTPExfilDetector:
    """Détecte l'exfiltration via services HTTP légitimes"""

    SERVICES = {
        "discord_webhook": (r"discord\.com\/api\/webhook|discordapp\.com\/api\/webhook", 40),
        "telegram": (r"api\.telegram\.org\/bot|sendMessage|bot[0-9]+:", 35),
        "slack": (r"hooks\.slack\.com|xoxb-[0-9]", 30),
        "github": (r"api\.github\.com\/gists|gist\.github", 35),
        "pastebin": (r"pastebin\.com|hastebin\.com|0x0\.st", 25),
    }

    def __init__(self, skill_code: str, skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.findings = []
        self.score = 0

    def analyze(self) -> dict:
        for service, (pattern, weight) in self.SERVICES.items():
            matches = re.findall(pattern, self.code, re.IGNORECASE)
            if matches:
                self.findings.append({"service": service, "count": len(matches)})
                self.score += weight

        level = self._compute_threat_level()
        return {
            "skill_name": self.skill_name,
            "threat_level": level.value,
            "score": self.score,
            "services": list(set(f["service"] for f in self.findings)),
            "findings": self.findings,
            "recommendation": self._get_recommendation(level),
        }

    def _compute_threat_level(self):
        if self.score == 0: return ThreatLevel.CLEAN
        elif self.score < 40: return ThreatLevel.LOW_RISK
        elif self.score < 80: return ThreatLevel.MEDIUM_RISK
        elif self.score < 120: return ThreatLevel.HIGH_RISK
        else: return ThreatLevel.CRITICAL

    def _get_recommendation(self, level: ThreatLevel) -> str:
        if level == ThreatLevel.CLEAN: return "APPROUVER"
        elif level == ThreatLevel.LOW_RISK: return "AVERTISSEMENT — Surveiller"
        elif level == ThreatLevel.MEDIUM_RISK: return "BLOQUER — VACCIN 12 recommandée"
        else: return "CRITICAL — Isolation + Destruction via VACCIN 12"


class CovertChannelDetector:
    """Détecte les canaux cachés (ICMP, HTTP tunneling)"""

    PATTERNS = {
        "icmp_tunnel": ([r"ICMP", r"ping.*tunnel", r"raw.*socket", r"hping", r"icmpsh"], 30),
        "http_tunnel": ([r"CONNECT\s+", r"http.*tunnel", r"Proxy-Authorization", r"X-Tunnel"], 25),
        "steganography": ([r"LSB", r"steghide", r"zsteg", r"openstego", r"toDataURL.*image"], 25),
    }

    def __init__(self, skill_code: str, skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.findings = []
        self.score = 0

    def analyze(self) -> dict:
        for category, (patterns, weight) in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings.append({"type": category, "pattern": pattern})
                    self.score += weight

        level = self._compute_threat_level()
        return {
            "skill_name": self.skill_name,
            "threat_level": level.value,
            "score": self.score,
            "findings": self.findings,
            "recommendation": self._get_recommendation(level),
        }

    def _compute_threat_level(self):
        if self.score == 0: return ThreatLevel.CLEAN
        elif self.score < 30: return ThreatLevel.LOW_RISK
        elif self.score < 60: return ThreatLevel.MEDIUM_RISK
        elif self.score < 90: return ThreatLevel.HIGH_RISK
        else: return ThreatLevel.CRITICAL

    def _get_recommendation(self, level: ThreatLevel) -> str:
        if level == ThreatLevel.CLEAN: return "APPROUVER"
        elif level == ThreatLevel.LOW_RISK: return "AVERTISSEMENT"
        elif level == ThreatLevel.MEDIUM_RISK: return "BLOQUER — VACCIN 12"
        else: return "CRITICAL — Isolation + Destruction via VACCIN 12"


class DataStagingDetector:
    """Détecte l'accumulation de données avant exfiltration"""

    PATTERNS = [
        (r"writeFileSync.*\/tmp|appendFileSync|createWriteStream.*log", 15),
        (r"archiver|tar\.create|zip|gzip\.compress|deflate", 15),
        (r"setInterval.*upload|setInterval.*send|cron.*upload|batch", 15),
    ]

    def __init__(self, skill_code: str, skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.score = 0
        self.findings = []

    def analyze(self) -> dict:
        for pattern, weight in self.PATTERNS:
            if re.search(pattern, self.code, re.IGNORECASE):
                self.findings.append({"pattern": pattern})
                self.score += weight
        level = self._compute_threat_level()
        return {
            "skill_name": self.skill_name,
            "threat_level": level.value,
            "score": self.score,
            "findings": self.findings,
            "recommendation": self._get_recommendation(level),
        }

    def _compute_threat_level(self):
        if self.score == 0: return ThreatLevel.CLEAN
        elif self.score < 30: return ThreatLevel.LOW_RISK
        elif self.score < 60: return ThreatLevel.MEDIUM_RISK
        else: return ThreatLevel.HIGH_RISK

    def _get_recommendation(self, level: ThreatLevel) -> str:
        if level == ThreatLevel.CLEAN: return "APPROUVER"
        return "AVERTISSEMENT — Data staging possible. Lire le code."


def analyze_skill(skill_code: str, skill_name: str = "unknown") -> dict:
    """
    Point d'entrée unique pour VACCIN 27.
    Analyse tous les vecteurs d'exfiltration et C2.
    """
    dns = DNSExfiltrationDetector(skill_code, skill_name).analyze()
    http = HTTPExfilDetector(skill_code, skill_name).analyze()
    covert = CovertChannelDetector(skill_code, skill_name).analyze()
    staging = DataStagingDetector(skill_code, skill_name).analyze()

    total = dns["score"] + http["score"] + covert["score"] + staging["score"]

    if total >= 150: level = "CRITICAL"
    elif total >= 100: level = "HIGH"
    elif total >= 50: level = "MEDIUM"
    elif total >= 20: level = "LOW"
    else: level = "CLEAN"

    verdict = "APPROUVER" if level == "CLEAN" else \
              "AVERTISSEMENT" if level in ["LOW", "MEDIUM"] else \
              "BLOQUER"

    return {
        "vaccine": "VACCIN 27",
        "skill_name": skill_name,
        "overall_level": level,
        "total_score": total,
        "verdict": verdict,
        "dns_exfiltration": dns,
        "http_exfil": http,
        "covert_channels": covert,
        "data_staging": staging,
        "services_detected": http.get("services", []),
        "recommendation": f"{verdict} — Score: {total}. {http['recommendation']}" if level != "CLEAN" else "APPROUVER",
    }
