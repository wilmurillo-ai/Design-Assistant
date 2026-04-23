# WordPal · 脚本契约

所有脚本成功时统一输出：

```json
{
  "meta": {
    "script": "<script-name>",
    "schema_version": "2026-03-15",
    "generated_at": "2026-03-15T00:00:00.000Z"
  },
  "data": {}
}
```

所有脚本失败时统一输出到 `stderr`：

```json
{
  "error": {
    "code": "<ERROR_CODE>",
    "message": "<human-readable message>"
  }
}
```

退出码：
- `0`：成功
- `2`：参数或输入错误
- `3`：业务规则错误
- `4`：运行时或存储错误

---

## profile.js

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `exists` | boolean | 用户画像文件是否已存在 |
| `created` | boolean | 仅 `set` 时返回；本次是否新建了画像文件 |
| `updated_fields` | string[] | 仅 `set` 时返回；本次实际更新的字段（snake_case） |
| `profile.created` | string \| null | 创建日期 |
| `profile.learning_goal` | string | CET4/CET6/POSTGRAD/IELTS/TOEFL/GRE/DAILY |
| `profile.push_times` | string[] | 推送时间列表（HH:MM） |
| `profile.report_style` | string | MIXED/EXAM/LIFE |
| `profile.difficulty_level` | string | I/II/III/IV/V |
| `profile.daily_target` | number | 每日目标词量 |

---

## push-plan.js

`data.registrations`（数组）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `index` | number | 时间点顺序（0-based） |
| `time` | string | 推送时间（HH:MM） |
| `kind` | string | `learn` \| `review` |
| `title` | string | 用户可读标题 |
| `description` | string | 宿主注册用固定描述 |

---

## select-review.js

`data.items`（数组，按优先级排序）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `word` | string | 单词 |
| `status` | number (0-8) | 当前状态 |
| `first_learned` | string (YYYY-MM-DD) | 首次学习日期 |
| `last_reviewed` | string (YYYY-MM-DD) | 上次复习日期 |
| `next_review` | string (YYYY-MM-DD) | 下次复习日期 |
| `srs` | object \| null | SRS 参数（仅 `--diagnostics`） |
| `srs.due` | string \| null | FSRS 到期日 |
| `srs.stability` | number \| null | 稳定性 |
| `srs.difficulty` | number \| null | 难度 |
| `srs.reps` | number \| null | 复习次数 |
| `srs.lapses` | number \| null | 遗忘次数 |
| `srs.state` | string \| null | new/learning/review/relearning |
| `diagnostics` | object \| null | 诊断字段（仅 `--diagnostics`） |
| `diagnostics.has_srs` | boolean | 是否有 SRS 数据 |
| `diagnostics.srs_due_matches_next_review` | boolean | srs.due 与 next_review 是否一致 |
| `diagnostics.overdue_days` | number \| null | 逾期天数 |
| `diagnostics.estimated_retrievability` | number \| null | 估算记忆保持率 |

---

## session-context.js

### 公共字段（所有 mode）

| 字段 | 类型 | 说明 |
|------|------|------|
| `data.profile_exists` | boolean | 是否存在可用用户画像；`false` 时应引导至 onboarding，不继续执行流程 |

`data.profile`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `learning_goal` | string | CET4/CET6/POSTGRAD/IELTS/TOEFL/GRE/DAILY |
| `report_style` | string | MIXED/EXAM/LIFE |
| `difficulty_level` | string | I/II/III/IV/V |
| `daily_target` | number | 每日目标词量 |

`data.progress`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `today_reviewed_count` | number | 今日已复习去重词数 |
| `active_count` | number | status 0-7 词数 |
| `mastered_count` | number | status=8 词数 |
| `pending_count` | number | pending 新词数 |

`data.memory_digest`（数组）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string (YYYY-MM-DD) | 日期 |
| `points` | string[] | 当日记忆要点（最多 3 条） |

### mode=learn 额外字段

`data.learn.queue_counts`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `daily_target` | number | 每日目标 |
| `queue_total` | number | 本轮队列总量 |
| `pending_total` | number | pending 词总量 |
| `due_total` | number | 到期词总量 |
| `pending_used` | number | 队列中 pending 词量 |
| `due_used` | number | 队列中到期词量 |
| `need_new_words` | number | 还需生成的新词数（≤0 表示已达标） |

`data.learn.queue_preview`（数组）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `item_type` | string | pending \| due |
| `word` | string | 单词 |
| `status` | number \| null | 当前状态（pending 为 null） |
| `first_learned` | string \| null | 首次学习日期 |
| `last_reviewed` | string | 上次复习日期 |
| `next_review` | string \| null | 下次复习日期 |

### mode=review 额外字段

`data.review`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `due_count` | number | 到期词总数 |
| `first_due_date` | string \| null | 最早到期日 |
| `due_candidates` | array | 到期词列表（word/status/last_reviewed/next_review，最多 30 条） |

