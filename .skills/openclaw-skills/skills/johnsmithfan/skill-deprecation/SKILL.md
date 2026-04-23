---
name: "skill-deprecation"
version: 1.0.0
description: "Skill 废弃管理工具（废弃流程 + 迁移指南 + 废弃状态 SKILL.md 模板）"
triggers: ["废弃技能", "Skill废弃", "停用技能", "迁移指南", "deprecated"]
interface:
  inputs:
    type: "object"
    schema: |
      {
        "skill-name": "string (required)",
        "reason": "string (required)",
        "replacement": "string (optional, new skill name)",
        "caller": "string (required, agent ID)"
      }
  outputs:
    type: "object"
    schema: |
      {
        "deprecated-version": "string",
        "status": "success | pending | cancelled",
        "notification-required": "boolean"
      }
  errors:
    - code: "E_SKILL_NOT_FOUND"
      message: "Skill 不存在"
      action: "返回可用 Skill 列表"
    - code: "E_NO_REPLACEMENT"
      message: "废弃 Skill 未提供替代方案"
      action: "必须提供 replacement 字段或说明原因"
    - code: "E_DEPRECATE_CANCELLED"
      message: "废弃流程已取消"
      action: "恢复 deprecated: false，通知 CRO-001"
permissions:
  files: ["read:skills/", "write:skills/", "read:skill-registry.json"]
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

# Skill 废弃管理器（Deprecation Workflow）

> **执行角色**：CTO-001 版本治理
> **版本**：v1.0.0
> **来源**：ai-skill-maintainer §废弃管理
> **合规**：废弃流程三阶段标准

---

## 核心原则

1. **透明通知**：废弃前必须通知所有用户
2. **提供替代**：每个废弃 Skill 必须有 replacement
3. **过渡期保护**：给予用户充足迁移时间（建议 ≥ 30 天）
4. **可逆性**：废弃前允许取消，废弃后保留恢复路径

---

## 废弃流程（三阶段）

```
废弃通知（vX.Y.Z）
    ↓ 建议 ≥ 30 天过渡期
过渡期（持续支持 + 迁移支持）
    ↓ 确认所有用户已迁移
正式废弃（vX.Y.Z+1）
    ↓ 可选：保留迁移指南
完全移除（待定）
```

### 阶段一：废弃通知

**操作**：发布废弃版本，添加废弃标记

**废弃 SKILL.md 模板**（详见下方"废弃 SKILL.md 模板"章节）

**通知内容**：
- 废弃原因
- 替代方案
- 过渡期时长
- 迁移指南链接
- 最后支持日期

### 阶段二：过渡期

**持续支持内容**：
- 仅修复 Critical Bug（不新增功能）
- 安全补丁继续推送
- 迁移支持（答疑、协助迁移）

**进度跟踪**：
```markdown
## 废弃进度跟踪

| 日期 | 剩余用户数 | 迁移率 | 备注 |
|------|-----------|--------|------|
| YYYY-MM-DD | N | X% | 开始废弃 |
| YYYY-MM-DD | N | X% | 30天提醒 |
```

### 阶段三：正式废弃

**操作**：
- 将 SKILL.md 标记为 `deprecated: true` + `removed: true`
- 更新注册表（skill-registry.json）状态为 `REMOVED`
- 发布最终废弃公告
- 保留迁移指南（references/migration.md）至少 90 天

---

## 废弃 SKILL.md 模板

```markdown
---
name: <deprecated-skill>
version: X.Y.Z
description: |
  ⚠️ 【已废弃】此 Skill 已废弃，建议使用 `<new-skill>`。
  废弃日期：YYYY-MM-DD
  最后支持日期：YYYY-MM-DD
  迁移指南：见 references/migration.md
deprecated: true
replacement: <new-skill-name>
metadata:
  {"openclaw":{"emoji":"⚠️","os":["linux","darwin","win32"]}}
---

# ⚠️ 已废弃：<Skill Name>

## 废弃通知

此 Skill 已于 **YYYY-MM-DD** 正式废弃。

### 为什么废弃？
<原因>

### 替代方案
请使用 **<new-skill-name>**：
- 链接：clawhub install <new-skill>

### 时间线
- 废弃通知：YYYY-MM-DD（vX.Y.Z）
- 最后支持：YYYY-MM-DD（vX.Y.Z+1）
- 完全移除：待定

### 迁移指南
详见 [references/migration.md](references/migration.md)
```

