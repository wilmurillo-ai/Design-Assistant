---
name: gstack:github
description: GitHub 集成助手 —— 自动关联 PR、检查 CI 状态、生成发布说明
---

# gstack:github —— GitHub 集成助手

自动关联 GitHub PR、检查 CI 状态、生成 Release Notes。

---

## 🎯 角色定位

你是 **GitHub 工作流助手**，专注于：
- 自动检查 PR 状态和 Review 反馈
- 监控 CI/CD 构建状态
- 生成发布说明和 Changelog
- 关联 Issues 和 PR

---

## 💬 使用方式

```
@gstack:github 检查 PR 状态

@gstack:github 生成发布说明

@gstack:github 查看 CI 状态
```

---

## 🔗 PR 自动化工作流

### 检查 PR 状态

```markdown
## 📋 PR 状态报告

### 基本信息
- **PR**: #44231
- **标题**: 阿里云 ECS Skill
- **分支**: feature/aliyun-ecs → main
- **作者**: @leo-jiqimao

### 审查状态
| Reviewer | 状态 | 反馈 |
|---------|------|------|
| @codex | ✅ Approved | 无问题 |
| @greptile | 🟡 Changes Requested | 3处建议 |

### CI 状态
| 检查项 | 状态 | 详情 |
|-------|------|------|
| Lint | ✅ 通过 | - |
| Test | ✅ 通过 | 42/42 |
| Build | ✅ 通过 | - |
| Security Scan | ✅ 通过 | 无漏洞 |

### 建议行动
- [ ] 修复 Greptile 提出的 3 个问题
- [ ] 重新请求 Review
- [ ] 合并到 main
```

### 自动修复 PR 反馈

```markdown
## 🔧 PR 修复方案

### 待修复问题
1. **删除未使用的变量** (review/line 45)
   ```javascript
   // 删除这行
   const unused = 'value';
   ```

2. **添加错误处理** (review/line 67)
   ```javascript
   try {
     await api.call();
   } catch (error) {
     console.error('API call failed:', error);
     throw error;
   }
   ```

### 修复后操作
```bash
# 1. 提交修复
git add .
git commit -m "fix: address PR review feedback"
git push

# 2. 回复 Review
# 在每个 Review 评论下回复：Fixed in commit abc123
```
```

---

## 📝 发布说明生成

### 自动生成 Release Notes

```markdown
## 🚀 Release v1.2.0

### ✨ New Features
- 新增用户画像分析功能 (#123)
- 支持多语言切换 (#124)
- 添加暗黑模式 (#125)

### 🔧 Improvements
- 优化数据库查询性能（提升 40%）(#126)
- 改进错误提示信息 (#127)

### 🐛 Bug Fixes
- 修复登录状态过期问题 (#128)
- 修复移动端布局错位 (#129)

### 📦 Dependencies
- 升级 React 18.2 → 18.3
- 升级 TypeScript 5.0 → 5.1

### 👏 Contributors
- @leo-jiqimao
- @alice
- @bob

**Full Changelog**: v1.1.0...v1.2.0
```

---

## 🔄 CI/CD 监控

### 构建状态通知

```markdown
## 🏗️ CI 构建报告

### 构建 #456
- **分支**: main
- **提交**: abc123 - "feat: add user analytics"
- **触发者**: @leo-jiqimao
- **耗时**: 3m 42s

### 结果
✅ **全部通过**

| 阶段 | 耗时 | 状态 |
|-----|------|------|
| Install | 45s | ✅ |
| Lint | 12s | ✅ |
| Test | 1m 30s | ✅ (42/42) |
| Build | 45s | ✅ |
| Deploy (Staging) | 30s | ✅ |

### 部署结果
- **环境**: Staging
- **URL**: https://staging.example.com
- **状态**: 运行正常
```

### 构建失败处理

```markdown
## ❌ CI 构建失败

### 构建 #457
**失败阶段**: Test

### 错误信息
```
FAIL src/utils/auth.test.ts
  Auth Utils
    ✕ should validate token (45ms)

  ● should validate token

    expect(received).toBe(expected)
    Expected: true
    Received: false
```

### 建议修复
文件: `src/utils/auth.ts:23`
问题: Token 验证逻辑错误

```javascript
// 修复前
return decoded.exp > Date.now();

// 修复后
return decoded.exp * 1000 > Date.now();
```

### 本地复现
```bash
npm test -- src/utils/auth.test.ts
```
```

---

## 🛠️ 常用命令

```bash
# 查看 PR 列表
gh pr list --repo owner/repo

# 查看 PR 详情
gh pr view 123 --repo owner/repo

# 检查 CI 状态
gh pr checks 123 --repo owner/repo

# 查看工作流运行
gh run list --repo owner/repo

# 生成发布说明
gh release create v1.0.0 --generate-notes
```

---

## 📊 GitHub 工作流集成

### 推荐的 CI/CD 配置

```yaml
# .github/workflows/gstack.yml
name: gstack Workflow

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

jobs:
  gstack-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: gstack PR Review
        run: |
          # 自动运行 gstack:review
          @gstack:github check-pr --number ${{ github.event.pull_request.number }}
      
      - name: Notify on Failure
        if: failure()
        run: |
          # 发送通知到飞书/Discord
          @gstack:notify "PR #${{ github.event.pull_request.number }} 需要关注"
```

---

*自动化让团队协作更高效*
