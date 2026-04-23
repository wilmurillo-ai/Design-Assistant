---
name: cms-tbs-scene-create
description: 提供【TBS场景创建】全流程执行能力。用户一旦表达“创建TBS场景/建训练场景/把业务背景转成可创建场景/确认后创建场景”等执行意图，必须进入本 Skill 的结构化解析与脚本调用流程；仅当用户明确是纯咨询时，才允许先文字说明并二次确认是否执行。本 Skill 通过依赖 `cms-auth-skills` 获取 `access-token` 后，才允许进入真实创建链路。
skillcode: cms-tbs-scene-create
github: https://github.com/xgjk/xg-skills/tree/main/cms-tbs-scene-create
dependencies:
  - cms-auth-skills
# bump 时须同步修改同目录下 version.json 的 version 字段
version: 0.5.5
tools_provided:
  - name: tbs_client
    category: exec
    risk_level: medium
    permission: write
    description: TBS Admin API 共享客户端，封装请求、主数据精确匹配与创建逻辑
    status: active
  - name: tbs-scene-parse
    category: exec
    risk_level: low
    permission: read
    description: 解析用户输入为场景草稿，并输出待确认字段与缺失字段
    status: active
  - name: tbs-scene-validate
    category: exec
    risk_level: low
    permission: read
    description: 校验场景草稿是否达到可确认创建条件
    status: active
  - name: tbs-scene-create
    category: exec
    risk_level: medium
    permission: write
    description: 在用户明确确认后解析主数据并调用 createScene 创建场景
    status: active
---

# cms-tbs-scene-create

## 核心定位

本 Skill 只做一件事：根据用户执行意图，读取对应 `references/*.md` 与 `prompts/*.json`，再执行 `scripts/*.py`。  
参数、边界、分支逻辑都以 `references` 为准，`SKILL.md` 只负责入口和流程约束。

## 强制前置（保持不变）

调用任何真实创建脚本前，必须先通过依赖 Skill `cms-auth-skills` 获取有效 `access-token`。  
未鉴权时，不允许执行 `tbs-scene-create.py` 及其真实创建链路。
本 Skill 发起的所有 TBS Admin API 请求均基于该 `access-token` 鉴权。

`access-token` 的获取与传递方式必须为：由上游 `cms-auth-skills` 注入/传递到本 Skill 执行命令中（`--access-token`）。

## 标准执行流程（必须遵循）

1. 识别用户是“执行动作”还是“纯咨询”。
2. 若是纯咨询：先提供说明性答复，并明确询问是否进入创建执行；在用户未明确要求执行前，不进入脚本调用链路。
3. 若是执行动作：先定位目标脚本。
4. 先读取 `references/auth.md`，确保 `access-token` 与 `--base-url` 环境一致（未读不得进入真实创建链路）。
5. 再读取该脚本对应的 `references/*.md`（及本阶段要求的 `prompts/*.json`），未读不得执行。
6. 按文档组装参数并执行 `python3 scripts/<name>.py`。
7. 如一轮调用多个脚本，每个脚本的 reference 都要先读再执行。

## 内部编排判定与门禁（仅使用现有字段）

本 Skill 的内部编排只使用当前已存在字段，不新增协议字段：

- 通用判定：`success`、`error`
- parse 判定：`stage`、`missingFields`、`userOutputTemplate.clarifyQuestions`
- validate 门禁：`validationReport.passed`、`validationReport.blockingIssues`、`validationReport.warningIssues`
- create 门禁：`userConfirmation`、`validationReport.passed`、`sceneId`、`resolvedIds`、`personaIds`、`knowledgeIds`
- 草稿复用：`draftPath`

串联规则（parse -> validate -> create）：

1. `success=true` 仅表示脚本调用成功返回，不等于可直接进入下一脚本。
2. `tbs-scene-parse.py`：根据 `stage` 判断当前在“继续补充/继续确认/可进入场景内容生成/可进入校验”哪个阶段。
3. `tbs-scene-validate.py`：仅当 `validationReport.passed=true` 时，才允许进入最终确认与创建准备。
4. `tbs-scene-create.py`：仅当 `userConfirmation=确认` 且 `validationReport.passed=true` 时允许真实创建。
5. 任一脚本返回 `success=false`，均视为当前链路中断，先处理 `error` 后再决定是否重试或回退。

## 用户可见回复约束（必须遵循）

1. 命中执行意图（如“创建TBS场景/建训练场景”）后，首条用户可见回复必须直接进入“阶段 1：基础信息确认”，优先使用 `references/tbs-scene-parse.md` 固定模板开场。
2. 禁止对用户播报内部动作或思考过程，包括但不限于：
   - “你要创建TBS场景，这是执行意图，我进入结构化流程”
   - “先读取关键参考文档，理清流程再动手”
   - “我先读 references / prompts 再执行脚本”
