# weixin-send-media

微信发图片/文件技能 - 解决 contextToken 持久化问题

[![ClawHub](https://img.shields.io/badge/clawhub-weixin--send--media-blue)](https://clawhub.com/skills/weixin-send-media)
[![Version](https://img.shields.io/badge/version-1.1.0-green)](https://clawhub.com/skills/weixin-send-media)
[![License](https://img.shields.io/badge/license-MIT--0-lightgrey)](./LICENSE)

---

## 🚀 快速开始

### 1. 安装

```bash
# 自动安装（推荐）
npx clawhub@latest install weixin-send-media

# 或手动安装
git clone https://github.com/lin-yac/openclaw-weixin-send-media.git
cd openclaw-weixin-send-media
./install.sh
```

### 2. 使用

```bash
# 发送图片
./scripts/send-image.js <user-id> <image-path> [caption]

# 发送文件
./scripts/send-file.js <user-id> <file-path> [description]

# 查看 token
./scripts/export-context-token.js list
```

---

## ✨ 功能特性

- ✅ 支持发送图片（PNG/JPG/GIF/WEBP）
- ✅ 支持发送文件（PDF/DOC/ZIP 等）
- ✅ 支持网络图片 URL
- ✅ contextToken 持久化（内存 + 磁盘双存储）
- ✅ CLI 友好
- ✅ 脚本可调用
- ✅ 完整的错误处理和日志
- ✅ 安全说明和最佳实践

---

## 📋 解决的问题

微信渠道原本无法通过 CLI 发送媒体消息，因为 `contextToken` 只缓存在 gateway 内存中，导致：

- ❌ CLI 命令无法发送媒体消息
- ❌ 自动化脚本无法调用
- ❌ 重启 gateway 后 token 丢失

本技能通过持久化 token 到磁盘，解决了这个问题：

- ✅ CLI/脚本都能发送消息
- ✅ gateway 重启后 token 不丢失
- ✅ 支持定时任务和自动化工作流

---

## 📖 文档

- **[SKILL.md](./SKILL.md)** - 完整使用文档（推荐先看这个）
- **[CHANGELOG.md](./CHANGELOG.md)** - 更新日志
- **[references/api-docs.md](./references/api-docs.md)** - API 文档

---

## 🔒 安全性

本技能需要修改 OpenClaw 核心扩展文件，ClawHub 可能显示安全警告。这是误报：

- ✅ 不窃取任何数据
- ✅ 不连接外部服务器
- ✅ 所有操作在本地完成
- ✅ 代码完全开源可审计

详见 [SKILL.md - 安全说明](./SKILL.md#-安全说明重要)

---

## 🧪 测试

```bash
# 运行测试脚本
./tests/test-token-persistence.sh
```

---

## 💡 典型用例

### 发送二维码给家人

```bash
# 生成二维码
openclaw qr > qr.png

# 发送
./scripts/send-image.js o9cq802hhREiOXPlXq_Tgb0MjPTo@im.wechat qr.png "扫码绑定 OpenClaw"
```

### 定时发送日报

```bash
# crontab 配置
0 18 * * * /path/to/scripts/send-image.js <user-id> /path/to/daily-report.png "📊 今日日报"
```

---

## 📦 文件结构

```
weixin-send-media/
├── SKILL.md                    # 完整文档
├── README.md                   # 本文件
├── CHANGELOG.md                # 更新日志
├── install.sh                  # 安装脚本
├── scripts/
│   ├── send-image.js           # 发图片脚本
│   ├── send-file.js            # 发文件脚本
│   └── export-context-token.js # Token 管理工具
├── patches/
│   └── inbound.ts.patch        # 补丁文件
├── references/
│   └── api-docs.md             # API 文档
└── tests/
    └── test-token-persistence.sh # 测试脚本
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT-0 License - 免费使用、修改、分发，无需署名。

---

## 🦆 作者

鸭鸭 (Yaya) - OpenClaw 微信渠道增强
