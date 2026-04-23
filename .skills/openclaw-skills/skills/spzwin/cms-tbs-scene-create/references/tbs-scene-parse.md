### 1. 解析场景 — `tbs-scene-parse.py`

**意图**：作为多阶段编排脚本，按“基础信息确认 → 产品知识/资料确认 → 场景内容生成 → 校验”的顺序，输出当前阶段需要用户确认/补充的内容。  
**本脚本不做自然语言全量语义生成**：自然语言长文本或用户零散补充内容，应该先通过 `references/base-info-parse.md` 提取基础信息骨架；本脚本只接收已有 `scene` / `parsedFields`，判断当前处于哪个阶段，并给出下一步动作。

```bash
python3 scripts/tbs-scene-parse.py --params-file payload.json
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--params-file` / `--input` | ✅ | 输入 JSON 文件 |

**输入 JSON 关键字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `userText` | ❌ | 用户自然语言输入 |
| `scene` | ❌ | 已有场景草稿 |
| `parsedFields` | ❌ | 上游结构化补丁，覆盖同名字段 |
| `userUpdates` / `userConfirmedFields` / `userProvidedFields` | ❌ | 用户本轮补充/纠正字段（与 `parsedFields` 等价，会按同名字段覆盖进 `scene`） |
| `draftPath` | ❌ | 草稿文件路径，便于后续 validate/create 复用 |
| `baseInfoAcknowledged` | ❌ | 仅当用户已明确确认基础信息无误时置为 `true`；用于区分“已识别”与“已确认”（也可写入 `scene.baseInfoAcknowledged` 或 `meta.baseInfoAcknowledged`） |
| `declineProductKnowledge` | ❌ | 用户已明确不补充产品知识/资料时置为 `true`（也可写入 `meta.declineProductKnowledge`）；与 `userText` 中「产品知识暂无」「不提供产品知识」等语义等价，用于跳过对产品证据状态/知识主题的反复追问 |
| `meta` | ❌ | 可选元信息；其中 `meta.baseInfoAcknowledged=true` 与顶层字段等价 |

**流程步骤**：
1. 读取 `scene` 和 `parsedFields`
2. 判断基础信息是否已齐备：`businessDomainName`、`departmentName`、`drugName`、`location`、`doctorConcerns`、`repGoal`
3. 若基础信息字段已齐备，仍需要用户明确确认（`baseInfoAcknowledged=true`）后，才允许把阶段推进到“可内部生成场景内容”
4. 在基础信息可被用户认可的前提下，基于这些信息分析该训练场景应覆盖的产品知识主题，并以关键词/主题列表形式写入 `productKnowledgeNeeds`
5. 再判断产品知识/资料是否已齐备：`productKnowledgeNeeds`、`productEvidenceStatus`、`productEvidenceSource`
   - 当 `userText` 或 `declineProductKnowledge` 表明用户**不补充**产品知识/资料时：在未出现 `PARTIAL`/`READY` 的前提下，自动设 `productEvidenceStatus=NOT_PROVIDED`、空缺的 `productKnowledgeNeeds` 写入占位主题、并补齐证据来源说明，**不再**要求用户单独回答「产品证据状态」或推断知识主题列表。
   - 当 `productEvidenceStatus` 为 `NOT_PROVIDED` 时：若未填写 `productEvidenceSource`，脚本会自动写入一条固定说明（「用户确认暂无书面证据资料」）并默认 `needsEvidenceConfirmation=true`，**不要求**用户再提供「待提供」类占位字符串。
6. 若用户有现成产品知识正文，可选补充到 `scene.knowledge`；若没有，可仅确认 `productKnowledgeNeeds` 并继续流程
7. 若基础信息已确认、且资料字段已齐备，则提示内部执行 `references/scenario-json-parse.md` 生成标题、场景背景、`repBriefing`、`actorProfile`、`doctorOnlyContext`、`coachOnlyContext`
8. 当场景内容生成完成后，提示进入 `tbs-scene-validate.py`
9. 若提供 `draftPath`，写回草稿文件

**内部编排判定（仅现有字段）**：

- 先看 `success`：
  - `success=false`：本轮 parse 失败，优先处理 `error`
  - `success=true`：继续按 `stage` 判定后续动作
- 再看 `stage` 与补充信号：
  - 若仍处于补充/确认阶段：结合 `missingFields` 与 `userOutputTemplate.clarifyQuestions` 向用户发起下一轮确认
  - 若 `stage=READY_FOR_SCENE_GENERATION`：先进入场景内容生成（读取 `references/scenario-json-parse.md` 并补齐内容字段），再回到 parse/validate 门禁
  - 若 `stage=READY_FOR_VALIDATE`：进入 `tbs-scene-validate.py`
