### 3. 创建场景 — `tbs-scene-create.py`

**意图**：在用户明确确认后，解析主数据并调用 `POST /scene/createScene` 创建 TBS 场景。

```bash
python3 scripts/tbs-scene-create.py \
  --params-file draft.json \
  --access-token "<ACCESS_TOKEN>"
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--params-file` / `--input` | ✅ | 输入 JSON 文件 |
| `--access-token` | ✅ | 由 `cms-auth-skills` 注入 |
| `--base-url` | ❌ | 默认生产环境 `https://sg-al-cwork-web.mediportal.com.cn/tbs-admin` |

**输入 JSON 关键字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `scene` | ✅ | 已通过 validate 的场景草稿 |
| `validationReport` | ✅ | 校验结果，且 `passed=true` |
| `userConfirmation` | ✅ | 仅允许：`确认` 或 `取消` |
| `draftPath` | ❌ | 草稿文件路径，成功后回写 `persistResult` |

`scene` 中与产品知识相关的补充约定（可选）：

- `productKnowledgeNeeds`：本场景需要覆盖的知识主题/关键词，来源于基础信息分析与用户确认。
- `knowledge`：用户额外补充的产品知识正文数组；若提供，则创建前按“先查后建”解析为 `knowledgeIds`。
- `knowledgeIds`：创建链路派生字段，不要求用户手填。

**流程步骤**：
1. 检查 `userConfirmation`
2. 校验 `validationReport.passed=true`
3. 解析或创建 `businessDomainId`
4. 解析或创建 `departmentId`
5. 解析或创建 `drugId`
6. 解析或创建 `personaIds`
7. 若 `scene.knowledge` 有用户补充的产品知识正文，则按 `drugId` 解析或创建 `knowledgeIds`
8. 调用 `POST /scene/createScene`
9. 返回 `sceneId`、`resolvedIds`、`personaIds`、`knowledgeIds` 与创建摘要

**创建门禁与失败判定（仅现有字段）**：

- 先看 `success`：
  - `success=false`：当前创建链路失败，先处理 `error`
  - `success=true`：继续核对创建结果字段
- create 前必须同时满足：
  1. `userConfirmation=确认`
  2. `validationReport.passed=true`
  3. 已提供有效 `--access-token`
- 任一门禁不满足时，视为当前轮不可创建，应回退到补充/确认步骤，不得调用真实创建接口。
- 创建成功后应至少可读取：`sceneId` 与创建摘要；若有主数据解析，附带 `resolvedIds`、`personaIds`、`knowledgeIds`。

**失败输出约定（沿用通用规则）**：

- 失败输出统一为 `success=false` + `error`（stderr），并返回非 0 exit code。
- Agent 侧收到失败后，优先依据 `error` 判断是“缺确认 / 缺校验 / 鉴权问题 / 上游失败”，再决定回退或重试。

**创建接口字段**：

- `title`
- `businessDomainId`
- `departmentId`
- `drugId`
- `location`
- `doctorOnlyContext`
- `coachOnlyContext`
- `repBriefing`
- `personaIds`
- `knowledgeIds`（若有）

补充约定：
- 本技能以 `sceneBackground` 作为场景背景正文的单一来源；创建前会将 `repBriefing` 同步为 `sceneBackground`，避免用户确认文本与落库展示文本不一致。

**画像解析规则（必经）**：

- 从 `scene.actorProfile` 读取；若为空，兼容读取 `scene.doctorProfile`。
- 先查 `GET /rolePersona/forResourceSelect`，按 `name + title` 优先精确匹配；若输入含 `roleType`，则优先要求角色类型一致。
- 未命中则 `POST /rolePersona/createRolePersona`。
- 成功响应在文档中多为 `data` 直接返回数字 ID；客户端需同时兼容 `data` 为数值、`{ id | personaId }` 字典或顶层 `personaId` 等变体（`tbs_client.extract_create_persona_id`）。
- 创建时默认：
  - `trustInitial=80`
  - `patienceInitial=80`
  - `isPreset=false`
- `personaIds` 传给 `createScene` 时使用接口要求的数组结构，例如：
  - `personaId`
  - `difficulty`（默认 `medium`）
  - `isDefault`（默认 `true`）
  - `rounds`（默认 `5`）

**产品知识解析规则（可选）**：

- 仅当 `scene.knowledge` 中存在可用条目时执行。
- 解析顺序采用“先查后建”：
  - 先查 `POST /knowledge/listProductKnowledge`
  - 回退 `GET /knowledge/forResourceSelect`
  - 未命中则 `POST /knowledge/createProductKnowledge`
- 同一 `drugId` 下优先按 `title` 精确复用，其次按 `content` 指纹复用。
- `productEvidenceStatus=NOT_PROVIDED` 时不创建知识正文，只保留待补充任务。
- `productEvidenceStatus=PARTIAL` 时，仅创建带证据来源的知识条目。
- `productEvidenceStatus=READY` 时，允许批量解析/创建并回写 `knowledgeIds`。

---
