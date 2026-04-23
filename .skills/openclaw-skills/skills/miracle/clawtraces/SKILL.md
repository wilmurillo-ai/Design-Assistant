---
name: clawtraces
description: "采集并提交本地 OpenClaw 对话记录到数据平台。当用户说「采集数据」「提交数据」「提交对话」「提交记录」「提交日志」「扫描对话」「扫描日志」「看看有哪些对话可以提交」「帮我提交对话记录」「查看提交记录」「提交了多少条」「clawtraces」「claw」，或表达想要扫描、采集、提交、查看本地对话记录的意图时使用此 Skill。"
user-invocable: true
---

# ClawTraces 数据采集

本 Skill 帮助用户从本地 OpenClaw 日志中采集符合要求的 session 数据，转换为 Anthropic 标准 trajectory 格式，并提交到数据收集服务器。

## 工作流程

按以下顺序执行，每一步完成后再进行下一步。

---

### 步骤 1：环境准备（认证 + 环境检查）

认证和环境检查作为一个整体自动完成，中间不需要额外提示。

#### 1.1 认证检查

```bash
python3 /{{baseDir}}/scripts/lib/auth.py
```

脚本输出 JSON，包含 `authenticated` 字段。

- **已认证**：直接进入 1.2。
- **未认证**：
  1. **必须先向用户询问手机号，等用户回复后才能继续。** 直接问："请提供你的手机号（11 位数字）"，然后 **停下来等待用户回复**。绝对不要自己编造或使用任何默认手机号。
  2. 用户回复手机号后，发送验证码：
     ```bash
     python3 -c "
     import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
     from lib.auth import send_code, get_server_url
     result = send_code(get_server_url(), '<用户回复的手机号>')
     import json; print(json.dumps(result, indent=2))
     "
     ```
     其中 `<用户回复的手机号>` 替换为用户实际提供的号码。
  3. 告诉用户"验证码已发送，请查看短信并回复验证码"，然后 **再次停下来等待用户回复验证码**。
  4. 用户回复验证码后，验证：
     ```bash
     python3 -c "
     import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
     from lib.auth import verify_code, save_key, get_server_url
     result = verify_code(get_server_url(), '<手机号>', '<用户回复的验证码>')
     import json; print(json.dumps(result, indent=2))
     if result.get('key'):
         save_key(result['key'])
     "
     ```
  5. 失败则提示错误并允许重试

#### 1.2 环境检查

```bash
python3 /{{baseDir}}/scripts/env_check.py
```

脚本会自动检查并修复三项配置：
- **cache-trace**：开启诊断日志（enabled + includeSystem），记录真实 system prompt
- **thinking level**：确保全局和所有 agent 的 thinkingDefault 至少为 high，提升推理质量
- **model reasoning**：确保自定义 provider 中白名单模型的 reasoning 为 true，启用推理能力

处理结果：

- **配置已正确**：无需额外操作。
- **配置被自动修改**：
  1. 将脚本输出的修改明细（`fixes` 字段）**完整展示给用户**，让用户知道对 openclaw.json 做了哪些改动
  2. 自动重启 OpenClaw：
     ```bash
     openclaw gateway restart
     ```
  3. 说明 cache-trace 仅记录重启后的新对话，之前的对话无法补充 system prompt 数据。如果当前没有重启后产生的新 session，本次扫描可能无结果，建议用户正常使用一段时间后再来采集。

#### 1.3 完成提示

- **如果 1.2 配置被修改（`changed: true`）**：本次流程到此结束，不继续后续步骤。输出：

  > ✅ 环境已就绪！cache-trace 已开启并已重启 OpenClaw。
  > 由于 cache-trace 只记录重启后的新对话，当前没有可采集的数据。
  > 请正常使用 OpenClaw 一段时间后，再运行 `/clawtraces` 采集数据。

- **如果 1.2 配置已正确（`changed: false`）**：输出以下提示，**然后停下来等待用户指令**：

  > ✅ 环境已就绪。你可以：
  > - **📋 采集数据** — 列出可采集的对话，选择后提交
  > - **📊 查看进度** — 已提交多少条、查看提交记录
  > - **📦 提交 Workspace** — 提交工作区配置文件

  **必须原样输出上面的提示，不要自行增减内容，然后停下来等待用户回复。** 用户回复后根据语义判断进入步骤 2（采集）、步骤 5（查看进度）或步骤 5.5（提交 Workspace）。

---

### 步骤 2：采集数据

