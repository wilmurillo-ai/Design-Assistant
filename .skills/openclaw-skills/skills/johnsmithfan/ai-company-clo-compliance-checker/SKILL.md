---
name: "AI Company CLO Compliance Checker"
slug: ai-company-clo-compliance-checker
version: 1.0.0
homepage: https://clawhub.com/skills/ai-company-clo-compliance-checker
description: |
  AI Company CLOcompliance审查模块。许可证分析、版权检查、compliance报告、risk assessment。
  触发关键词：compliance检查、许可证审查、版权检查、法律审查
license: MIT-0
tags: [ai-company, clo, compliance, license, legal]
triggers:
  - compliance检查
  - 许可证审查
  - 版权检查
  - 法律审查
  - compliance check
  - license review
interface:
  inputs:
    type: object
    schema:
      type: object
      properties:
        skill_path:
          type: string
          description: 待审查skill路径
        jurisdiction:
          type: string
          enum: [GLOBAL, US, EU, CN, GDPR, CCPA]
          default: GLOBAL
          description: 适用法域
        check_dependencies:
          type: boolean
          default: true
          description: 是否检查依赖许可证
      required: [skill_path]
  outputs:
    type: object
    schema:
      type: object
      properties:
        verdict:
          type: string
          enum: [COMPLIANT, CONDITIONAL, NON_COMPLIANT]
        license_analysis:
          type: object
          properties:
            main_license:
              type: string
            license_family:
              type: string
            compatibility_score:
              type: number
            restrictions:
              type: array
              items:
                type: string
        copyright_check:
          type: object
          properties:
            has_copyright_notice:
              type: boolean
            copyright_year:
              type: string
            copyright_holder:
              type: string
        dependency_compliance:
          type: array
          items:
            type: object
            properties:
              dependency:
                type: string
              license:
                type: string
              status:
                type: string
                enum: [OK, WARNING, BLOCK]
              reason:
                type: string
        regulatory_compliance:
          type: object
        risk_assessment:
          type: object
          properties:
            overall_risk:
              type: string
              enum: [LOW, MEDIUM, HIGH, CRITICAL]
            risk_factors:
              type: array
              items:
                type: string
            recommendations:
              type: array
              items:
                type: string
        compliance_report:
          type: string
      required: [verdict, license_analysis]
  errors:
    - code: COMPLIANCE_001
      message: "Skill path not found"
    - code: COMPLIANCE_002
      message: "No license declared"
    - code: COMPLIANCE_003
      message: "Incompatible license detected"
    - code: COMPLIANCE_004
      message: "Copyright violation suspected"
    - code: COMPLIANCE_005
      message: "Regulatory compliance issue"
permissions:
  files: [read]
  network: []
  commands: []
  mcp: []
dependencies:
  skills:
    - ai-company-hq
    - ai-company-kb
    - ai-company-clo
    - ai-company-standardization
  cli: []
quality:
  saST: Pass
  vetter: Approved
  idempotent: true
metadata:
  category: governance
  layer: AGENT
  cluster: ai-company
  maturity: STABLE
  license: MIT-0
  standardized: true
  tags: [ai-company, clo, compliance, legal]
---

# AI Company CLO Compliance Checker v1.0

> CLO主导的compliance审查模块。许可证分析、版权检查、依赖审查、compliance报告。

---

## 概述

**ai-company-clo-compliance-checker** 是AIskilllearning流程的法务模块，负责：

1. **许可证分析**: 识别许可证类型，评估兼容性
2. **版权检查**: 验证版权声明有效性
3. **依赖审查**: 检查第三方依赖许可证
4. **compliance报告**: 生成compliance评估报告

---

## Module 1: 许可证分析

### 许可证分类

| 类别 | 许可证 | 商业可用 | 修改可用 | 分发限制 |
|------|--------|----------|----------|----------|
| **Permissive** | MIT, BSD, Apache 2.0 | ✅ | ✅ | 需声明 |
| **Copyleft** | GPL, AGPL, LGPL | ⚠️ | ✅ | 需开源 |
| **Weak Copyleft** | MPL, EPL | ⚠️ | ✅ | 文件级开源 |
| **Proprietary** | 商业许可证 | ❌ | ❌ | 禁止 |
| **Public Domain** | CC0, Unlicense | ✅ | ✅ | 无 |

### 兼容性矩阵

```yaml
license_compatibility:
  MIT:
    compatible_with: [MIT, BSD, Apache, GPL, LGPL, MPL]
    restrictions: ["必须保留版权声明"]
  
  Apache_2.0:
    compatible_with: [MIT, BSD, Apache, GPL, LGPL]
    restrictions: ["必须保留NOTICE文件", "专利授权"]
  
  GPL_3.0:
    compatible_with: [GPL, AGPL]
    restrictions: ["必须开源", "禁止添加限制"]
  
  CC0:
    compatible_with: [ALL]
    restrictions: []
```

### 许可证检测

```python
LICENSE_PATTERNS = {
    'MIT': [
        r'Permission is hereby granted.*MIT License',
        r'licensed under the MIT License',
    ],
    'Apache-2.0': [
        r'Licensed under the Apache License.*Version 2.0',
        r'Apache License.*Version 2.0',
    ],
    'GPL-3.0': [
        r'GNU General Public License.*version 3',
        r'GPL-3.0',
    ],
    'BSD': [
        r'Redistribution and use in source.*BSD',
        r'BSD 3-Clause License',
    ],
}

def detect_license(file_content: str) -> LicenseInfo:
    for license_type, patterns in LICENSE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, file_content, re.IGNORECASE):
                return LicenseInfo(
                    type=license_type,
                    confidence=0.9,
                    notice=extract_notice(file_content, pattern),
                )
    return LicenseInfo(type="UNKNOWN", confidence=0.0)
```

