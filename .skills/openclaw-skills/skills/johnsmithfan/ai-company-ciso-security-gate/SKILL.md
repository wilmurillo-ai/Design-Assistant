---
name: "AI Company CISO Security Gate"
slug: ai-company-ciso-security-gate
version: 2.1.0
homepage: https://clawhub.com/skills/ai-company-ciso-security-gate
description: |
  AI Company CISOsecurity门禁模块v2.1.0。STRIDE威胁建模、CVSS漏洞评分、security红线审查、最终发布审查、CEO-EXEC危机直通接口security规范。
  触发关键词：security审查、security检查、漏洞扫描、威胁建模、危机直通、双重审批
license: MIT-0
tags: [ai-company, ciso, security, gate, threat-modeling, crisis-channel, dual-approval]
triggers:
  - security审查
  - security检查
  - 漏洞扫描
  - 威胁建模
  - security review
  - security gate
  - 危机直通
  - 双重审批
  - crisis channel
  - dual approval
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        skill_path:
          type: string
          description: 待审查Skill路径
        review_depth:
          type: string
          enum: [basic, full, critical]
          default: full
          description: 审查深度
        check_types:
          type: array
          items:
            type: string
            enum: [stride, cvss, red_flags, permissions, dependencies, compliance]
          default: [stride, cvss, red_flags, permissions]
          description: 检查类型
      required: [skill_path]
  outputs:
    type: object
    schema:
      type: object
      properties:
        verdict:
          type: string
          enum: [APPROVED, CONDITIONAL, REJECTED]
        overall_score:
          type: number
        stride_results:
          type: array
          items:
            type: object
            properties:
              category:
                type: string
              status:
                type: string
                enum: [PASS, WARNING, FAIL]
              threats:
                type: array
              mitigations:
                type: array
        cvss_results:
          type: array
          items:
            type: object
            properties:
              vulnerability:
                type: string
              severity:
                type: string
                enum: [LOW, MEDIUM, HIGH, CRITICAL]
              score:
                type: number
              status:
                type: string
        red_flag_results:
          type: array
          items:
            type: string
        permission_audit:
          type: object
        security_report:
          type: string
        recommendations:
          type: array
          items:
            type: string
      required: [verdict, overall_score]
  errors:
    - code: SECURITY_001
      message: "Skill path not found"
    - code: SECURITY_002
      message: "CVSS score >= 7.0 (REJECTED)"
    - code: SECURITY_003
      message: "RED FLAG detected"
    - code: SECURITY_004
      message: "Dangerous permission detected"
    - code: SECURITY_005
      message: "Dependency security issue"
permissions:
  files: [read]
  network: []
  commands: []
  mcp: []
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-ciso
    - ai-company-standardization
    - ai-company-engr
  cli: []
references:
  - path: references/stride-assessment-l4.md
    description: ENGR L4 STRIDE评估报告 (CVSS 2.92)
  - path: references/stride-assessment-crisis-channel.md
    description: CEO-EXEC危机直通STRIDE评估+白名单 (CVSS 2.87)
  - path: references/dual-approval-e2e-test.md
    description: 双重审批E2E测试用例 (10个TC)
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: security
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  tags: [ai-company, ciso, security, gate]
---

# AI Company CISO Security Gate v2.1.0

> CISO主导的security门禁模块。STRIDE + CVSS + 红线审查 + 发布审查 + CEO-EXEC危机直通security规范。

## P0security紧急修复完成 (2026-04-17)

✅ **ENGR L4 STRIDE评估**: CVSS 2.92, conditional-pass  
✅ **CEO-EXEC危机直通 STRIDE评估**: CVSS 2.87, conditional-pass  
✅ **双重审批E2E测试**: 10个测试用例  
✅ **危机白名单**: 5允许+5禁止  
✅ **Skill版本更新**: CISO v2.1.0, ENGR v1.0.1, Harness v1.0.2

---

## 概述

**ai-company-ciso-security-gate** 是AIskilllearning流程的核心security模块，负责：

1. **STRIDE威胁建模**: 识别6类security威胁
2. **CVSS漏洞评分**: 量化漏洞严重程度
3. **RED FLAGS检测**: 识别危险信号
4. **权限audit**: 检查permissions声明
5. **依赖审查**: 分析依赖security性
6. **发布审查**: 最终security放行

---

## Module 1: STRIDE威胁建模

