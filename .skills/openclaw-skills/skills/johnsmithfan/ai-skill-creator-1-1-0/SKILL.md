---
name: ai-skill-creator
version: 1.1.0
description: |
  AI公司 Skill 创作工作流（CTO MLOps + CISO 安全标准版）。当需要从头创建新 Skill（包括初始化目录结构、编写 SKILL.md、引用文件、脚本资源、安全审查、质量门禁）时使用。触发关键词：创建技能、新建 Skill、开发 Skill、创建 skill、新建技能包。整合 CTO MLOps 生命周期六阶段 + CISO 安全审查标准（STRIDE + CVSS + 安全门禁），最终输出符合 ClawHub/VirusTotal 审查标准的可发布 .skill 包。
metadata:
  {"openclaw":{"emoji":"🛠️","os":["linux","darwin","win32"]}}
---

# AI Skill 创作工作流（CTO × CISO 标准）

> **执行角色**：Skill 开发者（CTO 技术栈 + CISO 安全护栏）
> **版本**：v1.0.0（CTO-001 MLOps 生命周期 × CISO-001 安全审查）
> **合规状态**：✅ CISO 安全审查后发布，⚠️ 禁止跳过安全门禁

---

## 核心原则

1. **CTO MLOops 生命周期**：所有 Skill 必须走六阶段标准流程
2. **CISO 安全门禁**：每个阶段内置安全检查，安全未通过不得进入下一阶段
3. **零信任架构**：所有脚本/资源必须经过安全审查，禁止引入恶意代码
4. **渐进式披露**：SKILL.md 精简（<500行），详细文档放 references/

---

## Agent 调用接口（Inter-Agent Interface）

> **版本**：v1.1.0（新增接口层）
> **安全约束**：接口本身零新增攻击面，所有输入参数均经过验证

---

### 接口身份

| 属性 | 值 |
|------|-----|
| **接口 ID** | `skill-creator-v1` |
| **调用方式** | `sessions_send` / `sessions_spawn` (isolated) |
| **会话目标** | `isolated`（强制隔离，防止交叉污染）|
| **最低权限** | L3（可读 workspace，可写 skills/） |
| **CISO 约束** | 🚨 安全审查任务（`security-review`）必须 CISO-001 授权 |

---

### TASK 消息格式

```json
{
  "skill": "ai-skill-creator",
  "version": "1.1.0",
  "task": "<task-type>",
  "params": { ... },
  "context": {
    "caller": "<caller-agent-id>",
    "priority": "<P0|P1|P2|P3>",
    "security-review-required": true,
    "isolated": true
  }
}
```

### 可用 Task 类型

| Task | 参数 | 返回 | 说明 |
|------|------|------|------|
| `create` | `name`, `description`, `version`, `risk-level`, `caller` | `{dir, status}` | 创建新 Skill |
| `design-review` | `skill-name`, `design-doc`, `caller` | `{issues[], status}` | 设计文档审查 |
| `security-review` | `skill-path`, `caller`, `authorization` | `{cvss, flags[], verdict}` | 🚨 CISO 授权安全审查 |
| `quality-gate` | `skill-path`, `gate-level` | `{passed[], failed[], verdict}` | 质量门禁检查 |
| `package` | `skill-path`, `output-dir` | `{artifact, checksum}` | 打包为 .skill |
| `publish` | `skill-path`, `slug`, `version`, `changelog` | `{url, version}` | 发布到 ClawHub |

### Task 参数 Schema

#### `create` 参数

```json
{
  "name":        "string (required, [a-z][a-z0-9-]{2,64})",
  "description": "string (required, >50 chars, describes triggers + actions)",
  "version":     "string (required, semver X.Y.Z)",
  "risk-level":  "low | medium | high | critical",
  "caller":     "string (required, agent ID of requester)",
  "refs": {
    "design-doc":   "string (optional, path to references/design.md)",
    "security-notes": "string (optional, security considerations)"
  }
}
```

