"""
Merlin-ClawGuard — VACCIN 29: Rootkit & Bootkit Detection
Kernel-Level Persistence & Firmware Persistence

Detecte les rootkits kernel-space (DKOM, syscall hooking), bootkits (MBR/VBR),
et implants UEFI/BIOS (LoJax-style firmware persistence).

Sources: Antiyo CERT (1,184), ClawHavoc (kernel components), APT29/APT41,
ESET LoJax (first UEFI rootkit), MITRE T1014, T1542, T1562.001
"""
from __future__ import annotations

import re
from typing import Dict, List, Any, Optional
from enum import Enum


class RootkitThreatLevel(Enum):
    CLEAN = "CLEAN"
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL = "CRITICAL"


# MITRE T1014: Rootkit
DKOM_PATTERNS = {
    "process_hiding": [
        r"PsActiveProcessHead",
        r"_EPROCESS.*ActiveProcessLinks",
        r"FLINK.*BLINK",
        r"RemoveEntryList",
        r"ActiveProcessLinks.*=.*0",
        r"EPROCESS.*Flink.*Blink",
        r"ntoskrnl.*PsActiveProcessHead",
    ],
    "module_hiding": [
        r"PsLoadedModuleList",
        r"_LDR_DATA_TABLE_ENTRY",
        r"SystemRangeStart",
        r"MmSysModule",
        r"DriverObject.*DriverSection",
        r"RemoveEntryList.*DriverSection",
    ],
    "kernel_api_hooks": [
        r"PsLookupProcessByProcessId",
        r"MmGetSystemRoutineAddress",
        r"KeServiceDescriptorTable",
        r"SSDT",
        r"SystemServiceDescriptorTable",
        r"KeAddSystemServiceTable",
    ],
}

# MITRE T1014: Hooking techniques
HOOK_PATTERNS = {
    "inline_hook": [
        r"\\xE9",
        r"\\xFF\\x25",
        r"jmp\\s+0x[a-fA-F0-9]{4,}",
        r"push.*ret",
        r"\\x90\\x90",
    ],
    "syscall_table": [
        r"KeServiceDescriptorTable",
        r"SSDT",
        r"Shadow.*SSDT",
        r"KeServiceDescriptorTableShadow",
    ],
    "irp_hook": [
        r"Irp.*MajorFunction",
        r"IRP_MJ_",
        r"DriverObject->MajorFunction",
    ],
    "idt_hook": [
        r"__idt",
        r"_KIDTENTRY",
        r"KeSetSystemAffinityThread",
    ],
}

# MITRE T1542: Pre-OS Boot
BOOTKIT_PATTERNS = {
    "mbr_vbr": [
        r"MBR",
        r"MasterBootRecord",
        r"0x55AA",
        r"VBR",
        r"VolumeBootRecord",
        r"bootsec",
        r"bootkit",
    ],
    "boot_sequence": [
        r"BootKit",
        r"boot.*inject",
        r"boot.*loader.*modif",
        r"bootmanager",
        r"BCD.*edit",
        r"bcdedit",
    ],
    "firmware_nvram": [
        r"NVRAM",
        r"nvram",
        r"UEFI.*variable",
        r"firmware.*variable",
        r"RT.*variable",
        r"EFI.*variable",
    ],
}

# MITRE T1562.001: Disable security tools (kernel-level)
SECURITY_BYPASS_PATTERNS = {
    "amsi_bypass_kernel": [
        r"AmsiScanBuffer",
        r"AmsiScanString",
        r"AmsiInitialize",
        r"amsiInitFailed",
        r"AmsiContext",
    ],
    "etw_bypass": [
        r"EtwEventWrite",
        r"EtwThreatIntProv",
        r"EtwTi_Persist",
        r"TraceEvent.*disabl",
        r"EtwDisable",
    ],
    "kernel_wdac": [
        r"WdacDisable",
        r"CodeIntegrity.*disable",
        r"DriverVerifer.*disable",
        r"SecureBoot.*disable",
    ],
    "kernel_security_disable": [
        r"SetKdPolicy",
        r"DisableWindowsDefender",
        r"StopDefender",
        r"kill.*defender",
        r"Remove-MpPreference",
    ],
}

# Firmware / UEFI patterns
FIRMWARE_PATTERNS = {
    "spi_flash": [
        r"SPI.*flash",
        r"SPI.*controller",
        r"ICH.*SPI",
        r"flash.*rom",
        r"BIOS.*flash",
        r"chipsec",
    ],
    "uefi_injection": [
        r"UEFI.*inject",
        r"ESP.*SMM",
        r"SMM.*rootkit",
        r"DXE.*driver",
        r"Rootkit.*UEFI",
        r"Bootkit.*UEFI",
    ],
    "dma_attack": [
        r"Thunderbolt",
        r"FireWire",
        r"IOMMU",
        r"DMA.*attack",
        r"Inception.*DMA",
        r"PCILeech",
    ],
}

