# OpenClaw 安全审计器 🛡️

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**一款强制执行的安全审计 AgentSkill，在工具调用前拦截危险操作，防止磁盘格式化、系统目录删除、敏感文件访问等灾难性操作。**

## 🎯 项目简介

OpenClaw 安全审计器是一个 OpenClaw AgentSkill，它在任何工具被调用**之前**执行安全检查。与传统的事后告警不同，本技能在源头拦截危险操作，要么自动阻止，要么要求用户明确确认。

### 核心特性

- **执行前审计** — 检查发生在工具调用之前，而非之后
- **多级风险分类** — 极高危 / 高危 / 中危 / 低危 四个等级
- **跨平台支持** — Windows、macOS、Linux 全覆盖
- **全面覆盖** — 文件操作、系统命令、敏感路径
- **用户确认流程** — 高危操作需要明确批准

## 📊 风险等级

| 等级 | 图标 | 描述 | 处理方式 |
|------|------|------|----------|
| **极高危** | 🔴 | 灾难性操作（磁盘格式化、删除系统目录） | **自动阻止** |
| **高危** | 🟠 | 危险操作（删除文件、安装软件） | **需要用户确认** |
| **中危** | 🟡 | 需谨慎处理（覆写文件、网络下载） | **记录并提醒** |
| **低危** | 🟢 | 安全操作（读取文件、列出目录） | **正常执行** |

## 🛡️ 防护范围

### 🔴 极高危（自动阻止）

- **磁盘格式化**：`format`、`mkfs`、`diskpart erase`、`newfs_*`
- **系统目录删除**：`rm -rf /`、`rd /s /q C:\`
- **直接写磁盘**：`dd of=/dev/sd*`
- **分区操作**：`fdisk`、`parted`、`diskutil partitionDisk`
- **关键系统服务**：杀死 init 进程、停止 systemd

### 🟠 高危（需要确认）

- **文件删除**：`rm -rf`、`del /s`、`Remove-Item`
- **软件安装**：`brew install`、`apt install`、`winget install`
- **系统配置**：修改 hosts、防火墙规则、PATH 环境变量
- **计划任务**：`crontab`、`schtasks`、`launchctl`
- **权限修改**：`chmod -R`、`chown`、`icacls`
- **用户管理**：`useradd`、`net user`

### 🟡 中危（记录提醒）

- **文件覆写**：`> file`、`tee`
- **网络下载**：`curl`、`wget`、`Invoke-WebRequest`
- **远程执行**：`curl | bash`、`iex (iwr)`
- **进程管理**：`kill`、`taskkill`、`Stop-Process`

## 📁 文件结构

```
openclaw-security-auditor/
├── SKILL.md                          # 主技能定义文件（必需）
├── README.md                         # 本文件
├── LICENSE                           # MIT 开源许可
├── references/
│   ├── command-risk-reference.md     # 命令风险参考数据库
│   └── path-risk-reference.md        # 路径风险分类参考
└── scripts/
    └── risk_assessor.py              # 可选的命令行风险评估工具
```

## 🚀 安装方法

### OpenClaw 用户

1. 将本技能克隆或下载到您的 OpenClaw 技能目录：

   **Windows (PowerShell)**：
   ```powershell
   git clone https://github.com/KukaNo996/openclaw-security-auditor.git `
     "$env:USERPROFILE\.qclaw\skills\qclaw-security-auditor"
   ```

   **macOS / Linux**：
   ```bash
   git clone https://github.com/KukaNo996/openclaw-security-auditor.git \
     ~/.qclaw/skills/qclaw-security-auditor
   ```

2. 下次会话启动时技能将自动加载。

### 手动安装

将整个 `openclaw-security-auditor` 文件夹复制到：
- **Windows**：`C:\Users\<用户名>\.openclaw\skills\`
- **macOS/Linux**：`~/.openclaw/skills/`

## 📖 使用说明

本技能**强制自动执行**——无需手动激活。它会透明地拦截工具调用：

### 示例 1：阻止极高危操作

```
用户: 帮我格式化 D 盘

AI: 🛡️ 【安全审计阻止】
    检测到极高危操作，已自动阻止执行：

    操作类型: 磁盘格式化
    目标: D:
    风险: 数据完全丢失

    此操作可能导致：
    - D 盘所有数据永久丢失
    - 文件系统被重建

    如需帮助寻找替代方案，请说明您的具体需求。
```

### 示例 2：要求用户确认

```
用户: 删除 D:\Downloads\test.pdf

AI: ⚠️ 【安全审计确认】

    检测到高危操作，请确认后执行：

    操作详情:
    ━━━━━━━━━━━━━━━━━━━━━━
    类型: 删除文件
    目标: D:\Downloads\test.pdf
    ━━━━━━━━━━━━━━━━━━━━━━

    请回复确认：
    ✅ 确认
    ❌ 取消
```

### 示例 3：安全操作

```
用户: 读取 C:\Users\test\document.txt 的内容

