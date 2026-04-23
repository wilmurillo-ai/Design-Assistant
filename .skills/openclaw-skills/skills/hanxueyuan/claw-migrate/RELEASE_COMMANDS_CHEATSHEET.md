# claw-migrate v2.2.0 发布命令速查

**版本:** v2.2.0  
**创建时间:** 2026-03-15

---

## 🚀 发布命令

### 1. 提交最终代码

```bash
cd /workspace/projects/workspace/skills/claw-migrate

# 添加所有更改
git add -A

# 提交
git commit -m "chore: v2.2.0 发布前最终准备"

# 推送
git push origin main
```

### 2. 创建 Git 标签

```bash
# 创建带注释的标签
git tag -a v2.2.0 -m "Release v2.2.0 - 配置管理与定时备份"

# 推送标签
git push origin v2.2.0

# 验证标签
git tag -l
# 应显示：v2.0.0, v2.2.0
```

### 3. 执行发布

```bash
# 使用 ClawHub 发布
clawhub publish

# 如果有 dry-run 选项（先预览）
clawhub publish --dry-run

# 发布到 npm（如果配置）
npm publish
```

### 4. 创建 GitHub Release

```bash
# 使用 GitHub CLI
gh release create v2.2.0 \
  --repo hanxueyuan/claw-migrate \
  --title "v2.2.0 - 配置管理与定时备份" \
  --notes-file RELEASE_NOTES_v2.2.0.md

# 或通过 Web 界面
# https://github.com/hanxueyuan/claw-migrate/releases/new
```

---

## ✅ 验证命令

### 安装验证

```bash
# 安装技能
openclaw skill install claw-migrate

# 查看版本
openclaw skill run claw-migrate --version
# 预期：2.2.0

# 查看帮助
openclaw skill run claw-migrate --help
```

### 功能验证

```bash
# 测试配置管理
openclaw skill run claw-migrate config

# 测试状态查看
openclaw skill run claw-migrate status

# 测试定时任务
openclaw skill run claw-migrate scheduler --start
openclaw skill run claw-migrate scheduler --stop

# 运行测试套件
openclaw skill run claw-migrate test
```

### CI/CD 验证

```bash
# 检查 GitHub Actions 状态
# https://github.com/hanxueyuan/claw-migrate/actions

# 使用 GitHub CLI
gh run list --repo hanxueyuan/claw-migrate
gh run view <run-id> --repo hanxueyuan/claw-migrate
```

---

## 🔙 回滚命令

### 紧急回滚

```bash
# 1. 删除 Git 标签（本地）
git tag -d v2.2.0

# 2. 删除 Git 标签（远程）
git push origin :refs/tags/v2.2.0

# 3. 删除 GitHub Release
gh release delete v2.2.0 --repo hanxueyuan/claw-migrate

# 4. 删除 ClawHub 版本
clawhub delete-version claw-migrate v2.2.0

# 5. 回滚代码
git checkout v2.0.0
```

### 标记为废弃

```bash
# 如果无法删除，标记为废弃
clawhub deprecate claw-migrate@2.2.0 "存在严重 Bug，请使用 v2.0.0"

# 或在 GitHub 标记为 Pre-release
# https://github.com/hanxueyuan/claw-migrate/releases
```

---

## 📊 监控命令

### 查看下载统计

```bash
# npm 下载量（如果发布到 npm）
npm show claw-migrate downloads

# GitHub 统计
# https://github.com/hanxueyuan/claw-migrate/graphs/traffic
```

### 查看 Issue

```bash
# 列出最近的 Issue
gh issue list --repo hanxueyuan/claw-migrate

# 查看特定 Issue
gh issue view <issue-number> --repo hanxueyuan/claw-migrate
```

### 查看 CI/CD 状态

```bash
# 列出最近的 workflow runs
gh run list --repo hanxueyuan/claw-migrate --limit 10

# 查看特定 run 的详情
gh run view <run-id> --repo hanxueyuan/claw-migrate
```

---

## 📝 文档清单

发布相关文件：

| 文件 | 用途 |
|------|------|
| PRE_RELEASE_REPORT_v2.2.0.md | 发布前审查报告 |
| ROLLBACK_PLAN_v2.2.0.md | 回滚方案 |
| RELEASE_MONITORING_v2.2.0.md | 发布监控清单 |
| RELEASE_COMMANDS_CHEATSHEET.md | 本文件 |
| CHANGELOG.md | 变更日志 |
| RELEASE_NOTES_v2.2.0.md | 发布说明 |

---

## 🔗 相关链接

| 资源 | URL |
|------|-----|
| GitHub 仓库 | https://github.com/hanxueyuan/claw-migrate |
| GitHub Actions | https://github.com/hanxueyuan/claw-migrate/actions |
| Issues | https://github.com/hanxueyuan/claw-migrate/issues |
| Releases | https://github.com/hanxueyuan/claw-migrate/releases |
| ClawHub | https://clawhub.io/packages/claw-migrate |

---

## 📞 紧急联系

- **维护者:** xueyuan_han@163.com
- **GitHub:** https://github.com/hanxueyuan
- **团队飞书群:** [内部群]

---

**快速参考，建议打印或保存**