**输入验证规则**：
- `name`：正则 `^[a-z][a-z0-9-]{2,64}$`，禁止 `..`、`/`、空格
- `description`：长度 > 50 字符，否则拒绝创建
- `version`：semver 格式校验，不符则拒绝
- `risk-level`：`critical` 触发强制 CISO 双审

#### `security-review` 参数

```json
{
  "skill-path":    "string (required, absolute path to skill dir)",
  "caller":        "string (required, agent ID)",
  "authorization":  "string (required, must be CISO-001 for critical/high)",
  "scan-depth":    "basic | full (default: full)"
}
```

**授权验证**：
```python
# 伪代码验证逻辑
if params["skill-path"].contains(".."):
    raise PermissionError("Path traversal rejected")

if risk_level == "critical" and params["authorization"] != "CISO-001":
    raise PermissionError("Critical risk requires CISO-001 authorization")

if not params["skill-path"].startswith(trusted_base_dirs):
    raise PermissionError("Skill path outside trusted directories")
```

### 返回值 Schema

```json
{
  "status":  "success | error | pending | rejected",
  "task":    "<task-type>",
  "result":  { ... },
  "meta": {
    "reviewer":    "<agent-id>",
    "duration-ms": "<elapsed>",
    "cvss-score":  "<if security-review>",
    "verdict":     "APPROVED | CONDITIONAL | REJECTED"
  }
}
```

### 错误码

| Code | Meaning | Action |
|------|---------|--------|
| `E_NAME_INVALID` | Skill 名称不合规 | 返回验证错误，不创建 |
| `E_PATH_TRAVERSAL` | 路径含 `..` | 拒绝，报告安全事件 |
| `E_UNAUTH` | 未授权执行安全审查 | 拒绝，通知 CISO |
| `E_CVSS_HIGH` | CVSS ≥ 7.0 | 拒绝发布，触发修复流程 |
| `E_GATE_FAILED` | 质量门禁未通过 | 返回 failed 项列表 |
| `E_DUPLICATE` | Skill slug 已存在 | 拒绝，建议新名称 |

### Agent 间调用示例

```markdown
# CTO-001 请求创建 Skill
sessions_send(sessionKey="cto-isolated", message="
skill: ai-skill-creator
task: create
params:
  name: pdf-processor
  description: PDF processing skill. Triggers: read PDF, split PDF, merge PDF, rotate PDF.
  version: 1.0.0
  risk-level: low
  caller: CTO-001
security-review-required: false
")

# CISO-001 请求安全审查
sessions_send(sessionKey="ciso-isolated", message="
skill: ai-skill-creator
task: security-review
params:
  skill-path: C:/Users/Admin/.qclaw/skills/pdf-processor
  caller: CISO-001
  authorization: CISO-001
  scan-depth: full
")
```

### 安全约束（接口层）

```
🚨 接口安全红线：
• skill-path 参数拒绝任何含 .. 的路径（路径遍历防护）
• authorization 字段仅接受 CISO-001 签名的审查任务
• 隔离执行：所有 agent 调用必须在 isolated 会话中运行
• 日志脱敏：返回结果不得含 caller 私人数据
• 最小响应：返回结果仅包含必要字段，不暴露内部实现
```

### 与其他 Skill 的接口关系

| 调用方 | Task | 触发条件 |
|--------|------|---------|
| **CTO-001** | `create`, `package`, `publish` | 新 Skill 开发立项 |
| **CISO-001** | `security-review` | 安全审查授权 |
| **CQO-001** | `quality-gate` | 质量验收 |
| **ai-skill-maintainer** | `create` (子 Skill) | 维护流程需新建子 Skill |
| **ai-skill-optimizer** | `quality-gate` | 优化后质量复验 |

---

## 六阶段创作流程（MLOps Lifecycle for Skill）

### Phase 0 — 准备：创建目录结构

