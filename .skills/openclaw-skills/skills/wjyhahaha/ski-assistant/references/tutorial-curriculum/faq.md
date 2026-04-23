# FAQ 框架（FAQ Framework）

定义各级别常见问题和回答要点。Agent 基于这些要点动态生成自然语言答案。

## 单板 FAQ

```yaml
faq_snowboard:
  level_0:
    - question: 我应该请教练吗
      answer_key_points: [强烈建议第一次上雪请 1-2 小时教练, 教程是补充不能替代现场指导]
    - question: 穿什么衣服
      answer_key_points: [速干内衣加抓绒中间层加防水外套, 不要穿棉质出汗后变冷, 具体参考装备清单]
    - question: 需要买装备吗
      answer_key_points: [第一次不需要全部租用, 滑 3 天后再决定是否购买]
    - question: 摔了很多次正常吗
      answer_key_points: [完全正常第一天摔 50-100 次是标准体验, 关键是学会安全地摔]
    - question: 年龄大了或体力不好学得会吗
      answer_key_points: [滑雪没有年龄上限, 关键请教练第一天不要滑太久循序渐进]
    - question: Regular 和 Goofy 哪个更好
      answer_key_points: [没有好坏之分天生决定的, 约 60% 的人 Regular 左脚前 40% Goofy 右脚前]
    - question: 滑雪后身体酸痛正常吗
      answer_key_points: [完全正常大腿小腿臀部手腕酸痛是标准体验, 通常 2-3 天后自然消失滑雪后拉伸和泡热水有助于缓解]

  level_1:
    - question: 换刃时总是摔倒怎么办
      answer_key_points: [正常换刃是 Level 1 最难的技术, 放慢速度在极缓坡上练习, 重点是视线引导到肩膀带到重心转移的顺序]
    - question: S 弯不连贯中间有停顿怎么办
      answer_key_points: [出弯后立刻准备下一个弯不要等完全停止, 练习时喊口令左右左右帮助建立节奏]
    - question: 前刃换后刃比后刃换前刃难正常吗
      answer_key_points: [完全正常前刃换后刃更难因为视线方向改变更大, 多练前刃到后刃比例 2:1]
    - question: 滑了 3 天还是不会 S 弯是不是不适合滑雪
      answer_key_points: [不是 S 弯通常需要 3-5 个雪日才能掌握, 关键每天练习 2-3 小时不要超过肌肉疲劳会影响学习]
    - question: 滑雪后身体酸痛正常吗
      answer_key_points: [完全正常大腿小腿臀部酸痛是标准体验, 通常 2-3 天后自然消失滑雪后拉伸和泡热水有助于缓解]

  level_2:
    - question: 搓雪小半径弯总是弯太大怎么办
      answer_key_points: [加快换刃节奏视线快速切换方向, 练习时喊口令左右左右每秒 1 个弯]
    - question: 刻滑时板尾总是扫雪怎么办
      answer_key_points: [立刃角度不够, 尝试更陡的坡让重力帮你建立立刃角度或者减小速度给边刃更多时间抓雪]
    - question: 反弓姿态和倾斜有什么区别
      answer_key_points: [倾斜是整个身体一起倾斜, 反弓是髋部偏移上半身保持直立反弓更稳定适合高速]
    - question: 粉雪中总是沉板怎么办
      answer_key_points: [重心需要更靠后（10-15%）, 身体放松不要僵硬转弯半径放大不要用硬雪的方式]
    - question: 三种风格选哪个
      answer_key_points: [喜欢速度选刻滑喜欢技巧选公园喜欢自由选野雪, Level 2 可以先都体验 Level 3 再专精一种]

  level_3:
    - question: 如何提高立刃角度
      answer_key_points: [反弓姿态是关键髋部偏移上半身直立, 宽阔雪道练习逐渐加速, 请同伴拍照测量角度]
    - question: 公园总是害怕跳台怎么办
      answer_key_points: [从小跳台开始建立信心, 重点是起跳时机和落地缓冲, 不要一开始就尝试大跳台]
    - question: 道外安全怎么学
      answer_key_points: [参加雪崩安全课程 AIARE 1 或等效, 购买安全装备搜救仪探杆雪铲, 有经验者带领下进入]
    - question: Level 3 之后是什么
      answer_key_points: [Level 4 是专家级通常涉及教练认证, 对于大多数滑行者 Level 3 是持续精进的级别]
    - question: 每年雪季前需要重新练基础吗
      answer_key_points: [建议每年雪季前 1-2 天回顾 Level 2 核心技能搓雪弯刻滑入门反弓, 肌肉记忆还在但神经连接需要重新激活, 不要一上来就冲黑道]
    - question: 如何判断自己是否真的达到 Level 3 水平
      answer_key_points: [最可靠的方式是发一段黑道滑行视频给 AI 教练打分, 如果 posture turning overall 三项均达到 7.5 分以上且能稳定保持说明已达 Level 3 水平]
```

