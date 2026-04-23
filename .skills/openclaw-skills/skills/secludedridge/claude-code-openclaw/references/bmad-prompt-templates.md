# BMad V6 Prompt 模板（可直接复制）

> 用法建议：**一个 workflow 一个 prompt 文件 / 一次 run。**
> 不要把很多 `/bmad-*` 串在一个 prompt 里。

---

## 模板 0：`/bmad-help` 路由模板

适合：
- 不确定当前阶段
- 不确定下一步
- workflow 结束后确认后续 required step

```text
/bmad-help

项目状态说明：
- 当前项目：<project>
- 已知产物：<列出已有 PRD/Architecture/Epics/Story/Sprint Status>
- 当前诉求：<一句话>

请基于当前安装的 BMad 命令和已有产物，回答：
1. 当前所处阶段
2. 下一条 required workflow
3. 可选 workflow 有哪些
4. 应该用哪条准确命令继续

输出语言使用中文。
```

---

## 模板 1：Quick Flow - Quick Spec

适合：
- bugfix
- 小功能
- 既有模式内的小范围改动

```text
/bmad-bmm-quick-spec

目标：<一句话描述目标>

约束：
- 技术栈：<stack>
- 禁止改动：<path/module>
- 兼容性要求：<runtime/browser>
- brownfield 规则：如果存在 project-context.md，请先读取

交互策略：
- 默认选择 Continue / C
- 不进入 Advanced Elicitation / Party Mode
- 不要凭空扩展范围

验收标准：
1. <验收1>
2. <验收2>

完成标准：
- 产出 implementation-ready tech spec
- 明确输出生成文件路径
- 明确给出下一条建议 workflow
```

---

## 模板 2：Quick Flow - Quick Dev

适合：
- 已有 quick spec，要直接实施

```text
/bmad-bmm-quick-dev

请基于现有 quick spec 执行实现。

执行要求：
- 如果存在 project-context.md，先读取并严格遵守
- 按 spec 中的任务顺序执行
- 不要扩展 spec 之外的范围
- 默认继续，不进入 Party Mode

验证要求：
- 单元测试：<test command>
- 质量检查：<lint command>
- 构建验证：<build command>

交付输出：
- 修改文件列表
- 关键实现说明
- 验证结果
- 风险与后续建议
```

---

## 模板 3：Full Method - Create PRD

```text
/bmad-bmm-create-prd

请基于以下信息生成正式 PRD：
- 产品背景：<背景>
- 目标用户：<用户画像>
- 核心问题：<痛点>
- 范围边界：
  - In Scope: <...>
  - Out of Scope: <...>
- 成功指标：
  - <指标1>
  - <指标2>

交互策略：
- 默认 Continue / C
- 不进入 A / P
- 不要凭空扩展未确认的业务范围

完成标准：
- 产物写入 `_bmad-output/planning-artifacts/prd.md` 或当前安装定义的标准 PRD 输出位置
- workflow 完成后明确输出：generated files / workflow status / next required workflow
- 输出语言使用中文
```

---

## 模板 4：Full Method - Create UX

适合：UI 是主要交付物时。

```text
/bmad-bmm-create-ux-design

请基于当前 PRD 生成 UX 设计文档。

重点：
- 核心用户旅程
- 关键交互路径
- 信息架构
- 组件 / 页面层级
- 关键状态与异常状态

交互策略：
- 默认 Continue / C
- 不进入 A / P

完成标准：
- 产物落到 planning-artifacts 的标准 UX 输出路径
- 输出 generated files / workflow status / next required workflow
- 输出语言使用中文
```

---

## 模板 5：Full Method - Create Architecture

```text
/bmad-bmm-create-architecture

请基于以下输入生成正式架构文档：
- _bmad-output/planning-artifacts/prd.md
- docs/PRD_input.md
- （如存在）UX / project-context / brownfield docs

要求：
1. 输出语言使用中文
2. 不要凭空扩展未确认的业务范围
3. 明确：
   - 模块边界
   - 数据流
   - 核心服务拆分
   - 安全与权限隔离
   - 测试与可观测性边界
   - 项目目录结构
4. 遇到交互菜单默认选择 Continue / C
5. 不进入 Advanced Elicitation / Party Mode

完成标准：
- 产物落到 `_bmad-output/planning-artifacts/architecture.md`
- 输出 generated files / workflow status / next required workflow
```

---

## 模板 6：Full Method - Create Epics and Stories