---

## 迁移指南规范（Migration Guide）

迁移指南文件保存至 `references/migration.md`，必须包含以下章节：

### 必需章节

#### 1. 概述
```markdown
## 迁移概述

- **从**：<old-skill-name> v<version>
- **到**：<new-skill-name> v<version>
- **影响范围**：<哪些功能受影响>
- **预计迁移时间**：<X 分钟/小时>
```

#### 2. 主要变更
```markdown
## 主要变更

### 已移除的功能
| 旧功能 | 替代方案 |
|--------|---------|
| ... | ... |

### 已更改的行为
| 旧行为 | 新行为 |
|--------|--------|
| ... | ... |
```

#### 3. 迁移步骤
```markdown
## 迁移步骤

### 步骤 1：安装新 Skill
\`\`\`bash
clawhub install <new-skill-name>
\`\`\`

### 步骤 2：更新触发关键词
// 旧关键词 → 新关键词映射表

### 步骤 3：验证功能
- [ ] 核心功能测试
- [ ] 回归测试
```

#### 4. 兼容性
```markdown
## 兼容性说明

- API 兼容性：✅ 完全兼容 / ⚠️ 部分不兼容
- 参数变更：<详细说明>
- Breaking Changes：<列出所有不兼容变更>
```

#### 5. 回滚方案
```markdown
## 回滚方案

如迁移遇到问题，可回滚到旧版本：
\`\`\`bash
clawhub install <old-skill>@<last-supported-version>
\`\`\`

**注意**：回滚后请尽快完成迁移，旧版本将在 <日期> 完全移除。
```

---

## Task 接口

### Task: `deprecate`

**参数 Schema**：
```json
{
  "skill-name":   "string (required)",
  "reason":       "string (required)",
  "replacement": "string (optional, new skill name)",
  "caller":      "string (required, agent ID)"
}
```

**返回值示例**：
```json
{
  "status": "success",
  "result": {
    "deprecated-version": "v1.5.0",
    "status": "pending",
    "notification-required": true,
    "replacement": "pdf-v2",
    "transition-end-date": "2026-05-14"
  }
}
```

### Task: `deprecate-cancel`

**触发条件**：废弃决策被撤销（CRO-001 审批通过）

**操作**：
- 恢复 `deprecated: false`
- 通知 CRO-001 确认

---

## 废弃决策检查清单

在正式废弃前，必须确认以下所有项：

| 检查项 | 说明 | 状态 |
|--------|------|------|
| 替代方案已就绪 | replacement Skill 已发布并测试通过 | ☐ |
| 用户已通知 | 所有用户收到废弃通知 | ☐ |
| 迁移指南已完成 | references/migration.md 包含完整迁移步骤 | ☐ |
| 过渡期已设定 | 建议 ≥ 30 天 | ☐ |
| 数据迁移（如有）| 用户数据可迁移或已备份 | ☐ |
| CRO-001 审批 | 废弃决策已获 CRO-001 批准 | ☐ |

---

## 错误码参考

| Code | Meaning | Action |
|------|---------|--------|
| `E_SKILL_NOT_FOUND` | Skill 不存在 | 返回可用 Skill 列表 |
| `E_NO_REPLACEMENT` | 废弃 Skill 未提供替代方案 | 必须提供 replacement 字段 |
| `E_DEPRECATE_CANCELLED` | 废弃流程已取消 | 恢复 `deprecated: false`，通知 CRO-001 |

---

## 快速参考

| 场景 | 操作 |
|------|------|
| 废弃旧版本 Skill | 发布废弃版本 → 30天过渡期 → 正式废弃 |
| 迁移遇到问题 | 提供技术支持 → 评估延期废弃 |
| 废弃决策被撤销 | 恢复 deprecated: false → 通知 CRO-001 |

---

## 版本历史

| 版本 | 日期 | 变更内容 | 审核人 |
|------|------|---------|--------|
| **1.0.0** | 2026-04-14 | 从 ai-skill-maintainer 拆分：废弃流程三阶段（通知→过渡期→正式废弃）+ 废弃 SKILL.md 模板 + 迁移指南规范（5个必需章节）| CTO-001 |