### 六类威胁

| 威胁类型 | 描述 | 典型攻击 |
|----------|------|----------|
| **S**poofing | 身份欺骗 | 伪造Token、会话劫持 |
| **T**ampering | 数据篡改 | 中间人攻击、注入 |
| **R**epudiation | 否认操作 | 日志伪造、抵赖 |
| **I**nformation Disclosure | 信息泄露 | 数据窃取、侧信道 |
| **D**enial of Service | 拒绝服务 | 资源耗尽、流量攻击 |
| **E**levation of Privilege | 权限提升 | 越权访问、逃逸 |

### 评估矩阵

```yaml
stride_assessment:
  Spoofing:
    likelihood: LOW|MEDIUM|HIGH
    impact: LOW|MEDIUM|HIGH
    status: PASS|WARNING|FAIL
    mitigations: []
  
  Tampering:
    likelihood: LOW|MEDIUM|HIGH
    impact: LOW|MEDIUM|HIGH
    status: PASS|WARNING|FAIL
    mitigations: []
  
  # ... 其他威胁类型
```

---

## Module 2: CVSS漏洞评分

### 评分标准

| 评分范围 | 等级 | 说明 |
|----------|------|------|
| 0.0 - 3.9 | LOW | 低危漏洞，可接受 |
| 4.0 - 6.9 | MEDIUM | 中危漏洞，需修复 |
| 7.0 - 8.9 | HIGH | 高危漏洞，必须修复 |
| 9.0 - 10.0 | CRITICAL | 严重漏洞，拒绝发布 |

### 评分方法

```python
def calculate_cvss(issue: SecurityIssue) -> float:
    """
    CVSS v3.1 简化评分
    """
    # Base Score
    attack_vector = issue.attack_vector      # N|A|L|P
    attack_complexity = issue.attack_complexity  # L|H
    privileges_required = issue.privileges    # N|L|H
    user_interaction = issue.user_interaction  # N|R
    scope = issue.scope                        # U|C
    confidentiality = issue.confidentiality    # N|L|H
    integrity = issue.integrity               # N|L|H
    availability = issue.availability         # N|L|H
    
    # 计算逻辑
    return cvss_score
```

### 通过标准

```
✅ CVSS < 7.0: PASS
⚠️  7.0 <= CVSS < 9.0: WARNING (需修复)
❌ CVSS >= 9.0: FAIL (拒绝发布)
```

---

## Module 3: RED FLAGS检测

### 危险信号清单

| 类别 | RED FLAG | 说明 |
|------|----------|------|
| 文件操作 | `os.remove`, `shutil.rmtree` | 无确认的删除 |
| 网络 | `requests` 无证书验证 | 明文传输 |
| 代码执行 | `eval`, `exec`, `subprocess` 动态参数 | 注入风险 |
| 权限 | `sudo`, `chmod 777` | 过度权限 |
| 密钥 | `password`, `token`, `secret` 硬编码 | 密钥泄露 |
| 外部调用 | `curl|bash` 管道执行 | 命令注入 |
| 路径 | 绝对路径 `C:\`, `/root/` | 硬编码路径 |
| 数据 | 未加密的 `pickle.load` | 反序列化攻击 |

### 检测规则

```python
RED_FLAGS = {
    'file_danger': [
        r'os\.remove\(',
        r'shutil\.rmtree\(',
        r'unlink\(',
    ],
    'network_danger': [
        r'requests\.[a-z]+\([^)]*\)\s*(?!.*verify)',
    ],
    'code_exec': [
        r'\beval\(',
        r'\bexec\(',
        r'os\.system\(',
    ],
    'subprocess_danger': [
        r'subprocess\.(run|call|Popen)\([^)]*shell\s*=\s*True',
    ],
    'secret_hardcode': [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
    ],
}

def detect_red_flags(skill_content: str) -> list[RedFlag]:
    findings = []
    for category, patterns in RED_FLAGS.items():
        for pattern in patterns:
            matches = re.finditer(pattern, skill_content)
            for m in matches:
                findings.append(RedFlag(
                    category=category,
                    match=m.group(),
                    line=skill_content[:m.start()].count('\n') + 1,
                ))
    return findings