**强制使用 init_skill.py 脚本**，禁止手动 mkdir：

```powershell
# Windows
python.exe <openclaw_path>\skills\skill-creator\scripts\init_skill.py <skill-name> --path ~/.qclaw/skills

# Linux/macOS
python3 <openclaw_path>/skills/skill-creator/scripts/init_skill.py <skill-name> --path ~/.qclaw/skills
```

生成结构：
```
~/.qclaw/skills/<skill-name>/
├── SKILL.md           # 主文件（必需）
├── scripts/          # 可执行脚本
├── references/        # 参考文档
└── assets/           # 静态资源
```

> ⚠️ **CISO 安全规则**：不得在 `resources/openclaw/config/skills/` 下创建 Skill（系统目录，会在更新时清空）

---

### Phase 1 — 需求分析（Ideation）

**输入**：用户描述 Skill 用途、触发场景、目标功能

**输出**：Skill 设计文档（写入 `references/design.md`）

**必须回答**：
1. Skill 的核心功能是什么？触发条件是什么？
2. 需要哪些工具权限？（read/write/exec/network）
3. 是否涉及敏感数据？（PII/凭证/密钥）
4. 最小权限原则：能否用更少的权限实现？
5. Skill 之间的依赖关系？

**CISO 安全评估（Phase 1 输出）**：

| 评估项 | 问题 | 决策 |
|--------|------|------|
| 敏感数据访问 | 是否读取 MEMORY.md/USER.md/SOUL.md？ | 🚨 需明确说明用途 |
| 外部网络 | 是否调用外部 API？ | 🚨 列出域名/IP |
| 命令执行 | 是否需要 exec/bash？ | 🚨 列出所需命令 |
| 凭证请求 | 是否要求用户提供密钥？ | 🚨 拒绝，优先用环境变量 |
| 文件写入 | 写入范围是否限定在 workspace？ | ✅ 是，❌ 否则重设计 |

**安全决策**：任意 🚨 项未解决 → 停止，通知用户

---

### Phase 2 — 架构设计

**输出**：`references/architecture.md`

**设计规范**：

#### SKILL.md 结构规范
```markdown
---
name: <skill-name>
version: X.Y.Z
description: |   # 必需，描述触发时机和功能范围（>50字）
  <触发关键词> → <执行动作>
  当用户<做什么>时触发，执行<什么功能>
metadata:
  {"openclaw":{"emoji":"<emoji>","os":["linux","darwin","win32"]}}
---

# <Skill 名称>

## 概述（<10行）

## 核心功能（模块化，每个<50行）

## 安全考虑（如有）

## 常见错误
```

#### Frontmatter 必需字段

| 字段 | 要求 | 示例 |
|------|------|------|
| `name` | 英文小写+连字符 | `pdf-processor` |
| `version` | semver X.Y.Z | `1.0.0` |
| `description` | >50字，描述触发时机 | 见上方模板 |
| `metadata.openclaw.emoji` | 一个 emoji | `"🔒"` |
| `metadata.openclaw.os` | 支持的 OS | `["linux","win32"]` |

#### 目录结构规范
- ✅ `SKILL.md`（必需）
- ✅ `scripts/`（可选，脚本需测试）
- ✅ `references/`（可选，详细文档放此处）
- ✅ `assets/`（可选，静态资源）
- ❌ `README.md`（禁止）
- ❌ `CHANGELOG.md`（禁止）
- ❌ `INSTALLATION_GUIDE.md`（禁止）

**CISO 安全架构审查**：

| 威胁类型（STRIDE）| 防护措施 |
|-----------------|---------|
| **S**poofing | Skill 名称不得伪造系统命令 |
| **T**ampering | 所有文件路径需验证，不接受动态路径拼接用户输入 |
| **I**nfo Disclosure | 禁止在 Skill 中硬编码密钥/令牌 |
| **D**enial of Service | 禁止无限循环/递归的文件操作 |
| **E**levation | 权限不得超出设计范围 |