**触发**：用户表达了想要采集、提交、查看对话清单的意图。常见表达包括"看看有哪些"、"采集"、"全部"、"最近 N 条"、"帮我处理"等。

**2.1 列出对话清单**

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --list-only
```

脚本输出 JSON 对象（分页），包含以下字段：

- `items`：当前页的对话列表（默认每页 10 条），每项包含 `index`（序号）、`session_id`、`model`、`started_at`、`ended_at`、`file_size_kb`、`topic`、`status`
- `total`：对话总数
- `page`：当前页码
- `page_size`：每页条数
- `has_more`：是否有下一页

**`status` 字段说明**：

| status 值 | 含义 | 能否处理 |
|-----------|------|---------|
| `null` | 正常，可直接处理提交 | ✅ |
| `"active"` | 当前活跃对话（尚未 /new 或 /reset） | ✅ 需通过 `--sessions` 显式指定 |
| `"rejected"` | 已在之前的初审中被标记为不合格 | ❌ |
| `"model_mismatch"` | 使用的模型不在采集白名单中 | ❌ |

将 `items` 以表格形式展示给用户。status 映射为中文标记：

- `null` → 不显示
- `"active"` → `⚡活跃中`
- `"rejected"` → `❌不合格`
- `"model_mismatch"` → `⚠️模型不符`

示例：

> 找到 85 个对话记录，显示第 1-10 条：
>
> | # | 开始时间 | 结束时间 | 模型 | 摘要 | 状态 |
> |---|---------|---------|------|------|------|
> | 1 | 04-04 14:00 | 04-04 15:30 | claude-opus-4-6 | 帮我调试一下这个内存泄漏... | ⚡活跃中 |
> | 2 | 04-04 10:30 | 04-04 12:15 | claude-opus-4-6 | 帮我把这个 React 组件重构一下... | |
> | ... | | | | | |
> | 10 | 04-01 11:00 | 04-01 12:00 | claude-sonnet-4-6 | 分析用户留存数据... | |
>
> 其中 {N} 个可直接处理（无状态标记的）。还有 75 条，回复「更多」查看下一页。
> **提示**：标记为「⚡活跃中」的对话尚未结束。如果确认已完成，可以选择它来处理；但提交后若继续在该对话中聊天，新增内容将无法补充到已提交的记录中。建议在对话完全结束后再提交。
>
> 你想处理哪些？回复"全部"、"前 3 个"、"第 1、3、5 个"等即可。

**分页**：当 `has_more` 为 true 时，展示"还有 {total - page*page_size} 条，回复「更多」查看下一页"。用户说"更多"时执行：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --list-only --page 2
```

继续展示下一页内容，累加到之前的列表上下文中。页码递增直到 `has_more` 为 false。

**如果列表为空**（`total` 为 0）：输出无可用数据的提示，流程结束。

**2.2 按用户选择处理**

用户可能说：
- "全部" → 不传 `--sessions`，走默认全量处理（只处理 `status: null` 的对话）
- "前 N 个" / "最近 N 条" → 从清单中取前 N 个 **`status: null` 的** session_id（跳过有状态标记的）
- "第 1、3、5 个" → 从清单取对应序号的 session_id。如果用户选择了 `status: "active"` 的对话，通过 `--sessions` 显式指定（可以处理）。如果用户选择了 `"rejected"` 或 `"model_mismatch"` 的对话，告知无法处理并说明原因
- 直接给 session_id → 直接使用

确定要处理的 session_id 列表后，执行：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --sessions <id1> <id2> <id3>
```

#### 快捷方式：指定数量

如果用户在一开始就说了"最近 3 条"、"处理 5 个"等指定数量的表达，可以跳过列表直接使用 `--limit` 参数：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --limit <N>
```

#### 快捷方式：按日期范围

如果用户说"最近一周的"、"只要 4 月的"、"从 3 月 20 号开始"等指定日期范围的表达：

