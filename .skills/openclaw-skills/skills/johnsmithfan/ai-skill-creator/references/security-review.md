# CISO 安全审查详细清单

> **版本**：v1.0.0
> **依据**：CISO-001 STRIDE 威胁建模 + CVSS 漏洞评分
> **适用范围**：所有 AI Skill 发布前必须通过

---

## 目录

1. [RED FLAGS 清单](#1-red-flags-清单)
2. [STRIDE 威胁建模检查表](#2-stride-威胁建模检查表)
3. [CVSS 评分标准](#3-cvss-评分标准)
4. [权限评估矩阵](#4-权限评估矩阵)
5. [审查报告模板](#5-审查报告模板)

---

## 1. RED FLAGS 清单

### 🚨 发现以下任意一项 → 立即拒绝

| 类别 | 危险模式 | 说明 |
|------|---------|------|
| **网络外传** | `curl`、`wget`、`fetch`、`http.request` 到未知 URL | 数据可能外泄 |
| **凭证窃取** | 读取 `~/.ssh/`、`~/.aws/`、`~/.config/`、`credentials` | 窃取密钥 |
| **身份冒充** | 读取 `MEMORY.md`、`USER.md`、`SOUL.md`、`IDENTITY.md` | 冒充用户身份 |
| **代码注入** | `eval()`、`exec()`、`new Function()` 处理用户输入 | 远程代码执行 |
| **混淆攻击** | `base64.decode()`、`atob()` 未知内容 | 隐藏恶意代码 |
| **权限提升** | 请求 `sudo`、`admin`、系统级权限 | 越权操作 |
| **Cookie 窃取** | 访问浏览器 `document.cookie`、`localStorage` | 会话劫持 |
| **文件污染** | 路径拼接含 `../`、动态路径拼接用户输入 | 目录遍历攻击 |
| **依赖投毒** | `pip install`、`npm install` 无版本锁定 | 供应链攻击 |
| **外部数据源** | API key 硬编码、环境变量注入未验证 | 密钥泄露 |
| **裸 IP 调用** | 直接请求 IP 地址而非域名 | 规避安全监控 |

### ⚠️ 发现以下项 → 高风险审查

| 类别 | 模式 | 审查要点 |
|------|------|---------|
| 文件删除 | `rm`、`unlink`、`del` | 确认在 workspace 内 |
| 环境变量 | `process.env`、`os.environ` | 确认变量名可信 |
| 子进程 | `child_process.exec`、`subprocess.run` | 确认命令白名单 |
| 正则表达式 | `ReDoS` 风险模式 | `(.+)*`、`(a+)+` 等 |
| 序列化 | `pickle.loads`、`yaml.load` | 确认输入来源 |

---

## 2. STRIDE 威胁建模检查表

### S — Spoofing（身份伪造）

| 检查项 | 问题 | 通过标准 |
|--------|------|---------|
| Skill 名称唯一性 | 名称是否与系统命令/其他 Skill 重名？ | 唯一的 slug |
| 来源验证 | 能否伪造 Skill 发布者？ | ClawHub 签名验证 |
| 内容完整性 | 发布后是否被篡改？ | SHA256 校验 |

### T — Tampering（篡改）

| 检查项 | 问题 | 通过标准 |
|--------|------|---------|
| 路径验证 | 文件路径是否可被用户注入 `../`？ | 拒绝含 `../` 的路径 |
| 输入验证 | 外部输入是否经过校验？ | Schema 验证 |
| 依赖锁定 | 依赖版本是否锁定？ | lock 文件存在 |
| 脚本完整性 | 脚本是否被篡改？ | SHA256 校验 |

### R — Repudiation（抵赖）

| 检查项 | 问题 | 通过标准 |
|--------|------|---------|
| 操作日志 | Skill 操作是否有日志？ | 记录到 references/ |
| 版本追溯 | 变更是否可追溯？ | semver + changelog |
| 发布签名 | 发布者身份是否可验证？ | ClawHub auth |

### I — Information Disclosure（信息泄露）

| 检查项 | 问题 | 通过标准 |
|--------|------|---------|
| 硬编码密钥 | 代码中是否含 API key/令牌？ | 零容忍 |
| PII 处理 | 是否处理个人身份信息？ | 需脱敏说明 |
| 错误信息 | 错误信息是否泄露敏感路径？ | 泛化错误信息 |
| 日志脱敏 | 日志中是否含敏感数据？ | 过滤 PII |

### D — Denial of Service（拒绝服务）

| 检查项 | 问题 | 通过标准 |
|--------|------|---------|
| 资源限制 | 是否有超时/内存限制？ | 超时中断 |
| 循环保护 | 是否有无限循环风险？ | 递归深度限制 |
| 文件大小 | 是否限制处理文件大小？ | 拒绝超大文件 |
| 贪婪匹配 | 正则是否贪婪匹配？ | 非贪婪优先 |

### E — Elevation of Privilege（权限提升）

| 检查项 | 问题 | 通过标准 |
|--------|------|---------|
| 最小权限 | 权限是否超出功能所需？ | 工具权限最小化 |
| Workspace 边界 | 是否写入 workspace 外？ | 限定 workspace |
| 命令白名单 | exec 命令是否在白名单？ | 明确列出 |

---

## 3. CVSS 评分标准

### 评分向量

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
     ↑    ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
     网络  低  无  无  未变更 高  高  高
```

### 严重性等级

| 分数范围 | 等级 | 决策 |
|----------|------|------|
| 9.0-10.0 | Critical | 🚫 拒绝发布，紧急修复 |
| 7.0-8.9 | High | 🚫 拒绝发布，修复后重审 |
| 4.0-6.9 | Medium | ⚠️ 通知用户，修复后发布 |
| 0.1-3.9 | Low | ✅ 通过，择机修复 |

### 常见漏洞 CVSS 评估

| 漏洞类型 | 典型 CVSS | 决策 |
|---------|----------|------|
| 命令注入 | 9.8 | 🚫 |
| SQL 注入 | 9.8 | 🚫 |
| 硬编码密钥 | 7.5 | 🚫 |
| 路径遍历 | 7.5 | 🚫 |
| 敏感文件读取 | 7.5 | 🚫 |
| 正则 DoS | 5.3 | ⚠️ |
| 信息泄露 | 3.7 | ✅ |

---

## 4. 权限评估矩阵

### 工具权限清单

| 工具 | 权限级别 | 评估要点 |
|------|---------|---------|
| `read` | 文件读取 | 读取范围是否限定？ |
| `write` | 文件写入 | 写入路径是否限定 workspace？ |
| `exec` | 命令执行 | 命令是否白名单化？ |
| `browser` | 浏览器控制 | 是否复用登录态？ |
| `nodes` | 设备控制 | 操作范围是否明确？ |
| `message` | 消息发送 | 发送目标是否用户授权？ |
| `cron` | 定时任务 | 执行频率是否合理？ |

### 权限申请书模板

```markdown
## 权限申请书

Skill 名称：<name>
版本：<version>

| 工具 | 权限范围 | 用途 | 风险评估 |
|------|---------|------|---------|
| read | `workspace/**/*.txt` | 读取用户文档 | 🟢 低 |
| write | `workspace/output/` | 输出结果 | 🟢 低 |
| exec | `python, node` | 运行脚本 | 🟡 中 |

最小权限声明：✅ Skill 不需要任何超出上述范围的权限
```

---

## 5. 审查报告模板

```
═══════════════════════════════════════════════════════════════
SKILL SECURITY REVIEW REPORT
═══════════════════════════════════════════════════════════════

Skill: <name>
Version: <version>
Author: <author>
Review Date: <ISO date>
Reviewer: CISO-001

───────────────────────────────────────────────────────────────
SECTION 1: RED FLAGS SCAN
───────────────────────────────────────────────────────────────

扫描方法：逐文件静态审查 + 动态执行测试

🚨 RED FLAGS FOUND: [None / List]
  • [file:line] <flag description>
  • [file:line] <flag description>

───────────────────────────────────────────────────────────────
SECTION 2: STRIDE THREAT MODEL
───────────────────────────────────────────────────────────────

S - Spoofing:     [✅ PASS / ❌ FAIL] — <reason>
T - Tampering:    [✅ PASS / ❌ FAIL] — <reason>
R - Repudiation:  [✅ PASS / ❌ FAIL] — <reason>
I - Info Disclosure: [✅ PASS / ❌ FAIL] — <reason>
D - Denial of Service: [✅ PASS / ❌ FAIL] — <reason>
E - Elevation:    [✅ PASS / ❌ FAIL] — <reason>

───────────────────────────────────────────────────────────────
SECTION 3: CVSS VULNERABILITY ASSESSMENT
───────────────────────────────────────────────────────────────

漏洞总数：<N>
Critical: <N>  High: <N>  Medium: <N>  Low: <N>

| 漏洞 | 文件:行 | CVSS | 严重性 | 修复方案 |
|------|---------|------|--------|---------|
| ... | ... | ... | ... | ... |

───────────────────────────────────────────────────────────────
SECTION 4: PERMISSIONS ASSESSMENT
───────────────────────────────────────────────────────────────

Files Read:  [list]
Files Write: [list]
Commands:    [list]
Network:     [list]

权限合理性： [✅ 合理 / ⚠️ 需澄清 / 🚫 超出必要范围]

───────────────────────────────────────────────────────────────
SECTION 5: DEPENDENCY SCAN
───────────────────────────────────────────────────────────────

声明依赖：<list>
已知 CVE： [None / List with CVSS]

───────────────────────────────────────────────────────────────
VERDICT
───────────────────────────────────────────────────────────────

OVERALL: [✅ APPROVED / 🚫 REJECTED / ⚠️ CONDITIONAL APPROVAL]

条件（如果有）：
1. [item]
2. [item]

Action Items:
• [item] — Due: <date>

═══════════════════════════════════════════════════════════════
```

---

## 附录：快速扫描命令

```bash
# 搜索敏感模式
grep -rn "eval\s*(" scripts/
grep -rn "exec\s*(" scripts/
grep -rn "curl\|wget" scripts/
grep -rn "base64" scripts/
grep -rn "\.ssh\|credentials\|\.aws" scripts/
grep -rn "MEMORY.md\|USER.md\|SOUL.md" scripts/

# 搜索硬编码密钥模式
grep -rn "sk-[0-9a-zA-Z]\{20,\}" .
grep -rn "ghp_\|github_pat_" .
grep -rn "-----BEGIN.*PRIVATE KEY-----" .

# 搜索路径遍历
grep -rn "\.\.\/" scripts/
```
