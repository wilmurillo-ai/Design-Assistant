---
name: wechat-daily-article
description: 微信公众号每日文章自动创作技能。自动化流程：搜索热点 → 撰写800-1500字SEO优化文章 → 生成7张配图 → 上传草稿箱。当用户要求创作微信公众号文章、设置每日公众号推送、创建公众号内容工作流、或需要定时发送公众号文章时触发。
---

# 微信公众号每日文章创作

自动化工作流，覆盖从热点发现到草稿箱保存的完整环节。

## 工作流程

```
搜索热点 → 选定主题 → 写文章（HTML）→ 生成7张配图 → 保存草稿
```

## 第一步：搜索热点

用 `web_search` 搜索以下关键词组合，获取当日热点：

```
「今日旅游热点」「今日美食热点」「小红书旅游爆款笔记」「抖音美食热门」
```

从微博、小红书、抖音、知乎等平台收集热度最高的话题。**旅游和美食方向优先**。

## 第二步：写文章

### 标题规范（SEO优化）

- 清晰、简洁、直接
- 表意明确不夸大
- 避免标题党、堆砌关键词
- 避免过长

### 正文规范

- 主题鲜明统一，围绕一个主旨展开
- 内容详实有深度，提供具体论据
- 表达简洁流畅
- 鼓励原创，拒绝搬运
- 开头 50 字必须抓住眼球
- 结尾要有引导话术（关注+互动）

### 排版规范

- 章节标题用 emoji 装饰：`🌸 一、xxx`
- 正文段落用 emoji 开头：`🌼 说到四月...`
- 列表项用 emoji：`<li>🦐 必吃推荐：...</li>`
- 适当分段，避免过度加粗

### 文章结构模板

```html
<!-- 封面占位 -->
<p><img src="COVERIMG_URL" /></p>

<h2>🌸 一、[章节1标题]</h2>
<p>🌼 [内容]</p>

<h2>🍜 二、[章节2标题]</h2>
<p>🥟 [内容]</p>

<!-- ... 3-4个章节 ... -->

<hr>
<p><em>关注【镜头逃亡·旅食记】，用镜头记录旅途，用味蕾丈量世界。</em></p>
<p><strong>#旅行 #美食 #探店 #打卡</strong></p>
```

### 图片占位符

在 HTML 正文中需要插入图片的位置使用占位符，生成图片后脚本会自动替换：

| 占位符 | 说明 |
|--------|------|
| `<p><img src="COVERIMG_URL" /></p>` | 封面图，1张 |
| `<p><img src="CHAPIMG1_URL" /></p>` | 章节图1 |
| `<p><img src="CHAPIMG2_URL" /></p>` | 章节图2 |
| `<p><img src="CHAPIMG3_URL" /></p>` | 章节图3 |
| `<p><img src="CHAPIMG4_URL" /></p>` | 章节图4 |
| `<p><img src="CHAPIMG5_URL" /></p>` | 章节图5 |
| `<p><img src="CHAPIMG6_URL" /></p>` | 章节图6 |

### 字数要求

800-1500 字（不含 HTML 标签）。

## 第三步：生成配图

用 `image_generate` 生成 7 张图，保存到 `/tmp/`：

```bash
# 封面图
image_generate "旅行/美食主题封面，高清，电影感，温馨氛围，浅景深，柔和色调" -> /tmp/cover.png

# 章节图1-6
image_generate "具体场景描述，高清，摄影作品，电影感，浅景深" -> /tmp/chap1.png ~ /tmp/chap6.png
```

**图片 prompt 规范：**
- 必须包含：具体场景 + 标志性元素 + 摄影风格
- 风格词：摄影作品、高清、电影感、温馨氛围（美食类用：烟火气/温馨家常）、浅景深、柔和色调
- 不要只写目的地名称，要有视觉元素

## 第四步：保存文件

```bash
# 保存文章HTML
标题保存到：/tmp/article_title.txt
内容保存到：/tmp/article.html

# 文件名格式
/tmp/cover.png        # 封面
/tmp/chap1.png ~ /tmp/chap6.png  # 章节图
```

## 第五步：创建草稿

```bash
python3 /root/.openclaw/workspace/skills/wechat-daily-article/scripts/create_draft.py \
  "$(cat /tmp/article_title.txt)" \
  "/tmp/article.html"
```

脚本会自动：
1. 获取 access_token
2. 上传所有图片到微信，获得永久 URL
3. 替换 HTML 中的本地路径和占位符
4. 自动注入 emoji 关键词
5. 清理标题重复
6. 创建草稿箱草稿

## 飞书通知（可选）

草稿创建成功后，可通过飞书通知：

```bash
# 获取 token
TOKEN=$(curl -s -X POST 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal' \
  -H 'Content-Type: application/json' \
  -d '{"app_id": "cli_a937a350cb789bc7", "app_secret": "Ss73fyDv2ZXHJbh25QJMnf8OqGFIWnpi"}' \
  | grep -o '"tenant_access_token":"[^"]*"' | cut -d'"' -f4)

# 发送文本
curl -s -X POST 'https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id' \
  -H "Authorization: Bearer ${TOKEN}" \
  -H 'Content-Type: application/json' \
  -d '{"receive_id": "ou_ed07e10338498478ac86cd8773ed695d", "msg_type": "text", "content": "{\"text\": \"📝 公众号文章已生成\\n标题：'$(cat /tmp/article_title.txt)'\\n请前往公众号后台草稿箱查看发布\"}"}'
```

## 定时任务配置

如需设置每日自动执行，创建 cron 任务：

```json
{
  "name": "公众号文章每日创作",
  "schedule": "cron 5 12 * * *",
  "payload": {
    "kind": "agentTurn",
    "message": "执行公众号文章每日创作流程。参考 skill: wechat-daily-article",
    "timeoutSeconds": 3600
  },
  "delivery": {
    "mode": "announce",
    "channel": "feishu",
    "to": "user:ou_ed07e10338498478ac86cd8773ed695d"
  }
}
```

## 排版美化（自动应用）

脚本 `create_draft.py` 会自动对 HTML 进行排版美化，包括：

- **结构重组**：自动识别长段落，将「必吃清单/景点攻略/交通指南」等段落升级为带小标题的 h3 块
- **视觉高亮**：自动给数字+量词（3公里、7家店）和感受词（好吃到哭、宝藏、yyds）加橙色底纹
- **列表改造**：自动把「美食1、美食2、美食3」纯文本列表转换成👉带图标的 <ul> 列表
- **章节标题样式**：h2 白色字+橙色渐变背景（卡片感），h3 橙色竖线+浅底色，与正文形成强烈对比
- **正文样式**：17px + 行高2.0 + 宽松字间距 + 两端对齐，阅读舒适
- **图片样式**：圆角 + 阴影，居中显示
- **引用块**：绿色左边框 + 浅绿背景，用于 Tips/注意事项

## 常见问题

**图片生成模糊/不贴合？** → prompt 必须包含具体场景+标志性元素+摄影风格，参考 references/image-prompts.md

**草稿创建失败？** → 检查 WECHAT_APPID/WECHAT_SECRET 凭据，或微信服务器 IP 白名单

**文章SEO不达标？** → 参考 references/seo-guidelines.md 优化标题和正文

## 相关文件

- `scripts/create_draft.py` — 草稿创建脚本（上传图片 + 写草稿 + emoji注入）
- `references/image-prompts.md` — 图片 prompt 规范与示例
- `references/seo-guidelines.md` — 公众号 SEO 规范