将用户的日期表达转换为 YYYY-MM-DD 格式，使用 `--since` 参数：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --since <YYYY-MM-DD>
```

`--since` 可与 `--limit` 组合使用。例如"最近一周的前 5 条"：

```bash
python3 /{{baseDir}}/scripts/scan_and_convert.py --since 2026-03-29 --limit 5
```

#### 处理结果（所有模式共用）

脚本会自动：
- 按硬性规则过滤（模型、轮次 > 5）
- 按数字指标过滤（用户消息平均长度、长消息数）
- 从 cache-trace 提取真实 system prompt（自动模式下无数据则跳过；`--sessions` 显式指定时使用重建 prompt）
- 为每个通过的 session 自动生成启发式 domain（基于工具使用模式）和 title（基于第一条用户消息）
- 生成 .trajectory.json 文件和 .stats.json 文件
- 输出 candidates.json（含每个候选的用户消息，供语义初审）

脚本 stdout 输出 JSON 对象，包含两个字段：
- `candidates`：通过所有过滤的候选列表（摘要信息，不含 user_messages）
- `filter_report`：过滤报告，包含 `total_found`（发现总数）、`total_scanned`（实际处理数）、`pre_filter`（前置过滤计数）、`passed`（通过数）、`filtered_count`（被过滤数）、`filtered`（每个被过滤 session 的 session_id、topic、reason、detail）

**展示过滤报告**：当 `filter_report.filtered_count > 0` 时，向用户展示过滤摘要。按 reason 分组，默认展示每条的 detail 和 session_id，例如：

> 扫描了 15 个 session，8 个通过，7 个被过滤：
> - 3 个轮次不足：
>   · 3 turns (min 6): session_id_1
>   · 4 turns (min 6): session_id_2
>   · 2 turns (min 6): session_id_3
> - 2 个无 cache-trace 数据：
>   · no system prompt available: session_id_4
>   · no system prompt available: session_id_5
> - 1 个质量检查未通过：
>   · long user messages (0) < 1: session_id_6
> - 1 个转换错误：
>   · tool_error_abort: session_id_7

**如果候选数量为 0**：本次流程结束，不继续后续步骤。基于 `filter_report` 展示具体原因：

> 本次扫描处理了 {total_scanned} 个 session，但全部被过滤：
> - {reason 分组}: {count} 个
>
> 如需了解具体哪些 session 被过滤及原因，可以查看详情。

如果 `total_found` 为 0，说明没有使用支持模型的对话，单独说明。

**如果有候选**：展示扫描结果（候选数量、每个 session 的模型、轮次和启发式 domain），然后继续步骤 3。

---

### 步骤 3：语义初审 + 领域/标题审核（合并为一次判断）

每个候选已有启发式 domain（基于工具使用模式推断）和 title（基于第一条用户消息截断）。本步骤审核并改善这些值。

读取 `output/candidates.json` 文件，对每个候选 session 的 `user_messages` 字段完成：

1. **初审判定**：PASS 或 FAIL（这是系统自动初审，不代表最终人工审核结果）
2. **领域分类**：审核启发式 domain 是否准确，必要时纠正为 13 个领域中更匹配的一个
3. **标题改善**：将启发式 title（截断的用户消息）改写为更精炼的任务概括

#### 分批审核

为控制单次上下文消耗，当候选数量 **超过 15 个**时，**必须分批审核**：

1. 将 candidates.json 按每批 15 个分组
2. 每批读取对应范围的候选（例如第 1-15 个、第 16-30 个...），逐批完成初审判定和领域/标题审核
3. 每批审核完成后立即执行该批的后续处理（更新 stats / 调用 reject.py），再进入下一批
4. 所有批次处理完毕后，汇总结果进入步骤 4

候选数量 ≤ 15 个时，一次性处理即可。

#### 初审判定标准

**合格（PASS）** — 满足以下任一条件：
- 用户围绕一个明确的任务目标在与 AI 协作（如开发功能、分析数据、撰写文档、解决技术问题等）
- 对话涉及特定领域的专业知识探讨（如编程、系统运维、数据分析、金融、内容创作等）
- 用户在进行有深度的信息调研或方案设计
- 对话体现了多轮迭代推进的工作过程（需求描述 → 方案讨论 → 执行 → 调整）

**不合格（FAIL）** — 满足以下任一条件：
- 用户消息几乎全是简单指令（"继续"、"好的"、"下一个"），没有实质性需求描述
- 对话内容是闲聊、打招呼、测试 AI 能力（"你是谁"、"讲个笑话"、"hello"）
- 用户在做重复性的简单操作，没有专业知识深度
- 对话内容涉及不当、违规或纯粹无意义的灌水

#### 领域分类（13 选 1）

根据用户消息的核心意图，从以下 13 个领域中选择最匹配的：

| ID | 名称 | 判定要点 |
|----|------|---------|
| `development` | 软件开发与工程 | 写代码、调试、测试、Git 操作、架构设计 |
| `system_admin` | 系统运维与管理 | 装软件、配服务器、管文件、网络/防火墙 |
| `data_analysis` | 数据分析与建模 | 数据清洗、统计、可视化、机器学习 |
| `research` | 研究与信息检索 | 调研、对比方案、文献查找、行业分析 |
| `content_creation` | 内容与文案创作 | 写文章、翻译、润色、报告、营销文案 |
| `communication` | 通信与消息管理 | 飞书/微信/邮件/Telegram 消息收发 |
| `media_processing` | 多媒体内容处理 | 图片/视频/音频处理、OCR、TTS |
| `automation` | 工作流与智能体编排 | 自动化脚本、定时任务、pipeline、agent |
| `monitoring` | 系统监控与诊断 | 监控告警、日志分析、性能诊断、健康检查 |
| `scheduling` | 日程与任务管理 | 日程安排、待办、提醒、日报周报 |
| `knowledge_mgmt` | 知识与记忆管理 | 笔记、知识库、归档、RAG 检索 |
| `finance` | 金融与量化交易 | 股票/基金/加密货币、量化策略、回测 |
| `crm` | 客户与业务运营 | 客户管理、销售、电商、订单运营 |

**判定原则**：基于用户的核心意图而非表面关键词。例如「用 Playwright 截图对比监控网页变化」核心意图是监控，应分类为 `monitoring` 而非 `development`。详细的边界判定规则参考 `showcase/domain-categories.md`。

#### 输出格式

对每个候选输出：
- **初审结果**：PASS 或 FAIL + 简短理由（不超过 20 字）。注意：展示时必须使用「初审结果」而非「审核结果」，以明确这是系统自动初审，提交后还需经过人工终审
- **领域**：13 个 ID 之一（仅 PASS 的需要）
- **标题**：一句话概括该 session 的核心任务（不超过 30 字，仅 PASS 的需要）。例如「为 React 项目添加用户认证模块」「分析 Q1 销售数据并生成可视化报告」

#### 后续处理

审核完成后，将所有结果（PASS 和 FAIL）合并为一个 JSON 数组，一次性提交给 `review.py` 处理：

```bash
python3 /{{baseDir}}/scripts/review.py <<'EOF'
[
  {"session_id": "xxx", "verdict": "pass", "domain": "development", "title": "为 React 项目添加认证"},
  {"session_id": "yyy", "verdict": "fail", "reason": "纯闲聊无实质内容"}
]
EOF
```

每个条目必须包含 `session_id` 和 `verdict`（`"pass"` 或 `"fail"`）。PASS 的需要 `domain`（13 个领域 ID 之一）和 `title`；FAIL 的可选 `reason`。

脚本自动完成：
- PASS：更新 stats 文件的 domain、title、review_status
- FAIL：删除 trajectory 和 stats 文件，记录到 manifest.json 的 `rejected` 字段

输出 JSON 汇总：`{"passed": N, "rejected": M, "errors": [...]}`。

**如果所有候选均 FAIL**：本次流程结束，不继续步骤 4。输出：

> 本次初审的所有候选均未通过语义质量检查，没有可提交的数据。

---

### 步骤 3.5：Workspace 门槛检查（进入提交前）

在展示待提交列表之前，先检查是否需要强制提交 Workspace 配置：

```bash
python3 -c "
import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
from submit import query_count
from lib.auth import get_server_url, get_stored_key
import json
result = query_count(get_server_url(), get_stored_key())
print(json.dumps(result, indent=2))
"
```

检查返回的 `workspace_force_required`、`workspace_threshold`、`workspace_submitted`、`count` 字段：

- 如果 `workspace_force_required == true` 且 `count >= workspace_threshold` 且 `workspace_submitted == false`：
  - 告知用户：「你已提交 {count} 条数据（达到 {threshold} 条阈值），需要先提交 Workspace 配置才能继续采集。」
  - 自动进入步骤 5.5（提交 Workspace）
  - Workspace 提交成功后继续步骤 4；用户拒绝则流程结束
- 否则：直接进入步骤 4

---

### 步骤 4：提交

展示通过初审的最终待提交列表，格式如下：

```
找到 N 条可提交的日志：

  1. 为 React 项目添加用户认证模块  | 软件开发 | 8 轮
  2. 分析 Q1 销售数据并生成报告    | 数据分析 | 12 轮

