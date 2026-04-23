# 📰 微信文章抓取器 - 安全版

> 快速、安全地抓取微信公众号文章，支持全文提取、元信息获取、自动保存，注重本地隐私保护。

---

## ⚡ 快速开始

### 1. 安装依赖

```bash
cd skills/wechat-article-fetcher-safe
npm install
```

### 2. 运行

```bash
# 方式 1: 直接运行
node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx

# 方式 2: 使用 npm 脚本
npm run fetch https://mp.weixin.qq.com/s/xxx

# 方式 3: 运行测试
npm test
```

---

## 📋 功能特性

- ✅ **本地运行** - 保护隐私，不向第三方发数据
- ✅ 微信公众号文章全文抓取
- ✅ 元信息提取（标题、作者、时间）
- ✅ 移动端 User-Agent 伪装
- ✅ JavaScript 渲染支持
- ✅ 自动保存为文本文件
- ✅ 错误处理和超时保护
- ✅ 100% 测试通过率

---

## 📖 文档

详细文档请查看：[SKILL.md](./SKILL.md)

---

## 🧪 测试记录

| 文章 | 结果 | 字数 |
|------|------|------|
| Evolver + EvoMap 实战 | ✅ | ~15000 |
| 小龙虾 Skills 推荐 | ✅ | ~100 |
| 全网都在养小龙虾 | ✅ | ~3000 |

---

## 📄 许可证

MIT License