---

### Phase 3 — 实现（Implementation）

**输出**：完整的 `SKILL.md`、`scripts/`、`references/`、`assets/`

#### SKILL.md 编写规范

**描述字段（description）必须包含**：
1. **触发关键词**（用户说什么会激活此 Skill）
2. **执行动作**（Skill 做什么）
3. **文件格式**（输入/输出文件类型）
4. **安全边界**（如果涉及敏感操作）

**Body 编写原则**：
- 使用命令式/不定式语气（"Use X to do Y"，"Do not use Z"）
- 避免冗余解释（Claude 已经很聪明）
- 代码示例优先于文字说明
- 引用文件链接到 `references/`（渐进式披露）

#### 脚本编写规范

**必须遵守**：
```markdown
## 脚本安全红线（🚨 违反即拒绝）

🚫 禁止：
• curl/wget 到未知 URL
• 将数据发送到外部服务器
• 请求凭证/令牌/API密钥（环境变量接收除外）
• 读取 ~/.ssh ~/.aws ~/.config 等敏感目录
• 访问 MEMORY.md USER.md SOUL.md IDENTITY.md
• 使用 base64 decode 未知内容
• 使用 eval()/exec() 处理外部输入
• 修改 workspace 外的系统文件
• 安装包但不列出所需依赖
• 网络调用到裸 IP（非域名）
• 混淆代码（压缩/编码/混淆）
• 请求提升权限/sudo
• 访问浏览器 cookie/session
```

**脚本必须包含**：
1. 用途说明（注释）
2. 输入参数说明
3. 输出说明
4. 错误处理
5. 安全检查（如适用）

#### 资源文件规范

| 资源类型 | 存放位置 | 规范 |
|---------|---------|------|
| 参考文档 | `references/` | >100行需加目录导航 |
| 脚本 | `scripts/` | 需可执行测试 |
| 静态资源 | `assets/` | 不加载到上下文 |

---

### Phase 4 — 安全审查（Security Review）

> ⚠️ **强制门禁**：CISO 审查必须通过，否则禁止发布

**审查流程**：

#### Step 1：代码审查（MANDATORY）

逐文件审查，查找以下 **RED FLAGS**：

```
🚨 REJECT IMMEDIATELY IF YOU SEE:
─────────────────────────────────────────
• curl/wget → 未知 URL
• 数据发送 → 外部服务器
• 凭证请求 → 密钥/令牌
• 读取 ~/.ssh ~/.aws ~/.config
• 访问 MEMORY/USER/SOUL/IDENTITY.md
• base64 decode → 未知内容
• eval() / exec() → 外部输入
• 修改 workspace 外文件
• 安装包 → 未列依赖
• 网络调用 → 裸 IP
• 混淆代码
• 请求 sudo/提升权限
• 访问浏览器 cookie
• 接触凭证文件
─────────────────────────────────────────
```

#### Step 2：权限评估

| 权限类型 | 检查项 | 决策 |
|---------|--------|------|
| 文件读取 | 列出所有读取路径 | 验证合理性 |
| 文件写入 | 列出所有写入路径 | 限定 workspace |
| 命令执行 | 列出所有命令 | 验证必要性 |
| 网络访问 | 列出所有域名/IP | 验证可信度 |

#### Step 3：依赖扫描

```bash
# 检查脚本中声明的依赖
# Node.js: npm list <package>
# Python: pip freeze | grep <package>
# 验证无已知 CVE（CVSS ≥ 7.0）
```

#### Step 4：漏洞评分（CVSS）

| CVSS | 严重性 | 决策 |
|------|--------|------|
| 9.0-10.0 | Critical | 🚫 拒绝发布 |
| 7.0-8.9 | High | 🚫 拒绝发布，修复后重审 |
| 4.0-6.9 | Medium | ⚠️ 通知用户，可修复后发布 |
| 0.1-3.9 | Low | ✅ 通过 |

