# Skill Publisher - 多平台 Skill 发布助手

> 一键发布 OpenClaw Skills 到 ClawHub、GitHub 等平台  
> 为手动平台生成标准提交文本

## 功能特性

- ✅ **全自动发布**：ClawHub、GitHub、SkillsMP
- ⏳ **生成提交文本**：COZE、腾讯元器、阿里百炼、SkillzWave
- 🔐 **安全 Token 管理**：交互式配置，本地存储，永不上传
- 📊 **状态检测**：查看各平台发布状态

---

## 快速开始

### 1. 配置 Token（首次使用）

```bash
cd /home/node/.openclaw/workspace/skills/skill-publisher
python scripts/setup_tokens.py
```

或直接编辑 `.env` 文件（确保不提交到 GitHub）：

```bash
# .env
GITHUB_TOKEN=ghp_xxxxx
CLAWHUB_TOKEN=
COZE_TOKEN=
```

### 2. 发布 Skill

```bash
# 发布单个 Skill
python scripts/publish.sh <slug>

# 示例
python scripts/publish.sh my-companion
python scripts/publish.sh health-checkup-recommender
```

### 3. 查看状态

```bash
# 查看所有平台状态
python scripts/check_status.py all

# 查看指定 Skill
python scripts/check_status.py my-companion
```

---

## 平台支持

| 平台 | 自动化 | Token | 说明 |
|------|--------|-------|------|
| 🌐 ClawHub | ✅ 全自动 | `CLAWHUB_TOKEN` | `npx clawhub publish` |
| 💻 GitHub | ✅ 全自动 | `GITHUB_TOKEN` | 推送到仓库 |
| 🟢 SkillsMP | ✅ 全自动 | — | GitHub 同步 |
| 🌊 SkillzWave | ⏳ 手动 | — | 生成提交文本 |
| 🤖 COZE | ⏳ 部分 | `COZE_TOKEN` | API + 手动审核 |
| 🟡 元器 | ⏳ 手动 | `YUANQI_TOKEN` | 生成提交文本 |
| 🔵 百炼 | ⏳ 手动 | `BAILIAN_TOKEN` | 生成提交文本 |

---

## Token 安全说明

**安全优先：**

1. **本地存储**：Token 只存在本地 `.env` 文件
2. **不上传**：`.env` 已在 `.gitignore` 中，绝不会提交到 GitHub
3. **加密传输**：所有 API 调用使用 HTTPS
4. **按需授权**：只申请必要权限（如 GitHub 的 `repo`）

**Token 申请：**

| 平台 | 申请地址 |
|------|---------|
| GitHub | https://github.com/settings/tokens |
| ClawHub | https://clawhub.ai |
| COZE | https://www.coze.cn/settings/api |
| 元器 | https://yuanqi.tencent.com |
| 百炼 | https://bailian.console.aliyun.com |

---

## 目录结构

```
skill-publisher/
├── SKILL.md
├── _meta.json
├── .env.example          # Token 模板
├── .gitignore            # 确保 .env 忽略
├── scripts/
│   ├── publish.sh        # 发布脚本
│   ├── check_status.py  # 状态检测
│   ├── gen_submission.py # 生成提交文本
│   └── setup_tokens.py  # 交互式 Token 配置
├── data/
│   └── platforms.json   # 平台元数据
└── docs/
    └── PLATFORM_RESEARCH.md  # 平台调研报告
```

---

## 自动化 vs 手动平台

### ✅ 可全自动发布（3个）
- **ClawHub** - 官方 `clawhub` CLI
- **GitHub** - Git 推送
- **SkillsMP** - GitHub 自动同步

### ⏳ 需手动提交（4个）
- **COZE** - 有 API 但审核必需
- **腾讯元器** - 手动提交市场
- **阿里百炼** - 手动提交市场
- **SkillzWave** - GitHub OAuth + 手动

### 为什么部分平台无法全自动？

1. **人工审核**：COZE、元器、百炼都需要官方审核
2. **OAuth 限制**：SkillzWave 需要 GitHub OAuth 授权
3. **平台政策**：AI 智能体分发平台普遍要求人工审核

---

## 使用示例

### 发布 my-companion 到所有平台

```bash
cd /home/node/.openclaw/workspace/skills/skill-publisher

# 1. 先检测状态
python scripts/check_status.py my-companion

# 2. 自动发布到 ClawHub + GitHub
python scripts/publish.sh my-companion

# 3. 为其他平台生成提交文本
python scripts/gen_submission.py my-companion
```

### 配置新平台 Token

```bash
python scripts/setup_tokens.py
```

---

## 故障排除

### Token 无效
```
Error: GitHub API token invalid
```
→ 检查 Token 是否过期，在 https://github.com/settings/tokens 重新生成

### 推送被拒绝
```
error: src refspec main does not match any
```
→ 确认已初始化 Git 仓库并有至少一次提交

### ClawHub 发布失败
```
Error: Published failed
```
→ 检查 `CLAWHUB_TOKEN` 是否正确，或使用 `--force` 强制发布

---

## 扩展平台支持

如需添加新平台，编辑 `data/platforms.json`：

```json
{
  "platforms": {
    "new-platform": {
      "name": "新平台",
      "url": "https://...",
      "auto": false,
      "requires": "API Token",
      "note": "说明"
    }
  }
}
```

---

## 相关文档

- [平台调研报告](./docs/PLATFORM_RESEARCH.md)
- [ClawHub 官方文档](https://docs.clawhub.ai)
- [GitHub API 文档](https://docs.github.com/rest)

---

*维护者：Ryan BihAI  
版本：2.1.0*
