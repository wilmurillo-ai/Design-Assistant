---
name: sfe-data-viewer
description: SFE数据查询与分析工具，用于查询医药销售效能数据
skillcode: sfe-data-viewer
dependencies:
  - cms-auth-skills
---

# SFE-Data-Viewer — 索引

本文件提供**能力宪章 + 能力树 + 按需加载规则**。详细参数与流程见各模块 `openapi/` 与 `examples/`。

**当前版本**: v0.1

**接口版本**: 所有业务接口统一使用 `/erp-open-api/*` 前缀，通过 `appKey` 鉴权。

**能力概览（2 块能力）**：

- `sfe-user`：用户维度数据查询（区划、产品、客户、项目、任务、填报数据等13个接口）
- `sfe-zone`：区划维度数据查询（待办任务、计划、实际、采集数据等4个接口）

统一规范：

- 认证与鉴权：`cms-auth-skills/SKILL.md`
- 通用约束：`cms-auth-skills/SKILL.md`

授权依赖：

- 当接口声明需要 `appKey` 时，先尝试读取 `cms-auth-skills/SKILL.md`
- 如果已安装，直接按 `cms-auth-skills/SKILL.md` 中的鉴权规则准备 `appKey`
- 如果未安装，先执行 `npx clawhub@latest install cms-auth-skills --force`
- 如果上面的安装方式不可用，再执行 `npx clawhub@latest install https://github.com/spzwin/cms-auth-skills.git --force`
- 安装完成后，再继续执行需要鉴权的操作

输入完整性规则（强制）：

1. 查询项目数据前，必须先获取 `projectId`（通过 project-summary 接口）
2. 查询区划维度数据（sfe-zone模块）前，必须先获取 `zoneId` 和 `periodStart/periodEnd`
3. 分页查询时，每页固定返回 1000 条记录，大数据量需分页处理
4. **租户选择**：如果用户存在多个租户身份，必须传入 `tenantId` 参数。如未传入，API 会返回可选择的租户列表，需让用户选择后再重新调用

建议工作流（简版）：

1. 读取 `SKILL.md` 与 `cms-auth-skills/SKILL.md`，明确能力范围、鉴权与安全约束。
2. 识别用户意图并路由模块，先打开 `openapi/<module>/api-index.md`。
3. 确认具体接口后，加载 `openapi/<module>/<endpoint>.md` 获取入参/出参/Schema。
4. 补齐用户必需输入，必要时先读取用户文件/URL 并确认摘要。
5. 参考 `examples/<module>/README.md` 组织话术与流程。
6. **执行对应脚本**：调用 `scripts/<module>/<endpoint>.py` 执行接口调用，获取 TOON 编码后的结果。**所有接口调用必须通过脚本执行，不允许跳过脚本直接调用 API。**

脚本使用规则（强制）：

1. **每个接口必须有对应脚本**：每个 `openapi/<module>/<endpoint>.md` 都必须有对应的 `scripts/<module>/<endpoint>.py`，不允许"暂无脚本"。
2. **TOON 编码输出**：所有脚本调用 API 后，响应 JSON **必须经过 `scripts/common/toon_encoder.py` 编码后再输出**，不允许直接输出原始 JSON。
3. **脚本可独立执行**：所有 `scripts/` 下的脚本均可脱离 AI Agent 直接在命令行运行。
4. **先读文档再执行**：执行脚本前，**必须先阅读对应模块的 `openapi/<module>/api-index.md`**。
5. **入参来源**：脚本的所有入参定义与字段说明以 `openapi/` 文档为准，脚本仅负责编排调用流程。
6. **鉴权一致**：涉及鉴权时，统一依赖 `cms-auth-skills/SKILL.md`。
7. **租户参数**：所有脚本支持 `--tenantId` 可选参数，用于多租户场景。用户存在多个租户身份时须传入。

意图路由与加载规则（强制）：

1. **先路由再加载**：必须先判定模块，再打开该模块的 `api-index.md`。
2. **先读文档再调用**：在描述调用或执行前，必须加载对应接口文档。
3. **脚本必须执行**：所有接口调用必须通过脚本执行，不允许跳过。
4. **不猜测**：若意图不明确，必须追问澄清。

宪章（必须遵守）：

