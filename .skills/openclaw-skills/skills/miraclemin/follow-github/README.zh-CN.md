# Follow GitHub

> 你的个性化 GitHub 摘要 —— 每日或每周一份，推到你的消息通道或邮箱。

一个追踪三类内容并重整成易读摘要的 skill：

1. **你关注的人** —— 新建的仓库、star 过的项目、维护的仓库发布新版本
2. **GitHub Trending** —— 当下 GitHub 的热门仓库，可按语言过滤
3. **新兴热门项目** —— 最近冒出来、star 增长快的新仓库

数据**实时**从 GitHub API 和 `github.com/trending` 获取。没有中央服务器、没有第三方
数据管道 —— 只是你自己的 token 直接请求 GitHub。

灵感来自 [follow-builders](https://github.com/zarazhangrui/follow-builders)。

---

## 输出示例

```markdown
# GitHub 速递 — 2026-04-20

## 你关注的人

**karpathy**
- star 了 unslothai/unsloth — 2-5x 更快的 LLM 微调 [Python] ★ 18.4k
- 新建了 karpathy/llm-c — 纯 C 实现的 LLM 训练 [C]

3 个你关注的人 star 了 anthropics/claude-cookbook
（levie、simonw、swyx）

## Trending

- forrestchang/andrej-karpathy-skills — 一个 CLAUDE.md 优化 Claude Code
  [Markdown] +45k ★ 本周
- NousResearch/hermes-agent — 会成长的 agent [Python] +38k ★

## 新兴项目

- multica-ai/multica — 开源的 managed agents 平台
  [TypeScript] ★ 17.2k（9 天前创建）
```

语言、语气、章节顺序、过滤条件 —— 首次配置后全部**可通过对话调整**。

---

## 安装方式

根据你使用的 agent 选一种。

### 方式 1：ClawHub（OpenClaw 用户最简）

```bash
openclaw skills install follow-github
```

然后开一个对话，说 "配置 follow-github" —— skill 会带你走完交互式引导。

### 方式 2：Claude Code

```bash
# 用户级（所有项目都能用）
git clone https://github.com/Miraclemin/follow-github ~/.claude/skills/follow-github

# 或 项目级（仅当前项目）
git clone https://github.com/Miraclemin/follow-github .claude/skills/follow-github
```

Claude Code 会自动发现这些目录下的 skill。开一个新会话，说 "配置 follow-github"。

### 方式 3：Codex CLI（或其他 agent）

Codex 没有一级 skill 机制，当成"参考文档 + 可执行脚本"使用：

```bash
git clone https://github.com/Miraclemin/follow-github ~/agents/follow-github
cd ~/agents/follow-github/scripts && npm install
```

然后让你的 agent 读 `SKILL.md`——可以在 `AGENTS.md` / 系统提示里引用它，或者直接说：

```bash
# Codex 里
"读一下 ~/agents/follow-github/SKILL.md 并按照里面的说明执行"
```

### 方式 4：手动（适用任何环境）

```bash
git clone https://github.com/Miraclemin/follow-github
cd follow-github/scripts && npm install
node prepare-digest.js   # 输出原始 JSON（需要先配置）
```

---

## 首次运行

Skill 会引导你走一个 10 步的交互式配置：

| 步骤 | 询问内容 |
|---|---|
| 1 | 介绍（无需输入） |
| 2 | 你的 GitHub 用户名 |
| 3 | 一个 GitHub PAT（有引导） |
| 4 | 要哪些内容流（任意组合） |
| 5 | 语言过滤（如 Python、Rust —— 或不限） |
| 6 | 频率和时间（日/周 + 时区） |
| 7 | 投递方式（OpenClaw 会自动检测） |
| 8 | 摘要语言（中/英/双语） |
| 9 | 自动注册 cron 任务 |
| 10 | 立刻发一份样例摘要让你反馈 |

偏好写入 `~/.follow-github/config.json`；token 存到 `~/.follow-github/.env`
（不会被提交，除了 GitHub API 不发往任何地方）。

### GitHub Token 配置

引导会带你走，这里仅供参考：

1. 打开 https://github.com/settings/personal-access-tokens/new（fine-grained token）
2. **Repository access**：Public Repositories (read-only)
3. **Permissions**：`Metadata: Read` 即可（默认勾上）
4. 复制 token（以 `github_pat_` 开头），引导时粘贴

---

## 通过对话定制

配置完成后，直接对话：

| 你说 | 会发生什么 |
|---|---|
| "改成日报" | `config.frequency` → `daily`，cron 重新注册 |
| "只看 Rust" | `config.languages` → `["rust"]` |
| "去掉 trending" | `config.sources.trending` → `false` |
| "摘要短一点" | 编辑 `~/.follow-github/prompts/summarize-*.md` |
| "语气更口语化" | 编辑 `~/.follow-github/prompts/digest-intro.md` |
| "显示我的设置" | 读取并展示 config.json |
| "恢复默认 prompt" | 删除你的自定义 prompt |

你的自定义 prompt 放在 `~/.follow-github/prompts/`，会**覆盖**默认版本 —— skill
升级不会冲掉你的个性化。

---

## 架构

```
GitHub API (实时)              ──┐
github.com/trending 爬虫       ──┼──▶ prepare-digest.js (本地)
GitHub Search API (实时)        ──┘              │
                                                  ▼ JSON blob
                                            LLM (你的 agent)
                                                  │  按 prompts 重整
                                                  ▼
                                        deliver.js ──▶ stdout / Telegram / 邮箱
```

**三级 prompt 优先级**：
1. `~/.follow-github/prompts/*.md` —— 你的定制（最高优先级）
2. `<remoteUrl>/*.md` —— 可选的远端更新（`config.prompts.remoteUrl` 配置）
3. `./prompts/*.md` —— skill 自带默认（兜底）

**去重** 通过 `~/.follow-github/state.json` 实现 —— 每条事件或新仓库在 30 天内只出现一次。

**无中央 feed** —— 和 `follow-builders` 不同，每个用户跑自己的抓取。好处：零基建，
不用维护服务器、GitHub Actions 或 API key 池。

---

## 配置文件格式

```json
{
  "platform": "openclaw",
  "github": { "username": "your-handle" },
  "sources": {
    "following": true,
    "trending": true,
    "hot": true
  },
  "languages": ["python", "typescript"],
  "frequency": "weekly",
  "weeklyDay": "monday",
  "deliveryTime": "09:00",
  "timezone": "Asia/Shanghai",
  "delivery": { "method": "stdout" },
  "digestLanguage": "zh",
  "prompts": { "remoteUrl": null },
  "onboardingComplete": true
}
```

所有字段都可以通过对话修改 —— 你不需要手动改这个文件。

---

## 依赖

- Node.js 18+（使用原生 `fetch`）
- 一个 GitHub PAT（只读公开仓库权限即可）
- 可选：`openclaw` CLI、Claude Code、或任何支持 LLM 的 CLI agent

---

## 许可证

MIT —— 见 [LICENSE](./LICENSE)。

---

## 相关

- [follow-builders](https://github.com/zarazhangrui/follow-builders) —— 本项目灵感来源，
  追踪 AI builders 的 X 动态和 YouTube 播客
- [ClawHub](https://clawhub.ai) —— OpenClaw 的 skill 注册中心

English: [README.md](./README.md)
