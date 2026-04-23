## 维护说明

- 修改 `SKILL.md` 中的 `version` 时，须同步更新 `version.json`
- 新增脚本时，必须同步更新：
  - `SKILL.md`
  - 对应 `references/*.md`
  - 目录结构说明
- `prompts/` 为 schema 真源，默认必须保留；不要把 `scenario-json-parse.model.schema.json`、`scene.schema.json` 直接删掉或只留在 `references/`
- 修改 `references/scenario-json-parse.md` 中的字段约束时，必须同步检查：
  - `prompts/scenario-json-parse.model.schema.json`
  - `prompts/scene.schema.json`
  - `scripts/tbs-scene-validate.py`
- 若变更真实创建接口字段，必须同时核对 `规范和接口/TBS_ADMIN_API_REFERENCE.md`
- 若变更编排判定口径（`success`/`error`/`stage`/`validationReport`/`userConfirmation` 等），必须同步更新：
  - `SKILL.md`
  - `references/common-params.md`
  - `references/tbs-scene-parse.md`
  - `references/tbs-scene-validate.md`
  - `references/tbs-scene-create.md`
- 若变更“用户可见输出拦截词规则 / 校验失败业务转写模板 / 阶段 3 固定清单 / 收口优先规则”，必须同步更新：
  - `SKILL.md`
  - `references/common-params.md`
  - `references/tbs-scene-parse.md`
  - `references/tbs-scene-validate.md`
  - `references/agent-patterns.md`
  - `references/scenario-json-parse.md`

## 结构例外说明（本 Skill 约定）

- `prompts/` 目录为 schema 真源，作为顶层目录保留，不迁移到 `references/`。
- Python 脚本文件名保持 Python 可导入规范（可使用下划线，如 `tbs_client.py`），不采用连字符文件名。