```

---

## Module 4: 权限audit

### 权限检查表

```yaml
permission_audit:
  files:
    - name: "read"
      risk: LOW
      requirement: "仅读取必要文件"
    - name: "write"
      risk: MEDIUM
      requirement: "需确认文件路径security"
    - name: "delete"
      risk: HIGH
      requirement: "必须二次确认"
  
  network:
    - name: "api"
      risk: MEDIUM
      requirement: "HTTPS强制"
    - name: "raw"
      risk: HIGH
      requirement: "禁止明文传输"
  
  commands:
    - name: "read_only"
      risk: LOW
    - name: "all"
      risk: CRITICAL
      requirement: "禁止发布"

  mcp:
    - name: "sessions_send"
      risk: MEDIUM
      requirement: "仅限受信任会话"
    - name: "subprocess_exec"
      risk: CRITICAL
      requirement: "禁止"
```

---

## 接口定义

### `security-gate`

执行完整security门禁。

**Input:**
```yaml
skill_path: "~/.qclaw/skills/new-skill"
review_depth: full
check_types: [stride, cvss, red_flags, permissions]
```

**Output:**
```yaml
verdict: APPROVED
overall_score: 88
stride_results:
  - category: Spoofing
    status: PASS
    threats: []
    mitigations: []
  - category: Tampering
    status: WARNING
    threats: ["配置可被修改"]
    mitigations: ["添加完整性校验"]
cvss_results:
  - vulnerability: "日志路径遍历"
    severity: LOW
    score: 3.5
    status: PASS
red_flag_results: []
permission_audit:
  files: [{type: "read", risk: "LOW", status: "PASS"}]
  network: [{type: "api", risk: "MEDIUM", status: "PASS"}]
security_report: "~/.qclaw/reports/security-{skill_name}-{timestamp}.md"
recommendations:
  - "建议添加输入验证"
  - "日志建议脱敏处理"
```

### `quick-check`

快速security扫描。

**Input:**
```yaml
skill_path: "string"
```

**Output:**
```yaml
has_issues: false
red_flag_count: 0
cvss_max_score: 0.0
quick_verdict: PASS|WARNING|FAIL
```

---

## security红线 (绝对禁止)

```
❌ CVSS >= 7.0
❌ RED FLAG: eval/exec 动态参数
❌ RED FLAG: rm -rf 无确认
❌ RED FLAG: 密钥硬编码
❌ permissions: commands: all
❌ permissions: mcp: subprocess_exec
❌ 无输入验证的文件操作
❌ 明文传输敏感数据
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 |
|------|-----|--------|
| 效率 | 扫描响应时间 | ≤ 30秒 |
| 覆盖率 | 威胁检测覆盖率 | 100% |
| 准确率 | CVSS评分准确度 | ≥ 90% |
| 通过率 | 首次通过率 | ≥ 80% |

---

## Section 4.4: CEO-EXEC危机直通接口security规范

### 4.4.1 架构概述

CEO-EXEC危机直通接口是AI Companygovernance体系中的最高优先级通信通道，用于在紧急情况下绕过常规审批流程，实现秒级决策响应。

```
┌─────────┐    危机事件    ┌─────────┐    直通请求    ┌─────────┐
│  监控源  │ ────────────→ │  CEO    │ ────────────→ │  EXEC   │
│ (CISO)  │               │         │               │ (CTO等) │
└─────────┘               └────┬────┘               └────┬────┘
                               │                         │
                               └──────────┬──────────────┘
                                          │
                               ┌──────────▼──────────┐
                               │   CISO强制审批      │
                               │  (≤24h自动撤销)     │
                               └──────────┬──────────┘
                                          │
                               ┌──────────▼──────────┐
                               │   独立audit流+      │
                               │   区块链存证       │
                               └─────────────────────┘
```

### 4.4.2 危机白名单定义

**允许触发的危机类型 (5项):**

| 代码 | 危机类型 | 触发条件 | 响应时限 |
|------|----------|----------|----------|
| C-001 | P0security漏洞 | CVSS≥7.0或主动攻击 | ≤5分钟 |
| C-002 | 生产事故 | 服务中断>30分钟 | ≤10分钟 |
| C-003 | compliance紧急 | 监管通知/法律诉讼 | ≤30分钟 |
| C-004 | 数据泄露 | 确认或疑似泄露 | ≤15分钟 |
| C-005 | 基础设施故障 | 核心系统不可用 | ≤10分钟 |

**禁止使用的场景 (5项):**