是否确认提交这 N 条记录？
```

每条展示标题、领域名称和轮次，不再展示 session_id。

**必须等待用户明确确认后才能提交。**

用户确认后运行：

```bash
python3 /{{baseDir}}/scripts/submit.py
```

提交完成后展示：本次提交数量 + 你累计已提交的数量（注意：这是当前用户个人的提交总数，不是全平台的）。并提示用户可以说「查看提交记录」来查看历史提交。

**workspace_required 错误处理**：如果提交过程中某条记录返回 `workspace_required` 错误（服务端 403），说明用户需要先提交 Workspace 配置。告知用户原因，自动进入步骤 5.5。Workspace 提交成功后，可重新运行提交。

提交脚本的输出中包含 `workspace_threshold`、`workspace_submitted`、`workspace_force_required` 字段，用于判断是否触发步骤 4.5。

---

### 步骤 4.5：Workspace 配置采集（条件触发）

**触发条件**：步骤 4 提交完成后，如果满足以下两个条件则触发：
1. 用户累计提交数量 ≥ `workspace_threshold`（阈值由服务端控制）
2. `workspace_submitted` 为 false（尚未提交过 workspace）

如果不满足条件，静默跳过此步骤。

注意：此步骤是**推荐性**提示，无论 `workspace_force_required` 是否启用都会触发。用户可以拒绝。强制拦截由步骤 3.5 和服务端 403 保证。

**触发后**：

#### 4.5.1 征询同意

告知用户：

> 你已提交 {count} 条数据（达到 {threshold} 条阈值）。为提升数据质量，我们希望额外采集你的 Workspace 配置文件（SOUL.md、USER.md 等）。这是一次性采集，所有文件会在本地自动脱敏后再提交。是否同意？

**等待用户确认。** 用户拒绝则跳过此步骤。

#### 4.5.2 本地打包 + 脱敏

用户同意后，先执行打包（不上传）：

```bash
python3 /{{baseDir}}/scripts/workspace_bundle.py --bundle-only
```

脚本输出 JSON，包含每个 workspace 的打包结果和脱敏报告：
- `workspaces[].zip_file` — 生成的 zip 文件名
- `workspaces[].zip_size` — 文件大小
- `workspaces[].scrub_report.total_redactions` — 脱敏替换总数
- `workspaces[].scrub_report.by_category` — 按类别统计（如 `{"手机号": 2, "邮箱": 1}`）
- `workspaces[].scrub_report.files_scrubbed` — 被脱敏的文件列表及各自的替换详情

#### 4.5.3 展示脱敏信息，确认提交

**必须将脱敏信息展示给用户**，让用户了解隐私处理情况：

- 如果有脱敏操作（`total_redactions > 0`）：

  > 打包完成。以下文件中检测到敏感信息并已自动脱敏：
  >
  > | 文件 | 脱敏项 |
  > |------|--------|
  > | SOUL.md | 手机号 ×2, 邮箱 ×1 |
  > | memory/user_profile.md | API Key ×1 |
  >
  > 共 {total} 处敏感信息已替换为占位符（如 `[PHONE]`、`[EMAIL]`），原始内容不会上传。
  > 是否确认提交？

- 如果没有脱敏操作（`total_redactions == 0`）：

  > 打包完成，未检测到需要脱敏的敏感信息。是否确认提交？

**等待用户确认。**

#### 4.5.4 上传

用户确认后执行上传：

```bash
python3 /{{baseDir}}/scripts/workspace_bundle.py --upload-only
```

展示上传结果（成功/失败的 workspace 数量）。

---

### 步骤 5：查询（可选）

**触发**：用户说「查看提交记录」「提交了多少条」「查看进度」等。

```bash
python3 /{{baseDir}}/scripts/query.py [--page N] [--page-size N]
```

展示已提交的 session 列表，每条包含标题、领域、模型、轮次、提交时间。默认每页 20 条，支持分页。

以表格形式展示：

> 提交记录（共 {total} 条）
>
> | # | 标题 | 领域 | 模型 | 轮次 | 提交时间 |
> |---|------|------|------|------|---------|
> | 1 | 为 React 项目添加认证 | 软件开发 | claude-opus-4-6 | 8 | 2026-04-08 14:30 |
> | ... | | | | | |

用户说「更多」或「下一页」时加载下一页。

---

### 步骤 5.5：独立 Workspace 提交

**触发**：用户说「提交 Workspace」「提交工作区配置」「workspace」等。

#### 5.5.1 查询已提交状态

```bash
python3 -c "
import sys; sys.path.insert(0, '/{{baseDir}}/scripts')
from submit import query_count
from lib.auth import get_server_url, get_stored_key
import json
print(json.dumps(query_count(get_server_url(), get_stored_key()), indent=2))
"
```

读取返回的 `workspace_submitted` 字段。

#### 5.5.2 已提交过的提醒（workspace_submitted == true）

如果用户之前已经提交过 Workspace 配置，**不要拒绝**，而是原样输出以下提示并 **停下来等待用户回复**：

> 你之前已经提交过 Workspace 配置。如果你本地的配置文件有了更新（比如 SOUL.md、USER.md、memory/ 下的内容有新变化），可以再提交一份最新版本，后端会保留所有历史版本作为参考。
>
> 是否需要提交一份新版本？

- 用户确认（"好"、"提交"、"更新"等）→ 进入 5.5.3
- 用户拒绝（"不用"、"算了"等）→ 流程结束

如果 `workspace_submitted == false`（首次提交），直接进入 5.5.3，不需要展示上面的提醒。

#### 5.5.3 本地打包 + 脱敏

```bash
python3 /{{baseDir}}/scripts/workspace_bundle.py --bundle-only
```

#### 5.5.4 展示脱敏报告，征询用户确认

展示格式与步骤 4.5.3 一致（按文件列出脱敏项，或说明未检测到敏感信息），然后等待用户确认。

#### 5.5.5 上传

```bash
python3 /{{baseDir}}/scripts/workspace_bundle.py --upload-only
```

展示上传结果。

---

### 步骤 6：重新提交（独立操作）

当用户明确要求"重新提交"某条记录时使用。**必须提供 session_id**，不提供则要求用户补充。

此操作会重新转换该 session 并强制覆盖服务端已有记录（trajectory 文件、metadata、stats 全部覆盖）。

#### 流程

1. 确认认证状态（同步骤 1.1）
2. 用户提供的 session_id 对应的 trajectory 文件必须已存在于 `output/` 目录。如果不存在，需要先重新运行扫描转换（步骤 2）生成该文件，再继续。
3. 运行重新提交：

```bash
python3 /{{baseDir}}/scripts/submit.py --resubmit {session_id}
```

4. 展示结果（是否覆盖成功、累计提交数）。

**注意**：此步骤仅在用户明确说"重新提交 xxx"时触发，正常的批量提交流程（步骤 2-4）不会使用 force 参数。

---

## 401 处理

在任何步骤中，如果 API 返回 401（unauthorized），说明 key 已失效：
1. 通知用户 key 已失效
2. 自动清除本地 key（脚本已自动完成）
3. 重新进入步骤 1.1 的认证流程（跳过 1.2 环境检查，因为环境配置不受 key 失效影响）
4. 认证成功后，从发生 401 的步骤继续执行

## 数据目录

数据文件存放在 workspace 根目录的 `.clawtraces/` 下（与 `.clawhub/` 同级），独立于 skill 安装目录，不受升级影响：

```
{workspace}/.clawtraces/
├── .env                             # API key + server URL
└── output/
    ├── candidates.json              # 扫描结果（候选 session 列表，含用户消息）
    ├── {session_id}.trajectory.json # 转换后的 Anthropic trajectory 文件
    ├── {session_id}.stats.json      # session 元数据
    └── manifest.json                # 提交记录 + 拒绝记录（已处理 session 跟踪）
