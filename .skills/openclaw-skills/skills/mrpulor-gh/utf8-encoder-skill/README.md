# UTF-8编码工具 (UTF-8 Encoder)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-≥14.0.0-green.svg)](https://nodejs.org/)

**解决核心问题**：PowerShell控制台使用GB2312编码显示UTF-8内容，导致控制台输出乱码，误导开发者认为发布失败。实际HTTP数据正确，但显示误导导致重复发布浪费API token。

> 基于真实痛点开发，避免重复发布浪费宝贵token资源。

## 特性

- ✅ **UTF-8编码保证**：端到端UTF-8处理，确保平台接收正确编码
- ✅ **字节长度计算**：准确计算UTF-8字节长度用于HTTP Content-Length头
- ✅ **多平台支持**：Discord Webhook、GitHub Gist/Issues、可扩展其他平台
- ✅ **乱码检测**：检测Unicode替换字符(�)和异常控制字符
- ✅ **中文优化**：中文字符统计、编码验证
- ✅ **成本意识**：避免因编码误解导致的重复发布浪费token

## 安装

```bash
# 方式1: npm全局安装
npm install -g utf8-encoder-tool

# 方式2: 本地项目使用
npm install utf8-encoder-tool

# 方式3: 直接使用源码
git clone https://github.com/mrpulorx2025-source/utf8-encoder-skill
cd utf8-encoder-skill
npm install
```

## 快速开始

### 基本使用
```javascript
const UTF8Encoder = require('utf8-encoder-tool');
const encoder = new UTF8Encoder();

// 确保文本UTF-8编码
const text = "中文测试 🎯";
const utf8Text = encoder.ensureUTF8(text);

// 计算UTF-8字节长度（用于HTTP Content-Length头）
const byteLength = encoder.calculateUTF8ByteLength(text);
console.log(`字符数: ${text.length}, UTF-8字节: ${byteLength}`);

// 验证无乱码
const validation = encoder.validateNoGarbledChars(text);
if (validation.valid) {
  console.log('✅ 文本无乱码');
} else {
  console.log(`❌ 发现${validation.garbledCount}个乱码字符`);
}
```

### 发送到Discord
```javascript
const result = await encoder.sendToDiscord(
  'https://discord.com/api/webhooks/...',
  'Discord消息：中文测试 🎯',
  {
    username: 'UTF8-Bot',
    avatar_url: 'https://example.com/avatar.png'
  }
);
console.log(result.success ? '✅ 发送成功' : '❌ 发送失败');
```

### 创建GitHub Gist
```javascript
const result = await encoder.createGitHubGist(
  'ghp_your_token_here',
  '# GitHub内容\n\n中文测试内容。',
  'test.md',
  'UTF-8测试Gist',
  true // 公开
);

if (result.gistUrl) {
  console.log(`Gist已创建: ${result.gistUrl}`);
}
```

## 命令行界面

```bash
# 安装后使用
npm install -g utf8-encoder-tool

# 验证文本编码
utf8-encoder validate "中文测试🎯"

# 计算UTF-8字节长度
utf8-encoder length ./document.md

# 发送测试消息到Discord
utf8-encoder test-discord "测试消息内容"

# 创建测试GitHub Gist
utf8-encoder test-github "# 测试内容"

# 设置环境变量避免命令行暴露敏感信息
export DISCORD_WEBHOOK_URL="your_webhook_url"
export GITHUB_TOKEN="your_github_token"
```

## 实战示例

### 示例1：发布调研到多个平台
```javascript
const UTF8Encoder = require('utf8-encoder-tool');
const encoder = new UTF8Encoder();
const fs = require('fs');

async function publishResearch() {
  // 1. 读取内容并验证
  const content = encoder.readFileUTF8('./research.md');
  const validation = encoder.validateNoGarbledChars(content);
  if (!validation.valid) {
    throw new Error('内容包含乱码，请检查文件编码');
  }
  
  // 2. 发送到Discord（自动处理消息拆分）
  const discordResult = await encoder.sendToDiscord(
    process.env.DISCORD_WEBHOOK,
    content.substring(0, 1900) // Discord消息限制
  );
  
  // 3. 创建GitHub Gist
  const gistResult = await encoder.createGitHubGist(
    process.env.GITHUB_TOKEN,
    content,
    'research.md',
    '用户调研',
    true
  );
  
  // 4. 生成报告
  const report = encoder.generateTestReport([discordResult, gistResult]);
  fs.writeFileSync('./publish-report.md', report, 'utf8');
  
  console.log('🎉 发布完成！');
}

publishResearch().catch(console.error);
```