### mode=report

- 仅返回公共字段：`profile / progress / memory_digest`
- 不返回 `learn / review` 分支

---

## question-plan.js

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `question_type` | string | `N1..N7/R1..R11` |
| `question_type_name` | string | 面向用户展示的题型名称 |
| `question_type_description` | string | 面向用户展示的题型说明 |
| `allowed_types` | string[] | 本次可选题型池 |
| `selection_reason` | string | 题型池来源说明 |
| `used_fallback` | boolean | 是否使用相邻风险等级回退 |
| `constraints.group` | string | `learn` \| `review` |
| `constraints.prompt_style` | string | 题面生成风格 |
| `constraints.answer_expectation` | string | 期待的用户作答形式 |
| `constraints.reveal_word_card` | boolean \| undefined | 是否要先展示词条信息 |
| `constraints.word_card_fields` | string[] \| undefined | 若展示词条，必须包含的中文展示字段名（如“单词/音标/词性/中文释义”） |
| `constraints.notes` | string[] | 生成题面与反馈时必须遵守的约束 |

`--compact` 时仅返回：

| 字段 | 类型 | 说明 |
|------|------|------|
| `question_type` | string | `N1..N7/R1..R11` |
| `question_type_name` | string | 面向用户展示的题型名称 |
| `constraints.group` | string | `learn` \| `review` |
| `constraints.reveal_word_card` | boolean | 是否需要先展示词卡 |
| `constraints.word_card_fields` | string[] \| null | 需展示的词卡字段；无则为 null |

---

## next-question.js

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `word` | string | 当前准备出题的单词 |
| `item_type` | string | pending \| due |
| `status` | number \| null | `due` 时为当前状态；`pending` 为 null |
| `stage` | object \| null | 仅 `--validate` 时返回，结构同 `stage-word.js` |
| `question.question_type` | string | `N1..N7/R1..R11` |
| `question.question_type_name` | string | 面向用户展示的题型名称 |
| `question.constraints.group` | string | `learn` \| `review` |
| `question.constraints.reveal_word_card` | boolean | 是否需要先展示词卡 |
| `question.constraints.word_card_fields` | string[] \| null | 词卡字段名；无则为 null |

校验失败时返回：

| 错误码 | details.reason |
|------|------|
| `WORD_REJECTED` | `duplicate_in_input / unsafe_word / exists_mastered / exists_active / exists_pending` |

---

## report-stats.js

`data.warnings`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `count` | number | 数据异常数 |
| `samples` | string[] | 异常说明（最多 5 条） |

`data.totals`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_words` | number | 词库总量 |
| `active_words` | number | status 0-7 词数 |
| `mastered_words` | number | status=8 词数 |
| `pending_words` | number | pending 词数 |
| `consolidating_words` | number | status 4-7 词数 |
| `mastered_ratio` | number (0-1) | 掌握率 |
| `consolidating_ratio` | number (0-1) | 巩固率 |
| `status_counts` | object | 各 status (0-8) 的词数 |
| `learned_counts.status_4_to_7` | number | 已学会 (4-7) 词数 |
| `learned_counts.status_0_to_3` | number | 学习中 (0-3) 词数 |

`data.due`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `today_due` | number | 今日到期词数 |
| `next_days_due_total` | number | 未来 N 天到期总数 |
| `next_days_due_by_date` | array | 逐日到期数 ({date, count}) |
| `earliest_due_date` | string \| null | 最早到期日 |
| `today` | string (YYYY-MM-DD) | 今天日期 |

`data.trend_7d`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `days` | number | 统计天数 |
| `new_words_by_date` | array | 逐日新增词 ({date, count}) |
| `reviewed_words_by_date` | array | 逐日复习词 ({date, count}) |
| `total_new_words` | number | 期间新增总数 |
| `total_reviewed_words` | number | 期间复习总数 |

`data.risk_words`（数组）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `word` | string | 单词 |
| `status` | number | 当前状态 |
| `overdue_days` | number | 逾期天数 |
| `estimated_retrievability` | number \| null | 估算保持率 |
| `lapses` | number | 遗忘次数 |
| `reps` | number | 复习次数 |
| `stability` | number \| null | FSRS 稳定性 |
| `difficulty` | number \| null | FSRS 难度 |
| `risk_score` | number | 风险评分 |
| `risk_level` | string | low/medium/high |

`data.next_action`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `kind` | string | `review_now` \| `learn_now` \| `light_encouragement` |
| `reason` | string | 命中该动作的固定规则说明 |

---

## session-summary.js

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_words` | number | 本轮去重后的单词数 |
| `event_counts.correct` | number | 本轮 `correct` 次数 |
| `event_counts.wrong` | number | 本轮 `wrong` 次数 |
| `event_counts.remembered_after_hint` | number | 本轮 `remembered_after_hint` 次数 |
| `event_counts.skip` | number | 本轮 `skip` 次数 |
| `event_counts.unreviewed` | number | 本轮 `unreviewed` 次数 |
| `new_words_count` | number | `first_learned=today` 的词数 |
| `review_words_count` | number | 非当日新学词数 |
| `upgraded_words` | array | 本轮升到 `status>=4` 且 `<8` 的词 |
| `upgraded_words[].word` | string | 单词 |
| `upgraded_words[].status` | number | 当前状态 |
| `upgraded_words[].status_emoji` | string | 当前状态表情 |
| `mastered_words` | string[] | 本轮升为 `status=8` 的词 |
| `risk_words` | array | 本轮结束后处于 `status 0/1` 的风险词 |
| `risk_words[].word` | string | 单词 |
| `risk_words[].status` | number | 当前状态 |
| `risk_words[].status_emoji` | string | 当前状态表情 |
| `next_review.earliest` | string \| null | 本轮涉及词条中最早的下次复习日 |
| `next_review.latest` | string \| null | 本轮涉及词条中最晚的下次复习日 |
| `next_review.scheduled_count` | number | 本轮仍有下次复习安排的词数 |
| `remaining_due_count` | number \| null | `mode=review` 时当天剩余到期词数 |
| `words` | array | 本轮逐词结果快照 |
| `words[].word` | string | 单词 |
| `words[].event` | string | 本次事件 |
| `words[].previous_status` | number \| null | 本次写回前状态 |
| `words[].next_status` | number | 本次写回后的状态 |
| `words[].current_status` | number | 当前最新状态 |
| `words[].status_emoji` | string | 当前状态表情 |
| `words[].first_learned` | string | 首次学习日期 |
| `words[].last_reviewed` | string | 最近复习日期 |
| `words[].next_review` | string \| null | 下次复习日期 |
| `words[].mastered_date` | string \| null | 掌握日期 |

