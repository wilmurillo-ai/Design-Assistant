# WeChat Article Fetcher - 微信文章抓取技能

> 使用 Puppeteer + Chrome 无头模式抓取微信公众号文章，绕过反爬虫机制。

---

## 📋 技能信息

| 字段 | 值 |
|------|-----|
| **技能名称** | wechat-article-fetcher-safe |
| **版本** | 1.1.0 |
| **作者** | 潜助 (基于实战经验整理) |
| **创建时间** | 2026-03-25 |
| **适用场景** | 微信公众号文章抓取、内容分析、素材收集 |
| **技术栈** | Node.js + Puppeteer + Chrome |
| **成功率** | 100% (3/3 测试通过) |

---

## 🎯 功能特性

### ✅ 支持
- 微信公众号文章全文抓取
- 文章元信息提取（标题、作者、时间）
- 移动端 User-Agent 伪装
- JavaScript 渲染页面支持
- 自动保存为文本文件
- 错误处理和超时保护

### ❌ 不支持
- 需要登录的文章
- 付费阅读内容
- 纯图片/视频内容
- 批量高频抓取（需额外配置代理）

---

## 📦 安装步骤

### 1. 确认 Node.js 环境

```bash
node -v  # 建议 v18+
```

### 2. 安装 Puppeteer

```bash
cd E:\Dev\.openclaw\workspace\skills\wechat-article-fetcher-safe
npm install puppeteer-core
```

### 3. 确认 Chrome 路径

**Windows 标准路径:**
```
C:\Program Files\Google\Chrome\Application\chrome.exe
```

**验证命令:**
```bash
where chrome
```

---

## 🚀 使用方法

### 方式一：命令行参数（推荐）

```bash
# 运行脚本抓取指定文章
node fetch-wechat-article.js https://mp.weixin.qq.com/s/xxx
```

### 方式二：作为 OpenClaw Skill 调用

```javascript
// 在 OpenClaw Agent 中调用
const { fetchWechatArticle } = require('./fetch-wechat-article');

const result = await fetchWechatArticle({
  url: 'https://mp.weixin.qq.com/s/xxx',
  saveToFile: true,
  outputDir: './output'
});

console.log(result.title);
console.log(result.content);
```

---

## 📝 输出示例

### 控制台输出

```
========== 文章信息 ==========

标题：全网都在养的小龙虾，正在没有人类的论坛里进化？
作者：差评 X.PIN
时间：差评君

========== 文章内容 ==========

要说最近最火的电子宠物是啥，肯定是那只全网都在养的小龙虾...
（正文内容）
...

========== 文章结束 ==========

内容已保存到：E:\Dev\.openclaw\workspace\article-wechat-1774081600976.txt
```

### 保存的文件

```
标题：全网都在养的小龙虾，正在没有人类的论坛里进化？
作者：差评 X.PIN
时间：差评君

要说最近最火的电子宠物是啥，肯定是那只全网都在养的小龙虾...
（完整正文内容）
```

---

## 🔑 核心实现

### 1. 启动 Chrome 无头模式

```javascript
const browser = await puppeteer.launch({
  executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  headless: true,
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-web-security'
  ]
});
```

**关键点:**
- `headless: true` - 无头模式，不显示浏览器窗口
- `--no-sandbox` - 禁用沙箱（必需）
- `--disable-gpu` - 禁用 GPU 加速（避免兼容性问题）

---

### 2. 设置移动端 User-Agent

```javascript
await page.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.0');
await page.setViewport({ width: 375, height: 812 });
```

**为什么有效？**
- 微信文章对移动端更友好
- 反爬机制相对宽松
- 模拟 iPhone + 微信内置浏览器

---

### 3. 等待页面加载

```javascript
await page.goto(url, {
  waitUntil: 'networkidle2',  // 等待网络空闲
  timeout: 60000
});
```

**waitUntil 选项:**
- `load` - 等待 load 事件
- `domcontentloaded` - 等待 DOMContentLoaded
- `networkidle0` - 等待 0 个网络连接（严格）
- `networkidle2` - 等待 ≤2 个网络连接（推荐）

---

### 4. 提取内容

```javascript
const articleData = await page.evaluate(() => {
  // 标题
  const title = document.querySelector('#activity-name')?.innerText || '无标题';
  
  // 作者
  const author = document.querySelector('.rich_media_meta_nickname')?.innerText || '未知';
  
  // 正文（多选择器回退）
  const selectors = ['#js_content', '.rich_media_content', '.rich_media_area_primary', 'article'];
  let content = '';
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      content = el.innerText;
      break;
    }
  }
  
  return { title, author, content };
});
```

**选择器说明:**
- `#js_content` - 微信文章主要内容容器
- `.rich_media_content` - 富媒体内容区
- `.rich_media_area_primary` - 主内容区
- `article` - 通用文章标签

---

