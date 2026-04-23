---
name: "skill-version-manager"
version: 1.0.0
description: "Skill 版本治理工具（semver 版本号规范 + 五步标准维护流程 + 回滚策略）"
triggers: ["更新技能", "版本升级", "semver", "changelog", "维护记录"]
interface:
  inputs:
    type: "object"
    schema: |
      {
        "skill-name": "string (required)",
        "issue": "string (required, user description)",
        "change-type": "PATCH | MINOR | MAJOR (required)",
        "caller": "string (required, agent ID)"
      }
  outputs:
    type: "object"
    schema: |
      {
        "new-version": "string (semver)",
        "changelog-entry": "string",
        "status": "success | error"
      }
  errors:
    - code: "E_VERSION_CONFLICT"
      message: "版本号冲突，请使用正确的 semver 格式"
      action: "返回正确版本号建议"
    - code: "E_SKILL_NOT_FOUND"
      message: "Skill 不存在"
      action: "返回可用版本列表"
    - code: "E_CHANGE_TYPE_MISMATCH"
      message: "变更类型与版本号不匹配"
      action: "根据变更内容建议正确的版本类型"
permissions:
  files: ["read:skills/", "write:skills/"]
  network: []
  commands: []
  mcp: []
dependencies:
  skills: []
  cli: []
quality:
  saST: "✅Pass"
  vetter: "✅Approved"
  idempotent: true
metadata:
  license: "MIT-0"
  author: "ai-skill-maintainer@workspace"
  securityStatus: "✅Vetted"
  layer: "AGENT"
  size: "SMALL"
  parent: "ai-skill-maintainer"
  split_from: "2026-04-14"
---

# Skill 版本管理器（CTO 版本治理标准）

> **执行角色**：CTO-001 版本治理
> **版本**：v1.0.0
> **来源**：ai-skill-maintainer §版本号规范 + §五步维护流程 + §回滚策略
> **合规**：semver 2.0 标准

---

## 核心原则

1. **版本可追溯**：所有变更必须记录 changelog
2. **向后兼容**：MINOR/PATCH 不得破坏现有功能
3. **最小变更**：只改必要的，拒绝过度工程化
4. **强制审查**：所有变更必须通过安全审查

---

## 版本号规范（Semver 2.0）

### 版本格式

```
v<MAJOR>.<MINOR>.<PATCH>[-<prerelease>][+<build>]
```

| 字段 | 说明 | 示例 |
|------|------|------|
| MAJOR | 不兼容的 API 变更 | `v1.0.0 → v2.0.0` |
| MINOR | 向后兼容的功能新增 | `v1.0.0 → v1.1.0` |
| PATCH | 向后兼容的 bug 修复 | `v1.0.0 → v1.0.1` |
| prerelease | 预发布版本 | `v1.0.0-alpha.1` |
| build | 构建元数据 | `v1.0.0+20260414` |

### 版本升级规则

| 变更类型 | 触发关键词 | 版本操作 | 兼容性 |
|---------|-----------|---------|--------|
| Bug 修复 | "修复 bug"、"修复错误" | PATCH +1 | ✅ 向后兼容 |
| 功能增强 | "增强功能"、"新增功能" | MINOR +1 | ✅ 向后兼容 |
| 不兼容变更 | "Breaking Change"、"重构" | MAJOR +1 | ❌ Breaking |
| 安全补丁 | "安全补丁"、"CVE 修复" | PATCH +1（强制） | ✅ 向后兼容 |
| 依赖升级 | "升级依赖"、"更新包" | PATCH +1 | ✅ 通常兼容 |

### 版本号更新规则

```bash
# Bug 修复
vX.Y.Z → vX.Y.(Z+1)

# 功能增强
vX.Y.Z → vX.(Y+1).0

# Breaking Change
vX.Y.Z → (X+1).0.0

# 安全补丁（强制 PATCH）
vX.Y.Z → vX.Y.(Z+1)
```

---

## 标准维护流程（五步）

### Step 1 — 诊断（Diagnosis）

**输入**：用户描述的问题或需求

**诊断记录模板**：

```markdown
## 诊断记录

Skill 名称：<name>
当前版本：<version>
问题类型：[Bug / 功能缺失 / 安全漏洞 / 依赖过时 / 其他]

### 问题描述
<用户描述>

### 复现步骤（如适用）
1.
2.
3.

### 影响范围
- 影响的功能：
- 影响的用户/Agent：

### 初步判断
- 根因：
- 修复方案：
- 版本影响：[PATCH / MINOR / MAJOR]
```

---

### Step 2 — 分析（Analysis）

**输出**：维护记录文件

#### 2.1 变更范围分析

```markdown
### 受影响文件
| 文件 | 变更类型 | 风险评估 |
|------|---------|---------|
| SKILL.md | [修改/新增/删除] | 🟢 低 |
| scripts/*.py | ... | ... |

### 兼容性影响
- 向后兼容：✅ / ❌
- 触发关键词变更：✅ / ❌（如有变更需通知用户）
- 工具权限变更：✅ / ❌

### 测试计划
- [ ] 本地测试用例：
- [ ] 回归测试：
```

#### 2.2 安全影响分析（CTO）