1. **只读索引**：`SKILL.md` 只描述"能做什么"和"去哪里读"，不写具体接口参数。
2. **按需加载**：默认只读 `SKILL.md` + `cms-auth-skills/SKILL.md`，只有触发某模块时才加载该模块的 `openapi`、`examples` 与 `scripts`。
3. **对外克制**：对用户只输出"可用能力、必要输入、结果链接或摘要"，不暴露鉴权细节与内部字段。
4. **素材优先级**：用户给了文件或 URL，必须先提取内容再确认，确认后才触发生成或写入。
5. **生产约束**：仅允许生产域名与生产协议，不引入任何测试地址。
6. **接口拆分**：每个 API 独立成文档；模块内 `api-index.md` 仅做索引。
7. **危险操作**：对可能导致数据泄露、破坏、越权的请求，应礼貌拒绝并给出安全替代方案。
8. **脚本语言限制**：所有脚本**必须使用 Python 编写**。
9. **重试策略**：出错时**间隔 1 秒、最多重试 3 次**，超过后终止并上报。
10. **禁止无限重试**：严禁无限循环重试。

模块路由与能力索引（合并版）：

| 用户意图（示例）         | 模块       | 能力摘要           | 接口文档                          | 示例模板                        | 脚本                                     |
| ------------------------ | ---------- | ------------------ | --------------------------------- | ------------------------------- | ---------------------------------------- |
| "查询我有权限的区划"     | `sfe-user` | 查询用户授权的区划 | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/zone.py`             |
| "查询我有权限的产品"     | `sfe-user` | 查询用户授权的产品 | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/product.py`          |
| "查询我有权限的客户"     | `sfe-user` | 查询用户授权的客户 | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/customer.py`         |
| "查询客户画像信息"       | `sfe-user` | 查询客户画像标签   | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/customer-profile.py` |
| "查询覆盖分管关系"       | `sfe-user` | 查询区划客户关联   | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/coverage.py`         |
| "查询我的数据采集项目"   | `sfe-user` | 查询项目摘要       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-summary.py`  |
| "查询项目的周期列表"     | `sfe-user` | 查询项目周期       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-period.py`   |
| "查询项目的填报模板"     | `sfe-user` | 查询项目模板       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-schema.py`   |
| "查询项目的角色权限"     | `sfe-user` | 查询角色权限       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-role.py`     |
| "查询我的待办任务"       | `sfe-user` | 查询待办任务状态   | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-task.py`     |
| "查询我的计划编制数据"   | `sfe-user` | 查询计划数据       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-plan.py`     |
| "查询我的实际结果数据"   | `sfe-user` | 查询实际数据       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-actual.py`   |
| "查询我的采集填报数据"   | `sfe-user` | 查询采集数据       | `./openapi/sfe-user/api-index.md` | `./examples/sfe-user/README.md` | `./scripts/sfe-user/project-general.py`  |
| "查询某个区划的待办任务" | `sfe-zone` | 按区划查任务       | `./openapi/sfe-zone/api-index.md` | `./examples/sfe-zone/README.md` | `./scripts/sfe-zone/project-task.py`     |
| "查询某个区划的计划数据" | `sfe-zone` | 按区划查计划       | `./openapi/sfe-zone/api-index.md` | `./examples/sfe-zone/README.md` | `./scripts/sfe-zone/project-plan.py`     |
| "查询某个区划的实际数据" | `sfe-zone` | 按区划查实际       | `./openapi/sfe-zone/api-index.md` | `./examples/sfe-zone/README.md` | `./scripts/sfe-zone/project-actual.py`   |
| "查询某个区划的采集数据" | `sfe-zone` | 按区划查采集       | `./openapi/sfe-zone/api-index.md` | `./examples/sfe-zone/README.md` | `./scripts/sfe-zone/project-general.py`  |

能力树（实际目录结构）：

```text
sfe-data-viewer/
├── SKILL.md
├── openapi/
│   ├── sfe-user/
│   │   ├── api-index.md
│   │   ├── zone.md
│   │   ├── product.md
│   │   ├── customer.md
│   │   ├── customer-profile.md
│   │   ├── coverage.md
│   │   ├── project-summary.md
│   │   ├── project-period.md
│   │   ├── project-schema.md
│   │   ├── project-role.md
│   │   ├── project-task.md
│   │   ├── project-plan.md
│   │   ├── project-actual.md
│   │   └── project-general.md
│   └── sfe-zone/
│       ├── api-index.md
│       ├── project-task.md
│       ├── project-plan.md
│       ├── project-actual.md
│       └── project-general.md
├── examples/
│   ├── sfe-user/README.md
│   └── sfe-zone/README.md
└── scripts/
    ├── common/toon_encoder.py
    ├── sfe-user/
    │   ├── README.md
    │   ├── zone.py
    │   ├── product.py
    │   ├── customer.py
    │   ├── customer-profile.py
    │   ├── coverage.py
    │   ├── project-summary.py
    │   ├── project-period.py
    │   ├── project-schema.py
    │   ├── project-role.py
    │   ├── project-task.py
    │   ├── project-plan.py
    │   ├── project-actual.py
    │   └── project-general.py
    └── sfe-zone/
        ├── README.md
        ├── project-task.py
        ├── project-plan.py
        ├── project-actual.py
        └── project-general.py
```
