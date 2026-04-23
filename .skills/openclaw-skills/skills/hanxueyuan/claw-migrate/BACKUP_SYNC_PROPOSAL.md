# claw-migrate 双向同步功能设计方案

**提案日期**: 2026-03-15  
**版本**: v2.1.0 (规划中)

---

## 📋 需求概述

### 当前功能（v2.0.x）
```
GitHub 仓库 → (pull) → 本地 OpenClaw
```
- ✅ 从 GitHub 拉取配置
- ✅ 智能合并
- ✅ 用于新机器安装、配置恢复

### 新增功能（v2.1.0）
```
本地 OpenClaw → (push) → GitHub 仓库
```
- 🆕 定期备份到 GitHub
- 🆕 增量更新
- 🆕 敏感信息过滤
- 🆕 定时任务支持

---

## 🎯 完整工作流程

```
┌─────────────────────────────────────────────────────────────┐
│                    完整迁移流程                              │
└─────────────────────────────────────────────────────────────┘

机器 A（源机器）                    GitHub 私有仓库
     │                                 │
     │  1. 定期备份 (push)             │
     │ ─────────────────────────────→  │
     │                                 │
     │                                 │  2. 存储历史版本
     │                                 │  （git history）
     │                                 │
     │                                 │
机器 B（目标机器）                     │
     │                                 │
     │  3. 迁移恢复 (pull)             │
     │ ←─────────────────────────────  │
     │                                 │
     ▼
  配置恢复完成
```

---

## 🔧 实现方案

### 推荐方案：本地 git + 定时任务

**核心思路**：
1. 技能提供 `backup` 命令（push 功能）
2. 使用 git 命令直接操作（比 GitHub API 更高效）
3. 支持手动执行和系统 cron 定时
4. 敏感信息自动过滤

### 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│  claw-migrate 技能                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐          ┌──────────────┐                │
│  │  pull 命令   │          │  backup 命令 │                │
│  │  (已有)      │          │  (新增)      │                │
│  │              │          │              │                │
│  │ 从 GitHub 拉  │          │ 推送到 GitHub │                │
│  │ 智能合并     │          │ 增量提交     │                │
│  └──────────────┘          └──────────────┘                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                共享组件                               │  │
│  │  • Token 管理（环境变量/gh CLI/交互式）               │  │
│  │  • 文件分类（核心配置/技能/记忆/学习记录）            │  │
│  │  • 敏感信息过滤（.env 等）                           │  │
│  │  • git 操作封装                                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 新增命令设计

### backup 命令

```bash
# 基本用法 - 备份到 GitHub
openclaw skill run claw-migrate backup --repo owner/repo

# 指定分支
openclaw skill run claw-migrate backup --repo owner/repo --branch backup

# 首次初始化（创建仓库）
openclaw skill run claw-migrate backup --init --repo owner/repo

# 仅备份特定类型
openclaw skill run claw-migrate backup --repo owner/repo --type config
openclaw skill run claw-migrate backup --repo owner/repo --type skills
openclaw skill run claw-migrate backup --repo owner/repo --type all

# 预览模式
openclaw skill run claw-migrate backup --repo owner/repo --dry-run

# 设置定时任务（cron）
openclaw skill run claw-migrate backup --repo owner/repo --schedule "0 2 * * *"
```

### 命令参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--repo` | GitHub 仓库（owner/repo） | 必填 |
| `--branch` | 分支名 | `main` |
| `--init` | 首次初始化（创建 .git 和远程仓库） | false |
| `--type` | 备份类型：all/config/skills/memory/learnings | `all` |
| `--dry-run` | 预览模式，不实际推送 | false |
| `--schedule` | cron 表达式，设置定时任务 | 无 |
| `--message` | commit 消息 | `backup: YYYY-MM-DD HH:mm:ss` |
| `--no-filter` | 不过滤敏感文件（默认过滤 .env） | false |

---

## 🔒 敏感信息处理

### 默认过滤列表