| 分析维度 | 检查项 | 结论 |
|---------|--------|------|
| **功能影响** | 修改是否改变核心功能？ | |
| **权限影响** | 权限是否变更？ | |
| **依赖影响** | 依赖是否新增/升级/删除？ | |
| **数据影响** | 是否影响数据处理？ | |

---

### Step 3 — 实施（Implementation）

#### 3.1 版本号更新

```bash
# 根据变更类型确定版本
# Bug 修复          → vX.Y.Z → vX.Y.(Z+1)
# 功能增强          → vX.Y.Z → vX.(Y+1).0
# Breaking Change   → vX.Y.Z → (X+1).0.0
# 安全补丁          → vX.Y.Z → vX.Y.(Z+1)  （强制）
```

#### 3.2 SKILL.md 更新

**更新 Frontmatter 版本**：
```yaml
---
name: <skill-name>
version: X.Y.Z   # ← 更新版本号
description: |   # ← 如有变更同步更新
  ...
---
```

**更新版本历史**（在文件顶部或底部）：
```markdown
## 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| X.Y.Z | YYYY-MM-DD | <变更摘要> |
| ... | ... | ... |
```

#### 3.3 scripts/ 更新

**更新检查清单**：
```markdown
- [ ] 脚本已更新
- [ ] 脚本版本号已更新（如有版本机制）
- [ ] 依赖已更新（如有）
- [ ] 新增依赖已记录
- [ ] 脚本测试已通过
```

---

### Step 4 — 安全审查（Security Review）

> ⚠️ **强制门禁**：所有变更必须通过 CISO 安全审查

#### 4.1 变更 diff 审查

**审查变更内容**（对比上一版本）：
- 新增的代码是否含 RED FLAGS？
- 修改的代码是否引入新漏洞？
- 删除的代码是否影响安全边界？

#### 4.2 依赖审查

```bash
# 列出新增/升级的依赖
# 检查 CVE
```

---

### Step 5 — 验证与发布（Verify & Publish）

#### 5.1 验证清单

```markdown
## 发布前验证

- [ ] 变更内容与诊断一致
- [ ] 版本号符合变更类型
- [ ] 安全审查通过
- [ ] 脚本测试通过
- [ ] changelog 已更新
- [ ] SKILL.md 已同步更新
```

#### 5.2 发布命令

```bash
# 打包
clawhub package ./<skill-name> --output ./dist

# 发布
clawhub publish ./<skill-name> \
  --slug <skill-name> \
  --name "<Skill Name>" \
  --version X.Y.Z \
  --changelog "<变更摘要>"
```

---

## 回滚策略（Rollback）

> 如维护操作失败，执行以下步骤恢复：

### 自动回滚条件

| 触发条件 | 回滚操作 | 通知人 |
|---------|---------|--------|
| `patch` 失败 | 回滚到隔离前版本 | CTO-001 |
| `deprecate` 误操作 | 恢复 `deprecated: false` | CRO-001 |
| 安全审查未通过 | 回滚至上一版本 | CTO-001 + CISO-001 |
| 回归测试失败 | 回滚至上一版本 | CTO-001 |

### 回滚命令

```bash
# 恢复到上一个可用版本
git checkout tags/v<上一版本> -- SKILL.md scripts/ references/

# 验证回滚成功
git log --oneline -3
```

### 解除 emergency-isolate 条件

1. CVE 已修复（CVSS < 7.0）
2. CISO-001 安全复审通过
3. CQO-001 质量验收通过
4. CTO-001 书面授权解除隔离

---

## 维护记录模板

保存至 `references/maintenance-log.md`：

```markdown
# Skill 维护记录

## Skill 信息
- 名称：<name>
- 当前版本：<version>
- 维护者：<maintainer>

## 维护历史

### 维护 #N — YYYY-MM-DD

**类型**：[Bug修复/功能增强/安全补丁/废弃/其他]
**版本**：<old> → <new>
**变更摘要**：<summary>

#### 变更详情
<detailed changes>

#### 安全审查
- CVSS：<score>
- 结论：[通过/拒绝/条件通过]

#### 测试结果
- [ ] 测试通过

#### 发布信息
- 发布日期：YYYY-MM-DD
- ClawHub 版本：<version>
```

---

## 快速参考

| 用户请求 | 执行动作 |
|---------|---------|
| "修复 Skill XX 的 bug" | 诊断 → 分析 → 实施 → 安全审查 → 发布 |
| "为 Skill XX 增加 XX 功能" | 需求确认 → 分析 → 实施 → 安全审查 → 发布 |
| "升级 Skill XX 的依赖" | 依赖检查 → 兼容性分析 → 更新 → 安全审查 → 发布 |
| "发现 Skill XX 有安全漏洞" | 🚨 紧急通道 → 立即隔离 → 紧急修复 → 紧急发布 |
| "废弃 Skill XX" | 废弃评估 → 通知用户 → 发布废弃版本 → 保留迁移指南 |

---

## 版本历史

| 版本 | 日期 | 变更内容 | 审核人 |
|------|------|---------|--------|
| **1.0.0** | 2026-04-14 | 从 ai-skill-maintainer 拆分：版本号规范（semver）+ 五步标准维护流程 + 回滚策略 + 维护记录模板 | CTO-001 |
