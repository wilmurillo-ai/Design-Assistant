# 贡献指南

欢迎为UTF-8编码工具贡献代码！本指南将帮助你开始贡献流程。

## 开发流程

### 1. 环境设置
```bash
# 克隆仓库
git clone https://github.com/mrpulorx2025-source/utf8-encoder-skill
cd utf8-encoder-skill

# 安装依赖（本项目无外部依赖，但建议安装开发工具）
npm install
```

### 2. 代码规范
- **编码标准**：使用UTF-8编码保存所有文件
- **代码风格**：遵循JavaScript Standard Style
- **注释要求**：公共API必须有JSDoc注释
- **测试覆盖**：新功能必须包含单元测试

### 3. 提交规范
使用约定式提交（Conventional Commits）：
```
feat: 添加新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具变动
```

### 4. 测试要求
```bash
# 运行所有测试
npm test

# 运行集成测试（需要设置环境变量）
export DISCORD_WEBHOOK_URL="your_webhook"
export GITHUB_TOKEN="your_token"
node integration-test.js
```

## 添加新平台支持

### 步骤
1. 在`UTF8Encoder`类中添加新方法（如`sendToReddit`）
2. 实现平台特定的参数处理和错误处理
3. 添加单元测试
4. 添加集成测试（可选）
5. 更新文档

### 示例模板
```javascript
async sendToReddit(token, subreddit, title, content, options = {}) {
  const payload = {
    title: this.ensureUTF8(title),
    text: this.ensureUTF8(content),
    sr: subreddit,
    kind: 'self',
    ...options
  };
  
  // Reddit API特定的头和处理逻辑
  // ...
}
```

## 问题反馈

### 提交Issue前
1. 检查是否已有类似Issue
2. 提供详细的复现步骤
3. 包括环境信息（Node.js版本、操作系统等）
4. 提供错误日志或截图

### Issue模板
```
## 问题描述
清晰描述遇到的问题

## 复现步骤
1. ...
2. ...
3. ...

## 期望行为
描述期望的结果

## 实际行为
描述实际发生的结果

## 环境信息
- Node.js版本: 
- 操作系统: 
- 工具版本: 
```

## Pull Request流程

### 1. 创建分支
```bash
git checkout -b feat/new-platform-support
```

### 2. 开发与测试
- 编写代码
- 添加测试
- 确保所有测试通过
- 更新文档

### 3. 提交PR
1. 推送到你的fork仓库
2. 创建Pull Request
3. 填写PR模板
4. 等待代码审查

### PR审查标准
- ✅ 代码符合规范
- ✅ 测试覆盖率足够
- ✅ 文档已更新
- ✅ 没有破坏性变更
- ✅ 解决明确的问题或需求

## 开发理念

### 核心原则
1. **务实导向**：解决真实问题，非技术炫耀
2. **成本意识**：避免不必要的复杂度，节约用户资源
3. **中文友好**：优先考虑中文开发者使用场景
4. **渐进增强**：核心功能稳定后再添加扩展功能

### 设计决策记录
重大设计决策应记录在`docs/decisions`目录中，使用ADR（Architecture Decision Record）格式。

## 发布流程

### 版本号规范
遵循语义化版本（SemVer）：
- **主版本号**：不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 发布步骤
1. 更新`CHANGELOG.md`
2. 更新`package.json`版本号
3. 创建git tag
4. 推送到GitHub
5. 创建GitHub Release

## 社区沟通

### 讨论渠道
- GitHub Issues：功能请求和问题反馈
- GitHub Discussions：一般性讨论
- Pull Requests：代码贡献

### 行为准则
我们遵循贡献者公约（Contributor Covenant），请保持尊重和专业的沟通态度。

## 致谢
感谢所有贡献者的付出！每个贡献，无论大小，都推动项目向前发展。

---

**注意**：在贡献代码前，请确保你理解并同意本项目的开源许可证（MIT License）。