### 示例2：PowerShell中调用
```powershell
# PowerShell脚本：通过Node.js确保UTF-8编码
$nodeScript = @'
const UTF8Encoder = require("utf8-encoder-tool");
const encoder = new UTF8Encoder();
console.log(encoder.ensureUTF8(process.argv[2]));
'@

$nodeScript | Out-File -FilePath "temp-utf8.js" -Encoding UTF8
$result = node temp-utf8.js "PowerShell中的中文"
Write-Host "UTF-8编码结果: $result"
Remove-Item "temp-utf8.js"
```

## API参考

### UTF8Encoder类

#### `ensureUTF8(text)`
确保文本是UTF-8编码的字符串，支持Buffer、字符串、数字等输入。

#### `calculateUTF8ByteLength(text)`
计算文本的UTF-8字节长度，用于HTTP Content-Length头。

#### `readFileUTF8(filePath)`
以UTF-8编码读取文件，自动验证中文字符。

#### `createUTF8JSONPayload(data, pretty = false)`
创建UTF-8编码的JSON字符串，确保中文内容正确编码。

#### `createUTF8Headers(payload, additionalHeaders = {})`
创建HTTP请求头，包含正确的Content-Type和Content-Length。

#### `validateNoGarbledChars(text)`
验证文本是否包含乱码字符（Unicode替换字符�、异常控制字符）。

#### `sendToDiscord(webhookUrl, content, options = {})`
发送消息到Discord Webhook，自动处理编码和请求头。

#### `createGitHubGist(token, content, filename, description, isPublic)`
创建GitHub Gist，支持私有/公开设置。

#### `generateTestReport(testResults)`
生成Markdown格式的测试报告。

## 技术原理

### 问题根源
1. **编码不一致**：PowerShell控制台使用GB2312编码显示，Node.js使用UTF-8编码传输
2. **验证缺失**：依赖控制台输出判断，未独立验证实际网页显示
3. **成本浪费**：因显示误导导致的重复发布浪费API token

### 解决方案
1. **统一使用Node.js**：端到端UTF-8处理，避免编码转换问题
2. **显式指定编码**：所有文件操作、Buffer转换明确使用`'utf8'`
3. **独立验证**：通过实际API调用和网页访问验证显示效果
4. **字节长度计算**：使用`Buffer.byteLength(text, 'utf8')`而非`text.length`

## 最佳实践

### 开发阶段
1. **先验证后发布**：创建测试Gist/Issue验证编码，确认无误后再正式发布
2. **使用环境变量**：将API Token、Webhook URL存储在环境变量中
3. **记录验证日志**：保存每次发布的验证结果，便于排查问题

### 生产环境
1. **错误处理**：所有API调用都要有try-catch和重试机制
2. **速率限制**：遵守平台API速率限制，添加适当的延迟
3. **监控告警**：监控发布成功率，失败时发送告警

## 常见问题

### Q: 为什么控制台显示乱码但网页正常？
**A**: 控制台使用GB2312编码显示UTF-8内容。解决方案：不依赖控制台输出，通过`web_fetch`或实际访问验证网页显示。

### Q: 如何验证编码是否正确？
**A**: 使用`encoder.validateNoGarbledChars(text)`检测乱码字符，或直接访问生成的Gist/Issue查看实际显示。

### Q: 支持哪些特殊字符？
**A**: 支持中文、日文、韩文、Emoji、特殊符号。使用正则表达式`/[\u4e00-\u9fa5]/`检测中文字符。

### Q: 与平台原生API有什么区别？
**A**: 平台API可能不处理编码问题。本工具确保请求体正确UTF-8编码、Content-Length头准确、Content-Type包含charset=utf-8。

## 更新日志

### v1.0.0 (2026-03-15)
- ✅ 核心UTF-8编码保障功能
- ✅ Discord Webhook支持
- ✅ GitHub Gist & Issues支持  
- ✅ 乱码检测与验证
- ✅ 字节长度计算
- ✅ 完整文档和示例

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 贡献

欢迎提交Issue和Pull Request：
1. Fork仓库
2. 创建功能分支
3. 提交更改
4. 创建Pull Request

问题反馈：https://github.com/mrpulorx2025-source/utf8-encoder-skill/issues

## 致谢

感谢OpenClaw社区的真实需求驱动开发，特别感谢主公的务实方法论指导："勿过度思考、从优解、避免token浪费"。

---

**核心教训**：控制台显示 ≠ 实际数据，必须独立验证网页显示！