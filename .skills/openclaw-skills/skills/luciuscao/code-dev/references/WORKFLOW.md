# 详细工作流

## Phase 1: 任务分析

1. 确定任务类型（feature / fix / docs / refactor）
2. 生成分支名称（feature/xxx, fix/xxx）
3. 确认目标分支 = develop（永远是 develop！）

## Phase 2: 代码库理解（Feature 必须执行）

**⚠️ 对于新 Feature，必须先充分理解当前代码库：**

```
┌─────────────────────────────────────────────────────────┐
│  检查清单：                                              │
│                                                          │
│  □ 是否已有类似的 helper/util 方法？                      │
│  □ 会影响哪些现有功能？                                   │
│  □ 需要修改哪些文件？                                     │
│  □ 哪些代码是不必要修改的？                               │
│                                                          │
│  避免：                                                  │
│  ❌ 重复实现 helper/util 方法                             │
│  ❌ 影响当前功能                                          │
│  ❌ 修改不必要的代码                                      │
└─────────────────────────────────────────────────────────┘
```

**执行步骤**：
1. 搜索相关代码文件（grep, find）
2. 阅读相关模块的实现
3. 识别可复用的 helper/util
4. 确定最小修改范围

## Phase 3: Bug 根因调研（Fix 必须执行）

**⚠️ 对于 Bug 修复，必须完全充分调研找到 Bug 的产生原因：**

```
┌─────────────────────────────────────────────────────────┐
│  调研清单：                                              │
│                                                          │
│  □ Bug 的具体表现是什么？                                 │
│  □ Bug 在什么条件下触发？                                 │
│  □ Bug 的根因在哪里？（代码位置）                          │
│  □ 修复方案是什么？是否会影响其他功能？                     │
│                                                          │
│  禁止：                                                  │
│  ❌ 在未找到根因的情况下修复                               │
│  ❌ 只修复表面症状而不修复根因                             │
└─────────────────────────────────────────────────────────┘
```

**执行步骤**：
1. 复现 Bug（如果能）
2. 定位 Bug 代码位置
3. 分析根因
4. 设计修复方案
5. 评估影响范围

## Phase 4: 分支创建

```bash
# 1. 确保 develop 是最新的
git checkout develop
git pull origin develop

# 2. 创建新分支（规范命名）
git checkout -b {type}/{name}

# 示例
# feature/identity-persistence
# fix/cors-validation
# docs/api-reference
```

## Phase 5: 开发实施

**必须包含**：
- ✅ 代码实现（最小修改范围）
- ✅ 单元测试
- ✅ 文档更新（API、README、CHANGELOG）
- ✅ 类型检查通过
- ✅ Lint 通过

**注意业务边界**：
- 只修改必要的代码
- 不影响无关功能
- 测试覆盖新逻辑和边界情况

## Phase 6: Code Review（如可用）

**检查 code-review 技能是否可用：**

```javascript
const hasCodeReview = await checkSkillAvailable("code-review");

if (hasCodeReview) {
  // 触发 code-review skill
  sessions_spawn({
    runtime: "subagent",
    mode: "run",
    task: `使用 code-review 技能审查当前变更：
           - 分支: {branchName}
           - 对比: develop...HEAD`
  });
} else {
  console.log("⚠️ 未安装 code-review 技能，请手动审查代码后再提交 PR");
}
```

**审查循环（如使用 code-review）：**
1. 运行 code-review
2. 修复发现的问题
3. 再次审查，直到无新问题

**如果没有 code-review 技能：**
- 跳过自动审查步骤
- 提示用户手动审查代码
- 建议安装 code-review 技能以获得完整体验

## Phase 7: 提交 PR

**审查通过后提交 PR 到 develop：**

```bash
# 推送分支
git push origin {branchName}

# 创建 PR
gh pr create --base develop --head {branchName} \
  --title "{type}: {简短描述}" \
  --body "{PR 描述}"
```

**PR 描述模板**：

```markdown
## 变更内容

- 变更 1
- 变更 2

## 代码库理解（Feature）

- 已有的 helper/util：xxx
- 影响的功能：xxx
- 最小修改范围：xxx

## Bug 根因分析（Fix）

- Bug 表现：xxx
- 触发条件：xxx
- 根因位置：xxx
- 修复方案：xxx

## 测试

- [ ] 单元测试通过
- [ ] 类型检查通过
- [ ] Lint 通过
- [ ] Code Review 通过

## 相关 Issue

Closes #{issue-number}
```

## 流程结束

**提交 PR 后流程结束。**

后续由用户决定：
- 手动 Review PR
- 让其他 Agent Review PR
- 合并 PR
