# scripts 目录说明

本目录存放 `cms-tbs-scene-create` 的 Python 执行脚本与共享客户端。

## 脚本清单

| 脚本 | 类型 | 作用 |
|---|---|---|
| `tbs-scene-parse.py` | 编排脚本 | 解析输入并推进分阶段确认流程 |
| `tbs-scene-validate.py` | 校验脚本 | 对场景草稿执行创建前门禁校验 |
| `tbs-scene-create.py` | 创建脚本 | 在用户确认后执行真实创建 |
| `tbs_client.py` | 共享库 | 封装 TBS Admin API 请求、主数据匹配/创建、知识去重逻辑 |
| `tbs_md_sanitize.py` | 工具脚本 | 对部分 Markdown 内容做预处理与清洗 |

---

## `tbs_client.py` 脚本说明

### 定位

`tbs_client.py` 是本 Skill 的共享客户端与领域工具库，不直接面向用户，也不是独立的业务入口脚本。  
它主要被 `tbs-scene-create.py`（以及可能的后续创建链路脚本）导入调用。

### 主要职责

1. 封装 HTTP 请求与通用重试（`TBSClient.request_json`）。
2. 统一解析不同响应包裹格式（如 `data` / `result`）。
3. 解析主数据 ID，并执行“先查后建”：
   - 业务领域：`resolve_or_create_business_domain`
   - 科室：`resolve_or_create_department`
   - 品种：`resolve_or_create_drug`
   - 画像：`resolve_or_create_persona`
4. 解析产品知识并去重复用（按标题精确匹配 + 内容指纹）：
   - `resolve_or_create_knowledge_for_scene`
5. 汇总创建场景所需关联 ID：
   - `resolve_ids_for_scene`

### 输入与依赖

- 依赖调用方提供：
  - `base_url`
  - `access-token`
  - `scene` 草稿（含主数据与可选知识条目）
- 依赖 `requests` 发起 API 调用。

### 输出形态

- 返回结构化对象（ID、解析动作摘要、去重结果等）供上层脚本继续组装创建请求。
- 遇到不可恢复问题时抛出 `RuntimeError`，由上层脚本统一处理并返回标准错误 JSON。

### 边界与约束

- `tbs_client.py` 不负责用户对话与用户话术输出。
- 不直接定义“是否创建”的业务门禁（如 `userConfirmation`、`validationReport.passed`）；门禁由上层脚本负责。
- 不单独负责鉴权获取；`access-token` 应由 `cms-auth-skills` 提供并由调用脚本注入。

### 维护注意事项

- 若新增/变更主数据解析逻辑（业务领域、科室、品种、画像、知识），需同步核对：
  - `references/tbs-scene-create.md`
  - `references/maintenance.md`
  - 相关调用脚本（当前主要是 `tbs-scene-create.py`）
