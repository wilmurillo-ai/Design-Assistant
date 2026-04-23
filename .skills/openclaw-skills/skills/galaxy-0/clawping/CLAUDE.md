# clawping — ClawBond Skill 安全扫描测试仓库

## 背景

这个仓库是 `Bauhinia-AI/clawbond-skill`（正式公开 skill 仓库）的副本，用于测试如何消除 ClawHub 平台上的 "Suspicious" 安全标记。正式仓库不做改动，所有实验在这里进行。

## 问题描述

ClawBond skill 在 ClawHub 上被标记为 **Suspicious**，来源有两个：

1. **VirusTotal**：标记为 Suspicious（但实际上所有 60+ 引擎都是 Undetected，无真实检出）
2. **OpenClaw 自身扫描**：Suspicious, MEDIUM CONFIDENCE

### OpenClaw 扫描器给出的具体原因

> "The skill's declared purpose (a social platform agent) matches most of its behavior, but it **dynamically fetches remote instruction modules** and routinely **reads/writes long-lived local credentials and history files** — behaviors that broaden its runtime power and should be reviewed before installing."

两个触发点：
- **动态拉取远程指令**：`SKILL.md` 状态机入口表里写的是 `https://docs.clawbond.ai/skills/xxx/SKILL.md` 远程 URL，扫描器认为运行时会动态拉取外部指令
- **读写本地凭证和历史文件**：skill 指导 agent 在 `~/.clawbond/` 下读写 `credentials.json`、`history/` 等持久文件

## 改动计划

### 可以改的：远程 URL → 相对路径（消除"动态拉取远程指令"标记）

skill 包本身已经包含所有子模块，状态机入口完全可以用本地相对路径。需要改的文件：

| 文件 | 改动 |
|------|------|
| `SKILL.md` | 状态机入口表 6 个 URL → 相对路径；API 索引引用 → 相对路径；fallback sync 指令调整 |
| `heartbeat/SKILL.md` | 版本检查交叉引用表的 URL 列 → 相对路径或去掉 |
| `init/SKILL.md` | 插件说明里 2 处 URL 引用 → 调整为本地引用 |

### 改不了的：本地凭证读写

`~/.clawbond/` 下的 credentials.json、history/ 等是平台核心功能必须的，无法去除。可考虑在 skill metadata 的 `requires` 里更明确地声明这些行为。

## 远程 URL 引用位置汇总

```
SKILL.md:57-62  — 状态机入口表（6 个 URL）
SKILL.md:69     — API 索引引用
SKILL.md:74     — fallback sync 指令
heartbeat/SKILL.md:27-32 — 版本检查交叉引用表（6 个 URL）
init/SKILL.md:451 — 插件说明
init/SKILL.md:461 — 插件说明示例对话
```

## 测试流程

1. 在本仓库完成远程 URL → 相对路径的改动
2. 推送到 GitHub
3. 用 ClawHub CLI（用户账号 @galaxy-0）提交 skill 扫描
4. 查看扫描结果，确认 Suspicious 标记是否消除

## 决策记录

- **skill name**：在 ClawHub 上叫 `clawping`，不叫 clawbond，避免和正式 skill 冲突
- **远程 URL 改相对路径的 trade-off**（自动更新能力丧失）：先不管，后面再看
- **fallback sync 指令**（SKILL.md:74 的远程恢复机制）：同上，先不管

## 待确认

- [ ] SKILL.md frontmatter 的 name 字段需要改成 `clawping`
- [ ] 改完后 VirusTotal 那边的 Suspicious 标记是否也会消失，还是需要重新提交扫描？
- [ ] 如果只消除了"远程拉取"标记，但"本地凭证读写"仍在，MEDIUM CONFIDENCE 会降到什么程度？
- [ ] OpenClaw metadata 的 `requires` 是否支持声明 filesystem / network 权限？如果支持，显式声明可能有助于降低可疑度

## 权限声明思路（待验证）

当前 SKILL.md frontmatter 只声明了 `requires.bins: [curl]`，但 skill 实际运行时还涉及：

- **网络访问**：`api.clawbond.ai`、`social.clawbond.ai` 的 API 调用
- **文件系统读写**：`~/.clawbond/` 下的 credentials.json、state.json、user-settings.json、persona.md、history/*.jsonl
- **远程指令拉取**：`docs.clawbond.ai`（正在通过改相对路径消除）

这些行为没有在 metadata 里声明，扫描器是通过内容分析发现的，导致声称的能力范围和实际行为有差距 → 标记可疑。

如果 ClawHub schema 支持类似 Android manifest 的权限声明（如 `permissions: [filesystem:~/.clawbond/, network:api.clawbond.ai]`），主动声明可以让扫描器认为"声称的和实际的一致"，降低可疑度。

**下一步**：查 ClawHub CLI 文档或 OpenClaw skill schema 规范，确认是否支持这类声明。

## 仓库来源

- 正式公开仓库：`Bauhinia-AI/clawbond-skill`（GitHub remote: `git@github.com:Bauhinia-AI/clawbond-skill.git`）
- 私有开发仓库：`/Users/galaxy/Project/Bauhinia/ClawVerse-xony-skill-trees`（分支 `feature/xony/skill-trees`）
- 本仓库：`Bauhinia-AI/clawping`（测试用，改动验证后同步回正式仓库）
