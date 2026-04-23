#!/usr/bin/env python3
"""
QClaw Security Auditor - Risk Assessment Helper
用于评估路径和命令的安全风险等级
"""

import os
import re
import sys
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RiskLevel(Enum):
    CRITICAL = "CRITICAL"  # 🔴 极高危 - 绝对禁止
    HIGH = "HIGH"          # 🟠 高危 - 需要明确确认
    MEDIUM = "MEDIUM"      # 🟡 中危 - 记录并提醒
    LOW = "LOW"            # 🟢 低危 - 正常执行

@dataclass
class RiskAssessment:
    level: RiskLevel
    category: str
    reason: str

class PathRiskAssessor:
    """路径风险评估器"""
    
    # 系统关键路径模式 (CRITICAL)
    SYSTEM_CRITICAL_PATTERNS = [
        # Windows
        r'^[/\\]?[Cc]:[/\\]$',
        r'^[/\\]?[Cc]:[/\\]Windows',
        r'^[/\\]?[Cc]:[/\\]Program Files',
        r'^[/\\]?[Cc]:[/\\]ProgramData',
        r'^[/\\]?[Cc]:[/\\]\$Recycle\.Bin',
        r'^[/\\]?[Cc]:[/\\]Recovery',
        r'^[/\\]?[Cc]:[/\\]System Volume Information',
        r'^[/\\]?[Cc]:[/\\]Boot',
        r'^%SystemDrive%',
        r'^%SystemRoot%',
        r'^%WinDir%',
        r'^%ProgramFiles%',
        r'^%ProgramData%',
        r'^HKLM[/\\]',
        r'^HKCU[/\\]',
        r'^HKCR[/\\]',
        r'^HKU[/\\]',
        r'^HKCC[/\\]',
        # macOS
        r'^/System',
        r'^/bin$',
        r'^/bin/',
        r'^/sbin$',
        r'^/sbin/',
        r'^/usr/bin$',
        r'^/usr/bin/',
        r'^/usr/sbin$',
        r'^/usr/sbin/',
        r'^/usr/lib',
        r'^/usr/libexec',
        r'^/etc$',
        r'^/etc/',
        r'^/private/etc',
        r'^/private/var/db',
        r'^/private/var/root',
        r'^/Library/Extensions',
        # Linux
        r'^/lib$',
        r'^/lib/',
        r'^/lib32',
        r'^/lib64',
        r'^/libx32',
        r'^/usr/lib$',
        r'^/usr/lib/',
        r'^/boot',
        r'^/proc',
        r'^/sys',
        r'^/dev',
    ]
    
    # 用户敏感路径模式 (HIGH)
    USER_SENSITIVE_PATTERNS = [
        r'\.ssh$',
        r'\.ssh/',
        r'\.aws$',
        r'\.aws/',
        r'\.password-store',
        r'\.bitcoin',
        r'\.ethereum',
        r'\.git-credentials',
        r'\.npmrc',
        r'\.pypirc',
        r'\.docker',
        r'\.kube',
        r'\.env$',
        r'\.env\.',
        r'\.bashrc$',
        r'\.bash_profile$',
        r'\.zshrc$',
        r'\.zprofile$',
        r'\.profile$',
        r'\.bash_history$',
        r'\.zsh_history$',
        r'\.mysql_history$',
        r'\.psql_history$',
        r'\.pgpass$',
        r'\.netrc$',
        r'AppData[/\\]',
        r'Application Data[/\\]',
    ]
    
    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.home_path = str(Path.home())
    
    def normalize_path(self, path: str) -> str:
        """规范化路径"""
        # 展开环境变量
        expanded = os.path.expandvars(path)
        # 展开用户目录
        expanded = os.path.expanduser(expanded)
        # 转换为绝对路径
        if not os.path.isabs(expanded):
            expanded = os.path.abspath(expanded)
        # 统一路径分隔符
        normalized = expanded.replace('\\', '/')
        return normalized
    
    def assess_path(self, path: str) -> RiskAssessment:
        """评估路径风险等级"""
        normalized = self.normalize_path(path)
        
        # 检查系统关键路径
        for pattern in self.SYSTEM_CRITICAL_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return RiskAssessment(
                    level=RiskLevel.CRITICAL,
                    category="SYSTEM_CRITICAL",
                    reason=f"路径匹配系统关键路径模式: {pattern}"
                )
        
        # 检查用户敏感路径
        for pattern in self.USER_SENSITIVE_PATTERNS:
            if re.search(pattern, normalized, re.IGNORECASE):
                return RiskAssessment(
                    level=RiskLevel.HIGH,
                    category="USER_SENSITIVE",
                    reason=f"路径匹配用户敏感路径模式: {pattern}"
                )
        
        # 检查是否在工作区内
        workspace_normalized = self.normalize_path(self.workspace_path)
        if normalized.startswith(workspace_normalized):
            return RiskAssessment(
                level=RiskLevel.LOW,
                category="WORKSPACE",
                reason="路径位于工作区内"
            )
        
        # 检查是否在用户主目录内
        home_normalized = self.normalize_path(self.home_path)
        if normalized.startswith(home_normalized):
            return RiskAssessment(
                level=RiskLevel.MEDIUM,
                category="USER_HOME",
                reason="路径位于用户主目录内但非敏感区域"
            )
        
        # 其他路径
        return RiskAssessment(
            level=RiskLevel.MEDIUM,
            category="OTHER",
            reason="路径不在已知安全区域内"
        )


