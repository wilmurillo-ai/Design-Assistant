# 自媒体文章发布工具

一个OpenClaw Skill，用于将文章自动发布到多个自媒体平台。

## 功能特点

- 🚀 **多平台支持** - 知乎、Bilibili、百家号、头条号、小红书
- 🔐 **扫码登录** - 支持扫码登录，自动保存Cookie
- 💾 **Cookie持久化** - 登录状态持久保存，免重复登录
- 📝 **一键发布** - 支持单平台发布和全平台一键发布
- 🖼️ **图片上传** - 支持封面图片上传

## 安装

```bash
# 从ClawHub安装
clawhub install article-publisher

# 或手动安装
cd ~/.openclaw/skills
git clone <repo-url> article-publisher
cd article-publisher
npm install
npm run build
```

## 使用方法

### 1. 登录平台

在OpenClaw对话中说：

```
请帮我登录知乎
```

系统会打开浏览器，显示登录二维码，扫码后自动保存登录状态。

### 2. 检查登录状态

```
检查我的登录状态
```

或

```
列出所有平台
```

### 3. 发布文章

发布到单个平台：

```
帮我发布一篇文章到知乎
标题：我的第一篇文章
内容：这是文章的正文内容...
```

发布到所有已登录平台：

```
把这篇文章发布到所有已登录的平台
```

### 4. 退出登录

```
退出知乎登录
```

## 支持的平台

| 平台 | 登录方式 | 发布类型 |
|------|---------|---------|
| 知乎 | 扫码登录 | 文章 |
| Bilibili | 扫码登录 | 专栏文章 |
| 百家号 | 扫码登录 | 图文 |
| 头条号 | 扫码登录 | 文章 |
| 小红书 | 扫码登录 | 笔记 |

## 配置

Cookie默认存储在 `data/cookies/` 目录下。

可以在 `src/lib/config.ts` 中修改配置：

```typescript
export const config = {
  cookieDir: './data/cookies',  // Cookie存储目录
  cookieExpiry: 30,              // Cookie有效期（天）
  headless: false,               // 是否无头模式
  timeout: 60000,                // 操作超时时间（毫秒）
};
```

## 开发

```bash
# 安装依赖
npm install

# 开发模式（监听编译）
npm run dev

# 构建
npm run build

# 清理
npm run clean
```

## 注意事项

1. 首次使用需要扫码登录各平台
2. Cookie有效期一般为7-30天，过期后需重新登录
3. 发布时请确保文章内容符合各平台规范
4. 建议不要频繁发布，避免被平台风控

## License

MIT
