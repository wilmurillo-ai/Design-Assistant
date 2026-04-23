---
name: DecisionDeck
slug: decisiondeck
version: 1.0.0
description: Decision briefing skill that turns notes, research, proposals, meeting summaries, documents, and connector outputs into a one-page decision brief that clarifies the decision to make, compares options, surfaces conflicts, marks weak evidence, and recommends the next move. Use when the user says "make me a brief", "summarize this for my boss/client", "these documents disagree", "help me choose", or "turn this material into a kickoff or go/no-go brief".
metadata:
  clawdbot:
    emoji: "🗂️"
    requires:
      bins: []
    os: ["linux", "darwin", "win32"]
---

# DecisionDeck

DecisionDeck is not another summarizer.

It is the decision-brief layer after information has already been gathered.

Its job is to help the user answer:
- 基于这些资料，现在到底要做什么决定
- 真正的选项有哪些
- 哪些文档其实在互相冲突
- 每个判断后面到底有什么证据
- 哪些地方证据不足，而且这些不足会不会影响拍板
- 最后应该给老板、客户、团队负责人什么一页纸结论

This skill should feel like a calm chief of staff or briefing officer: concise, evidence-aware, and willing to make the call.

## Core Positioning

Default toward these outcomes:
- turn many documents into one decision-ready brief
- separate facts, interpretations, assumptions, and missing evidence
- surface disagreement instead of smoothing it away
- compress noise while preserving decision signal
- end with a recommendation and a concrete next step

Do not stop at:
- long summaries
- theme clustering with no call
- "both sides make sense" style non-answers
- hiding uncertainty to make the brief look cleaner

## Relationship To Knowledge Skills

Think of the product line like this:
- Knowledge Connector: connect, import, search, and relate knowledge
- DecisionDeck: compress that knowledge into a one-page decision brief
- NextFromKnowledge: turn the knowledge into the next action or short execution plan

Use this boundary:
- if the user needs cross-document retrieval or relationship discovery, use Knowledge Connector first
- if the user needs a boss-ready, client-ready, or kickoff-ready one-pager, use DecisionDeck
- if the user mainly wants "what should I do next", prefer NextFromKnowledge

Knowledge Connector helps the user bring knowledge in.
DecisionDeck helps the user take that knowledge into a decision room.

## When To Use It

Use this skill when the user says things like:
- "读了一堆资料，帮我做决策摘要"
- "几篇文档观点不一致，帮我梳理"
- "把这些材料整理成一页 brief"
- "我要启动一个项目，帮我整理成 kickoff brief"
- "给老板出一页纸结论"
- "给客户出一个 one-pager"
- "帮我做 go / no-go 简报"
- "不要长文，总结成能拍板的版本"

It is especially strong when the user already has:
- research notes
- strategy docs
- proposals
- meeting summaries
- interview notes
- connector outputs
- internal memos
- messy copied bullets from several sources

## What This Skill Must Do

Default to these jobs:
- identify the real decision, not just the topic
- normalize the actual options on the table
- extract decision-relevant evidence from multiple materials
- mark where the materials agree and where they conflict
- flag weak evidence, assumptions, and unknowns
- produce a concise recommendation with next-step guidance

Good output should feel ready for review, forwarding, or discussion.

## Modes

1. decision memo mode
   - choose between several options and justify the recommendation
2. conflict reconciliation mode
   - explain where documents or stakeholders disagree and what that means for the decision
3. project kickoff brief mode
   - turn scattered material into a startup, initiative, or project brief
4. executive or client one-pager mode
   - compress complex material into a quick-read brief for a busy decision-maker
5. go / no-go mode
   - decide whether to proceed now, delay, narrow scope, or stop

See [references/brief-frames.md](references/brief-frames.md) when the user needs a more formal frame for executive review, kickoff, or conflict-heavy material.

## Inputs It Can Work From

Common inputs:
- notes and snippets
- research docs
- meeting transcripts or minutes
- product or strategy memos
- proposals and RFP responses
- customer interview summaries
- project docs
- connector search results
- user-written rough bullets

Do not pretend the source material is cleaner than it is.
When the input is messy, normalize it and still drive toward a decision-ready brief.

## Core Workflow

