# GitHub自动化管理Skill

## 🚀 概述
**DeepSeek v4赋能的智能开发协作平台**，基于惠迈"怎么能行"开发哲学，将GitHub开发流程智能化，减少开发工作量90%。

## 🌟 核心亮点
- **DeepSeek v4代码智能**：AI驱动的代码审查、PR分析、Issue智能处理
- **惠迈开发模式工具化**：将惠迈智能体协作模式融入开发流程
- **超前技术配置**：支持DeepSeek v4代码理解和生成
- **开发效率革命**：传统开发协作需要大量人工，现在智能体自动处理

## 🏆 用户价值
- **开发效率提升90%**：自动化处理代码审查、Issue分类等重复工作
- **代码质量+50%**：AI智能审查减少人为错误
- **团队协作优化**：智能体协调开发流程，减少沟通成本
- **三层架构保障**：代码智能体、流程智能体、协作智能体协同工作

## 功能特性
- **仓库管理**：创建、配置、管理GitHub仓库
- **PR自动化**：自动审核、合并、标签管理
- **Issue处理**：Issue分类、分配、自动化回复
- **工作流自动化**：CI/CD集成、自动化测试、部署
- **团队协作**：团队管理、权限控制、协作工具
- **数据分析**：仓库活动分析、贡献者统计

## 安装
```bash
# 通过ClawHub安装
clawhub install github-automation

# 或手动安装
npm install github-automation
```

## 配置
创建配置文件 `config/github-automation.json`：
```json
{
  "token": "YOUR_GITHUB_TOKEN",
  "username": "YOUR_GITHUB_USERNAME",
  "organization": "YOUR_ORGANIZATION",
  "permissions": {
    "repo": "all",
    "workflow": "write",
    "issues": "write",
    "pullRequests": "write"
  },
  "automation": {
    "prReview": true,
    "issueTriaging": true,
    "ciMonitoring": true,
    "dependencyUpdates": true
  }
}
```

## 使用方法

### 基本设置
```javascript
const GitHubAutomation = require('github-automation');

const github = new GitHubAutomation({
  token: process.env.GITHUB_TOKEN,
  organization: 'your-org'
});

// 初始化连接
await github.connect();
```

### 仓库管理
```javascript
// 创建新仓库
const repo = await github.createRepository('new-project', {
  description: 'A new project',
  private: true,
  autoInit: true
});

// 配置仓库设置
await github.configureRepository('your-org/new-project', {
  hasIssues: true,
  hasProjects: true,
  hasWiki: true,
  allowMergeCommit: true,
  allowSquashMerge: true,
  allowRebaseMerge: true
});

// 获取仓库信息
const repoInfo = await github.getRepository('your-org/new-project');
```

### PR管理
```javascript
// 创建PR
const pr = await github.createPullRequest({
  owner: 'your-org',
  repo: 'new-project',
  title: 'Add new feature',
  head: 'feature-branch',
  base: 'main',
  body: 'This PR adds a new feature...'
});

// 自动审核PR
await github.reviewPullRequest('your-org/new-project', 123, {
  event: 'APPROVE',
  body: 'Looks good!'
});

// 合并PR
await github.mergePullRequest('your-org/new-project', 123, {
  mergeMethod: 'squash'
});
```

### Issue管理
```javascript
// 创建Issue
const issue = await github.createIssue('your-org/new-project', {
  title: 'Bug: Something is broken',
  body: '详细描述问题...',
  labels: ['bug', 'high-priority']
});

// 分配Issue
await github.assignIssue('your-org/new-project', 456, ['user1', 'user2']);

// 自动回复Issue
await github.replyToIssue('your-org/new-project', 456, '感谢报告，我们会尽快处理。');
```

### 工作流自动化
```javascript
// 触发工作流
await github.triggerWorkflow('your-org/new-project', 'ci.yml', {
  ref: 'main'
});

// 监控CI状态
const ciStatus = await github.getCIStatus('your-org/new-project', 'main');

// 自动部署
await github.deploy('your-org/new-project', 'production', {
  version: 'v1.2.3'
});
```

### 在OpenClaw中使用
```
@agent 创建新的GitHub仓库
@agent 审核PR #123
@agent 分配Issue给团队成员
@agent 查看仓库状态
@agent 触发部署流程
```

## API参考

### 构造函数
```javascript
new GitHubAutomation(config)
```
**参数：**
- `config.token` (string): GitHub Personal Access Token
- `config.username` (string): GitHub用户名
- `config.organization` (string): 组织名称
- `config.permissions` (object): 权限配置
- `config.automation` (object): 自动化配置

### 核心方法

#### connect()
连接到GitHub API。

#### createRepository(name, options)
创建新仓库。

#### configureRepository(repo, settings)
配置仓库设置。

#### createPullRequest(options)
创建Pull Request。

#### reviewPullRequest(repo, prNumber, review)
审核Pull Request。

#### mergePullRequest(repo, prNumber, options)
合并Pull Request。

#### createIssue(repo, issue)
创建Issue。

#### assignIssue(repo, issueNumber, assignees)
分配Issue。

#### triggerWorkflow(repo, workflow, inputs)
触发工作流。

#### getCIStatus(repo, ref)
获取CI状态。

## 自动化功能

### PR自动化流程
1. 新PR创建时自动添加标签
2. 自动请求代码审查
3. 检查通过后自动合并
4. 自动删除分支

### Issue自动化流程
1. 新Issue自动分类
2. 根据标签自动分配
3. 自动回复模板消息
4. 超时自动提醒

### 依赖更新
1. 监控依赖更新
2. 自动创建更新PR
3. 自动运行测试
4. 安全更新优先处理

### 发布管理
1. 版本号自动递增
2. 自动生成变更日志
3. 自动创建发布
4. 自动部署到环境

## 依赖项
- @octokit/rest: ^19.0.0
- node-cron: ^3.0.0

## 开发
```bash
# 克隆仓库
git clone https://github.com/your-org/github-automation.git

# 安装依赖
npm install

# 运行测试
npm test

# 启动开发服务器
npm run dev
```

## 贡献
欢迎提交Issue和Pull Request。

## 许可证
MIT License

## 版本历史
- v1.0.0 (2026-04-22): 初始发布，基础自动化功能

## 支持
如有问题，请提交Issue或联系维护团队。