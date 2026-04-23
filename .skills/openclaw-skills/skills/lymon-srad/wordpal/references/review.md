# WordPal · Review 流程

## Session 状态展示

进入复习前，展示状态摘要：

```
📘 WordPal · 复习模式
🎯 目标：<learning_goal>
📅 今日待复习：<due_count> 词
```

数据来自 `session-context.js --mode review` 返回的 `data.profile` 和 `data.review`。

## 执行顺序

1. 若 `data.review.due_count = 0`，结束本轮。
2. 每题出题前调用 `next-question.js --mode review --item-type due --word "<word>" --status <0-7> [--last-type <Rk>]`
3. 读取 `data.question` 后，按下方 A → B → C 流程出题。题面规则见"题型速查"。
4. 每题反馈后记录题型编号，下一题传入 `--last-type`。
5. 全部完成后，收集所有 `op_id`，调用 `session-summary.js --mode review --op-ids "<op1>,<op2>,..."`.

## 题型速查

- **R1 用法判断**：给含目标词的句子，判断用法是否正确并简述原因
- **R2 固定搭配选择**：给多个搭配，选最自然的目标词用法
- **R3 英文填空**：给英文上下文，把目标词填进空格
- **R4 反向语义猜词**：根据同义/反义/概念线索猜目标词
- **R5 递进线索猜词**：逐步追加线索，让用户猜目标词
- **R6 用法纠错**：指出句子里目标词的误用并改正
- **R7 词汇升级替换**：把基础表达替换成更准确的目标词表达
- **R8 场景精准选词**：根据口语场景回答最精确的目标词
- **R9 场景造句复现**：根据场景提示，用目标词写 1 句原创英文句子
- **R10 中文句子回忆单词**：根据中文句子线索，只回答目标词
- **R11 中文释义拼写**：根据中文释义，完整拼出目标词

## 单题输出规范

每道题分三个阶段，顺序固定：

### 阶段 A：出题

```
【<question_type_name>】

[词卡] （仅 reveal_word_card=true）
  单词：xxx | 音标：/xxx/ | 词性：xxx | 中文释义：xxx

[题面] 严格遵守 constraints
```

信息保护：reveal_word_card=false 时禁止泄露中文释义/词性/音标；选择题正确答案位置随机；不给暗示性线索。

### 阶段 B：答题判定

- **B-1 正确** → event=`correct`，调用 `submit-answer.js`，进入 C
- **B-2 跳过**（"跳过/会了/斩词"）→ event=`skip`，调用 `submit-answer.js`，进入 C
- **B-3 答错** → 子流程：
  1. 展示正确答案+解析（1-2 句）+ 补充词卡（若阶段 A 未展示）。不调用 submit-answer.js
  2. 引导确认："记住了吗？"
  3. 判定：用户主动复述/造句/说"懂了" → `remembered_after_hint`；仅被动确认"嗯/好"或说"记不住" → `wrong`
  4. 调用 `submit-answer.js`，进入 C

### 阶段 C：答后反馈

submit-answer.js 返回后展示：

```
[结果] ✅正确 / ❌答错 / 💡提示后记住 / ⏭️已跳过
[解析] 仅 correct 时可补充扩展用法（可选，1 句）
[词卡] 仅 correct 且阶段 A 未展示时补充
[状态] <status_emoji>（status N）| 下次复习：<next_review>
[进度] <已完成数> / <总数>
```
