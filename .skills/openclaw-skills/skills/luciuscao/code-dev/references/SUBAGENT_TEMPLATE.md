# Subagent 任务模板

## 前置检查

```javascript
// 检查环境支持
const supportsSubagent = await checkSubagentSupport();
const hasCodeReview = await checkSkillAvailable("code-review");
```

## 任务内容模板

```javascript
const taskContent = `你是 Git Workflow 开发助手。

## 任务信息
- 类型：{feature|fix}
- 描述：{taskDescription}
- 分支名称：{branchName}
- code-review 可用：${hasCodeReview}

## ⚠️ 如果是 Feature，必须先理解代码库：

1. 搜索相关代码文件
2. 阅读相关模块实现
3. 识别可复用的 helper/util
4. 确定最小修改范围

避免：
- 重复实现 helper/util 方法
- 影响当前功能
- 修改不必要的代码

## ⚠️ 如果是 Fix，必须先找到 Bug 根因：

1. 复现 Bug（如果能）
2. 定位 Bug 代码位置
3. 分析根因
4. 设计修复方案
5. 评估影响范围

## 开发流程

1. 从 develop 创建分支：{branchName}
2. 实现变更（最小修改范围）
3. 编写测试
4. 更新文档
5. 运行检查（typecheck, lint, test）

## 代码审查

${hasCodeReview ? `
1. 使用 code-review 技能审查代码
2. 修复发现的问题
3. 再次审查，直到无新问题
` : `
⚠️ code-review 技能不可用，请手动审查代码
`}

## 完成后

1. 提交 PR 到 develop

## 安全规则

- ❌ 不要推送到 main
${hasCodeReview ? '- ✅ 使用 code-review 审查代码（如可用）' : '- ⚠️ 手动审查代码'}
- ✅ 必须从 develop 创建分支
- ✅ 必须 PR 到 develop`;
```

## 执行方式

### 方式一：Subagent（优先）

```javascript
if (supportsSubagent) {
  sessions_spawn({
    runtime: "subagent",
    mode: "run",
    cwd: "{projectDir}",
    task: taskContent
  });
}
```

### 方式二：直接执行（降级）

```javascript
else {
  console.log("⚠️ 当前环境不支持 subagent，直接执行开发任务");
  // 在当前会话执行 taskContent 中的逻辑
}
```