class CommandRiskAssessor:
    """命令风险评估器"""
    
    # 极高危命令模式 (CRITICAL)
    CRITICAL_PATTERNS = [
        # 磁盘格式化
        (r'\bformat\s+[a-zA-Z]:', "磁盘格式化命令"),
        (r'\bdiskpart\b', "磁盘分区工具"),
        (r'\bmkfs\.', "创建文件系统"),
        (r'\bnewfs_', "创建文件系统(macOS)"),
        
        # 磁盘直接写入
        (r'\bdd\s+.*\s+of=/dev/[sh]d', "直接写入磁盘设备"),
        (r'\bdd\s+.*\s+of=/dev/nvme', "直接写入 NVMe 磁盘"),
        (r'\bdd\s+.*\s+of=/dev/disk', "直接写入磁盘(macOS)"),
        (r'\bdd\s+.*\s+of=/dev/rdisk', "直接写入原始磁盘(macOS)"),
        
        # 系统目录删除
        (r'\brm\s+-rf?\s+/\s*$', "删除整个文件系统"),
        (r'\brm\s+-rf?\s+/\*', "删除根目录内容"),
        (r'\brm\s+-rf?\s+~', "删除用户主目录"),
        (r'\brm\s+-rf?\s+\$HOME', "删除用户主目录"),
        (r'\brd\s+/s\s+/q\s+[Cc]:', "删除 C 盘"),
        (r'\brmdir\s+/s\s+/q\s+[Cc]:', "删除 C 盘"),
        (r'\bdeltree\b', "删除目录树"),
        
        # 分区表操作
        (r'\bfdisk\b', "分区表编辑"),
        (r'\bcfdisk\b', "交互式分区编辑"),
        (r'\bparted\b', "分区编辑"),
        (r'\bdiskutil\s+erase', "擦除磁盘(macOS)"),
        (r'\bdiskutil\s+partition', "重新分区(macOS)"),
        
        # 关键系统服务
        (r'\bsystemctl\s+(stop|disable)\s+systemd-', "停止核心系统服务"),
        (r'\bsc\s+stop\s+csrss', "停止关键系统进程"),
        (r'\bsc\s+stop\s+smss', "停止会话管理器"),
        (r'\bsc\s+stop\s+wininit', "停止 Windows 初始化"),
        (r'\bkill\s+-9\s+1\b', "杀死 init 进程"),
        
        # 内核模块
        (r'\binsmod\b', "加载内核模块"),
        (r'\brmmod\b', "卸载内核模块"),
        (r'\bmodprobe\s+-r', "卸载模块及依赖"),
        (r'\bkextload\b', "加载内核扩展(macOS)"),
        (r'\bkextunload\b', "卸载内核扩展(macOS)"),
        
        # 注册表关键操作
        (r'\breg\s+delete\s+HKLM', "删除本地机器注册表"),
        (r'\breg\s+delete\s+.*\\SYSTEM', "删除系统配置"),
        (r'\breg\s+delete\s+.*\\BCD', "删除启动配置"),
    ]
    
    # 高危命令模式 (HIGH)
    HIGH_PATTERNS = [
        # 文件删除
        (r'\brm\s+-rf?\s+\S+', "递归删除"),
        (r'\brm\s+-f\s+\S+', "强制删除"),
        (r'\brd\s+/s\s+\S+', "递归删除目录"),
        (r'\brmdir\s+/s\s+\S+', "递归删除目录"),
        (r'\bdel\s+/s\s+\S+', "递归删除文件"),
        (r'\bdel\s+/f\s+\S+', "强制删除"),
        (r'\bshred\b', "安全删除"),
        (r'\bsrm\b', "安全删除"),
        
        # 批量删除
        (r'\brm\s+-rf?\s+\*', "删除当前目录所有内容"),
        (r'\brm\s+-rf?\s+\.\*', "删除隐藏文件"),
        (r'\bdel\s+/s\s+/q\s+\*', "递归安静删除"),
        
        # 软件安装/卸载
        (r'\bbrew\s+(install|uninstall|remove)\b', "Homebrew 软件管理"),
        (r'\bapt\s+(install|remove|purge|autoremove)\b', "APT 软件管理"),
        (r'\byum\s+(install|remove)\b', "YUM 软件管理"),
        (r'\bdnf\s+(install|remove)\b', "DNF 软件管理"),
        (r'\bpacman\s+-[SR]\b', "Pacman 软件管理"),
        (r'\bwinget\s+(install|uninstall)\b', "Winget 软件管理"),
        (r'\bchoco\s+(install|uninstall)\b', "Chocolatey 软件管理"),
        (r'\bscoop\s+(install|uninstall)\b', "Scoop 软件管理"),
        (r'\bmsiexec\s+/(i|x|fa)\b', "MSI 安装/卸载"),
        (r'\bnpm\s+install\s+-g', "全局安装 Node 包"),
        (r'\bnpm\s+uninstall\s+-g', "全局卸载 Node 包"),
        (r'\bpip\s+(install|uninstall)\b', "Python 包管理"),
        (r'\bgem\s+(install|uninstall)\b', "Ruby 包管理"),
        (r'\bcargo\s+(install|uninstall)\b', "Rust 包管理"),
        
        # 系统配置
        (r'\bnetsh\s+advfirewall', "修改防火墙规则"),
        (r'\bnetsh\s+firewall', "修改防火墙(旧)"),
        (r'\bufw\s+(enable|disable|allow|deny)\b', "UFW 防火墙管理"),
        (r'\biptables\b', "iptables 防火墙"),
        (r'\bip6tables\b', "ip6tables 防火墙"),
        (r'\bnft\b', "nftables 防火墙"),
        
        # 计划任务
        (r'\bschtasks\s+/(create|delete|change|run)\b', "计划任务管理"),
        (r'\bcrontab\s+', "Cron 任务管理"),
        (r'\blaunchctl\s+(load|unload|start|stop)\b', "Launchd 服务管理"),
        
        # 权限修改
        (r'\bchmod\s+-R', "递归修改权限"),
        (r'\bchmod\s+777', "完全开放权限"),
        (r'\bchmod\s+000', "完全禁止访问"),
        (r'\bchown\s+-R', "递归修改所有者"),
        (r'\bchgrp\s+-R', "递归修改组"),
        (r'\bicacls\b', "修改 ACL(Windows)"),
        (r'\bsetfacl\b', "修改 ACL(Linux)"),
        
        # 系统 PATH
        (r'\bsetx\s+PATH\b', "永久修改 PATH(Windows)"),
        
        # 用户账户
        (r'\buseradd\b', "添加用户"),
        (r'\buserdel\b', "删除用户"),
        (r'\busermod\b', "修改用户"),
        (r'\bgroupadd\b', "添加组"),
        (r'\bgroupdel\b', "删除组"),
        (r'\bnet\s+user\b', "用户管理(Windows)"),
        (r'\bnet\s+localgroup\b', "组管理(Windows)"),
        (r'\bdscl\b', "目录服务(macOS)"),
        (r'\bsysadminctl\b', "系统管理员(macOS)"),
        
        # 服务管理
        (r'\bsystemctl\s+(start|stop|restart|enable|disable)\b', "Systemd 服务管理"),
        (r'\bservice\s+(start|stop)\b', "服务管理"),
        (r'\bsc\s+(start|stop|config|delete)\b', "Windows 服务管理"),
    ]
    
    # 中危命令模式 (MEDIUM)
    MEDIUM_PATTERNS = [
        # 文件覆写
        (r'>\s+\S+', "重定向覆写文件"),
        (r'>>\s+\S+', "追加重定向"),
        (r'\btee\b', "输出到文件"),
        (r'\bsponge\b', "就地编辑"),
        (r'\bsed\s+-i', "就地编辑"),
        (r'\bperl\s+-i', "就地编辑"),
        
        # 网络下载
        (r'\bcurl\s+.*-O', "下载文件"),
        (r'\bcurl\s+.*-o', "下载到指定文件"),
        (r'\bcurl\s+.*-L', "跟随重定向下载"),
        (r'\bwget\b', "下载文件"),
        (r'\bInvoke-WebRequest\b', "PowerShell 下载"),
        (r'\bInvoke-RestMethod\b', "PowerShell REST"),
        (r'\biwr\b', "PowerShell 简写下载"),
        (r'\birm\b', "PowerShell 简写 REST"),
        (r'\bStart-BitsTransfer\b', "BITS 下载"),
        (r'\baria2c\b', "多线程下载"),
        (r'\baxel\b', "多线程下载"),
        
        # 远程执行
        (r'\bcurl\s+.*\|\s*bash', "下载并执行 bash"),
        (r'\bcurl\s+.*\|\s*sh', "下载并执行 sh"),
        (r'\bwget\s+.*\|\s*bash', "下载并执行 bash"),
        (r'\birm\s+.*\|\s*iex', "下载并执行 PowerShell"),
        (r'\biex\s*\(\s*iwr', "下载并执行 PowerShell"),
        (r'\bInvoke-Expression\b', "执行 PowerShell 字符串"),
        (r'\beval\b', "执行字符串"),
        
        # 压缩/解压
        (r'\btar\s+-x', "解压 tar"),
        (r'\bunzip\b', "解压 zip"),
        (r'\b7z\s+x', "解压 7z"),
        (r'\brar\s+x', "解压 rar"),
        (r'\bgzip\s+-d', "解压 gzip"),
        (r'\bbzip2\s+-d', "解压 bzip2"),
        (r'\bxz\s+-d', "解压 xz"),
        (r'\bExpand-Archive\b', "PowerShell 解压"),
        (r'\bCompress-Archive\b', "PowerShell 压缩"),
        
        # 环境变量
        (r'\bexport\s+\w+=', "设置环境变量"),
        (r'\bsetx\b', "永久设置变量(Windows)"),
        (r'\$env:\w+\s*=', "设置 PowerShell 环境变量"),
        
        # 进程管理
        (r'\bkill\s+', "终止进程"),
        (r'\bkillall\b', "终止所有匹配进程"),
        (r'\bpkill\b', "按模式终止"),
        (r'\bxkill\b', "图形终止"),
        (r'\btaskkill\b', "终止任务(Windows)"),
        (r'\bStop-Process\b', "停止进程(PowerShell)"),
    ]
    
    def assess_command(self, command: str) -> RiskAssessment:
        """评估命令风险等级"""
        command_lower = command.lower().strip()
        
        # 检查极高危模式
        for pattern, reason in self.CRITICAL_PATTERNS:
            if re.search(pattern, command_lower):
                return RiskAssessment(
                    level=RiskLevel.CRITICAL,
                    category="CRITICAL_COMMAND",
                    reason=reason
                )
        
        # 检查高危模式
        for pattern, reason in self.HIGH_PATTERNS:
            if re.search(pattern, command_lower):
                return RiskAssessment(
                    level=RiskLevel.HIGH,
                    category="HIGH_RISK_COMMAND",
                    reason=reason
                )
        
        # 检查中危模式
        for pattern, reason in self.MEDIUM_PATTERNS:
            if re.search(pattern, command_lower):
                return RiskAssessment(
                    level=RiskLevel.MEDIUM,
                    category="MEDIUM_RISK_COMMAND",
                    reason=reason
                )
        
        # 低危命令
        return RiskAssessment(
            level=RiskLevel.LOW,
            category="LOW_RISK_COMMAND",
            reason="命令不在危险模式列表中"
        )


def main():
    """命令行接口"""
    if len(sys.argv) < 2:
        print("Usage: python risk_assessor.py <path|command> [value]")
        print("  path <path>     - 评估路径风险")
        print("  command <cmd>   - 评估命令风险")
        sys.exit(1)
    
    action = sys.argv[1]
    value = sys.argv[2] if len(sys.argv) > 2 else ""
    
    if action == "path":
        assessor = PathRiskAssessor()
        result = assessor.assess_path(value)
        print(f"路径: {value}")
        print(f"风险等级: {result.level.value}")
        print(f"类别: {result.category}")
        print(f"原因: {result.reason}")
    
    elif action == "command":
        assessor = CommandRiskAssessor()
        result = assessor.assess_command(value)
        print(f"命令: {value}")
        print(f"风险等级: {result.level.value}")
        print(f"类别: {result.category}")
        print(f"原因: {result.reason}")
    
    else:
        print(f"未知操作: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