- 若提供 `draftPath`，后续 validate/create 必须优先复用同一草稿路径，避免多版本漂移。

**`stage` 常见取值（以脚本实际返回为准）**：

- `BASE_INFO_CONFIRM`：先确认基础信息
- `KNOWLEDGE_CONFIRM`：再确认产品知识与资料
- `READY_FOR_SCENE_GENERATION`：已可进入场景内容生成
- `READY_FOR_VALIDATE`：已可执行场景校验

说明：调用方不应硬编码阶段推进逻辑，应以脚本本轮返回的 `stage` 为准决定下一步。

**对用户输出约束**：
- 向用户展示确认清单时，只允许使用中文标签与自然语言说明。
- 禁止直接暴露字段名，如 `title`、`businessDomainName`、`productKnowledgeNeeds`、`repBriefing`。
- 命中执行意图后的首条用户可见回复，必须直接进入“第一步：收集场景基本信息”，不得先描述内部判断、读文档、脚本执行计划。
- 禁止输出内部过程话术（例如“进入结构化流程”“先读取关键参考文档”）。
- 若用户本轮对已确认字段做了修改，必须先向用户回显“修改后的确认清单”（至少覆盖被修改字段）并等待确认，再进入内部生成或校验。
- 应优先使用 `userOutputTemplate.confirmationItems` 展示确认清单；该清单按阶段累计展示（包含本阶段及之前阶段已确认内容），避免用户在后续阶段看不到已确认信息。完整阶段总览可用 `userOutputTemplate.phaseSections`。
- 阶段 1 基础信息确认时，确认清单仅限：业务领域、科室、产品、地点、医生顾虑、代表目标；不要额外拼接“关键决策者/利好背景/场景氛围”等扩展条目。
- `confirmationItems` 与 `phaseSections[*].items` 中的 `status` 用于区分“待补充 / 待确认 / 请确认”：`KNOWLEDGE_CONFIRM` 及后续阶段里，基础信息字段在未收到 `baseInfoAcknowledged=true` 前应显示为 **待确认**（脚本不会把它当成用户已口头确认的事实）。
- 若存在推断或待确认说明，应同时展示 `userOutputTemplate.pendingConfirmNotes`；若存在补充追问，应展示 `userOutputTemplate.clarifyQuestions`。

**阶段 1：基础信息确认字段**：
- `businessDomainName`
- `departmentName`
- `drugName`
- `location`
- `doctorConcerns`
- `repGoal`

**阶段 2：产品知识与资料确认字段（用户侧）**：
- `productKnowledgeNeeds`
- `knowledge`（建议知识内容草案，可由系统先给出并请用户确认/调整）

**阶段 2 内部推断字段（用户无需填写）**：
- `productEvidenceStatus`
- `productEvidenceSource`

说明：
- `productKnowledgeNeeds` 表示**系统根据基础信息分析出来的建议知识主题/关键词**，用于向用户确认“这个训练场景需要哪些产品知识”。
- `productEvidenceStatus` 与 `productEvidenceSource` 由系统根据用户给出的知识主题/资料自动推断，不要求用户逐项填写。
- 用户可以：
  - 仅确认/调整这些主题关键词；
  - 基于系统给出的建议知识内容草案，确认、删改或补充；
  - 额外补充产品知识正文、证据来源、政策内容等材料；
  - 也可以暂时不补充正文，只保留需求关键词继续流程。
- 若用户补充了“代表话术/经验”，默认归入 `coachOnlyContext` 的 `## 最佳实践`。
- 若用户补充了可落库的产品知识正文，建议写入可选字段 `scene.knowledge`（数组），供创建前执行“先查后建”的知识解析流程。

**阶段 3：内容生成后对用户展示的完整确认清单（累计）**：
- `businessDomainName`
- `departmentName`
- `drugName`
- `location`
- `doctorConcerns`
- `repGoal`
- `productKnowledgeNeeds`
- `title`
- `sceneBackground`
- `actorProfile`

说明：以上为阶段 3 固定清单字段，默认不得临时新增展示项。若需新增字段，必须先同步更新本文件模板与相关联动文档。

**不进入用户确认清单的内部生成字段**：
- `repBriefing`
- `doctorOnlyContext`
- `coachOnlyContext`

这些字段继续参与后续 `validate` 与创建门禁，但默认由模型/系统内部生成与校验，不向用户逐段确认正文。

---

## 标准 payload 示例

### 示例 1：基础信息确认阶段

```json
{
  "scene": {},
  "parsedFields": {
    "businessDomainName": "临床推广",
    "departmentName": "消化内科",
    "drugName": "美沙拉秦肠溶片",
    "location": "三级医院门诊",
    "doctorConcerns": [
      "产品优势",
      "集采与价格"
    ],
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑",
    "generationNotes": "drugName 为推断结果，待用户确认。"
  }
}
```