```text
/bmad-bmm-create-epics-and-stories

请基于以下已完成产物继续：
- _bmad-output/planning-artifacts/prd.md
- _bmad-output/planning-artifacts/architecture.md
- （如存在）UX / project-context / docs/*

执行要求：
1. 输出语言使用中文
2. 生成标准产物 `_bmad-output/planning-artifacts/epics-and-stories.md`（或当前安装定义的标准输出位置）
3. 默认替用户完成交互项：遇到 Continue / C 或 A-P-C 菜单默认选 C
4. 不进入 A / P
5. 不凭空扩展业务范围
6. story 拆分要：
   - 可实施
   - 可验证
   - 边界清晰
   - 适合多个 AI agents 一致开发

完成后请明确输出：
- generated files
- workflow status
- next required workflow
```

---

## 模板 7：Implementation Readiness

```text
/bmad-bmm-check-implementation-readiness

请检查以下产物是否已经对齐并可进入实施：
- PRD
- Architecture
- Epics and Stories
- （如存在）UX

输出要求：
- 给出 PASS / CONCERNS / FAIL
- 明确阻塞项
- 明确缺失产物
- 明确是否可以进入 sprint planning
- 输出语言使用中文
```

---

## 模板 8：Sprint Planning

```text
/bmad-bmm-sprint-planning

请基于当前 epics/stories 生成或更新 sprint 计划。

要求：
- 输出语言使用中文
- 默认 Continue / C
- 不进入 A / P
- 目标产物：`_bmad-output/implementation-artifacts/sprint-status.yaml`
- 明确当前 sprint 中的 story 顺序、依赖、状态

完成后输出：
- generated files
- workflow status
- next required workflow
```

---

## 模板 9：Create Story

```text
/bmad-bmm-create-story

请根据当前 sprint status 生成下一条可执行 story。

要求：
- story 必须包含：背景、目标、任务清单、验收标准、测试要求、文件提示
- 如果存在 project-context.md，先读取
- 默认 Continue / C
- 不进入 A / P
- 输出语言使用中文

完成后输出：
- story 文件路径
- 当前 workflow status
- 下一条 required workflow
```

---

## 模板 10：Dev Story

```text
/bmad-bmm-dev-story

请实现当前 sprint 中下一条 story（或指定 story 文件）。

执行要求：
- 严格按 story 文件任务顺序执行
- 不要跳过测试
- 每个任务完成后再更新 story 中的任务状态
- 真实运行以下验证：
  - <test command>
  - <lint command>
  - <build command>
- 如果存在 project-context.md，先读取

交付输出：
- 修改文件列表
- story 更新情况
- 验证结果
- 风险与下一步建议
```

---

## 模板 11：Code Review

```text
/bmad-bmm-code-review

请对当前 story 的代码改动执行审查。

要求：
- 重点检查：正确性、边界情况、回归风险、架构一致性、测试覆盖
- 输出语言使用中文
- 如果存在 architecture / epics / story / project-context，请全部用于审查上下文

输出格式：
- 必修复项
- 建议项
- 风险等级
- 是否建议返回 dev-story 修复
```

---

## 模板 12：QA Automate

```text
/bmad-bmm-qa-automate

请为当前已实现功能补充 API / E2E 自动化测试。

要求：
- 优先复用项目现有测试框架
- 不引入无关测试基础设施
- 覆盖 happy path + 核心 edge cases
- 测试必须真实可运行

输出：
- 新增/修改测试文件
- 执行结果
- 覆盖范围说明
```

---

## 模板 13：Brownfield - Document Project

```text
/bmad-bmm-document-project

请扫描当前存量项目，生成适合人类与 AI 后续协作使用的项目文档。

重点：
- 技术栈
- 目录结构
- 构建与测试入口
- 核心约束
- 重要模块边界
- 已存在实现模式

输出语言使用中文。
```

---

## 模板 14：Brownfield - Generate Project Context

```text
/bmad-bmm-generate-project-context

请扫描当前仓库并生成 lean 的 project-context.md，重点覆盖：
- 技术栈与版本
- 代码组织约定
- 测试策略
- 框架特定实现规则
- AI agents 必须遵守的实现边界

输出语言使用中文。
```

---

## 运行命令模板

```bash
./scripts/claude_code_run.py \
  --mode auto \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  --prompt-file ./bmad-run.txt
```

---

## 每轮最少验收清单

每轮结束至少检查：
1. 这轮到底执行了哪个 workflow
2. 目标产物文件是否真的存在
3. frontmatter / 状态是否更新
4. 验证命令与结果（若本轮涉及实现）
5. 下一条 required workflow 是什么