```javascript
// 不备份的文件（包含敏感信息）
const EXCLUDE_FROM_BACKUP = [
  '.env',                    // 环境变量（API keys 等）
  '.env.local',
  '*.log',                   // 日志文件
  'node_modules/',           // 依赖
  '.git/',                   // git 目录
  '.migrate-backup/',        // 备份目录
  'sessions/',               // 会话数据
  '*.tmp',                   // 临时文件
];

// 需要备份的文件（包含 channel 配置）
const INCLUDE_FOR_BACKUP = [
  'AGENTS.md',
  'SOUL.md',
  'IDENTITY.md',
  'USER.md',
  'TOOLS.md',
  'HEARTBEAT.md',
  'MEMORY.md',
  'memory/*.md',
  '.learnings/*.md',
  'skills/**/SKILL.md',
  'feishu/*.json',          // ⭐ 飞书配置（channel 信息等）
  'feishu/dedup/*.json',    // ⭐ 飞书去重配置
  '*.yaml',                 // ⭐ 其他 YAML 配置
];
```

### 用户自定义过滤

支持 `.backupignore` 文件：

```bash
# .backupignore
.env
*.log
secrets/
private-keys/
```

---

## ⏰ 定时任务支持

### 方案 A：系统 cron（推荐）

```bash
# 1. 创建 cron 任务
crontab -e

# 2. 添加每日凌晨 2 点备份
0 2 * * * cd /workspace/projects/workspace && openclaw skill run claw-migrate backup --repo owner/repo --type all
```

### 方案 B：技能内置调度器

```bash
# 设置定时备份（技能内部管理）
openclaw skill run claw-migrate backup --repo owner/repo --schedule "0 2 * * *"

# 查看已设置的定时任务
openclaw skill run claw-migrate backup --list-schedules

# 删除定时任务
openclaw skill run claw-migrate backup --remove-schedule
```

### 方案 C：OpenClaw 定时任务

如果 OpenClaw 支持定时任务：

```json
// ~/.openclaw/openclaw.json
{
  "scheduledTasks": [
    {
      "name": "daily-backup",
      "schedule": "0 2 * * *",
      "command": "claw-migrate backup --repo owner/repo"
    }
  ]
}
```

---

## 📦 实现细节

### 1. git 初始化（首次备份）

```javascript
async function initBackup(options) {
  // 1. 检查本地是否有 .git
  if (!fs.existsSync('.git')) {
    execSync('git init');
    console.log('✓ 已初始化 git 仓库');
  }

  // 2. 创建 .backupignore
  if (!fs.existsSync('.backupignore')) {
    fs.writeFileSync('.backupignore', DEFAULT_BACKUP_IGNORE);
    console.log('✓ 已创建 .backupignore');
  }

  // 3. 添加远程仓库
  execSync(`git remote add origin ${getRepoUrl(options.repo)}`);
  console.log('✓ 已添加远程仓库');

  // 4. 首次提交
  execSync('git add -A');
  execSync(`git commit -m "init: initial backup"`);
  
  // 5. 推送到 GitHub
  execSync(`git push -u origin ${options.branch}`);
  console.log('✓ 首次备份完成');
}
```

### 2. 增量备份

```javascript
async function incrementalBackup(options) {
  // 1. 检查变更
  const status = execSync('git status --porcelain').toString();
  if (!status.trim()) {
    console.log('✓ 无变更，跳过备份');
    return;
  }

  // 2. 添加变更
  execSync('git add -A');

  // 3. 提交
  const message = options.message || `backup: ${new Date().toISOString()}`;
  execSync(`git commit -m "${message}"`);

  // 4. 推送
  execSync(`git push origin ${options.branch}`);
  
  console.log('✓ 增量备份完成');
}
```

### 3. 错误处理

```javascript
try {
  await backup(options);
} catch (err) {
  if (err.message.includes('Authentication failed')) {
    console.error('❌ 认证失败：请检查 GitHub Token 是否正确');
  } else if (err.message.includes('remote repository not found')) {
    console.error('❌ 仓库不存在：请先创建仓库或使用 --init 初始化');
  } else if (err.message.includes('Changes not staged')) {
    console.error('❌ 有未提交的变更，请先处理冲突');
  } else {
    console.error(`❌ 备份失败：${err.message}`);
  }
  process.exit(1);
}
```

---

## 🎯 用户使用流程

### 场景 1：首次设置备份

```bash
# 1. 在 GitHub 创建私有仓库（例如：my-openclaw-backup）

# 2. 初始化备份
cd /workspace/projects/workspace
export GITHUB_TOKEN=ghp_xxx
openclaw skill run claw-migrate backup --init --repo my-username/my-openclaw-backup

# 3. 设置每日自动备份
openclaw skill run claw-migrate backup --repo my-username/my-openclaw-backup --schedule "0 2 * * *"
```