## 双板 FAQ

```yaml
faq_ski:
  level_0:
    - question: 我应该请教练吗
      answer_key_points: [强烈建议第一次上雪请 1-2 小时教练, 教程是补充不能替代现场指导]
    - question: 穿什么衣服
      answer_key_points: [速干内衣加抓绒中间层加防水外套, 不要穿棉质出汗后变冷]
    - question: 需要买装备吗
      answer_key_points: [第一次不需要全部租用, 滑 3 天后再决定是否购买]
    - question: 摔了很多次正常吗
      answer_key_points: [完全正常第一天摔 50-100 次是标准体验, 关键是学会安全地摔]
    - question: 我年龄大了体力不好学得会吗
      answer_key_points: [滑雪没有年龄上限, 关键请教练第一天不要滑太久循序渐进]
    - question: 滑雪后身体酸痛正常吗
      answer_key_points: [完全正常大腿小腿臀部酸痛是标准体验, 通常 2-3 天后自然消失滑雪后拉伸和泡热水有助于缓解]

  level_1:
    - question: 平行转弯时内侧板总是飘在外面怎么办
      answer_key_points: [内侧板没有参与转弯是因为重心偏向外侧板, 练习时有意将重心放在两脚中间感受内侧板的刃抓雪]
    - question: 搓雪小回转节奏不匀怎么办
      answer_key_points: [用口令 1-2-1-2 或点-转-点-转帮助建立节奏, 先在极缓坡上慢速练习逐渐加快]
    - question: 点杖时总是戳雪太深怎么办
      answer_key_points: [点杖是点不是戳手腕发力像用手指轻点桌面, 练习时在平地反复感受手腕发力的感觉]
    - question: 上蓝道很害怕怎么办
      answer_key_points: [正常第一次上蓝道都会害怕, 选择最宽缓的蓝道用犁式到平行过渡速度慢一点]
    - question: 我滑了 3 天还是不会平行转弯是不是不适合滑雪
      answer_key_points: [不是平行转弯通常需要 3-5 个雪日才能掌握, 关键每天练习 2-3 小时不要超过肌肉疲劳会影响学习]

  level_2:
    - question: 搓雪小回转总是弯太大怎么办
      answer_key_points: [加快点杖和转弯节奏, 练习时喊口令 1-2-1-2 每秒 1 个弯膝盖引导方向要快]
    - question: 卡宾时内侧板总是飘怎么办
      answer_key_points: [确保双板平行重心均匀分配, 内侧板要主动立刃不是被动跟着]
    - question: 反弓姿态和倾斜 Inclination 有什么区别
      answer_key_points: [倾斜是整个身体一起倾斜, 反弓是髋部偏移上半身保持直立反弓更稳定适合高速]
    - question: 蘑菇总是直冲上去怎么办
      answer_key_points: [膝盖弯曲更多像弹簧一样吸收, 线路选择走雪包之间不是正对着冲速度慢一点]
    - question: 三种风格选哪个
      answer_key_points: [喜欢速度选卡宾喜欢节奏选蘑菇喜欢自由选野雪, Level 2 可以先都体验 Level 3 再专精一种]

  level_3:
    - question: 如何提高立刃角度
      answer_key_points: [反弓姿态是关键髋部偏移上半身直立, 宽阔雪道练习逐渐加速请同伴拍照测量角度确保内侧板主动立刃]
    - question: 蘑菇总是越来越快怎么办
      answer_key_points: [每个雪包都要吸收和转弯减速, 点杖引导节奏不要被动跟随速度太大时增大转弯半径减速]
    - question: 道外安全怎么学
      answer_key_points: [参加雪崩安全课程 AIARE 1 或等效, 购买安全装备搜救仪探杆雪铲有经验者带领下进入]
    - question: Level 3 之后是什么
      answer_key_points: [Level 4 是专家级通常涉及教练认证 CSIA Level 4 或 PSIA Level 3, 对于大多数滑行者 Level 3 是持续精进的级别]
    - question: 每年雪季前需要重新练基础吗
      answer_key_points: [建议每年雪季前 1-2 天回顾 Level 2 核心技能搓雪回转卡宾入门反弓, 肌肉记忆还在但神经连接需要重新激活不要一上来就冲黑道]
    - question: 如何判断自己是否真的达到 Level 3 水平
      answer_key_points: [最可靠的方式是发一段黑道滑行视频给 AI 教练打分, 如果 posture turning overall 三项均达到 7.5 分以上且能稳定保持说明已达 Level 3 水平]
```
