# DecisionDeck

把接进来的资料，直接变成一页能拿去做决定的简报。

`DecisionDeck` 是“决策简报官”这条产品线的第一版可发布仓库。它承接 `Knowledge Connector` 之后的下一步：不是继续接更多来源，而是把已经进来的资料压缩成一个能给老板、客户、团队负责人直接看的 decision brief。

它要解决的问题很直接：
- 读了一堆资料，结论到底是什么
- 几份文档观点打架，冲突点到底在哪
- 现在该选哪个方案
- 项目该不该启动，怎么写成一页 kickoff brief
- 给老板或客户的一页纸，应该怎么写到能直接拍板

## 适合的输入

- research notes
- strategy memo
- 会议纪要
- proposal / 方案文档
- 用户访谈摘要
- 内部对比材料
- Knowledge Connector 的搜索或图谱结果
- 用户自己整理的散乱 bullet points

## 默认输出什么

DecisionDeck 默认不是产出长摘要，而是产出一页能拿来讨论和决策的内容：
- `Decision In One Line`
- `Recommendation`
- `Options On The Table`
- `What The Evidence Supports`
- `Where The Materials Conflict`
- `What Is Still Unclear`
- `Next Step`

## 核心命令

```bash
deck brief --file notes.md
deck brief --text "..."
deck compare --file materials.md --options "方案A,方案B,方案C"
deck conflicts --file materials.md
deck kickoff --file research.md
deck gaps --file research.md
deck analyze --file research.md --json
```

这些命令分别对应：
- 默认一页式决策简报
- 显式选项比较
- 冲突梳理
- kickoff brief
- 证据缺口梳理
- 原始结构化分析结果

## 为什么它贴合 Knowledge Connector

Knowledge Connector 解决的是“把知识接进来、连起来、搜出来”。

DecisionDeck 解决的是更靠近结果的一步：
- 从多个文档提炼选项
- 找出观点冲突
- 标出证据不足的地方
- 生成一页决策简报
- 给出下一步建议

也就是说，不让 Knowledge Connector 停在“接进来”，而是把它推进到“产出可决策结果”。

## 和相邻 skill 的边界

- `Knowledge Connector`：负责导入、连接、搜索、关系理解
- `DecisionDeck`：负责一页式决策简报
- `NextFromKnowledge`：负责把已有知识变成下一步动作或短计划

如果用户要的是“给我一个能拿去开会或发老板的 one-pager”，更适合 `DecisionDeck`。

## 典型问题

- “读了一堆资料，帮我做决策摘要”
- “几篇文档观点不一致，帮我梳理”
- “我要启动一个项目，帮我整理成 brief”
- “给老板出一页纸结论”
- “给客户写一个 one-pager”
- “帮我做一个 go / no-go 简报”

## 建议安装名

```bash
clawhub install decisiondeck
```

## 仓库结构

```text
decisiondeck/
├── SKILL.md
├── README.md
├── CHANGELOG.md
├── RELEASE.md
├── clawhub.json
├── package.json
├── .gitignore
├── agents/openai.yaml
├── references/brief-frames.md
├── bin/cli.js
├── src/index.js
├── test/test.js
└── scripts/publish.sh
```

## 本地验证

```bash
npm test
node bin/cli.js brief --text "方案A 继续扩展连接器来源，但实现更重。方案B 先做一页式决策简报，最快本周能验证。建议先做方案B。"
```

## 发布

```bash
npm run publish:clawhub
```

或直接执行：

```bash
sh ./scripts/publish.sh
```

## 一句话卖点

把多份资料压缩成一页可决策简报：选项、冲突、证据缺口、推荐结论和下一步，一次讲清楚。