AI: [正常执行，无需干预]
```

### 示例 4：中危操作提醒

```
用户: 帮我清空 D:\12746\Downloads\流量信息.txt 文件中的数据

AI: ⚠️ 【安全审计确认】

    检测到覆写文件操作，请确认后执行：

    操作详情:
    ━━━━━━━━━━━━━━━━━━━━━━
    类型: 清空文件内容
    目标: D:\12746\Downloads\流量信息.txt
    ━━━━━━━━━━━━━━━━━━━━━━

    请回复 确认 执行操作，或 取消 放弃。
```

## 🔧 配置选项

本技能开箱即用。如需高级自定义：

### 设为可选

默认情况下，技能在元数据中设置了 `always: true`。如需改为可选：

```yaml
metadata:
  openclaw:
    emoji: "🛡️"
    always: false  # 从 true 改为 false
```

### 自定义风险模式

编辑 `scripts/risk_assessor.py` 添加自定义的命令或路径模式：

```python
# 添加自定义极高危模式
CRITICAL_PATTERNS = [
    (r'\bmy_dangerous_command\b', "自定义的危险命令"),
    # ...
]

# 添加自定义高危路径
USER_SENSITIVE_PATTERNS = [
    r'\.my_secrets/',
    r'\.private_keys/',
    # ...
]
```

## 🗺️ 风险评估参考

### 命令风险分类

| 类别 | 示例 | 风险等级 |
|------|------|----------|
| 磁盘操作 | `format`、`mkfs`、`dd` | 🔴 极高危 |
| 系统删除 | `rm -rf /`、`rd /s C:\` | 🔴 极高危 |
| 文件删除 | `rm -rf`、`del` | 🟠 高危 |
| 包管理 | `brew install`、`apt install` | 🟠 高危 |
| 系统配置 | `netsh`、`ufw`、hosts | 🟠 高危 |
| 网络下载 | `curl`、`wget` | 🟡 中危 |
| 文件覆写 | `>`、`tee` | 🟡 中危 |
| 文件读取 | `cat`、`Get-Content` | 🟢 低危 |
| 目录列表 | `ls`、`dir` | 🟢 低危 |

### 路径风险分类

| 路径类型 | 示例 | 风险等级 |
|----------|------|----------|
| 系统目录 | `C:\Windows`、`/System`、`/etc` | 🔴 极高危 |
| 程序目录 | `C:\Program Files`、`/usr/bin` | 🔴 极高危 |
| 凭证文件 | `~/.ssh`、`~/.aws`、`.env` | 🟠 高危 |
| 浏览器数据 | Chrome/Firefox 配置目录 | 🟠 高危 |
| 密码管理器 | 1Password、Bitwarden 数据 | 🟠 高危 |
| 用户文档 | `~/Documents`、`D:\` | 🟡 中危 |
| 工作区 | `./workspace` | 🟢 低危 |

## 🤝 参与贡献

欢迎提交以下贡献：

- **新的风险模式** — 需要审计的命令或路径
- **问题报告** — 误报/漏报情况
- **文档改进** — 更好的示例、翻译
- **代码增强** — Python 评估工具的改进

### 开发测试

```bash
# 克隆仓库
git clone https://github.com/KukaNo996/openclaw-security-auditor.git
cd openclaw-security-auditor

# 测试 Python 风险评估工具
python scripts/risk_assessor.py path "/etc/passwd"
python scripts/risk_assessor.py command "rm -rf /"

# 预期输出示例：
# 路径: /etc/passwd
# 风险等级: CRITICAL
# 类别: SYSTEM_CRITICAL
# 原因: 路径匹配系统关键路径模式: ^/etc/
```

## 📜 开源许可

本项目采用 MIT 许可证 —— 详见 [LICENSE](LICENSE) 文件。

## 🔗 相关项目

- [OpenClaw](https://github.com/openclaw/openclaw) — 本技能所设计的 AI 助手框架
- [ClawHub](https://clawhub.com) — 发现更多 OpenClaw 技能

## ❓ 常见问题

### Q: 为什么有些操作需要确认？

**A:** 高危操作（如删除文件、安装软件）可能导致数据丢失或系统变更。为了防止误操作，我们要求用户明确确认。

### Q: 如何绕过安全检查？

**A:** 不建议绕过。如果确实需要执行某些操作，安全审计器会引导您明确确认。这是为了保护您的数据和系统安全。

### Q: 可以添加自定义的危险命令吗？

**A:** 可以。编辑 `scripts/risk_assessor.py` 文件，在对应的模式列表中添加您的自定义命令模式。

### Q: 这个技能会影响性能吗？

**A:** 影响极小。安全检查是基于正则表达式的快速匹配，通常在毫秒级完成，不会对用户体验产生明显影响。

## 📝 更新日志

### v1.0.0 (2024-03-18)

- 首次发布
- 四级风险分类系统
- 跨平台支持（Windows、macOS、Linux）
- 完整的命令和路径参考数据库
- Python 命令行风险评估工具

---

**🛡️ 安全第一 —— 预防胜于补救。**