---

## stage-word.js

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `result` | string | staged \| idempotent |
| `word` | string | 暂存的单词 |
| `op_id` | string | 操作 ID（SHA256 前 24 位） |
| `created_at` | string (ISO 8601) | 创建时间 |

---

## validate-new-words.js

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `input_count` | number | 输入词数 |
| `available_count` | number | 可用词数 |
| `rejected_count` | number | 被拒词数 |
| `available` | string[] | 可用词列表 |
| `rejected` | array | 被拒词列表 |
| `rejected[].word` | string | 被拒单词 |
| `rejected[].reason` | string | duplicate_in_input / unsafe_word / exists_mastered / exists_active / exists_pending |

---

## updater.js

说明：调用时以 `event` 作为主要输入，脚本内部负责计算新的 `status`；`--status` 仅保留为 legacy 校验参数。

`data`：

| 字段 | 类型 | 说明 |
|------|------|------|
| `result` | string | success / archived / idempotent |
| `word` | string | 单词 |
| `status` | number (0-8) | 新状态 |
| `status_emoji` | string | 状态表情 |
| `today_count` | number | 今日截至本题已复习的去重词数（含本题） |
| `previous_status` | number \| null | 原状态 |
| `first_learned` | string (YYYY-MM-DD) | 首次学习日期 |
| `last_reviewed` | string (YYYY-MM-DD) | 本次复习日期 |
| `mastered_date` | string \| null | 掌握日期（status=8 时有值） |
| `next_review` | string \| null | 下次复习日期（status=8 时为 null） |
| `review_event` | string | correct / wrong / remembered_after_hint / skip / unreviewed |
| `op_id` | string | 操作 ID |
| `retention` | number | 目标保持率（默认 0.9） |
| `srs` | object \| null | SRS 参数 |
| `srs.due` | string \| null | FSRS 到期日 |
| `srs.stability` | number \| null | 稳定性 |
| `srs.difficulty` | number \| null | 难度 |
| `srs.reps` | number \| null | 复习次数 |
| `srs.lapses` | number \| null | 遗忘次数 |
| `srs.state` | string \| null | new/learning/review/relearning |
| `created_at` | string \| null | 记录创建时间 |
| `updated_at` | string | 记录更新时间 |

---

## submit-answer.js

`data`：面向热路径的轻量返回，仅保留答题后继续对话需要的字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `result` | string | success / archived / idempotent |
| `word` | string | 单词 |
| `status` | number (0-8) | 新状态 |
| `status_emoji` | string | 状态表情 |
| `today_count` | number | 今日截至本题已复习的去重词数（含本题） |
| `previous_status` | number \| null | 原状态 |
| `next_review` | string \| null | 下次复习日期（status=8 时为 null） |
| `review_event` | string | correct / wrong / remembered_after_hint / skip |
| `op_id` | string | 操作 ID |
| `remaining_in_queue` | number \| null | 调用方传入的剩余队列数；未传则为 null |