| 代码 | 禁止场景 | 违规后果 |
|------|----------|----------|
| X-001 | 常规功能发布 | 流程违规，记大过 |
| X-002 | 非紧急配置变更 | 流程违规，警告 |
| X-003 | 预算/采购审批 | 财务违规，audit介入 |
| X-004 | 人员任免 | HR违规，记大过 |
| X-005 | 非工作时间非紧急事务 | 滥用权限，警告 |

### 4.4.3 CISO强制审批机制

```yaml
crisis_channel_approval:
  # 触发条件验证
  trigger_validation:
    - check: crisis_type in whitelist
    - check: severity in [P0, P1]
    - check: impact_assessment.completed
  
  # CISO审批流程
  ciso_approval:
    required: true
    auto_escalation: "15 minutes no response"
    approval_timeout: "24 hours"
    auto_revoke: true  # 超时自动撤销
  
  # 双重确认机制
  dual_confirmation:
    primary: CEO
    secondary: CISO
    consensus_required: true
  
  # audit与存证
  audit_trail:
    blockchain_hash: true
    immutable_log: true
    retention_period: "7 years"
```

### 4.4.4 security条件

**STRIDE评估结果 (CVSS 2.87, Conditional Pass):**

| 威胁类型 | 评级 | 缓解措施 |
|----------|------|----------|
| Spoofing | LOW | 多因素认证+设备绑定 |
| Tampering | LOW | 数字签名+完整性校验 |
| Repudiation | MEDIUM | 区块链存证+时间戳 |
| Info Disclosure | LOW | 端到端加密+最小权限 |
| DoS | MEDIUM | 高可用架构+限流 |
| Elevation | LOW | 白名单匹配+人工复核 |

**有条件通过项:**
- D-001: DoS风险 → 缓解: 高可用+限流
- E-001: 权限越界风险 → 缓解: 白名单匹配

### 4.4.5 监控与audit

| 监控项 | 频率 | 责任人 | 触发条件 |
|--------|------|--------|----------|
| 直通事件审查 | 每次 | CISO | 事件驱动 |
| 白名单compliance检查 | 每周 | CLO | 定期 |
| 权限使用audit | 每月 | CISO | 定期 |
| CVSS复评 | 每季度 | CISO | 定期 |

---

## Section 4.5: ENGR L4生产操作security规范

### 4.5.1 L4权限定义

L4 (Level 4) 是生产环境最高操作权限，包括：
- 生产部署 (production deployment)
- 数据库变更 (schema migration)
- 配置变更 (config change)
- 紧急回滚 (emergency rollback)

### 4.5.2 双重审批机制

```yaml
l4_dual_approval:
  # 审批人要求
  approvers:
    primary: CTO
    secondary: CISO
    both_required: true
  
  # 审批流程
  process:
    - step: 技术评审 (ENGR)
    - step: security评审 (CISO)
    - step: 双重签章 (CTO+CISO)
    - step: 执行窗口 (变更management)
  
  # E2E测试要求
  e2e_testing:
    required: true
    test_cases: 10  # 详见references/dual-approval-e2e-test.md
    coverage: [auth, audit, rollback, alerting]
```

### 4.5.3 STRIDE评估 (CVSS 2.92, Conditional Pass)

| 威胁类型 | 评级 | 缓解措施 |
|----------|------|----------|
| Spoofing | LOW | 身份验证+审批链 |
| Tampering | MEDIUM | 变更audit+版本控制 |
| Repudiation | LOW | 完整audit日志 |
| Info Disclosure | LOW | 敏感信息脱敏 |
| DoS | LOW | 灰度发布+回滚 |
| Elevation | MEDIUM | 最小权限+时限 |

**有条件通过项:**
- T-004: DDL操作风险 → 缓解: 备份+staging预验
- E-002: P0豁免权限 → 缓解: 实时告警+人工复核

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 2.1.0 | 2026-04-17 | P0security紧急修复: +CEO-EXEC危机直通规范(§4.4) +ENGR L4规范(§4.5) +STRIDE签裁 +双重审批 +references |
| 1.0.0 | 2026-04-15 | 初始版本：STRIDE+CVSS+RED FLAGS+权限audit |

---

*本Skill由AI Company CISO开发*  
*作为ai-company-skill-learner的模块组件*  
*遵循NIST AI RMF标准*  
*P0security修复完成: 2026-04-17*