```

## 注意事项

- **认证完成后必须原样输出提示文案并等待用户指令**，不要自动开始采集，不要自行增减提示内容
- `--list-only` 是轻量操作（只读索引和文件元数据），不消耗大量资源
- `--limit N` 只处理最近 N 个对话，减少处理量和后续语义审核的 token 消耗
- `--since YYYY-MM-DD` 只处理该日期之后的对话，可与 `--limit` 组合使用
- `--sessions` 指定的对话会跳过"活跃"和"已提交"的自动过滤，因为用户明确选择了它们
- `--list-only` 列出除已提交外的所有对话（包括活跃、已拒绝、模型不符的），用 `status` 字段区分
- 默认处理（不带 `--sessions`）仍然严格过滤：只处理白名单模型、非活跃、非已拒绝的对话
- 用户消息中的隐私信息（Sender 身份、时间戳）会在转换时自动清除
- System prompt 从 cache-trace 提取。自动模式下，无 cache-trace 数据的对话会被跳过（历史对话）；通过 `--sessions` 显式指定的对话会使用重建的 system prompt 作为回退
- 提交需要用户确认，确保数据授权合规
- 已提交和已拒绝的对话不会重复处理（manifest.json 跟踪）
- **面向用户的文案中统一使用"对话"而非"session"**，session_id 等技术字段仅在内部处理时使用