### 场景 2：迁移到新机器

```bash
# 1. 新机器安装 OpenClaw 和 claw-migrate 技能
openclaw skill install claw-migrate

# 2. 从 GitHub 拉取配置（包含飞书 channel 配置）
export GITHUB_TOKEN=ghp_xxx
openclaw skill run claw-migrate --repo my-username/my-openclaw-backup

# 3. 验证配置
cat AGENTS.md
cat feishu/dedup/default.json  # 飞书 channel 配置
ls skills/
```

### 场景 3：仅备份 Channel 配置

```bash
# 仅备份 channel 相关配置（飞书、Telegram 等）
openclaw skill run claw-migrate backup --repo my-username/my-openclaw-backup --type channel

# 仅拉取 channel 配置
openclaw skill run claw-migrate --repo my-username/my-openclaw-backup --type channel
```

### 场景 3：手动触发备份

```bash
# 修改配置后手动备份
openclaw skill run claw-migrate backup --repo my-username/my-openclaw-backup

# 预览将备份的文件
openclaw skill run claw-migrate backup --repo my-username/my-openclaw-backup --dry-run
```

---

## 📊 版本对比

| 功能 | v2.0.x | v2.1.0 (规划) |
|------|--------|---------------|
| 从 GitHub 拉取 | ✅ | ✅ |
| 智能合并 | ✅ | ✅ |
| 推送到 GitHub | ❌ | ✅ |
| 增量备份 | ❌ | ✅ |
| 定时任务 | ❌ | ✅ |
| 敏感信息过滤 | ⚠️ 部分 | ✅ 完整 |
| .backupignore | ❌ | ✅ |
| 预览模式 | ✅ | ✅ |
| 自动初始化 | ❌ | ✅ |

---

## 🔐 安全考虑

### Token 安全

- ✅ 优先使用 `GITHUB_TOKEN` 环境变量
- ✅ 支持 gh CLI 临时获取
- ✅ Token 不保存，仅本次会话使用
- ✅ 不写入日志

### 仓库安全

- ✅ 默认创建私有仓库
- ✅ 敏感文件自动过滤
- ✅ 支持自定义过滤列表

### 数据安全

- ✅ git history 保留所有版本
- ✅ 支持回滚到任意版本
- ✅ 本地保留 git 仓库

---

## ⚠️ 潜在风险及缓解

| 风险 | 可能性 | 影响 | 缓解措施 |
|------|--------|------|----------|
| Token 泄露 | 低 | 高 | Token 不保存、使用环境变量 |
| 误提交敏感信息 | 中 | 高 | 默认过滤列表 + .backupignore |
| 覆盖远端变更 | 低 | 中 | push 前先 pull，处理冲突 |
| 定时任务失败 | 中 | 低 | 失败通知 + 手动重试 |
| GitHub API 限流 | 低 | 低 | 使用 git 命令而非 API |

---

## 📋 开发计划

### Phase 1: 核心功能（v2.1.0）
- [ ] 实现 `backup` 命令
- [ ] git 操作封装
- [ ] 敏感信息过滤
- [ ] .backupignore 支持

### Phase 2: 定时任务（v2.2.0）
- [ ] cron 表达式解析
- [ ] 系统 cron 集成
- [ ] 失败通知机制

### Phase 3: 增强功能（v2.3.0）
- [ ] 冲突检测与解决
- [ ] 备份历史查看
- [ ] 版本回滚支持
- [ ] Web UI（可选）

---

## 🎯 推荐结论

**推荐方案**: 本地 git + 系统 cron

**理由**:
1. **简单可靠** - 使用成熟 git 工具，不重复造轮子
2. **灵活** - 支持手动和自动，不依赖 OpenClaw 常驻
3. **安全** - 敏感信息过滤，Token 不保存
4. **高效** - 增量提交，只传输变更
5. **可追溯** - git history 保留所有版本

**实现优先级**:
1. 首先实现 `backup` 命令（手动）
2. 添加敏感信息过滤
3. 集成系统 cron（定时）
4. 增强功能（冲突解决、回滚等）

---

**提案状态**: 待 QA 评估  
**预计版本**: v2.1.0  
**预计完成**: TBD
