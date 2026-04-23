# 🔥 火花 Spark — AI 品牌内容创作 | AI Brand Content Creator

> 一个 Skill 覆盖全场景品牌内容创作。对话式采集需求，自动读取 workspace 品牌资料，2-3 轮对话完成从灵感到成品。
>
> One Skill for all brand content creation. Collects requirements through natural conversation, auto-reads brand materials from your workspace, and delivers from idea to finished content in 2-3 dialogue turns.

## 触发场景 | Trigger Scenarios

任何涉及品牌内容创作的请求 / Any brand content creation request:
- "帮我写一篇..." / "Write me a post about..."
- "帮我发一条小红书/公众号/微博..." / "Create a LinkedIn/Twitter/Instagram post..."
- "帮我做个海报" / "Make a marketing poster"
- "写个口播脚本" / "Write a video script"
- "帮我推一波..." / "Help me promote..."

## 核心能力 | Core Features

### 🌍 18 平台支持 | 18 Platforms
**国内 9 平台 (China):** 微信公众号 · 微博 · 小红书 · 抖音 · 知乎 · B站 · 今日头条 · 百家号 · 快手
**海外 9 平台 (Global):** X/Twitter · LinkedIn · Instagram · Facebook · Threads · TikTok · YouTube · Medium · Reddit

### 🏗️ 多工作台路由 | Multi-Workspace Routing
一个 Skill 统一入口，自动路由到对应工作台：
One entry point, auto-routes to the right workspace:
- 📝 社交媒体图文 Social Media Content（✅ Live）
- 🎨 营销海报 Marketing Poster（✅ Live）
- 🎬 短视频脚本 Short Video Script（🔜 Coming Soon）
- 🛒 电商文案 E-commerce Copy（🔜 Coming Soon）

### 🧠 Workspace 感知 | Workspace-Aware
Skill 运行在用户的 OpenClaw 环境中，会主动：
Runs inside the user's OpenClaw environment and proactively:
- 扫描 workspace 下的品牌/产品/公司文档 | Scans brand/product/company docs in workspace
- 用 memory_search 搜索历史记忆 | Searches historical memory via memory_search
- 自动填充上下文字段 | Auto-fills context fields (brand, product_features, industry, etc.)
- 在确认摘要中标注信息来源 | Marks data sources in the confirmation summary

### 🎛️ 15+ 可控参数 | 15+ Controllable Parameters
写作风格 Writing Style · 内容深度 Content Depth · 段落长度 Paragraph Length · 章节数量 Section Count · 情绪基调 Emotional Tone · 受众定位 Target Audience · 语言风格 Language Register · CTA 策略 CTA Style · 目标字数 Word Count · 图片风格 Image Style · 图片质量 Image Quality · 每段配图数 Images per Paragraph · 去AI味开关 Humanizer Toggle · 去AI味强度 Humanizer Strength

### ✨ AI 能力 | AI Capabilities
- **Humanizer 去 AI 味** — 三级强度，让内容像真人写的 | 3 levels, makes content sound human-written
- **智能配图** — AI 自动为每段生成配图，6 种风格 | Auto-generates images per paragraph, 6 styles
- **多平台适配** — 一次创作，自动适配多平台 | One creation, auto-adapts to multiple platforms
- **参数智能推断** — 根据场景自动选最优参数 | Auto-infers optimal params from context

## 工作流程 | Workflow

```
第 1 轮 Turn 1: 用户说需求 → 提取意图 + 扫描 workspace
               User states need → Extract intent + Scan workspace

第 2 轮 Turn 2: 展示富摘要 → 用户确认 → 提交生成
               Show rich summary → User confirms → Submit

第 3 轮 Turn 3: （仅在用户要修改时）调整后提交
               (Only if user wants changes) Adjust and submit
```

## 安装配置 | Setup

### 1. 编辑 `config.json` | Edit config.json

```json
{
  "apiKey": "spark_your_key_here",
  "apiUrl": "https://ijyztlzuggwrpqeqjkwf.supabase.co/functions/v1/create-session"
}
```

