# DECISIONS_GEMINI.md — cross-project.synthesis 设计决策

## 1. 核心架构：知识综合引擎

`synthesis_gemini.py` 负责将多源知识输入（Compare, Discovery, Community）转化为一套最终的知识决策。

- **共识优先**：所有 `ALIGNED` 信号被自动视为 `consensus` 并默认 `include`。这保证了多项目验证通过的最佳实践能够被继承。
- **独创识别**：`ORIGINAL` 信号被视为 `unique_knowledge`。通过简单的关键词匹配（与 `NeedProfile` 对比）来决定是 `include` 还是作为 `option` 推荐。
- **冲突检测**：
    - 针对 `CONTESTED` 和 `DIVERGENT` 信号进行分组。
    - 特别强化了 **License 冲突** 的检测逻辑。
    - 冲突类别映射到规定的 6 类：`semantic`, `scope`, `architecture`, `dependency`, `operational`, `license`。

## 2. 状态门控与安全性

根据规格要求，实现了严格的冲突门控：
- 如果检测到类别为 `license` 的冲突，模块将进入 `blocked` 状态，并返回 `E_UNRESOLVED_CONFLICT`。
- 这确保了法律合规性不会被静默忽略。

## 3. ID 稳定性与追溯性

- **Decision ID**：使用 `CON-{NNN}` 和 `UNI-{NNN}` 格式，确保在相同输入下的稳定性。
- **追溯性 (Traceability)**：每个决策的 `source_refs` 字段严格链接到原始的 `signal_id` 或 `project_id`，确保最终编译出的 Skill 每一条规则都有据可查。

## 4. 双模输出

- **JSON Canonical**：`synthesis_report.json` 作为唯一权威的机器可读结果，供下游 `skill-compiler` 使用。
- **Markdown Mirror**：`synthesis_report.md` 为镜像输出，专为人类评审设计，清晰展示共识、冲突和最终选择。

## 5. 局限与优化空间

- **冲突解决**：目前的 Mock 实现中，冲突解决逻辑较为简单（标记为 TBD）。真实场景下应利用 LLM 根据 `NeedProfile` 的倾向性自动给出 `recommended_resolution`。
- **Rationale 生成**：目前的理由较为公式化，未来可引入更自然的解释性语言，提高报告的可读性。
