# 更新日志

## v1.1.0 (2026-03-26)

### 🛡️ 安全性增强
- 添加完整的安全说明章节，解释为什么需要修改核心文件
- 添加安全最佳实践指南（文件权限、定期清理等）
- 说明 ClawHub 安全警告的原因和解决方案

### 📚 文档改进
- 添加完整的常见问题 FAQ（5 个问题）
- 添加故障排查指南（4 个常见问题）
- 优化错误处理表格，添加更多错误码
- 添加技术细节章节（Token 生命周期、存储格式等）

### 🔧 功能增强
- 补全 `scripts/` 目录：
  - `send-image.js` - 发送图片脚本
  - `send-file.js` - 发送文件脚本
  - `export-context-token.js` - Token 管理工具
- 创建 `patches/inbound.ts.patch` 补丁文件
- 创建 `references/api-docs.md` API 文档
- 创建 `tests/test-token-persistence.sh` 测试脚本

### 🐛 Bug 修复
- 修复示例代码中硬编码的 account ID 和 user ID
- 修复文件结构中引用但不存在的文件

### 📝 其他
- 更新许可证为 MIT-0（更宽松）
- 优化文档结构和可读性

---

## v1.0.0 (2026-03-23)

### ✨ 初始发布

#### 核心功能
- ✅ 实现 contextToken 磁盘持久化
- ✅ 支持 CLI 发送图片/文件
- ✅ 支持网络图片 URL
- ✅ 内存 + 磁盘双存储架构
- ✅ 自动回退机制（先查内存，再查磁盘）

#### 技术实现
- 修改 `inbound.ts` 添加文件读写逻辑
- 创建 token 存储目录 `~/.openclaw/openclaw-weixin/context-tokens/`
- JSON 格式存储（包含 accountId, userId, token, savedAt）

#### 文档
- SKILL.md 完整使用文档
- README.md 快速入门指南
- 安装脚本和使用示例

---

## 计划中

### v1.2.0
- [ ] 支持批量发送
- [ ] 添加消息队列
- [ ] 支持发送视频

### v1.3.0
- [ ] 添加 Web UI 管理界面
- [ ] 支持 token 自动续期
- [ ] 添加发送统计和日志分析
