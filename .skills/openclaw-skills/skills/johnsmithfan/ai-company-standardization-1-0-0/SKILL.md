---
name: "AI Company Standardization"
slug: "ai-company-standardization"
version: "1.0.0"
homepage: "https://clawhub.com/skills/ai-company-standardization"
description: "AI Company 标准化流程 Skill — 将任意 Skill 转换为 ClawHub Schema v1.0 合规标准。包含 Frontmatter 审计、内容结构规范、Schema 合规检查、接口标准化、质量门五步流程。"
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

AI Company 标准化流程 Skill。将任意格式不规范、包含组织特定内容、或结构混乱的 Skill 转换为 ClawHub Schema v1.0 合规的标准化 Skill。

---

## 概述

**标准化（Standardization）** 是 AI Company Skill 质量保证的第一道门。它确保所有 Skill 满足统一的格式规范、接口定义和文档结构，使 Skill 可被发现、可被理解、可被安全地安装和执行。

### 目标

- 统一 ClawHub 生态中所有 Skill 的格式规范
- 消除组织特定的内容（hardcoded references）
- 确保接口定义完整且类型安全
- 为后续模块化和通用化流程奠定基础

### 适用范围

| Skill 状态 | 是否需要标准化 |
|------------|-------------|
| 新建 Skill | ✅ 强制 |
| 已有 Skill（无 frontmatter）| ✅ 强制 |
| 已有 Skill（frontmatter 不合规）| ✅ 强制 |
| ClawHub 发布过的 Skill | ⚠️ 需版本升级 |
| 已完全合规的 Skill | ❌ 不需要 |

---

## 标准化五步流程

### Step 1 — Frontmatter 审计

检查所有必需字段是否存在且格式正确：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `name` | string | ✅ | 人类可读名称 |
| `slug` | string | ✅ | kebab-case，唯一，与目录名一致 |
| `version` | semver | ✅ | 格式：`X.Y.Z` |
| `homepage` | URL | ✅ | ClawHub 发布地址 |
| `description` | string | ✅ | 简洁描述（≤200字符）|
| `license` | string | ✅ | 推荐 MIT-0 |
| `tags` | string[] | ✅ | 搜索标签 |
| `triggers` | string[] | ✅ | 触发词（用户说什么会调用此 Skill）|
| `interface` | object | ✅ | 接口定义 |
| `permissions` | object | ✅ | 权限显式声明 |
| `dependencies` | object | ✅ | 依赖声明 |
| `quality` | object | ✅ | 质量指标 |
| `metadata` | object | ✅ | 分类、分层、许可证等 |

**审计检查：**

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
    
    # slug 必须与目录名一致
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

### Step 2 — 内容结构规范化

将 Skill 正文组织为标准化模块结构：

```
## Module X: [模块名称]

### 功能描述
[模块负责什么]

### 接口定义
[typed inputs/outputs YAML]

### 错误代码
[code: ERR_XXX — message]

### 依赖
[其他模块或外部依赖]
```

**标准化章节顺序：**

1. **概述（Overview）** — Skill 定位、功能摘要
2. **模块定义（Modules）** — N× 模块详细说明
3. **接口定义（Interfaces）** — 所有调用接口汇总
4. **KPI 仪表板（KPI Dashboard）** — 质量指标
5. **变更日志（Changelog）** — 版本历史

**禁止内容：**

- ❌ 硬编码组织名称（DELLIGHT.AI、Acme Corp 等）
- ❌ 硬编码具体金额、日期、ID
- ❌ 指向特定环境的文件路径（如 `ABSOLUTE_PATH/`）
- ❌ 未声明的网络调用
- ❌ 隐藏的凭据或密钥引用

### Step 3 — Schema 合规检查

| 检查项 | 标准 | 错误码 |
|--------|------|--------|
| Frontmatter 格式 | YAML 有效，字段完整 | STD_001/003 |
| Semver 版本号 | `^\\d+\\.\\d+\\.\\d+$` | STD_002 |
| Slug 命名 | kebab-case，与目录名一致 | STD_004 |
| Interface 定义 | 有 inputs/outputs/errors | STD_005 |
| 权限声明 | 不含通配符 `*` | STD_006 |
| 依赖声明 | 所有依赖已列出 | STD_007 |
| Idempotency | quality.idempotent 已声明 | STD_008 |
| License | 已声明（推荐 MIT-0）| STD_009 |

### Step 4 — 接口标准化

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

**接口命名规范：**

- 使用 kebab-case（`skill-name`）
- 每个接口独立一个 error code 前缀
- 至少包含 2 个示例

### Step 5 — 质量门

| 质量门 | 条件 | 通过标准 |
|--------|------|---------|
| Frontmatter | 所有必需字段存在 | 0 errors |
| YAML 有效性 | 文件可被 YAML 解析器读取 | 解析成功 |
| Idempotency | 可重复执行不改变结果 | 幂等性验证通过 |
| 接口完整性 | 所有接口有 inputs/outputs/errors | 100% 覆盖 |
| 文档完整性 | 每个模块有 description | 无空模块 |

---

## 接口定义

### `standardize-skill`

将目标 Skill 目录标准化。

**Input:**

```yaml
target_skill_path: string  # 目标 Skill 目录路径
force_rewrite: boolean     # 若 true，即使已有 frontmatter 也重写
dry_run: boolean           # 若 true，只报告问题不实际修改
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
manual_review_required: string[]  # 需要人工处理的问题
```

### `audit-skill`

审计 Skill 合规性，不修改文件。

**Input:**

```yaml
skill_path: string
strict_mode: boolean  # 若 true，任何问题都报告为失败
```

**Output:**

```yaml
compliant: boolean
score: 0-100           # 0-100 分，100 = 完全合规
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

批量标准化多个 Skills。

**Input:**

```yaml
skill_paths: string[]
force_rewrite: boolean
parallel: boolean  # 若 true，并行处理（max 5）
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

| 指标 | 目标 | 测量方式 |
|------|------|---------|
| 标准化成功率 | ≥ 95% | 批量标准化结果统计 |
| Frontmatter 完整率 | 100% | 审计工具自动检测 |
| Schema 合规率 | ≥ 98% | STD_* 错误统计 |
| 自动化修复率 | ≥ 80% | 手动修复占比统计 |
| 批量处理吞吐量 | ≥ 10 skills/min | 计时基准测试 |

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

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.0.0 | 2026-04-14 | 初始版本：五步标准化流程 + 批量处理接口 |