---

## Module 2: 版权检查

### 版权声明格式

```yaml
copyright_formats:
  standard:
    - "{year} {copyright_holder}"
    - "Copyright {year} {copyright_holder}"
    - "(c) {year} {copyright_holder}"
  
  with_permission:
    - "Copyright {year} {copyright_holder}. All rights reserved."
    - "Copyright {year} {copyright_holder}. Licensed under {license}."
```

### 检查项目

```python
COPYRIGHT_CHECKLIST = [
    "main_license_in_frontmatter",
    "copyright_notice_in_skill_md",
    "copyright_year_valid",
    "no_infringing_code",
    "attribution_files_present",
]

def check_copyright(skill_path: str) -> CopyrightReport:
    issues = []
    
    # 检查Frontmatter
    frontmatter = read_frontmatter(f"{skill_path}/SKILL.md")
    if 'license' not in frontmatter:
        issues.append("No license declared in frontmatter")
    
    # 检查版权声明
    content = read_file(f"{skill_path}/SKILL.md")
    if not re.search(r'[Cc]opyright', content):
        issues.append("No copyright notice found")
    
    # 检查年份
    year_match = re.search(r'20\d{2}', content)
    if year_match:
        declared_year = int(year_match.group())
        current_year = datetime.now().year
        if declared_year < current_year - 1:
            issues.append(f"Copyright year may be outdated: {declared_year}")
    
    return CopyrightReport(issues=issues)
```

---

## Module 3: 依赖审查

### 依赖许可证扫描

```python
def scan_dependency_licenses(skill_path: str) -> list[DependencyLicense]:
    dependencies = []
    
    # 检测依赖文件
    dep_files = [
        'requirements.txt',
        'package.json',
        'pyproject.toml',
        'Cargo.toml',
        'go.mod',
    ]
    
    for dep_file in dep_files:
        if os.path.exists(f"{skill_path}/{dep_file}"):
            deps = parse_dependencies(f"{skill_path}/{dep_file}")
            for dep in deps:
                license_info = lookup_license(dep.name)
                dependencies.append({
                    'name': dep.name,
                    'version': dep.version,
                    'license': license_info.type,
                    'status': evaluate_license_compatibility(license_info),
                })
    
    return dependencies
```

### 许可证冲突检测

```python
LICENSE_CONFLICTS = {
    ('GPL-2.0', 'Apache-2.0'): "GPL may terminate Apache's patent rights",
    ('GPL-3.0', 'Proprietary'): "GPL incompatible with proprietary",
    ('LGPL-3.0', 'Proprietary'): "Dynamic linking may cause contagion",
}

def detect_conflicts(dependencies: list) -> list[Conflict]:
    conflicts = []
    licenses = [d['license'] for d in dependencies]
    
    for (lic1, lic2), reason in LICENSE_CONFLICTS.items():
        if lic1 in licenses and lic2 in licenses:
            conflicts.append({
                'license_1': lic1,
                'license_2': lic2,
                'reason': reason,
                'severity': 'HIGH',
            })
    
    return conflicts
```

---

## Module 4: 监管compliance

### GDPRcompliance检查

```yaml
gdpr_compliance:
  data_handling:
    - "是否处理个人数据"
    - "数据保留期限"
    - "数据删除机制"
    - "跨境传输"
  
  consent:
    - "是否获取明确同意"
    - "同意可撤回"
  
  security:
    - "数据加密"
    - "访问控制"
    - "漏洞management"
```

### CCPAcompliance检查

```yaml
ccpa_compliance:
  rights:
    - "知情权"
    - "删除权"
    - "拒绝销售权"
  
  disclosures:
    - "隐私政策"
    - "数据收集声明"
    - "第三方共享披露"
```

---

## 接口定义

### `check`

执行完整compliance检查。

**Input:**
```yaml
skill_path: "~/.qclaw/skills/new-skill"
jurisdiction: GLOBAL
check_dependencies: true
```

**Output:**
```yaml
verdict: COMPLIANT
license_analysis:
  main_license: "MIT-0"
  license_family: "Permissive"
  compatibility_score: 95
  restrictions:
    - "保留版权声明"
copyright_check:
  has_copyright_notice: true
  copyright_year: "2026"
  copyright_holder: "AI Company"
dependency_compliance:
  - dependency: "requests"
    license: "Apache-2.0"
    status: OK
  - dependency: "pyyaml"
    license: "MIT"
    status: OK
regulatory_compliance:
  gdpr: PASS
  ccpa: PASS
  dpa: PASS
risk_assessment:
  overall_risk: LOW
  risk_factors: []
  recommendations:
    - "建议添加CHANGELOG文件"
    - "建议增加贡献者指南"
compliance_report: "~/.qclaw/reports/compliance-{skill_name}-{timestamp}.md"
```

---

## KPI 仪表板

| 维度 | KPI | 目标值 |
|------|-----|--------|
| 准确性 | 许可证识别准确率 | ≥ 95% |
| 覆盖率 | 依赖扫描覆盖率 | 100% |
| 效率 | compliance检查时间 | ≤ 20秒 |

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2026-04-15 | 初始版本：许可证分析+版权检查+依赖审查+监管compliance |

---

*本Skill由AI Company CLO开发*  
*作为ai-company-skill-learner的模块组件*  
*遵循AI法律compliance标准*
