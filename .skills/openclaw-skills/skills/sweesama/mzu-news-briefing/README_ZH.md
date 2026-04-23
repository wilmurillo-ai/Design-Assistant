# Mzu 新闻简报 · 每日科技简报

> 多源 AI / 科技新闻聚合与智能简报生成工具。覆盖 AI、大模型、科技行业、财经市场、世界大事——按热度分级输出，来源全程可溯。
>
> 支持 **Twitter/X**（通过 bird CLI）和 **Grok API** 两条搜索后端。Twitter 路线无需 API Key，完全免费。

---

## 这个 Skill 能做什么

当被触发时，自动执行：

1. **7 个维度分层搜索**（A 周报聚合 / B 社区热度 / C AI 模型与大厂动态 / D 中文专业媒体 / E 财经融资 / F 监管政策 / G 市场事件）
2. 每次简报 **8+ 次搜索**，串行执行（Brave Free 并发限制为 1）
3. **交叉验证**：同一事件 3+ 来源提及 → 确认为热点，深入挖掘
4. **去重合并**：多家报道同一事件 → 并为一条，选最权威来源作主链
5. **热度分级**：🔥 高（深度分析段落）/ ⚡ 中（标准摘要）/ 💤 低（仅标题或丢弃）
6. **结构化输出**：10-15 条，高热度条目附分析段落

输出语言：**中文为主**，专业术语首次出现附英文原词。

---

## 内容优先级

| 层级 | 比重 | 覆盖范围 |
|------|------|---------|
| 🥇 核心 | 50% | AI / 大模型 / Agent / 工具 / 研究 / 融资 |
| 🥈 延伸 | 30% | 科技行业 · 大厂动态 · 产品发布 · 平台新闻 |
| 🥉 补充 | 20% | 财经市场 · 股市 · 大宗商品 · 货币政策 |
| 🌍 背景 | 10% | 世界大事 · 地缘冲突 · 重大突发事件 |

> 军事新闻：极少入选，仅当直接冲击科技供应链、能源市场或 AI 行业格局时入选。

---

## 安装步骤

### 第一步：安装 agent-reach

```bash
python -m venv ~/.agent-reach-venv
source ~/.agent-reach-venv/bin/activate  # Windows: .\.agent-reach-venv\Scripts\activate
pip install agent-reach
```

### 第二步：配置搜索后端（二选一）

#### 方案 A：Twitter/X（推荐，免费）

```bash
# 1. 安装 bird CLI
npm install -g @steipete/bird

# 2. 从 Chrome 导出 Twitter Cookies
#    - 在 Chrome 登录 x.com
#    - 按 F12 → Application → Cookies → x.com
#    - 找到 auth_token 和 ct0，复制完整值

# 3. 保存到本地文件
echo "AUTH_TOKEN=你的auth_token值" > ~/.agent-reach-twitter.env
echo "CT0=你的ct0值" >> ~/.agent-reach-twitter.env

# 4. 验证连接
bird --auth-token 你的auth_token --ct0 你的ct0 whoami
# 正确返回你的 Twitter 用户名
```

**每次新 session 加载认证：**
```bash
# Linux/macOS
export $(cat ~/.agent-reach-twitter.env | xargs)

# Windows PowerShell
Get-Content ~\.\.agent-reach-twitter.env | ForEach-Object { $kvp = $_.Split('=',2); [Environment]::SetEnvironmentVariable($kvp[0], $kvp[1], 'Process') }
```

#### 方案 B：Grok API

```bash
# 1. 在 https://x.ai/api 免费注册，获取 API Key
# 2. 保存到本地文件
echo "你的Grok_API_Key" > ~/.grok-api-key

# Grok 直接集成在工作流中，无需额外 CLI 调用
```

### 第三步：设置每日定时简报（可选）

```bash
# 每天 08:00 早间简报
openclaw cron add "0 8 * * *" "请按 skills/mzu-news-briefing/SKILL.md 生成今日简报" --announce

# 每天 22:00 晚间简报
openclaw cron add "0 22 * * *" "请按 skills/mzu-news-briefing/SKILL.md 生成今日简报" --announce
```

---

## 搜索维度说明

| 维度 | 主题 | 主要信源 |
|------|------|---------|
| A | 周报 / Newsletter 聚合 | NeuralBuddies、gtmaipodcast、labla.org |
| B | 社区热度信号 | Hacker News、Reddit r/MachineLearning、GitHub Trending |
| C | AI 模型 / 大厂动态 | Twitter/X（bird）、releasebot.io、Grok API |
| D | 中文专业媒体 | 36氪、机器之心、量子位 |
| E | 财经 / 融资 | aifundingtracker.com、Bloomberg AI |
| F | 监管 / 政策 | Reuters AI、Politico、NYT AI |
| G | 市场事件 | （补充维度，有重大波动时触发） |

> **重要**：每次简报搜索不少于 8 次，串行执行，每次间隔 ≥2 秒（Brave 免费套餐并发限制为 1）。

---

## 输出格式示例

```
📰 Mzu 每日简报 YYYY-MM-DD HH:MM

本班共收录 XX 条 | 搜索 XX 次 | 覆盖维度：A/B/C/D/E/F
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 高热度

1. [新闻标题](https://...)
   来源：媒体名 | 时间：YYYY-MM-DD | 标签：#AI #Agent
   摘要：（50字以内）

   ▶ 深度：为什么这条重要
   · （分析点1）
   · （分析点2）

⚡ 中热度

2. [新闻标题](https://...)
   来源：媒体名 | 时间：YYYY-MM-DD | 标签：#大厂 #产品
   摘要：（含关键数据）

💤 低热度（如有）

3. [新闻标题](https://...)
   来源：... | 标签：...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
维度覆盖：A(X) B(X) C(X) D(X) E(X) F(X)
下一班：HH:MM
```

---

## 信源优先级

当同一事件多来源可选时，按此顺序选主链：

1. **X / Twitter** — 大厂官方第一时间发布（时效最快）
2. **Reuters / BBC** — 突发新闻、硬事实
3. **Hacker News** — 技术社区反应、工具热度
4. **36Kr / 机器之心 / 量子位** — 中文科技专业报道
5. **The Verge / Wired / TechCrunch** — 产品评测与行业分析
6. **MIT Tech Review** — 研究与深度报道
7. **周报 / Newsletter** — 信息密度最高的策划内容

---

## 反模式清单

❌ `"AI news today"` → 大量 SEO 聚合页，信息噪音
❌ 加具体年月日 → 偏向预测 / 展望文章
❌ 只搜 3 次就开始写 → 覆盖率不到 30%

✅ 用 "this week" / "latest" 代替具体日期
✅ 至少 8 次搜索后再开始输出

---

## 常见问题

**bird 报 "Missing auth_token"**
→ 重新加载认证：Linux/macOS 执行 `export $(cat ~/.agent-reach-twitter.env | xargs)`，Windows PowerShell 重新运行加载命令

**Twitter 认证过期**
→ Chrome 重新登录 x.com → F12 → Cookies → x.com → 复制新的 auth_token 和 ct0 → 更新 `~/.agent-reach-twitter.env`

**Brave 触发并发限制**
→ 每次搜索间隔等待至少 5 秒。Brave 免费套餐只允许 1 个并发请求。

**没有 Grok API Key**
→ 使用 Twitter 路线（免费）或 Brave 搜索引擎作为备用方案

---

## 更新日志

### v1.0.0
- 初始版本
- 支持 Twitter/X（bird CLI）和 Grok API 双后端
- 覆盖 7 个搜索维度
- 热度分级输出
- 支持每日定时简报
