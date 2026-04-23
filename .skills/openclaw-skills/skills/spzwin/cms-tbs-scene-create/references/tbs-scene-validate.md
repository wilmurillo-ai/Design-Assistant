### 2. 校验场景 — `tbs-scene-validate.py`

**意图**：校验场景草稿是否已经达到“可向用户发起最终确认”的条件。

```bash
python3 scripts/tbs-scene-validate.py --params-file draft.json
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--params-file` / `--input` | ✅ | 输入 JSON 文件 |

**校验要求**：

- 必须具备：`title`
- 必须具备：`businessDomainName`
- 必须具备：`departmentName`
- 必须具备：`drugName`
- 必须具备：`location`
- 必须具备：`doctorConcerns`
- 必须具备：`repGoal`
- 必须具备：`sceneBackground`
- 必须具备：`productKnowledgeNeeds`
- 必须具备：`repBriefing`
  - `repBriefing` 额外规则：长度 <= 180；不得包含【】或“待补充”；不得使用标签化前缀（如“场景背景：”）；`departmentName` 与 `location` 需作为子串出现；`drugName` 允许以括号前主名称作为锚点（与 `references/scenario-json-parse.md` 描述一致）；避免出现面向具体个人的代词（你/我/他/她/它/咱/咱们/我们/你们/他们/她们）。
- 必须具备：`doctorOnlyContext`
- 必须具备：`coachOnlyContext`

> 说明：`doctorOnlyContext` 与 `coachOnlyContext` 仍然是创建前必过的内部门禁，但不属于用户逐段确认内容。

**说明**：草稿在进入本脚本前，若 `productEvidenceStatus=NOT_PROVIDED` 且证据来源列表为空，会先规范为一条「用户确认暂无书面证据资料」说明（与 `tbs-scene-parse.py` 行为一致），避免向用户反复索要占位文案。

**说明**：若 `doctorOnlyContext` 中 `## 核心顾虑` 下出现 3 条及以上以 `-` 开头的 bullet，本脚本会在校验前**自动合并为至多 2 条**（满足固定模板），并在 `validationReport.autoNormalized` 中注明；模型仍应在 `scenario-json-parse` 阶段尽量直接生成合规条数。

**流程步骤**：
1. 读取当前 `scene`
2. 检查必填字段是否缺失
3. 检查 `businessDomainName` 是否属于允许值
4. 生成分级 `validationReport`：
   - `blockingIssues`：阻断项（必须修复）
   - `warningIssues`：提示项（建议优化，不阻断）
5. `passed=true`（即 `blockingIssues` 为空）时，允许进入用户【确认 / 取消】

**内部判定口径（仅现有字段）**：

- 先看 `success`：
  - `success=false`：校验脚本调用失败，先处理 `error`
  - `success=true`：再看 `validationReport`
- 以 `validationReport.passed` 作为唯一放行门禁：
  - `passed=true`：允许进入最终确认与创建准备
  - `passed=false`：不得进入 create，需先修复 `blockingIssues`
- `warningIssues` 仅提示优化，不阻断流程。
- 若存在 `validationReport.autoNormalized`，应记录在流程上下文中，但不改变放行门禁规则。

**分级规则（当前实现）**：
- 以下 `repBriefing` 细分码归类为 `warningIssues`（不阻断最终确认）：
  - `scene.repBriefing_too_long`
  - `scene.repBriefing_placeholder`
  - `scene.repBriefing_label_style`
  - `scene.repBriefing_pronoun`
  - `scene.repBriefing_anchor_missing`
- 其他现有 issue code 默认归类为 `blockingIssues`

**自动修复（当前实现）**：
- 校验前会对 `repBriefing` 做低风险规范化（去除 `【】` / “待补充”、去标签化前缀、补齐科室/产品/地点锚点、超长截断）。
- 若发生自动修复，会写入 `validationReport.autoNormalized` 供流程记录与追踪。

**对用户输出约束**：

- `userOutputTemplate.confirmationItems` 已按「场景标题 → 场景背景 → …」排序；Agent 转述给用户时须保留 **场景背景** 一项，不得用「训练目标」等自拟标题替换场景背景。
- 向用户展示「待最终确认的字段摘要」或「未通过原因」时，请使用 `userOutputTemplate.confirmationItems`（`label` 已为中文）与 `userOutputTemplate.issueHints`（中文说明）。
- 若存在 `warningIssues`，可展示 `userOutputTemplate.warningHints`；但在 `passed=true` 时，不应把 warning 表述成“必须修复”。
- 不要直接把 `confirmedFields` 的键名、`validationReport.issues` 里的英文码抄给用户。
- 若 `passed=false`，应统一改写为业务话术，不直接回显字段级技术错误。推荐：
  - `内容结构需微调，我已自动修正并重新校验。`
  - 若仍未通过：`当前有关键项未满足创建条件，我已整理成待确认项，请补充后我继续处理。`
- 若 `passed=true` 且用户未提出新的修改请求，进入收口优先分支：只提供“确认创建 / 取消”两项选择，不再主动发起额外信息采集。

---

## 判定示例（内部）

### 可进入确认

```json
{
  "success": true,
  "validationReport": {
    "passed": true,
    "blockingIssues": [],
    "warningIssues": [
      "scene.repBriefing_pronoun"
    ]
  }
}
```

### 不可进入确认

```json
{
  "success": true,
  "validationReport": {
    "passed": false,
    "blockingIssues": [
      "scene.title_missing"
    ],
    "warningIssues": []
  }
}
```