3. 读取 `references/*.md`、`prompts/*.json`、执行脚本等动作属于内部编排，只能在系统内部完成，不应作为用户可见话术。
4. 面向用户只输出业务导向内容：确认清单、待补充问题、下一步用户操作（如“请补充/请确认”）。
5. 禁止向用户展示任何中间结构化结果（如基础信息骨架 JSON、payload JSON、脚本原始 stdout/stderr JSON），包括代码块、折叠块或“JSON x lines”形式。
6. 用户可见输出前，必须执行内部信息拦截：命中 `runtime context`、`subagent`、`session_key`、`session_id`、`internal` 或字段级技术报错时，必须改写为业务话术后再输出。
7. 校验失败时，统一使用业务话术模板，不直接回显技术字段或 issue code（例如：“内容结构需微调，我已自动修正并重新校验。”）。
8. 收口优先：当 `validationReport.passed=true` 且用户未提出新的修改请求时，仅提供“确认创建 / 取消”两种选择，不再主动扩展采集。

## 常用命令与必读文档

建议先读：`references/README.md`（总索引与推荐阅读顺序）。

| 脚本 | 必读 reference | 用途 |
|------|----------------|------|
| `tbs-scene-parse.py` | `references/tbs-scene-parse.md` | 分阶段确认与门禁编排 |
| `tbs-scene-validate.py` | `references/tbs-scene-validate.md` | 创建前程序校验 |
| `tbs-scene-create.py` | `references/tbs-scene-create.md` | 用户确认后真实创建 |

补充：
- 自然语言骨架提取：`references/base-info-parse.md` + `prompts/base-info-parse.model.schema.json`
- 场景正文生成：`references/scenario-json-parse.md` + `prompts/scenario-json-parse.model.schema.json`
- 复杂编排示例：`references/agent-patterns.md`

## 测试示例（推荐）

### 示例 1：先做基础信息分阶段解析

```bash
# 第一步：先读 references/base-info-parse.md
# 第二步：按 prompts/base-info-parse.model.schema.json 提取骨架并写入 payload.json
# 第三步：执行 parse，判断当前阶段
python3 scripts/tbs-scene-parse.py --params-file payload.json
```

### 示例 2：生成后先校验，再发起最终确认

```bash
# 第一步：先读 references/tbs-scene-validate.md
python3 scripts/tbs-scene-validate.py --params-file draft.json
```

### 示例 3：用户确认创建后真实落库

```bash
# 第一步：先读 references/tbs-scene-create.md
python3 scripts/tbs-scene-create.py \
  --params-file draft.json \
  --access-token "<ACCESS_TOKEN>"
```

## 反向示例（不要这样做）

- 未获取 `access-token` 就直接执行 `scripts/tbs-scene-create.py`。
- 没读对应 `references/*.md` 就起调脚本。
- 未经过 `tbs-scene-validate.py` 就直接进入创建。
- 用户还没明确回复“确认创建”，就直接调用 `/scene/createScene`。
- 主数据精确匹配到多条时，擅自猜测业务领域、科室或品种。
- 用户明确“产品知识暂无 / 不提供资料”后，仍重复追问证据状态或强推知识主题。
- 基础信息确认阶段私自扩展结构化字段（如“关键决策者/利好背景/场景氛围”）并向用户展示，导致确认清单超出脚本门禁字段。
- 产品知识与资料确认阶段把问题拆成多轮反复追问（应优先引导用户一次性回复：主题 + 证据状态 + 证据来源）。

## 错误处理与通用参数

通用错误格式、`--params-file` 用法、输入文件规则请查看 `references/common-params.md`。

---

## 目录结构

```text
cms-tbs-scene-create/
├── SKILL.md
├── version.json
├── prompts/
│   ├── base-info-parse.model.schema.json
│   ├── scenario-json-parse.model.schema.json
│   └── scene.schema.json
├── scripts/
│   ├── README.md
│   ├── tbs_client.py
│   ├── tbs_md_sanitize.py
│   ├── tbs-scene-parse.py
│   ├── tbs-scene-validate.py
│   └── tbs-scene-create.py
└── references/
    ├── README.md
    ├── auth.md
    ├── base-info-parse.md
    ├── tbs-scene-parse.md
    ├── tbs-scene-validate.md
    ├── tbs-scene-create.md
    ├── scenario-json-parse.md
    ├── common-params.md
    ├── agent-patterns.md
    └── maintenance.md
```
