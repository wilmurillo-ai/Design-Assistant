# claw-migrate v2.2.0 回滚方案

**版本:** v2.2.0  
**创建时间:** 2026-03-15  
**用途:** 紧急回滚操作指南

---

## 🚨 何时需要回滚

出现以下情况时考虑回滚：

1. **严重 Bug** - 影响核心功能（备份/恢复）
2. **安全漏洞** - 敏感信息泄露风险
3. **兼容性问题** - 大量用户无法使用
4. **数据损坏** - 导致用户配置丢失

---

## 📋 回滚命令清单

### 1. Git 回滚

#### 1.1 删除 Git 标签

```bash
# 切换到项目目录
cd /workspace/projects/workspace/skills/claw-migrate

# 查看当前标签
git tag -l

# 本地删除标签
git tag -d v2.2.0

# 远程删除标签
git push origin :refs/tags/v2.2.0

# 验证删除
git tag -l
# 应该只显示 v2.0.0
```

#### 1.2 代码回滚到 v2.0.0

```bash
# 方法 1: Checkout 到上一版本
git checkout v2.0.0

# 方法 2: Reset 到特定提交
git log --oneline  # 找到 v2.0.0 的 commit hash
git reset --hard <commit-hash>

# 方法 3: Revert 发布提交
git log --oneline  # 找到发布相关的 commit
git revert <commit-hash>
```

#### 1.3 强制推送（谨慎使用）

```bash
# 仅在你确定需要覆盖远程历史时使用
git push --force origin main

# ⚠️ 警告：这会覆盖远程历史，确保团队知晓
```

### 2. ClawHub 版本删除

#### 2.1 命令行删除（如果支持）

```bash
# 尝试通过 CLI 删除
clawhub delete-version claw-migrate v2.2.0

# 或者
clawhub unpublish claw-migrate@2.2.0
```

#### 2.2 Web 界面删除

1. 访问：https://clawhub.io/packages/claw-migrate/manage
2. 找到版本 v2.2.0
3. 点击 "Delete Version" 或 "Unpublish"
4. 确认删除

#### 2.3 标记为废弃（推荐）

如果无法删除，可以标记为废弃：

```bash
clawhub deprecate claw-migrate@2.2.0 "存在严重 Bug，请升级到 v2.2.1 或回退到 v2.0.0"
```

### 3. GitHub Release 处理

#### 3.1 删除 Release

```bash
# 通过 GitHub CLI
gh release delete v2.2.0 --repo hanxueyuan/claw-migrate

# 或者通过 Web 界面
# https://github.com/hanxueyuan/claw-migrate/releases
# 点击 v2.2.0 → Delete release
```

#### 3.2 标记为 Pre-release

如果不想完全删除：

1. 访问：https://github.com/hanxueyuan/claw-migrate/releases
2. 编辑 v2.2.0
3. 勾选 "Set as a pre-release"
4. 保存

---

## 🔧 回滚后的操作

### 1. 恢复 v2.0.0 为最新稳定版

```bash
# 确保 v2.0.0 标签存在
git tag -l

# 推送 v2.0.0 标签（如果需要）
git push origin v2.0.0

# 更新 GitHub Release
# 将 v2.0.0 标记为 "Latest release"
```

### 2. 通知用户

#### 2.1 GitHub Issue 通知

创建 Issue 或更新现有 Issue：

```markdown
## ⚠️ v2.2.0 回滚通知

由于发现严重 Bug，v2.2.0 已回滚。

**影响:**
- 问题描述

**建议操作:**
1. 已安装 v2.2.0 的用户请降级到 v2.0.0
2. 等待 v2.2.1 发布

**降级方法:**
```bash
openclaw skill uninstall claw-migrate
openclaw skill install claw-migrate@2.0.0
```

抱歉带来不便。
```

#### 2.2 CHANGELOG 更新

在 CHANGELOG.md 中添加回滚说明：

```markdown
## [2.2.0] - 2026-03-15 (已回滚)

⚠️ **此版本已回滚，请使用 v2.0.0**

回滚原因：[具体原因]
回滚时间：2026-03-15
```

### 3. 修复问题

```bash
# 创建修复分支
git checkout -b fix/v2.2.1-hotfix

# 修复问题
# ... 代码修改 ...

# 提交修复
git add -A
git commit -m "fix: 修复 v2.2.0 的严重 Bug"

# 推送分支
git push origin fix/v2.2.1-hotfix

# 创建 Pull Request
# https://github.com/hanxueyuan/claw-migrate/pulls
```

### 4. 重新发布 v2.2.1

```bash
# 更新版本号
# package.json: "version": "2.2.1"

# 更新 CHANGELOG
# 添加 v2.2.1 记录

# 提交
git add package.json CHANGELOG.md
git commit -m "chore: 准备 v2.2.1 发布"

# 创建新标签
git tag -a v2.2.1 -m "Release v2.2.1 - Hotfix for v2.2.0"

# 推送
git push origin main
git push origin v2.2.1

# 发布
clawhub publish
```

---

## 📊 回滚决策树

```
发现问题
    │
    ├─ 严重 Bug? ──是─→ 立即回滚
    │                    ↓
    │              删除标签 + 删除版本
    │                    ↓
    │              通知用户
    │                    ↓
    │              修复后重新发布
    │
    └─ 轻微问题? ──是─→ 发布补丁版本
                         ↓
                   v2.2.1 (不回滚)
```

---

## 📞 紧急联系人

| 角色 | 联系方式 | 职责 |
|------|----------|------|
| 维护者 | xueyuan_han@163.com | 回滚决策、执行 |
| 技术负责人 | [待补充] | 技术审核 |
| QA | [待补充] | 问题验证 |

---

## ✅ 回滚检查清单

### 回滚前

- [ ] 确认问题严重性
- [ ] 评估影响范围
- [ ] 准备回滚方案
- [ ] 通知团队成员

### 回滚中

- [ ] 删除 Git 标签
- [ ] 删除 ClawHub 版本
- [ ] 删除 GitHub Release
- [ ] 更新文档

### 回滚后

- [ ] 验证 v2.0.0 正常工作
- [ ] 通知用户
- [ ] 创建修复分支
- [ ] 计划新版本发布

---

**文档版本:** 1.0  
**最后更新:** 2026-03-15
