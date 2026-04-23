---
name: "AI Company Standardization"
slug: "ai-company-standardization"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-standardization"
description: "AI Company standard化process Skill — 将任意 Skill 转换为 ClawHub Schema v1.0 compliancestandard。包含 Frontmatter audit、内容结构standard、Schema compliance检查、接口standard化、质量门5步process。"
license: MIT-0
tags: [standardization, schema, ai-company, clawhub, frontmatter, governance]
triggers:
  - standardize skill
  - fix frontmatter
  - schema compliance
  - ClawHub schema
  - frontmatter audit
interface:
  inputs:
    type: object
  outputs:
    type: object
  errors:
    - code: STD_001
      message: "Frontmatter missing or malformed"
    - code: STD_002
      message: "Version field invalid semver"
    - code: STD_003
      message: "Required field missing"
    - code: STD_004
      message: "Slug mismatch with directory name"
permissions:
  files: [read/write skills/]
  network: []
  commands: []
  mcp: []
dependencies:
  skills: [ai-company-hq, skill-vetter]
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
  tags: [standardization, schema, ai-company, clawhub, frontmatter]
---

# AI Company Standardization — ClawHub Schema v1.0

AI Company standard化process Skill。将任意格式不standard、包含组织特定内容、或结构混乱的 Skill 转换为 ClawHub Schema v1.0 compliance的standard化 Skill。

---

## Overview

**standard化（Standardization）** 是 AI Company Skill 质量保证的第1道门。它ensure所有 Skill 满足统1的格式standard、接口Definition和文档结构，使 Skill 可被discover、可被理解、可被security地安装和execute。

### Goal

- 统1 ClawHub 生态中所有 Skill 的格式standard
- 消除组织特定的内容（hardcoded references）
- ensure接口Definition完整且类型security
- 为后续模块化和通用化process奠定基础

### 适用范围

| Skill 状态 | 是否需要standard化 |
|------------|-------------|
| 新建 Skill | ✅ 强制 |
| 已有 Skill（无 frontmatter）| ✅ 强制 |
| 已有 Skill（frontmatter 不compliance）| ✅ 强制 |
| ClawHub publish过的 Skill | ⚠️ 需版本upgrade |
| 已完全compliance的 Skill | ❌ 不需要 |

---

## standard化5步process

### Step 1 — Frontmatter audit

检查所有必需字段是否存在且格式正确：

| 字段 | 类型 | 必需 | Description |
|------|------|------|------|
| `name` | string | ✅ | 人类可读名称 |
| `slug` | string | ✅ | kebab-case，唯1，与目录名1致 |
| `version` | semver | ✅ | 格式：`X.Y.Z` |
| `homepage` | URL | ✅ | ClawHub publish地址 |
| `description` | string | ✅ | 简洁描述（≤200字符）|
| `license` | string | ✅ | 推荐 MIT-0 |
| `tags` | string[] | ✅ | 搜索标签 |
| `triggers` | string[] | ✅ | trigger词（用户说什么会调用此 Skill）|
| `interface` | object | ✅ | 接口Definition |
| `permissions` | object | ✅ | permission显式声明 |
| `dependencies` | object | ✅ | 依赖声明 |
| `quality` | object | ✅ | 质量metric |
| `metadata` | object | ✅ | 分类、分层、许可证等 |

**audit检查：**

```python
def audit_frontmatter(skill_path: str) -> AuditResult:
    fm = parse_frontmatter(skill_path)
    errors = []
    
    # 必须以 --- 开头
    if not content.startswith('---\n'):
        errors.append("STD_001: Frontmatter must start with '---'")
    
    # version 必须是合法 semver
    if not is_valid_semver(fm.get('version', '')):
        errors.append("STD_002: Version must be valid semver (e.g. 1.0.0)")
    
    # slug 必须与目录名1致
    dir_name = os.path.basename(os.path.dirname(skill_path))
    if fm.get('slug') != dir_name:
        errors.append(f"STD_004: slug '{fm.get('slug')}' must match directory '{dir_name}'")
    
    # 必需字段
    required = ['name', 'slug', 'version', 'description', 'license', 
                'triggers', 'interface', 'permissions', 'dependencies', 'quality', 'metadata']
    for field in required:
        if field not in fm or not fm[field]:
            errors.append(f"STD_003: Required field '{field}' missing")
    
    return AuditResult(passed=len(errors)==0, errors=errors)
```

### Step 2 — 内容结构standard化

将 Skill 正文组织为standard化模块结构：

```
## Module X: [模块名称]

### Function描述
[模块负责什么]

### 接口Definition
[typed inputs/outputs YAML]

### 错误代码
[code: ERR_XXX — message]

### 依赖
[其他模块或外部依赖]
```

**standard化章节顺序：**

1. **Overview（Overview）** — Skill 定位、Function摘要
2. **模块Definition（Modules）** — N× 模块详细Description
3. **接口Definition（Interfaces）** — 所有调用接口汇总
4. **KPI 仪表板（KPI Dashboard）** — 质量metric
5. **Change Log（Changelog）** — 版本历史

**prohibit内容：**

- ❌ 硬编码组织名称（DELLIGHT.AI、Acme Corp 等）
- ❌ 硬编码具体金额、日期、ID
- ❌ 指向特定环境的文件path（如 `ABSOLUTE_PATH/`）
- ❌ 未声明的网络调用
- ❌ 隐藏的凭据或密钥引用

### Step 3 — Schema compliance检查

