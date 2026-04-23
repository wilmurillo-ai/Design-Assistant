# DecisionDeck Release Notes

## Short Description

把多份资料、纪要、调研和连接器结果，直接压成一页可决策简报。

## Marketplace Card Copy

Title:
- DecisionDeck

Short description:
- 决策简报官：把多份资料压成一页能拿去拍板的 decision brief

Install hook:
- 不只是把知识接进来，而是把资料直接推进成可决策结果

## Announcement Copy

DecisionDeck 不是再做一个总结器。

它解决的是一个更靠近结果的问题：
- 资料很多，但要怎么拍板
- 文档不少，但观点互相冲突
- 要给老板、客户、项目 owner 出一页纸，到底怎么写

这一版把事情收敛到 5 个高价值结果：
- 从多个文档提炼真实选项
- 找出观点冲突和分歧来源
- 标出证据不足的地方
- 生成一页式决策简报
- 给出推荐结论和下一步建议

它和 Knowledge Connector 是天然上下游：
- Knowledge Connector 负责把知识接进来、连起来、搜出来
- DecisionDeck 负责把这些材料带进决策场景

## Suggested Tags

- latest
- decision
- brief
- executive-summary
- knowledge
- planning

## Suggested Repo Name

- `openclaw-skill-decisiondeck`

## Publish Command

```bash
clawhub publish /absolute/path/to/decisiondeck \
  --slug decisiondeck \
  --name "DecisionDeck" \
  --version "1.0.0" \
  --changelog "Initial release of DecisionDeck: turn scattered notes, docs, and connector outputs into a one-page decision brief with options, conflicts, evidence gaps, and a recommended next move." \
  --tags "decision,brief,executive-summary,knowledge,planning"
```