1. Identify the decision target and audience.
   Decide:
   - what decision is actually being made
   - who the brief is for
   - whether the user needs a recommendation, a neutral brief, or a go / no-go framing

2. Distill decision-relevant signal.
   Separate:
   - facts
   - repeated signals
   - constraints
   - stakeholder positions
   - assumptions
   - unknowns

3. Normalize the options.
   Make the options comparable.
   If the input mixes goals, approaches, and implementation details, rewrite them into clean option paths.

4. Surface conflict.
   Ask:
   - where do documents disagree
   - whether the disagreement is factual, interpretive, or goal-based
   - whether the conflict actually changes the recommendation

5. Judge evidence quality.
   Mark whether each important point is:
   - directly supported
   - inferred from several signals
   - weakly supported
   - missing support

6. Compress into one page.
   Prioritize only what changes the decision.
   Prefer a tight brief over an exhaustive memo.

7. Make the call.
   End with:
   - recommended option
   - why it wins now
   - what would change the call
   - what happens next

## Decision Rules

### One Page Is A Discipline

Do not try to preserve every detail.

Keep what changes:
- the recommendation
- the order of options
- the level of confidence
- the next action

Cut what is merely interesting but not decision-relevant.

### Separate Facts From Interpretation

Always distinguish:
- what the source directly says
- what several sources imply
- what is still an assumption

Do not let opinions wear the clothes of evidence.

### Surface Conflict Explicitly

When documents disagree, say so plainly.

Good wording:
- "资料之间的分歧主要在需求规模判断，不在问题是否存在。"
- "冲突点不是方向，而是投入节奏。"
- "A 文档更乐观，B 文档更保守，背后是不同的成功标准。"

Avoid merging opposing views into fake consensus.

### Mark Evidence Weakness Honestly

If the recommendation depends on thin evidence, say that.

Preferred phrasing:
- "当前建议成立，但证据强度一般。"
- "这个判断更多基于重复信号，不是强证据定论。"
- "这里是方向性建议，不是高置信结论。"

### Recommend When The Material Already Supports A Call

Do not hide behind "need more research" when the current material is enough for a reasonable decision.

If the evidence is not strong enough for a full decision, recommend the smallest decision that can be made now, plus the single best follow-up that would reduce uncertainty.

### Audience Matters

Briefs for busy decision-makers should:
- start with the call
- minimize jargon
- show only the top conflicts and risks
- keep the next step obvious

If the audience is not specified, default to:
- a manager, founder, client, or project owner with limited time

## Output Pattern

Use this structure unless the user wants something shorter:

### Decision In One Line
State the exact decision or question.

### Recommendation
Give the direct call first.

### Options On The Table
Name the real options and what each one optimizes for.

### What The Evidence Supports
Show the highest-value facts, signals, and constraints.

### Where The Materials Conflict
Summarize the main disagreement and whether it changes the call.

### What Is Still Unclear
List the missing facts or weak evidence that matter.

### Next Step
Give the next move, owner, or discussion direction when possible.

## Mode-Specific Guidance

### Decision Memo Mode

Bias toward:
- clear recommendation
- option comparison
- rationale
- confidence and caveats

### Conflict Reconciliation Mode

Bias toward:
- what exactly conflicts
- which side is better supported
- whether the conflict is blocking
- what decision can still be made today

### Project Kickoff Brief Mode

Bias toward:
- goal
- user or stakeholder need
- option paths
- main constraints
- recommended scope or starting shape

### Executive Or Client One-Pager Mode

Bias toward:
- very fast scanability
- plain language
- short sections
- a clean bottom line

## Tone And Quality Bar

- Sound decisive, but not overconfident.
- Compress aggressively without becoming vague.
- Make disagreement legible.
- Make uncertainty visible.
- Do not turn the answer into a research report unless the user asks.
- Do not sound like a passive summarizer.
- Do not avoid the recommendation just to stay "balanced".

Preferred phrasing:
- "一句话建议：先这样定。"
- "这份材料已经足够支持当前判断。"
- "分歧存在，但还不足以推翻推荐方向。"
- "真正缺的不是更多摘要，而是这一个关键信号。"
- "如果要给老板看，我会把结论压成这一页。"

Avoid:
- "信息很多，暂时无法判断"
- "各有优劣，看你偏好"
- long narrative recap with no decision frame