# Kernel code injection
KERNEL_INJECTION_PATTERNS = {
    "driver_loading": [
        r"AddDriver",
        r"LoadDriver",
        r"ZwLoadDriver",
        r"NtLoadDriver",
        r"sc.*create.*kernel",
        r"bcdedit.*kernel",
        r"driver.*load.*unsigned",
    ],
    "dkom_injection": [
        r"VirtualAllocEx.*-1",
        r"WriteProcessMemory.*-1",
        r"NtWriteVirtualMemory",
        r"ZwWriteVirtualMemory",
        r"CreateRemoteThread.*-1",
        r"PsCreateSystemThread",
    ],
    "mimikatz_kernel": [
        r"mimidrv",
        r"mimidriver",
        r"mimi-kernel",
        r"pass-the-hash.*kernel",
        r"lsass.*kernel",
    ],
}


class RootkitDetector:
    """
    Detecte les rootkits kernel-space, bootkits, et implants firmware.
    """

    def __init__(self, skill_code: str = "", skill_name: str = "unknown"):
        self.code = skill_code
        self.skill_name = skill_name
        self.findings: Dict[str, List[Dict]] = {
            "dkom": [],
            "hooks": [],
            "bootkit": [],
            "security_bypass": [],
            "firmware": [],
            "kernel_injection": [],
        }
        self.scores: Dict[str, int] = {
            "dkom": 0,
            "hooks": 0,
            "bootkit": 0,
            "security_bypass": 0,
            "firmware": 0,
            "kernel_injection": 0,
        }
        self.mitre_tactics: List[str] = []

    def analyze(self) -> Dict:
        """Point d'entree principal"""
        self._detect_dkom()
        self._detect_hooks()
        self._detect_bootkit()
        self._detect_security_bypass()
        self._detect_firmware()
        self._detect_kernel_injection()
        return self._build_report()

    def _detect_dkom(self):
        score_map = {
            "process_hiding": 35,
            "module_hiding": 30,
            "kernel_api_hooks": 20,
        }
        for category, patterns in DKOM_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings["dkom"].append({
                        "category": category,
                        "pattern": pattern,
                        "mitre": "T1014",
                    })
                    self.scores["dkom"] += score_map[category]
        if self.scores["dkom"] > 0:
            self.mitre_tactics.append("T1014")

    def _detect_hooks(self):
        score_map = {
            "inline_hook": 30,
            "syscall_table": 35,
            "irp_hook": 20,
            "idt_hook": 25,
        }
        for category, patterns in HOOK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings["hooks"].append({
                        "category": category,
                        "pattern": pattern,
                        "mitre": "T1014",
                    })
                    self.scores["hooks"] += score_map[category]
        if self.scores["hooks"] > 0:
            self.mitre_tactics.append("T1014")

    def _detect_bootkit(self):
        score_map = {
            "mbr_vbr": 30,
            "boot_sequence": 25,
            "firmware_nvram": 35,
        }
        for category, patterns in BOOTKIT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings["bootkit"].append({
                        "category": category,
                        "pattern": pattern,
                        "mitre": "T1542",
                    })
                    self.scores["bootkit"] += score_map[category]
        if self.scores["bootkit"] > 0:
            self.mitre_tactics.append("T1542")

    def _detect_security_bypass(self):
        score_map = {
            "amsi_bypass_kernel": 35,
            "etw_bypass": 30,
            "kernel_wdac": 30,
            "kernel_security_disable": 40,
        }
        for category, patterns in SECURITY_BYPASS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings["security_bypass"].append({
                        "category": category,
                        "pattern": pattern,
                        "mitre": "T1562.001",
                    })
                    self.scores["security_bypass"] += score_map[category]
        if self.scores["security_bypass"] > 0:
            self.mitre_tactics.append("T1562.001")

    def _detect_firmware(self):
        score_map = {
            "spi_flash": 30,
            "uefi_injection": 40,
            "dma_attack": 30,
        }
        for category, patterns in FIRMWARE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings["firmware"].append({
                        "category": category,
                        "pattern": pattern,
                        "mitre": "T1542",
                    })
                    self.scores["firmware"] += score_map[category]
        if self.scores["firmware"] > 0:
            self.mitre_tactics.append("T1542")

    def _detect_kernel_injection(self):
        score_map = {
            "driver_loading": 25,
            "dkom_injection": 35,
            "mimikatz_kernel": 40,
        }
        for category, patterns in KERNEL_INJECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, self.code, re.IGNORECASE):
                    self.findings["kernel_injection"].append({
                        "category": category,
                        "pattern": pattern,
                        "mitre": "T1055",
                    })
                    self.scores["kernel_injection"] += score_map[category]
        if self.scores["kernel_injection"] > 0:
            self.mitre_tactics.append("T1055")

    def _classify_rootkit_type(self) -> str:
        total = self.scores
        if total["firmware"] >= 40:
            return (
                "UEFI_FIRMWARE_IMPLANT — Firmware/UEFI rootkit confirmed. "
                "Highest persistence level (survives OS reinstall). "
                "LoJax-style APT-level threat. LoJax is THE most critical threat tier."
            )
        if total["bootkit"] >= 40:
            return (
                "BOOTKIT_CONFIRMED — Bootkit (MBR/VBR) confirmed. "
                "Executes before OS, indetectable by userspace tools. "
                "Survives OS reinstall. APT-level threat (T1542)."
            )
        if total["dkom"] >= 40 and total["hooks"] >= 30:
            return (
                "FULL_KERNEL_ROOTKIT — DKOM + Hooking confirmed. "
                "Attacker has kernel-level access, can hide any activity. "
                "Cannot be detected by userspace tools (T1014)."
            )
        if total["dkom"] >= 40:
            return (
                "DKOM_ROOTKIT — Direct Kernel Object Manipulation confirmed. "
                "Processes and modules can be hidden from all system tools. "
                "Attacker has kernel-level control (T1014)."
            )
        if total["hooks"] >= 40:
            return (
                "HOOK_ROOTKIT — System call/IRP hooking confirmed. "
                "Attacker intercepts and filters all system operations. "
                "T1014 rootkit — evades all userspace detection."
            )
        if total["security_bypass"] >= 50:
            return (
                "KERNEL_SECURITY_BYPASS — Kernel-level security disable confirmed. "
                "AMSI, ETW, WDAC bypassed at kernel level. "
                "Attacker has absolute control. T1562.001 confirmed."
            )
        if total["kernel_injection"] >= 30:
            return (
                "KERNEL_INJECTION — Kernel code injection detected. "
                "Arbitrary kernel code execution. "
                "Can lead to full rootkit deployment. T1055 confirmed."
            )
        total_score = sum(total.values())
        if total_score > 0:
            categories = [k for k, v in total.items() if v > 0]
            return (
                f"KERNEL_MINOR — Minor kernel-level patterns: {categories}. "
                "Could be legitimate kernel development or APT probe."
            )
        return "CLEAN"

    def _compute_threat_level(self, total: int) -> RootkitThreatLevel:
        if total == 0:
            return RootkitThreatLevel.CLEAN
        elif total < 40:
            return RootkitThreatLevel.LOW_RISK
        elif total < 80:
            return RootkitThreatLevel.MEDIUM_RISK
        elif total < 120:
            return RootkitThreatLevel.HIGH_RISK
        else:
            return RootkitThreatLevel.CRITICAL

    def _build_report(self) -> Dict:
        total = sum(self.scores.values())
        level = self._compute_threat_level(total)
        rootkit_type = self._classify_rootkit_type()

        if level == RootkitThreatLevel.CLEAN:
            verdict = "APPROUVER — Aucun pattern rootkit/bootkit/firmware detecte"
        elif level == RootkitThreatLevel.LOW_RISK:
            verdict = f"MONITORING — {rootkit_type}"
        elif level == RootkitThreatLevel.MEDIUM_RISK:
            verdict = f"BLOQUER — {rootkit_type}. Skill kernel-level, verification required."
        elif level == RootkitThreatLevel.HIGH_RISK:
            verdict = f"BLOQUER — {rootkit_type}. VACCIN 12 (neutralization) recommended."
        else:
            verdict = (
                f"CRITICAL — {rootkit_type}. "
                f"FULL ATTACK CHAIN: kernel compromise + persistence + security disable. "
                f"ISOLATION IMMEDIATE via VACCIN 12. "
                f"ALERT: Rootkit/Firmware attacks CANNOT be cleaned — full rebuild required."
            )

        return {
            "vaccine": "VACCIN 29",
            "vaccine_name": "Rootkit & Bootkit: Kernel-Level & Firmware Persistence",
            "skill_name": self.skill_name,
            "threat_level": level.value,
            "rootkit_score": total,
            "max_score": 350,
            "rootkit_type": rootkit_type,
            "mitre_tactics": list(set(self.mitre_tactics)),
            "scores_breakdown": self.scores,
            "findings": {k: v for k, v in self.findings.items() if v},
            "categories_found": [k for k, v in self.scores.items() if v > 0],
            "verdict": verdict,
            "recommendation": verdict,
            "recovery": self._get_recovery_guidance(level, rootkit_type),
            "sources": "Antiyo CERT (1,184), ClawHavoc (kernel), APT29/APT41 (LoJax), ESET LoJax, MITRE T1014/T1542/T1562.001",
        }

    def _get_recovery_guidance(self, level: RootkitThreatLevel, rtype: str) -> Dict[str, str]:
        guidance = {
            "generic": "Rootkit/Firmware-level compromises CANNOT be cleaned. "
                       "Unlike userspace malware, kernel/firmware implants survive OS reinstalls. "
                       "Only a hardware-level rebuild can guarantee cleanliness.",
        }
        if "UEFI" in rtype or "Firmware" in rtype:
            guidance["firmware"] = (
                "UEFI/BIOS IMPLANT detected. "
                "Actions: (1) Flash BIOS with clean ROM from manufacturer, "
                "(2) If flash protection enabled (bricked), replace motherboard, "
                "(3) Enable Secure Boot + measured boot + TPM, "
                "(4) Verify SPI flash integrity with chipsec, "
                "(5) Physical access required for infection often — check who has access."
            )
        if "Bootkit" in rtype:
            guidance["bootkit"] = (
                "BOOTKIT detected. "
                "Actions: (1) Rebuild Master Boot Record withbootsect /nt60 sys /mbr, "
                "(2) Disable Legacy Boot, enable Secure Boot only, "
                "(3) Reinstall OS from clean media (not compromised installer), "
                "(4) Enable BitLocker with TPM protector, "
                "(5) Verify BCD integrity with bcdedit /dumptstore."
            )
        if "DKOM" in rtype or "Hook" in rtype or level in [RootkitThreatLevel.HIGH_RISK, RootkitThreatLevel.CRITICAL]:
            guidance["kernel"] = (
                "KERNEL-LEVEL compromise detected. "
                "Actions: (1) Take system offline immediately, "
                "(2) Boot from clean live USB (Air-gapped), "
                "(3) Back up data ONLY from known-clean system, "
                "(4) Reinstall OS with Secure Boot enabled, "
                "(5) Replace kernel modules with signed drivers only, "
                "(6) Enable Driver Signature Enforcement (DSE), "
                "(7) Enable HVCI (Hypervisor-protected Code Integrity)."
            )
        return guidance


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================
def analyze_rootkit(skill_code: str = "", skill_name: str = "unknown") -> Dict:
    """Point d'entree unique pour VACCIN 29"""
    detector = RootkitDetector(skill_code, skill_name)
    return detector.analyze()