### 示例 2：产品知识与资料确认阶段

```json
{
  "scene": {
    "businessDomainName": "临床推广",
    "departmentName": "消化内科",
    "drugName": "美沙拉秦肠溶片",
    "location": "三级医院门诊",
    "doctorConcerns": [
      "产品优势",
      "集采与价格"
    ],
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑"
  },
  "parsedFields": {
    "productKnowledgeNeeds": [
      "作用机制与剂型特点",
      "临床定位",
      "安全性特点",
      "集采价格与可及性"
    ],
    "productEvidenceStatus": "PARTIAL",
    "productEvidenceSource": [
      "产品说明书",
      "待补充：集采政策文件"
    ]
  }
}
```

### 示例 3：内容生成完成后的复检阶段

```json
{
  "scene": {
    "businessDomainName": "临床推广",
    "departmentName": "消化内科",
    "drugName": "美沙拉秦肠溶片",
    "location": "三级医院门诊",
    "doctorConcerns": [
      "产品优势",
      "集采与价格"
    ],
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑",
    "productKnowledgeNeeds": [
      "作用机制与剂型特点",
      "临床定位"
    ],
    "productEvidenceStatus": "PARTIAL",
    "productEvidenceSource": [
      "产品说明书"
    ],
    "needsEvidenceConfirmation": true,
    "title": "消化内科门诊 - 美沙拉秦肠溶片产品沟通",
    "sceneBackground": "......",
    "repBriefing": "......",
    "actorProfile": {
      "name": "消化内科医生"
    },
    "doctorOnlyContext": "......",
    "coachOnlyContext": "......"
  }
}
```

## 内部判定示例（不直接展示给用户）

```json
{
  "success": true,
  "stage": "KNOWLEDGE_CONFIRM",
  "missingFields": [
    "productKnowledgeNeeds"
  ],
  "userOutputTemplate": {
    "clarifyQuestions": [
      "请确认本场景需要覆盖的产品知识主题。"
    ]
  }
}
```

## 面向用户的固定展示模板

### 阶段 1：基础信息确认

```text
第一步：收集场景基本信息。
我先整理了这次训练场景的基础信息，请你确认：

- 业务领域：{{业务领域}}
- 科室：{{科室}}
- 产品：{{产品}}
- 地点：{{地点}}
- 医生顾虑：{{医生顾虑}}
- 代表目标：{{代表目标}}

待确认说明：
- {{待确认说明}}

如有不准确或缺失，请直接补充；确认后我继续整理产品知识需求。
```

### 阶段 2：产品知识与资料确认

```text
基于当前整理的基础信息（如你尚未明确确认，请先核对是否准确），我建议这个训练场景重点覆盖以下产品知识：

- {{产品知识需求1}}
- {{产品知识需求2}}
- {{产品知识需求3}}

我先给出一版建议知识内容草案（用于你快速确认/调整）：

1) {{建议知识内容草案1}}
2) {{建议知识内容草案2}}
3) {{建议知识内容草案3}}

请按以下分支回复（可同一条消息完成）：

A) 若你暂无产品资料/不提供书面证据：
1) 仅确认或调整产品知识主题（可写“暂无”）
2) 建议知识内容草案可只做方向确认，不要求你补充证据原文
3) 我将自动标记产品证据状态为“未提供（NOT_PROVIDED）”，产品证据来源无需你填写（系统内部自动补固定说明）

B) 若你有产品资料可提供：
1) 产品知识主题（确认/调整）
2) 对建议知识内容草案做补充或修正（也可直接替换）
3) 可选补充：说明书、指南、政策文件等资料（产品证据状态与证据来源由系统自动判断与归一，无需你填写）

你也可以额外补充产品知识正文或政策文件；若暂时没有正文，不阻断继续下一步。
```

### 阶段 3：内容生成后复核

```text
我已根据前面确认的信息生成场景内容，请确认以下完整清单（含之前已确认项）：

- 业务领域：{{业务领域}}
- 科室：{{科室}}
- 产品：{{产品}}
- 地点：{{地点}}
- 医生顾虑：{{医生顾虑}}
- 代表目标：{{代表目标}}
- 产品知识需求：{{产品知识需求}}
- 场景标题：{{场景标题}}
- 场景背景：{{场景背景}}（须展示正文，勿省略；勿用「训练目标」类自创小节替代）
- 对练对象角色：{{对练对象角色}}

如业务含义无误，我将先做内部程序校验（含格式收敛与门禁检查）；若仅有提示项不会阻断创建。校验通过后你只需回复一次「确认」即可发起真实创建。若你更改正文，请直接说明。
```