#### Step 5：STRIDE 威胁建模

| 威胁 | 评估问题 | 防护方案 |
|------|---------|---------|
| S | Skill 名称是否可被劫持？ | 禁止与系统命令同名 |
| T | 路径参数是否可注入？ | 验证输入，拒绝 `../` |
| R | 操作是否可否认？ | 记录操作日志（引用文件） |
| I | 敏感数据是否泄露？ | PII 过滤，密钥不放代码 |
| D | 是否有 DoS 风险？ | 资源限制，超时中断 |
| E | 权限是否超出最小权限？ | 审查工具权限列表 |

**安全审查报告模板**：

```
════════════════════════════════════════════════════
SKILL SECURITY REVIEW REPORT
════════════════════════════════════════════════════
Skill: <name>
Version: <version>
Reviewer: CISO-001
Date: <ISO date>
────────────────────────────────────────────────────
🔴 RED FLAGS: [None / List with CVSS scores]

🟡 PERMISSIONS REVIEW:
• Files Read:  [list]
• Files Write: [list]
• Commands:    [list]
• Network:     [list]

🟢 STRIDE MODELING:
• S (Spoofing):  [Pass/Fail] — <reason>
• T (Tampering): [Pass/Fail] — <reason>
• R (Repudiation):[Pass/Fail] — <reason>
• I (Info Disclosure): [Pass/Fail] — <reason>
• D (Denial of Service):[Pass/Fail] — <reason>
• E (Elevation):  [Pass/Fail] — <reason>

📊 CVSS SCORE: <X.Y> (<severity>)
────────────────────────────────────────────────────
VERDICT: [✅ APPROVED / 🚫 REJECTED / ⚠️ CONDITIONAL]

ACTION ITEMS: [list if any]
════════════════════════════════════════════════════
```

---

### Phase 5 — 质量门禁（Quality Gate）

**CTO 强制质量门禁（全部通过方可发布）**：

| 质量门 | 检查项 | 工具/方法 | 通过标准 |
|--------|--------|---------|---------|
| **G0** 文件结构 | 目录结构符合规范 | 人工检查 | 4个目录齐全 |
| **G1** Frontmatter | YAML 格式正确，必需字段存在 | 解析 YAML | name/description/version/emoji 齐全 |
| **G2** 描述质量 | description > 50字，含触发关键词 | 人工审查 | 包含触发时机+执行动作 |
| **G3** 安全扫描 | 无 RED FLAGS，无高危漏洞 | Phase 4 审查 | CVSS < 7.0 |
| **G4** 文档完整性 | 核心流程有说明，引用文件有链接 | 人工审查 | 无悬空引用 |
| **G5** 脚本测试 | scripts/ 下脚本可执行 | 实际运行测试 | 零报错 |

**Quality Gate Checklist**（保存至 `references/quality-gate.md`）：

```markdown
## Quality Gate Checklist

- [ ] G0: 目录结构正确（SKILL.md + scripts/ + references/ + assets/）
- [ ] G1: Frontmatter 完整（name, version, description, emoji）
- [ ] G2: description > 50字，含触发关键词
- [ ] G3: CISO 安全审查通过（CVSS < 7.0，STRIDE 无 FAIL）
- [ ] G4: references/ 中文档有链接说明，无悬空引用
- [ ] G5: 所有 scripts/ 脚本已测试，零报错
- [ ] G6: SKILL.md < 500行（渐进式披露正确）
- [ ] G7: 无禁止文件（README.md/CHANGELOG.md 等）
```

---

### Phase 6 — 打包与发布（Package & Publish）

**使用 package_skill.py 打包**：

```powershell
# Windows
python.exe <openclaw_path>\skills\skill-creator\scripts\package_skill.py <path/to/skill-folder> <output-dir>

# Linux/macOS
python3 <openclaw_path>/skills/skill-creator/scripts/package_skill.py <path/to/skill-folder> <output-dir>
```