### 2. 获取 API Key | Get API Key

1. 访问 Visit [spark.babelink.ai](https://spark.babelink.ai)
2. 注册/登录 Sign up / Log in
3. 个人中心 → API Key 管理 | Profile → API Key Management
4. 生成新 Key Generate new key（格式 format：`spark_xxxxxxxx`）
5. 填入 config.json | Paste into config.json

### 3. 开始使用 | Start Using

```
你 You: 帮我写一篇公司融资的公众号文章
        Write a WeChat article about our funding round

Agent:  [自动扫描 workspace 品牌资料，展示确认摘要]
        [Auto-scans workspace brand docs, shows confirmation summary]

你 You: 确认 Confirm

Agent:  🔥 已提交！Submitted!
        🔗 https://spark.babelink.ai/article/xxx?token=yyy
```

## 平台关键词映射 | Platform Keyword Mapping

| 用户说 User Says | platform ID |
|-----------------|------------|
| 公众号/微信 WeChat | wechat |
| 微博 Weibo | weibo |
| 小红书/种草 Xiaohongshu/RED | xiaohongshu |
| 抖音/口播 Douyin | douyin |
| 知乎 Zhihu | zhihu |
| B站/哔哩哔哩 Bilibili | bilibili |
| 头条/今日头条 Toutiao | toutiao |
| 百家号/百度 Baidu/Baijiahao | baidu |
| 快手 Kuaishou | kuaishou |
| Twitter/X/推特 | twitter |
| LinkedIn/领英 | linkedin |
| Instagram/Ins | instagram |
| Facebook/脸书 | facebook |
| Threads | threads |
| TikTok | tiktok |
| YouTube/油管 | youtube |
| Medium | medium |
| Reddit | reddit |

## 参数智能推断 | Smart Parameter Inference

| 场景 Scenario | 推断参数 Inferred Params |
|--------------|------------------------|
| 融资/上市 Funding/IPO | professional + detailed + positive |
| 种草/安利 Product Review | casual + overview + empathetic |
| 行业分析 Industry Analysis | professional + expert + neutral |
| 促销活动 Promotion | provocative + overview + urgent |
| 品牌故事 Brand Story | storytelling + detailed + inspiring |
| 产品发布 Product Launch | professional + detailed + positive |
| 教程/干货 Tutorial/Guide | professional + expert + neutral |

## API 接口 | API Reference

**POST** `https://ijyztlzuggwrpqeqjkwf.supabase.co/functions/v1/create-session`

**Headers:** `x-api-key: spark_xxxxx`

**请求体 Request Body:**

| 字段 Field | 说明 Description |
|-----------|-----------------|
| topic | 内容主题（必填）Content topic (required) |
| platform | 目标平台 ID Target platform ID |
| tones | 调性数组 Tone array |
| adapt_platforms | 多平台适配数组 Multi-platform array |
| context.brand | 品牌名 Brand name |
| context.audience | 目标受众 Target audience |
| context.campaign_goal | 营销目标 Campaign goal |
| context.key_messages | 核心信息 Key messages |
| context.product_features | 产品特点 Product features |
| context.industry | 行业 Industry |
| generation_params | 15+ 生成参数 Generation parameters |

**响应 Response:** 返回 `sessionId` + `dashboardUrl`（含自动登录 token）
Returns `sessionId` + `dashboardUrl` (with auto-login token)

## 关于火花 | About Brand Spark

火花 (Brand Spark) 是 AI 驱动的多工作台品牌内容创作 SaaS 平台，由半人马AI / Centaur AI 开发。
Brand Spark is an AI-powered multi-workspace brand content creation SaaS platform, built by Centaur AI.

- 🌐 平台 Platform: [spark.babelink.ai](https://spark.babelink.ai)
- 📦 GitHub: [github.com/finewood2008/brand-spark](https://github.com/finewood2008/brand-spark)