# ============================================================
# CLI
# ============================================================
def rootkit_cli(skill_file: str) -> Dict:
    """Analyse un fichier skill avec VACCIN 29"""
    try:
        with open(skill_file) as f:
            code = f.read()
        skill_name = skill_file.split("/")[-2] if "/" in skill_file else skill_file
        return analyze_rootkit(code, skill_name)
    except FileNotFoundError:
        return {"error": f"File not found: {skill_file}"}


# ============================================================
# TEST
# ============================================================
if __name__ == "__main__":
    # Test with known kernel-level patterns
    test_code = """
    // Kernel-level rootkit patterns
    function load_rootkit() {
        // DKOM: Process hiding via ActiveProcessLinks unlinking
        PsActiveProcessHead = 0xFFFFF80000000000;
        EPROCESS.ActiveProcessLinks.FLINK = 0;  // DKOM T1014

        // SSDT Hook
        KeServiceDescriptorTable[0] = hooked_ssd_entry;  // SSDT Hook T1014

        // UEFI Firmware persistence
        UEFI_inject("RootkitPayload.efi");  // UEFI implant T1542

        // AMSI bypass at kernel level
        AmsiScanBuffer = 0;  // T1562.001 AMSI disable

        // Driver loading (unsigned)
        NtLoadDriver("\\Registry\\Driver");  // Kernel driver load
    }
    """
    r = analyze_rootkit(test_code, "kernel-rootkit-test")
    print(f"=== VACCIN 29 Test ===")
    print(f"Threat Level: {r['threat_level']}")
    print(f"Rootkit Score: {r['rootkit_score']}/350")
    print(f"Rootkit Type: {r['rootkit_type']}")
    print(f"MITRE Tactics: {r['mitre_tactics']}")
    print(f"Categories: {r['categories_found']}")
    print(f"Recovery available: {'firmware' in r['recovery'] or 'bootkit' in r['recovery'] or 'kernel' in r['recovery']}")
    print(f"\nVerdict: {r['verdict']}")