| 检查项 | standard | 错误码 |
|--------|------|--------|
| Frontmatter 格式 | YAML 有效，字段完整 | STD_001/003 |
| Semver 版本号 | `^\\d+\\.\\d+\\.\\d+$` | STD_002 |
| Slug 命名 | kebab-case，与目录名1致 | STD_004 |
| Interface Definition | 有 inputs/outputs/errors | STD_005 |
| permission声明 | 不含通配符 `*` | STD_006 |
| 依赖声明 | 所有依赖已列出 | STD_007 |
| Idempotency | quality.idempotent 已声明 | STD_008 |
| License | 已声明（推荐 MIT-0）| STD_009 |

### Step 4 — 接口standard化

所有接口必须包含：

```yaml
interface_name:
  description: string
  inputs:
    param1:
      type: string | number | boolean | object | array
      required: boolean
      description: string
      default?: any
    param2: ...
  outputs:
    type: string | object | array
    description: string
  errors:
    - code: IFACE_001
      message: string
  examples:
    - name: string
      input: object
      expected_output: object
```

**接口命名standard：**

- 使用 kebab-case（`skill-name`）
- 每个接口独立1个 error code 前缀
- 至少包含 2 个示例

### Step 5 — 质量门

| 质量门 | 条件 | 通过standard |
|--------|------|---------|
| Frontmatter | 所有必需字段存在 | 0 errors |
| YAML 有效性 | 文件可被 YAML 解析器读取 | 解析成功 |
| Idempotency | 可重复execute不改变结果 | 幂等性verify通过 |
| 接口完整性 | 所有接口有 inputs/outputs/errors | 100% 覆盖 |
| 文档完整性 | 每个模块有 description | 无空模块 |

---

## 接口Definition

### `standardize-skill`

将Goal Skill 目录standard化。

**Input:**

```yaml
target_skill_path: string  # Goal Skill 目录path
force_rewrite: boolean     # 若 true，即使已有 frontmatter 也重写
dry_run: boolean           # 若 true，只report问题不实际修改
```

**Output:**

```yaml
status: success | failed | skipped | dry_run_report
skill_slug: string
version_assigned: string   # 分配的新版本号
changes_made:
  - type: added | removed | modified | renamed
    field: string
    before: string
    after: string
    location: string       # e.g. "frontmatter.line 23"
errors: string[]           # 未能自动修复的问题
warnings: string[]         # 警告信息
manual_review_required: string[]  # 需要人工handle的问题
```

### `audit-skill`

audit Skill compliance，不修改文件。

**Input:**

```yaml
skill_path: string
strict_mode: boolean  # 若 true，任何问题都report为失败
```

**Output:**

```yaml
compliant: boolean
score: 0-100           # 0-100 分，100 = 完全compliance
issues:
  - code: string
    severity: error | warning | info
    field: string
    message: string
    location: string
recommendations:
  - priority: high | medium | low
    suggestion: string
compliance_checklist:
  frontmatter_valid: boolean
  semver_valid: boolean
  slug_matches_directory: boolean
  interface_complete: boolean
  permissions_declared: boolean
  dependencies_listed: boolean
  idempotent_declared: boolean
  license_declared: boolean
```

### `batch-standardize`

批量standard化多个 Skills。

**Input:**

```yaml
skill_paths: string[]
force_rewrite: boolean
parallel: boolean  # 若 true，并行handle（max 5）
```

**Output:**

```yaml
total: number
succeeded: number
failed: number
skipped: number
results:
  - skill_slug: string
    status: string
    version: string
    changes: number
    errors: string[]
```

---

## KPI 仪表板

| metric | Goal | 测量方式 |
|------|------|---------|
| standard化成功率 | ≥ 95% | 批量standard化结果统计 |
| Frontmatter 完整率 | 100% | audit工具自动detect |
| Schema compliance率 | ≥ 98% | STD_* 错误统计 |
| automation修复率 | ≥ 80% | 手动修复占比统计 |
| 批量handle吞吐量 | ≥ 10 skills/min | 计时baseline测试 |

---

## ClawHub Schema v1.0 完整 Frontmatter 模板

```yaml
---
name: "Skill Name"
slug: "skill-name"
version: "1.0.0"
homepage: "https://clawhub.com/skills/skill-name"
description: "简洁描述（≤200字符）"
license: MIT-0
tags: [tag1, tag2, tag3]
triggers:
  - trigger phrase 1
  - trigger phrase 2
interface:
  inputs:
    type: object
  outputs:
    type: object
  errors:
    - code: SKILL_001
      message: "Error description"
permissions:
  files: []       # 空数组或显式列出
  network: []     # 空数组或显式列出
  commands: []    # 空数组或显式列出
  mcp: []         # 空数组或显式列出
dependencies:
  skills: []      # 依赖的 Skill slug 列表
  cli: []         # 依赖的 CLI 工具列表
quality:
  saST: Pass | Fail | Not Run
  vetter: Approved | Pending | Rejected
  idempotent: true | false
metadata:
  category: governance | functional | platform | agent
  layer: PLATFORM | AGENT | FUNCTIONAL | USER | L3
  cluster: string
  maturity: EXPERIMENTAL | STABLE | DEPRECATED
  license: MIT-0 | Apache-2.0 | Proprietary | CC-BY
  standardized: true
  tags: [tag1, tag2, tag3]
---
```

---

## Change Log

| 版本 | 日期 | Changes |
|------|------|---------|
| 1.0.0 | 2026-04-14 | Initial version：5步standard化process + 批量handle接口 |
