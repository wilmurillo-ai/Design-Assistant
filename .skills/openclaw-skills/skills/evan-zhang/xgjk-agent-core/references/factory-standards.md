# 工厂标准规范

## 启动序列（每次会话必须执行）

每次会话开始，按顺序读取：
1. `SOUL.md` — 角色定位（我是谁）
2. `USER.md` — 用户信息（服务谁）
3. `06_memory/YYYY-MM-DD.md` — 今日记忆
4. `06_memory/RULES.md` — 全局规则

不得跳过，不得等用户要求才读。

## Telegram 输出风格（强制）

- 先结论，再分点
- 每点 ≤ 3 行
- 不用表格（除非用户明确要求）
- 不用长代码块
- 内容过长拆成多条消息
- 数字结论放第一句

## 角色边界

| 角色 | 文件 | 说明 |
|------|------|------|
| 我是谁 | SOUL.md | 角色定位、职责、交互风格 |
| 服务谁 | USER.md | 用户偏好、背景、称呼 |
| 工厂成员 | AGENTS.md | 各角色分工、协作规范 |
| 工具说明 | TOOLS.md | 环境特定的工具配置 |

读取这些文件是启动序列的一部分，不是可选项。

## 工厂路径约定

| 用途 | 路径 |
|------|------|
| 记忆 | `06_memory/` |
| 项目 | `04_workshop/AF-{日期}-{序号}/` |
| 已发布产品 | `05_products/` |
| 工作流规范 | `02_guides/` |
| 治理文档 | `03_governance/` |

## SOP 执行规范

凡涉及以下情况，启动 cms-sop Lite 实例：
- 有发布操作（ClawHub）
- 有文件删除/归档操作
- 有跨多个产品的批量修改
- 预计耗时 > 20 分钟

## 产品发布规范

发布 Skill 到 ClawHub 后必须：
1. 验证 latest 版本号（clawhub inspect 或 API）
2. 更新 `05_products/index.md` 版本号
3. 更新 `05_products/{skill}/design/SHARE-LOG.jsonl`
4. 同步 design/DISCUSSION-LOG.md（本次变更原因）
