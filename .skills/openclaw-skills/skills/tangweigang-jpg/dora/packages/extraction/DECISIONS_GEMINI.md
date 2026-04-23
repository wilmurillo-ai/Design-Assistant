# DECISIONS_GEMINI.md — extraction.stage15_agentic 设计决策

## 1. 核心架构：Mock Agent 循环

由于无法在测试环境中调用真实 LLM，我们实现了一个 `Stage15AgenticGemini` 类来模拟 Agent 的决策过程。

- **假说驱动**：Agent 按优先级（High > Medium > Low）依次处理 Stage 1 输出的假说。
- **工具模拟**：为每个假说模拟调用了 `search_repo`, `list_tree`, `read_artifact`, `read_file` 等工具。
- **证据绑定**：对于 High 和 Medium 优先级的假说，模拟生成 `confirmed` 状态的 Claim，并强制绑定 `file_line` 类型的证据（EvidenceRef）。Low 优先级假说模拟为 `rejected`。

## 2. 状态与 Budget 控制

实现了三层 Budget 监控：
- **硬限制**：`max_rounds` 和 `max_tool_calls`。一旦达到限制，立即停止探索，返回 `degraded` 状态并标记 `termination_reason = "budget_exhausted"`。
- **软限制**：`max_prompt_tokens`。模拟每个工具调用消耗 1000 tokens。
- **信息增益**：`stop_after_no_gain_rounds`。如果连续 N 轮没有产出新的 Claim，自动停止。

## 3. 中间产物落盘

严格遵守规格要求，生成以下 5 个文件：
1. `hypotheses.jsonl`：处理过的假说列表。
2. `exploration_log.jsonl`：完整的工具调用轨迹和观察。
3. `claim_ledger.jsonl`：产出的知识声明。
4. `evidence_index.json`：`file:line` 到 `claim_id` 的反向索引，用于快速追溯。
5. `context_digest.md`：本次探索的摘要报告。

## 4. 关键 ID 命名规范

- **Claim ID**：严格遵循 `C-{REPO_ID}-{NNN}` 格式。
- **Step ID**：使用 `S-{NNN}` 格式，在探索轨迹中唯一。

## 5. 已知局限与后续计划

- **Mock 局限性**：当前的工具返回是确定性的 Mock，无法体现真实 LLM 在不同代码库下的探索深度差异。
- **Prompt Token 计算**：目前是固定值模拟，未来应集成真实 Token 计数器。
- **并发探索**：目前是串行处理假说，未来可考虑并行化以提高性能（虽然 10 min/repo 已经很宽裕）。