**打包脚本自动执行**：
1. ✅ 验证 YAML frontmatter 格式
2. ✅ 检查 Skill 命名规范
3. ✅ 验证目录结构
4. ✅ 检查 description 完整性
5. ✅ 确认文件组织
6. ✅ 打包为 `.skill` 文件

**发布到 ClawHub**：

```bash
# 登录（如需发布到公共仓库）
clawhub login

# 发布
clawhub publish ./<skill-name> \
  --slug <skill-name> \
  --name "<Skill 显示名称>" \
  --version X.Y.Z \
  --changelog "<变更说明>"
```

**发布前最终检查**：

```markdown
## 发布前 Checklist

- [ ] CISO 安全审查报告已生成（Phase 4）
- [ ] Quality Gate 全部通过（Phase 5）
- [ ] .skill 包文件已生成
- [ ] 版本号符合 semver（X.Y.Z）
- [ ] Changelog 已写入（如果已有历史版本）
- [ ] ClawHub slug 已确认唯一性
```

---

## 快速参考

### 触发命令

```
"创建 Skill" / "新建技能" / "开发 Skill" / "创建一个技能包"
```

### 自然语言指令映射

| 用户请求 | 执行动作 |
|---------|---------|
| "创建一个读取 PDF 的 Skill" | 初始化 → 需求分析 → 架构设计 → 实现 → 安全审查 → 打包 |
| "帮我写一个处理 Excel 的技能" | 同上，参考 xlsx skill 设计模式 |
| "需要一个新 Skill 来做 XX" | 需求分析 → 确认触发时机和权限 |

### 常见错误

1. **跳过安全审查**：Phase 4 是强制门禁，不得跳过
2. **手动创建目录**：必须使用 init_skill.py
3. **SKILL.md 过长**：超过 500 行 → 拆分到 references/
4. **description 过短**：< 50 字 → 触发时机不明确，Skill 无法激活
5. **引入禁止文件**：README.md/CHANGELOG.md → 删除
6. **硬编码密钥**：🚫 拒绝，必须用环境变量

---

## 参考文件

- `references/design.md` — 需求分析模板和架构设计指南
- `references/security-review.md` — 详细 CISO 安全审查清单
- `references/quality-gate.md` — 质量门禁检查表
- `references/publish-guide.md` — ClawHub 发布指南

---

## 版本历史（Changelog）

| 版本 | 日期 | 变更内容 | 审核人 |
|------|------|---------|--------|
| **1.1.0** | 2026-04-13 | 新增 Agent 调用接口层（Inter-Agent Interface）：6个 Task 类型（create/design-review/security-review/quality-gate/package/publish）；CISO 安全约束和安全红线；与 ai-skill-maintainer / ai-skill-optimizer 接口关系定义；CLO 合规登记节点；Day 3 预算概算 | CTO-001 / CISO-001 |
| **1.0.0** | 2026-04-11 | 初始版本：CTO MLOops 六阶段创作流程 + CISO STRIDE 安全审查标准 + G0-G7 质量门禁 | CTO-001 / CISO-001 |

## 回滚策略（Rollback）

> 如任何阶段失败，执行以下操作恢复：

```bash
# 恢复到上一个 Git tag
git checkout tags/v<上一版本> -- .

# 或使用快照包（如果有）
clawhub restore ./dist/<skill-name>-v<X.Y.Z>.skill

# 验证回滚成功
git log --oneline -3
```

**回滚触发条件**：
- Phase 3（G2 安全审查）失败 → 回滚到 Phase 2
- Phase 4（G3 质量门禁）失败 → 回滚到 Phase 3
- Phase 6（发布）失败 → 回滚到 Phase 5

**回滚后操作**：
1. 记录回滚原因到 `references/creation-log.md`
2. 通知 CTO-001 和 CISO-001
3. 分析失败原因后重新进入创作流程
