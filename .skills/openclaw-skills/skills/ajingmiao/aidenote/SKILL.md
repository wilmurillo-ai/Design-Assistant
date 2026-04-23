---
name: SlonAide 录音笔记
description: 智能录音笔记管理助手 - AI 自动转写和总结录音，支持知识库管理和语义搜索
version: 2.0.0
author: SlonAide Team
capabilities:
  - 查询和搜索录音笔记
  - 获取转写文本和 AI 总结
  - 知识库管理和语义检索
  - 文件夹分类和标签管理
---

# SlonAide 录音笔记技能 v2.0

## 🚀 快速开始

### 1. 安装技能
```bash
openclaw skills install slonaide
```
或通过 ClawHub:
```bash
npx clawhub install slonaide
```

### 2. 获取 API Key
1. 访问 https://h5.aidenote.cn/ 并登录
2. 进入"我的"页面 → 点击"API Key"
3. 输入密钥名称（如：OpenClaw）
4. 点击"生成访问密钥"
5. 复制生成的 API Key（格式：`sk-xxxxxxxx...`）

### 3. 配置 API Key
```bash
openclaw config set slonaide.apiKey "sk-你的API密钥"
```

### 4. 测试连接
```bash
# 在 OpenClaw 会话中使用
slonaide_test_connection
```

## 🛠️ 可用工具

### 1. 获取录音笔记列表
```bash
slonaide_get_list
```
**参数：**
- `page`: 页码（默认: 1）
- `pageSize`: 每页数量（1-50，默认: 10）
- `keyword`: 搜索关键词（可选）

**示例：**
```bash
# 获取第一页，每页10条
slonaide_get_list

# 搜索包含"会议"的笔记
slonaide_get_list keyword="会议"

# 获取第二页，每页20条
slonaide_get_list page=2 pageSize=20
```

### 2. 获取笔记详情
```bash
slonaide_get_detail fileId="笔记ID"
```
**参数：**
- `fileId`: 录音笔记文件ID（必填）

**示例：**
```bash
slonaide_get_detail fileId="787760209850437"
```

### 3. 获取最新笔记摘要
```bash
slonaide_get_summary
```
**参数：**
- `count`: 要获取的记录数量（1-10，默认: 3）

**示例：**
```bash
# 获取最新3条笔记摘要
slonaide_get_summary

# 获取最新5条笔记摘要
slonaide_get_summary count=5
```

### 4. 测试连接
```bash
slonaide_test_connection
```
测试 API 连接和配置状态。

## 🔧 配置说明

### 配置文件位置
`~/.openclaw/openclaw.json`

### 配置示例
```json
{
  "plugins": {
    "entries": {
      "slonaide": {
        "enabled": true,
        "config": {
          "apiKey": "sk-你的API密钥",
          "baseUrl": "https://api.aidenote.cn"
        }
      }
    }
  }
}
```

### 配置参数
- `apiKey`: SlonAide API Key（必填）
- `baseUrl`: API 基础地址（默认: `https://api.aidenote.cn`）

## 🔒 安全规则

### 隐私保护
- 笔记数据属于用户隐私，不在群聊中主动展示完整内容
- 转写文本默认只显示前500字符
- 敏感信息自动脱敏处理

### API 安全
- API Key 加密存储
- 令牌自动缓存和刷新
- 请求失败时自动重试（最多3次）
- 连接超时保护（15秒）

## 🐛 故障排除

### 常见问题

#### 1. "未配置 API Key"
**解决方案：**
```bash
openclaw config set slonaide.apiKey "你的API密钥"
```

#### 2. "认证失败"
**可能原因：**
- API Key 无效或已过期
- 网络连接问题
- API 服务暂时不可用

**解决方案：**
1. 重新生成 API Key
2. 检查网络连接
3. 等待服务恢复

#### 3. "获取列表失败"
**可能原因：**
- 令牌过期
- API 响应格式变化
- 服务器错误

**解决方案：**
```bash
# 测试连接
slonaide_test_connection

# 如果测试失败，重新配置
openclaw config set slonaide.apiKey "新API密钥"
```

### 调试模式
启用详细日志：
```bash
openclaw config set slonaide.debug true
```

## 📊 使用场景

### 场景1：日常笔记管理
```bash
# 查看最新笔记
slonaide_get_summary count=5

# 查看某条笔记详情
slonaide_get_detail fileId="笔记ID"
```

### 场景2：会议记录整理
```bash
# 搜索会议相关笔记
slonaide_get_list keyword="会议"

# 获取未转写的会议记录
slonaide_get_list keyword="会议" pageSize=20
```

### 场景3：问题跟踪
```bash
# 查看异常记录
slonaide_get_list keyword="异常"

# 获取技术问题记录
slonaide_get_list keyword="系统" keyword="错误"
```

## 🔄 更新日志

### v2.0.0 (2026-03-26)
**重大改进：**
- ✅ 完整的 OpenClaw 工具实现
- ✅ 自动令牌管理和缓存
- ✅ 完善的错误处理和用户提示
- ✅ 优化的输出格式和可读性
- ✅ 连接测试工具
- ✅ 摘要统计功能
- ✅ 类型分析和建议

### v1.0.0 (初始版本)
- 基础技能框架
- Python 辅助脚本
- API 文档

## 📝 技术细节

### API 端点
- **Base URL**: `https://api.aidenote.cn`
- **认证**: `POST /api/UserapikeyMstr/GetToken/{apiKey}`
- **列表**: `POST /api/audiofileMstr/audiofileseleUserAllList`
- **详情**: `GET /api/audiofileMstr/GetAudioFileDetail/{fileId}`

### 数据格式
```json
{
  "code": 200,
  "message": "成功",
  "result": {
    "total": 111,
    "records": [
      {
        "id": "文件ID",
        "audiofileTitle": "标题",
        "audiofileFileName": "文件名",
        "createTime": "时间戳",
        "audiofileTimeLength": "时长(毫秒)",
        "transcriptStatus": 2,
        "summaryStatus": 2,
        "transcriptText": "转写文本",
        "aiSummary": "AI总结",
        "tags": ["标签1", "标签2"]
      }
    ]
  }
}
```

### 状态码
- `transcriptStatus`: 0=未开始, 1=进行中, 2=已完成
- `summaryStatus`: 0=未开始, 1=进行中, 2=已完成

## 🤝 贡献指南

### 报告问题
在 GitHub Issues 中报告问题，包括：
1. 问题描述
2. 复现步骤
3. 错误信息
4. 环境信息

### 提交改进
1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📞 支持

### 官方支持
- 网站: https://h5.aidenote.cn/
- API 文档: 内置文档

### 社区支持
- GitHub Issues: 问题反馈
- OpenClaw 社区: 使用讨论

## 📄 许可证
MIT License - 详见 LICENSE 文件

---

**提示**: 首次使用前请务必配置 API Key，否则工具无法正常工作。
