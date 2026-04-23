# 规格驱动开发（SDD）流程参考

## 1) 什么时候用 SDD

适用场景：
- 需求不止一个改动点，需要“规格→计划→任务→实现”分阶段推进
- 需要沉淀规范、降低返工
- 需要多人协作或后续审计（为什么这么做）

不适用场景：
- 单文件小修、小范围 bugfix
- 一次性脚本改动且无需规格沉淀

---

## 2) Spec Kit 推荐流程

### 前置检查（每仓库至少一次）

```bash
# 在目标仓库
specify init . --ai claude

git init
git add -A
git commit -m "chore: init"
```

> 若仓库已是 git 项目，保留现有历史，跳过 `git init`。

### 执行（建议 interactive/orchestrator）

将以下内容写入 `spec-flow.txt`：

```text
/speckit.constitution 定义项目原则：质量、可维护性、安全性、可观测性
/speckit.specify <功能需求描述>
/speckit.plan 技术栈=<stack> 约束=<constraints>
/speckit.tasks
/speckit.implement
```

运行：

```bash
./scripts/claude_code_run.py \
  --mode interactive \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  --prompt-file ./spec-flow.txt
```

---

## 3) OpenSpec 推荐流程

### 初始化

```bash
npm install -g @fission-ai/openspec@latest
openspec init --tools claude
```

### 交互命令顺序

```text
/opsx:onboard
/opsx:new <change-name>
/opsx:ff
/opsx:apply
/opsx:archive
```

建议用 interactive orchestrator，避免长流程在无状态 headless 下失去结构化运行状态。

---

## 4) 输出与验收清单（必须）

每次交付至少包含：

1. 规格产物位置（spec / plan / tasks 文件）
2. 修改文件列表
3. 验证命令与结果（tests/lint/build）
4. 风险与未完成项
5. 下一步建议

---

## 5) 常见问题

### Q1: slash 流程执行到一半停住
- 先看 `latest_run_report` / `events.jsonl` / `user-update.txt`
- 若是权限问题，补充 `--allowedTools` 或切 `--permission-mode acceptEdits`

### Q2: headless 模式经常挂住
- 使用 `scripts/run_claude_task.sh`
- 不要在 OpenClaw 中直接启动裸 `claude -p` 后台任务
- slash 命令统一走 orchestrator

### Q3: 规格写了但实现偏离
- 在 prompt 明确 DoD 与验收命令
- 先 `/speckit.plan` 审核通过再 `/speckit.implement`
