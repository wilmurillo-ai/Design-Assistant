---
name: group-buy-helper
description: Analyze group-buy and bargain campaigns, estimate success probability, and suggest participation strategies. Use when the user asks to 分析拼团、估算砍价成功率、判断是否值得参团、生成拉人分享文案 or assess group-buy outcomes.
---

# Group Buy Helper - 拼团/砍价助手

拼团砍价活动分析和成功率预测。

## 功能

- 🎯 砍价成功率估算
- 📊 拼团成团概率分析
- 💡 最优策略建议
- 📝 分享文案生成
- ⏰ 活动状态追踪

## 使用

```
分析砍价活动 还差多少
拼团成功率 还差2人
生成分享文案
```

## 输入建议

- 拼团场景：原价、拼团价、还差人数、剩余时间
- 砍价场景：目标价、当前价、已助力人数、每次助力金额（如已知）
- 平台：拼多多 / 淘宝等

## 输出要求

- 明确给出是否建议继续参与
- 给出成功概率或难度等级
- 给出下一步动作建议：继续拉人 / 尽快下单 / 直接放弃
- 需要生成分享文案时，输出可直接复制的文本

## 边界

- 估算结果是策略建议，不应伪装成平台官方概率
- 输入缺少关键字段时，应先提示信息不足
- 已达成目标时，应直接返回完成状态，不继续计算剩余人数

