## 错误处理

所有脚本遵循统一错误约定：

- **成功**：JSON 到 stdout，含 `"success": true`
- **失败**：JSON 到 stderr，含 `"success": false` 和 `"error"` 字段，exit code ≠ 0
- **Agent 应同时检查 stdout 和 stderr**

### Agent 判定顺序（统一）

> 交叉引用：本文件提供通用判定顺序；全局串联门禁与脚本进入条件以 `SKILL.md` 的“内部编排判定与门禁（仅使用现有字段）”为主。

1. 先判断 `success`：
   - `success=false`：当前链路中断，先处理 `error`
   - `success=true`：进入当前脚本的阶段字段判定
2. 再按脚本类型判断：
   - parse：看 `stage`、`missingFields`、`userOutputTemplate.clarifyQuestions`
   - validate：看 `validationReport.passed`、`validationReport.blockingIssues`、`validationReport.warningIssues`
   - create：看 `userConfirmation`、`validationReport.passed` 与创建结果字段（如 `sceneId`）
3. 最后按 `userOutputTemplate` 组织用户可见中文话术，不直出内部 JSON。

### 统一示例（成功）

```json
{
  "success": true,
  "stage": "BASE_INFO_CONFIRM",
  "missingFields": [],
  "userOutputTemplate": {
    "clarifyQuestions": []
  }
}
```

### 统一示例（失败）

```json
{
  "success": false,
  "error": "创建前校验未通过：validationReport.passed=false，请先修复 blockingIssues"
}
```

## 用户展示规则

- stdout/stderr 中的 JSON 主要用于 Agent 内部判断流程、读字段、决定下一步，不应原样贴给用户。
- 面向用户时，必须把内部 JSON 改写成中文业务表达，优先使用各脚本返回的 `userOutputTemplate`。
- 禁止直接展示英文字段名或内部状态码，例如：`title`、`businessDomainName`、`doctorConcerns`、`repGoal`、`productEvidenceStatus`、`READY_TO_CONFIRM`（常见于 validate 阶段）、`scene.xxx_missing`。
- 若需要展示字段摘要，请改成中文标签，如：`场景标题`、`业务领域`、`科室`、`产品`、`地点`、`医生顾虑`、`代表目标`、`场景背景`、`产品知识需求`。

### 用户可见输出前的内部信息拦截（强制）

在输出用户可见内容前，必须执行一次“内部信息脱敏/拦截”。若命中以下关键词或同类技术描述，必须改写为业务话术后再回复用户：

- `runtime context`
- `subagent`
- `session_key`
- `session_id`
- `internal`
- 字段级技术错误描述（例如 `doctorOnlyContext`、`validationReport.*`、`*.missing`、issue code）
- 鉴权敏感信息（例如 `access-token`、`appKey`、`Authorization`、Cookie、签名参数）

说明：

- 拦截命中后，不得把原句直接发送给用户。
- 应改写为用户可执行的业务提示（例如“内容结构需微调，我已处理并继续校验”）。
- 不得在用户可见内容中回显鉴权原文、凭据片段或调试请求头。

### 校验失败统一转写模板（用户侧）

当内部校验未通过时，用户可见话术统一采用业务表达，不直接回显技术细节。推荐模板：

1. `内容结构需微调，我已自动修正并重新校验。`
2. 若仍未通过：`当前有关键项未满足创建条件，我已整理成待确认项，请补充后我继续处理。`

### 用户可见输出自检清单（5条）

每次输出前按以下顺序自检，全部通过才可发送：

1. **是否含内部词**：不得出现 `runtime context`、`subagent`、`session_key`、`session_id`、`internal`。
2. **是否含技术字段**：不得出现字段级技术描述（如 `validationReport.*`、`doctorOnlyContext`、`*.missing`、issue code）。
3. **是否可执行**：必须给用户一个明确下一步（如“请确认创建”或“请补充 X 项”）。
4. **是否业务化**：失败/异常必须使用业务话术模板，不可直接回显脚本原始错误。
5. **是否收口优先**：若已 `passed=true` 且用户未提新修改，仅给“确认创建 / 取消”两项，不再扩展采集。

## 通用参数

所有脚本均支持以下通用参数：

| 参数 | 说明 |
|------|------|
| `--params-file <path>` | 从 UTF-8 JSON 读参数，解决长文本和中文转义问题。 |
| `--input <path>` | 与 `--params-file` 等价，兼容旧调用。 |

### 用法示例（`--params-file` 参数层）

```json
{
  "userText": "帮我创建一个心内科沟通场景",
  "scene": {},
  "parsedFields": {},
  "draftPath": ".cms-log/state/cms-tbs-scene-create/demo-draft.json"
}
```

```bash
python3 scripts/tbs-scene-parse.py --params-file payload.json
```

> 文件参数与命令行参数可混用，命令行参数优先级更高。文件必须为 UTF-8 编码。

### 推荐链路示例（自然语言长文本）

1. 先按 `references/base-info-parse.md` 提取基础信息骨架。
2. 将基础信息结果放入 `parsedFields`，执行 `tbs-scene-parse.py`。
3. 根据 `tbs-scene-parse.py` 返回的 `stage` 继续做用户确认或内部生成。

推荐 payload 形状：

```json
{
  "userText": "用户原始输入",
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
    "repGoal": "帮助医生快速了解产品特点并回应价格顾虑"
  },
  "draftPath": ".cms-log/state/cms-tbs-scene-create/demo-draft.json"
}
```