## ⚠️ 常见问题

### Q1: 找不到 Chrome 路径

**错误:** `Error: Failed to launch the browser process`

**解决:**
```bash
# Windows
where chrome

# macOS
mdfind -name "Google Chrome.app"

# Linux
which google-chrome
```

然后修改脚本中的 `chromePath`。

---

### Q2: 抓取内容为空

**可能原因:**
1. 页面未完全加载
2. 选择器不匹配
3. 文章需要登录

**解决:**
```javascript
// 增加等待时间
await page.waitForSelector('#js_content', { timeout: 30000 });

// 添加额外等待
await new Promise(r => setTimeout(r, 3000));

// 尝试其他选择器
const selectors = ['#js_content', '.rich_media_content', 'article'];
```

---

### Q3: 被微信反爬拦截

**症状:** 返回验证码页面或空白页

**解决:**
1. ✅ 使用移动端 User-Agent（已内置）
2. ✅ 添加随机延迟
3. ✅ 限制抓取频率（建议间隔 >5 秒）
4. ✅ 使用住宅 IP 代理（批量抓取时）

---

### Q4: Puppeteer 连接失败

**错误:** `Error: connect ECONNREFUSED`

**解决:**
```bash
# 关闭所有 Chrome 进程
taskkill /F /IM chrome.exe  # Windows
killall Chrome              # macOS/Linux

# 重新启动脚本
```

---

## 📊 测试记录

| 序号 | 文章标题 | URL | 结果 | 字数 | 备注 |
|------|----------|-----|------|------|------|
| 1 | Evolver + EvoMap 实战 | .../VxW1ZyFgs_KeXZ8ygf3K6A | ✅ | ~15000 | 长文 |
| 2 | 小龙虾 Skills 推荐 | .../UqSGc7d6RxgOzFNI9JWYPg | ✅ | ~100 | 短文 |
| 3 | 全网都在养小龙虾 | .../mCH_H29Zaepwk2NGukU_Fg | ✅ | ~3000 | 中长文 |

**成功率**: 100% (3/3)  
**平均耗时**: ~5 秒/篇

---

## 🔧 进阶用法

### 1. 批量抓取

```javascript
const urls = [
  'https://mp.weixin.qq.com/s/xxx',
  'https://mp.weixin.qq.com/s/yyy',
  'https://mp.weixin.qq.com/s/zzz'
];

for (const url of urls) {
  await fetchWechatArticle({ url });
  await sleep(5000);  // 间隔 5 秒，避免被封
}
```

### 2. 保存图片

```javascript
// 下载文章中的图片
const images = await page.$$('img');
for (let i = 0; i < images.length; i++) {
  const img = images[i];
  const src = await img.getPropertyValue('src');
  // 下载图片到本地
}
```

### 3. 导出为 Markdown

```javascript
// 将 HTML 转换为 Markdown
const { htmlToText } = require('html-to-text');
const markdown = htmlToText(htmlContent, {
  wordwrap: false,
  format: 'markdown'
});
```

---

## 📁 文件结构

```
wechat-article-fetcher-safe/
├── SKILL.md                    # 技能文档（本文件）
├── fetch-wechat-article.js     # 主脚本
├── package.json                # npm 配置
├── README.md                   # 使用说明
├── examples/                   # 示例输出
│   ├── article-1.txt
│   └── article-2.txt
└── tests/                      # 测试记录
    ├── test-results.md
    └── run-tests.js
```

---

## 🎓 学习资源

- [Puppeteer 官方文档](https://pptr.dev/)
- [微信文章结构分析](https://developers.weixin.qq.com/community/develop)
- [反爬虫对抗指南](https://github.com/lorien/awesome-web-scraping)
- [Node.js 爬虫实战](https://github.com/chenjiandongx/awesome-crawler)

---

## 📝 更新日志

### v1.1.0 (2026-03-25)
- ✅ 重命名为安全版 (safe) 明确隐私保护特性
- ✅ 优化正文清洗和失败识别机制
- ✅ 自动探测 Chrome 路径，提高可移植性
- ✅ 统一测试与执行入口

### v1.0.0 (2026-03-21)
- ✅ 初始版本
- ✅ 支持微信公众号文章抓取
- ✅ 移动端 User-Agent 伪装
- ✅ 自动保存为文本文件
- ✅ 错误处理和超时保护
- ✅ 测试通过率 100%

---

## 🙏 致谢

本技能基于以下实战经验整理：
- 成功抓取 3 篇微信文章（长文、短文、中长文）
- 验证多种反爬对抗策略
- 优化选择器和等待策略

感谢 Captain AI 实验室、差评君等公众号提供的测试素材。

---

## 📄 许可证

MIT License - 可自由使用、修改、分发

---

**最后更新**: 2026-03-21  
**维护者**: 潜助 🤖  
**反馈**: 欢迎提交 Issue 或 PR
