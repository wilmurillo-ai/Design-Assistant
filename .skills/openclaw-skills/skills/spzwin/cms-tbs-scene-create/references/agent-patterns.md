## Agent 调用模式示例

> 说明（强约束）：本文件中的 `Agent → 先读... / exec...` 是**内部编排动作**，仅用于指导调用顺序，禁止原样或改写后向用户播报。
> 命中“创建场景”执行意图时，用户首条可见回复应直接进入“第一步：收集场景基本信息”。

### 模式 A：自然语言场景 -> 基础信息确认

```
用户：「帮我建一个心内科的训练场景，主任担心长期安全性」
Agent → 先读 references/base-info-parse.md
Agent → 再读 prompts/base-info-parse.model.schema.json
Agent → 从用户输入提炼 businessDomainName / departmentName / drugName / location / doctorConcerns / repGoal
Agent → exec: python3 scripts/tbs-scene-parse.py --params-file payload.json
Agent ← JSON（stage=BASE_INFO_CONFIRM 或后续阶段）
Agent → 向用户展示中文标签版基础信息确认清单与待补充问题，不暴露英文字段名
Agent → 话术优先套用 references/tbs-scene-parse.md 中“阶段 1：基础信息确认”模板，并以“第一步：收集场景基本信息”开场
Agent → 若用户在对话中纠正基础字段（例如把 drugName 收窄为更短口径），下一轮必须把纠正写回 `parsedFields` 再执行 `tbs-scene-parse.py`，避免后续生成/校验仍引用旧值
Agent → 检测到用户纠正字段后，先回显“修改后的确认清单”（至少覆盖改动字段）并请用户确认，再进入内部生成/校验
```

反例（不要这样展示给用户）：
`title: ...`
`businessDomainName: ...`
`productEvidenceStatus: PARTIAL`
`收到，业务场景已记录。基础信息骨架如下：{...JSON...}`

正例（应改写成中文业务表达）：
`场景标题：...`
`业务领域：临床推广`
`产品证据状态：部分提供`

### 模式 B：基础信息确认后 -> 产品知识/资料确认

```
用户：「产品是某某，顾虑主要是长期安全性和价格」
Agent → 重新执行 tbs-scene-parse.py
Agent ← JSON（stage=KNOWLEDGE_CONFIRM）
Agent → 先核对脚本返回的 `stage` 与确认清单项状态（`userOutputTemplate.confirmationItems[*].status`）是否仍为“待确认”；只有当用户明确确认基础信息无误后，才在下一轮 payload 顶层设置 `baseInfoAcknowledged: true`（或写入 `scene.baseInfoAcknowledged: true`）
Agent → 基于当前基础信息（已确认或待确认），在同一轮里同时给出“建议知识主题 + 建议知识内容草案”，再让用户确认/调整；`productEvidenceStatus`、`productEvidenceSource` 由系统内部自动推断与归一
Agent → 若用户明确不提供书面证据或产品知识（如「产品知识暂无，不提供」）：**不得**再追问产品证据状态/知识主题列表；将原话写入 `userText` 再次执行 parse，或传 `declineProductKnowledge: true`；由 `tbs-scene-parse.py` 自动设 `NOT_PROVIDED`、占位 `productKnowledgeNeeds` 与证据来源说明
Agent → 若用户补充了产品知识正文/政策解读，则写入 scene.knowledge；若未补充正文，也可先保留建议内容草案并继续后续流程
Agent → 话术优先套用 references/tbs-scene-parse.md 中“阶段 2：产品知识与资料确认”模板
```

### 模式 C：资料确认后 -> 内部生成场景内容

```
Agent → 再次执行 tbs-scene-parse.py
Agent ← JSON（stage=READY_FOR_SCENE_GENERATION）
Agent → 此时才在内部读取 references/scenario-json-parse.md 与 prompts/*.json
Agent → 生成 title / sceneBackground / repBriefing / actorProfile / doctorOnlyContext / coachOnlyContext
Agent → 生成后立刻合并进 scene，并执行 tbs-scene-parse.py（写 draft 更佳）与 tbs-scene-validate.py 各至少一次；**在向用户展示「阶段 3」业务摘要之前**，应已拿到 validate 结果或已根据 issueHints 完成可自动修复项
Agent → 对用户展示时套用 references/tbs-scene-parse.md「阶段 3」模板：必须回显“累计确认清单”（含前序已确认的基础信息/产品知识 + 新生成的标题/背景/角色），避免用户在终检前看不到已确认项；程序校验（含 doctorOnlyContext 固定节）属于创建前门禁，可与业务确认同轮静默完成，不要把「请你确认无误」与「我再跑一遍校验」拆成两次心理门槛
```

### 模式 D：用户补充后终检

```
用户：「标题叫高血压门诊首诊沟通，目标是推动小范围试用」
Agent → exec: python3 scripts/tbs-scene-validate.py --params-file draft.json
Agent ← JSON（passed=true/false、validationReport）
Agent → 向用户展示时用 userOutputTemplate.confirmationItems / issueHints（中文标签），勿暴露英文字段名或 issues 码
Agent → 仅在 passed=true 时向用户发起最终确认；若仅有 warningHints，可提示“建议优化但不阻断确认”；转述 `confirmationItems` 时须含 **场景背景**，勿用「训练目标」替代
Agent → 若 passed=true 且用户未提出新的修改请求，进入收口优先：只给“确认创建 / 取消”两项，不再主动扩展采集
```

### 模式 E：确认后真实创建

```
用户：「确认」
Agent → 先通过 cms-auth-skills 获取 access-token
Agent → exec: python3 scripts/tbs-scene-create.py --params-file draft.json --access-token "<ACCESS_TOKEN>"
Agent ← JSON（sceneId、resolvedIds、knowledgeIds）
Agent → 告知场景创建成功
```
