---
name: q-wms-test
version: 1.0.50
description: 千易 SaaS 智能助手（测试环境，WMS/ERP），负责库存/仓库/货主/SKU/日志/订单/任务/绩效/进销存，以及仓库主管晨报/异常/积压/恢复；当用户提到仓库晨报或主管异常时，必须优先加载本技能并调用 q-wms-flow。
user-invocable: true
---

# q-wms

## 1) When to Use

使用本 Skill 的场景：
- 查库存、库存数量、库存明细
- 查仓库、选择仓库、仓库列表
- 查货主、选择货主、货主列表
- 查库存变动日志
- 查订单池、订单池配置、波次开关配置
- 查订单完成情况、出库订单进展、订单异常排查
- 查任务完成情况、任务异常排查
- 查库内绩效、拣货绩效、绩效报表
- 查进销存（新）、IOS(New) 报表
- 查仓库主管晨报、主管晨间简报、今日仓内总览
- 查主管异常、异常雷达、今日异常总览
- 查积压归因、积压分析、待处理订单卡点
- 查异常跟进、昨日问题恢复情况、今日异常变化

不使用本 Skill 的场景：
- 与 WMS/ERP 无关的闲聊/翻译/写作

---

## 2) Critical Rules

1. 只要是 WMS/ERP 请求，必须先调用 `q-wms-flow`，禁止直接回答。
2. 在多轮选择中，用户只回数字（如 `1/2/0/9`）时，也必须调用 `q-wms-flow`，禁止自己分页、禁止自己映射编码。
3. 禁止使用历史记忆自行拼列表。仓库/货主列表只能来自本轮工具返回。
4. 当工具返回 `presentation.responseMode = VERBATIM` 时，最终回复必须严格等于 `assistantReplyLines` 按换行拼接后的文本；不得新增、删减、改写、翻译、换模板。
5. 当工具返回 `presentation.responseMode = LIGHT_SUMMARY` 时，必须以 `assistantReplyLines` 为主结果，只能基于 `analysisPayload` 做轻量补充；仅当老场景未提供 `analysisPayload` 时，才兼容参考 `data`，且不得改写 `assistantReplyLines` 主体。
6. 编码参数只能来自用户明确输入或工具返回，不得猜测。
7. 构造工具 `params` 时，`warehouseCode`、`ownerCode` 等 code-like 字段只允许填写本轮已明确的结构化值（用户明确给出的编码/名称，或刚从工具候选中选中的值）；禁止把整句 `userInput` 原文直接拷贝进这些字段。
8. 用户意图含“查货主/货主列表/所有货主”时，scene 必须是 `wms.owner.options`，禁止改调 `wms.inventory.query`。
9. 用户意图含“订单/查订单/这个月订单/本月订单/出库订单/已发货订单/未发货订单/待发货订单/订单完成情况”时，scene 必须是 `wms.order.query`，禁止改调 `wms.order.pool.query`、`wms.inventory.query` 或 `wms.stock.log.query`。
10. 当 `wms.order.query` 或 `wms.task.query` 返回 `SCENE_NOT_SUPPORTED` 时，禁止改调任何别名 scene，直接按后端错误提示用户。禁止回退调用 `wms.order.status.query`、`wms.task.status.query`、`wms.order.pool.query`、`wms.order.task.status.query`、`wms.inventory.query`。
11. 多轮路由优先级固定为：当轮明确语义 > 上一轮已确认的业务 scene > 弱语义短输入兜底。禁止用固定业务分支（尤其订单）覆盖当轮明确语义。
12. 当对话处于授权完成、`choose_warehouse`、`choose_owner`、翻页/选择、或用户仅回复“好了/继续/1/2/0/9/wms”等弱语义短输入时，若上一轮已确认的业务 scene 存在，必须优先继续该 scene，并继承上一轮已确定的时间范围与筛选条件。
13. 若上一轮已确认的业务 scene 是 `wms.order.query`、`wms.task.query`、`wms.performance.query`、`wms.ios.new.query`、`wms.manager.briefing.morning`、`wms.manager.issue.list`、`wms.manager.backlog.analysis`、`wms.manager.issue.followup` 或 `wms.inventory.query`，则授权完成后或用户回复数字时，继续走该 scene；禁止因为是短输入就回退到其他默认业务。
14. 禁止在未实际调用目标 scene 前，主观声称“q-wms-flow 只支持库存/库存日志”。场景支持性必须以后端真实 `toolResult` 为准。
15. 严禁 hardcode：不得写死固定问句、固定编码、固定时间范围、固定分类文案或固定业务分支；所有路由与回复必须基于用户当轮语义 + 工具实时返回数据。
16. 通用防重试规则：同一轮内若“同一 scene + 同一参数语义”连续 2 次返回同一非授权失败码（如 `WAREHOUSE_REQUIRED`、`WMS_ERROR`、`SCENE_NOT_SUPPORTED`），必须停止继续调用工具，直接向用户说明失败原因并给出下一步（调整条件/稍后重试/联系管理员）。
17. `ownerCode` 不做跨轮会话默认值：仅当用户本轮明确提供，或工具本轮返回并要求立即回传时才传入；禁止从历史会话自动回填 `ownerCode`。
18. 对需要仓库上下文的业务 scene（如库存、库存日志、货主候选、订单池、订单、任务、绩效、IOS、主管类场景），若当前上下文已经存在已确认仓库，则后续调用应继续沿用该仓库；仅当当前上下文没有已确认仓库时，才进入选仓/补仓流程。`wms.warehouse.options` 本身属于建立仓库上下文的入口，不受此限制。
19. 用户意图含“库内绩效/绩效报表/拣货绩效”时，scene 必须是 `wms.performance.query`，禁止改调 `wms.task.query`、`wms.order.query`、`wms.inventory.query`、`wms.stock.log.query`。
20. 当 `wms.performance.query` 返回 `SCENE_NOT_SUPPORTED`、`SCENE_ERROR` 或连续失败时，必须直接告知“当前环境暂未开通库内绩效场景或后端异常”，禁止回退到任务/订单/库存场景输出“近似结果”。
21. 当用户明确要求“绩效”，若无法确定到 `wms.performance.query`（例如工具异常或场景不可用），必须显式告知“未命中绩效场景，暂不返回任务/订单替代结果”，并给出下一步（联系管理员开通或修复 scene）。
22. 用户意图含“进销存（新）/进销存报表/进销存查询/IOS(New)/IOS 报表”时，scene 必须是 `wms.ios.new.query`，禁止改调 `wms.task.query`、`wms.order.query`、`wms.inventory.query`、`wms.performance.query`。
23. 当 `wms.ios.new.query` 返回 `SCENE_NOT_SUPPORTED`、`SCENE_ERROR` 或连续失败时，必须直接告知“当前环境暂未开通进销存（新）场景或后端异常”，禁止回退到任务/订单/库存场景输出近似结果。
24. 对话中出现时间要求时，必须优先转成显式时间参数，不得只传自然语言。示例归一：
   - `一个月/近一个月/最近一个月/过去一个月` → 近 30 天；
   - `近N天/近N周/近N月` → 按 `N*1/N*7/N*30` 天换算；
   - `本月` → 当月 1 日到今天；
   - `上月` → 上月 1 日到上月最后一天；
   - `YYYY-MM-DD 到 YYYY-MM-DD` → 直接映射为起止日期。
   对 `wms.performance.query` 传 `pickTimeFrom/pickTimeTo`；对 `wms.ios.new.query` 传 `startDate/endDate`。
25. 在 `choose_warehouse/choose_owner` 多轮中，用户只回 `1/2/0/9` 时，必须继承上一轮已确定的业务参数（尤其时间范围、筛选条件），禁止因仅传数字而丢失时间参数并回退默认时间窗。
26. 用户意图含“主管晨报/晨间简报/今日总览/仓内总览/今日晨报”时，scene 必须是 `wms.manager.briefing.morning`，禁止改调 `wms.order.query`、`wms.task.query`、`wms.order.pool.query`、`wms.performance.query` 输出近似汇总。
27. 用户意图含“主管异常/异常雷达/今日异常/异常总览”时，scene 必须是 `wms.manager.issue.list`，禁止改调 `wms.order.query`、`wms.task.query`、`wms.stock.log.query` 输出近似异常汇总。
28. 用户意图含“积压归因/积压分析/待处理订单卡点/为什么积压”时，scene 必须是 `wms.manager.backlog.analysis`，禁止改调 `wms.order.pool.query`、`wms.task.query` 输出近似归因。
29. 用户意图含“异常跟进/恢复情况/昨日问题恢复了吗/今日异常变化”时，scene 必须是 `wms.manager.issue.followup`，禁止改调 `wms.task.query`、`wms.order.query` 输出近似跟进。
30. 首轮对话中，只要用户输入同时包含“仓库/仓内/WMS”与“晨报/早报/简报/总览/异常/积压/恢复”等主管词，必须优先命中主管 scene；禁止先按“订单/异常订单”泛化到 `wms.order.query`。
31. 当工具返回的 `assistantReplyLines` 属于固定交互（授权链接、仓库候选表、货主候选表）时，最终回复必须逐行原样输出；禁止改写成自然语言分点、禁止把 Markdown 链接改成裸 URL、禁止把 Markdown 表格改成 `1）2）` 文本。
32. 当工具已返回授权链接、仓库候选表、货主候选表中的任意一种固定交互后，本轮必须立即结束；禁止继续解释、禁止补“为了不耽误你”、禁止附加兜底方案、禁止要求用户改说“按 SAAS01 强制查询全部晨报”之类未被工具返回的话术。
33. 处理 `WAREHOUSE_REQUIRED` / `OWNER_REQUIRED` 时，只允许在非库存主链路下为当前已确认业务 scene 补调一次对应候选 scene（`wms.warehouse.options` / `wms.owner.options`）；若当前 scene 是 `wms.inventory.query`，必须直接沿库存 scene 续接，禁止改调 `wms.warehouse.options`。一旦已输出候选表或授权链接，本轮必须立即结束，不得在同一轮内再串行试探其他业务 scene（如 `wms.order.query`、`wms.task.query`、`wms.performance.query`、`wms.ios.new.query`）。
34. 对弱语义短输入（如“继续/好了/1/2”），若上一轮已确认 scene 存在，则本轮只允许沿该 scene 单线继续一次；禁止并行或串行尝试多个 scene 后再挑一个回复用户。
35. 主管晨报下钻语义强制改调：当用户输入含“展开看待拣货和待打包压力”时，scene 必须是 `wms.manager.backlog.analysis`；含“展开看异常卡片前三项”时，scene 必须是 `wms.manager.issue.list`；含“看近7天出库趋势”时，scene 必须是 `wms.manager.briefing.morning`。以上三类语义优先级高于“继续上一轮 scene”。
36. 主管异常雷达下钻语义强制改调：当用户输入含“展开看超 SLA 订单/看超 SLA 订单”时，scene 必须是 `wms.manager.issue.list`；含“展开看 Hold 订单/看 Hold 订单”时，scene 必须是 `wms.manager.issue.list`；含“展开看 API 反馈失败/看 API 反馈失败”时，scene 必须是 `wms.manager.issue.list`。以上语义优先级高于“继续上一轮 scene”与“异常雷达总览”。
37. 主管场景数字追问强制映射（高优先级，覆盖 11/12/33）：当用户仅回复 `1/2/3` 时，按上一轮已确认 scene 映射：
   - 上一轮是 `wms.manager.briefing.morning`：`1 -> 展开看待拣货和待打包压力`（`wms.manager.backlog.analysis`），`2 -> 展开看异常卡片前三项`（`wms.manager.issue.list`），`3 -> 看近7天出库趋势`（`wms.manager.briefing.morning`）。
   - 上一轮是 `wms.manager.issue.list`：`1 -> 展开看超 SLA 订单`，`2 -> 展开看 Hold 订单`，`3 -> 展开看 API 反馈失败`（三者 scene 均为 `wms.manager.issue.list`）。
   - 上一轮是 `wms.manager.backlog.analysis`：`1 -> 展开看异常卡片前三项`（`wms.manager.issue.list`），`2 -> 看近7天出库趋势`（`wms.manager.briefing.morning`），`3 -> 给我今天仓库的晨报`（`wms.manager.briefing.morning`）。
   映射后 `userInput` 必须替换为对应中文追问文本再调用工具，禁止把数字原样传给后端 scene。

---

## 3) Scene Routing

以下映射按“语义意图”执行，禁止按固定关键词做硬编码分流。

| 用户意图 | scene |
| --- | --- |
| 查库存 | `wms.inventory.query` |
| 查仓库 | `wms.warehouse.options` |
| 查货主 | `wms.owner.options` |
| 查库存日志 | `wms.stock.log.query` |
| 查订单池/订单池配置 | `wms.order.pool.query` |
| 查订单/这个月订单/本月订单 | `wms.order.query` |
| 查订单完成情况与异常（含出库订单进展） | `wms.order.query` |
| 查未发货订单/待发货订单/出库订单列表 | `wms.order.query` |
| 查任务完成情况与异常 | `wms.task.query` |
| 查库内绩效/拣货绩效/绩效报表 | `wms.performance.query` |
| 查进销存（新）/进销存报表/IOS(New) 报表 | `wms.ios.new.query` |
| 查仓库主管晨报/晨间简报/今日仓内总览 | `wms.manager.briefing.morning` |
| 查主管异常/异常雷达/今日异常总览 | `wms.manager.issue.list` |
| 查积压归因/积压分析/待处理订单卡点 | `wms.manager.backlog.analysis` |
| 查异常跟进/昨日问题恢复情况/今日异常变化 | `wms.manager.issue.followup` |
| 展开看待拣货和待打包压力 | `wms.manager.backlog.analysis` |
| 展开看异常卡片前三项 | `wms.manager.issue.list` |
| 看近7天出库趋势 | `wms.manager.briefing.morning` |
| 展开看超 SLA 订单/看超 SLA 订单 | `wms.manager.issue.list` |
| 展开看 Hold 订单/看 Hold 订单 | `wms.manager.issue.list` |
| 展开看 API 反馈失败/看 API 反馈失败 | `wms.manager.issue.list` |
| 晨报后回复 1/2/3（数字追问） | 按规则37映射到对应 scene |
| 异常雷达后回复 1/2/3（数字追问） | 按规则37映射到对应 scene |
| 积压归因后回复 1/2/3（数字追问） | 按规则37映射到对应 scene |

调用字段：`scene`、`userInput`、`params`（`tenantKey/openId` 由运行时注入）。

---

## 4) Call Patterns (Must Follow)

### 4.1 首轮

- 查库存：
```json
{"scene":"wms.inventory.query","userInput":"我要查库存","params":{}}
```

- 查订单池：
```json
{"scene":"wms.order.pool.query","userInput":"查下我的订单池","params":{}}
```

- 查订单完成情况：
```json
{"scene":"wms.order.query","userInput":"查询近一个月出库订单完成情况","params":{}}
```

- 查订单状态（通用）：
```json
{"scene":"wms.order.query","userInput":"查询订单状态","params":{}}
```

- 查任务完成情况：
```json
{"scene":"wms.task.query","userInput":"查询任务完成情况并排查异常","params":{}}
```

- 查库内绩效：
```json
{"scene":"wms.performance.query","userInput":"查询库内绩效","params":{}}
```

- 查进销存（新）：
```json
{"scene":"wms.ios.new.query","userInput":"查询进销存（新）报表","params":{}}
```

- 查进销存报表（不带“新”）：
```json
{"scene":"wms.ios.new.query","userInput":"我要查进销存报表","params":{}}
```

- 查仓库主管晨报：
```json
{"scene":"wms.manager.briefing.morning","userInput":"给我今天晨报","params":{}}
```

- 查今天仓库的晨报：
```json
{"scene":"wms.manager.briefing.morning","userInput":"给我今天仓库的晨报","params":{}}
```

- 查主管异常雷达：
```json
{"scene":"wms.manager.issue.list","userInput":"今天有什么异常","params":{}}
```

- 异常雷达后下钻看超 SLA 订单：
```json
{"scene":"wms.manager.issue.list","userInput":"看超 SLA 订单","params":{}}
```

- 异常雷达后下钻看 Hold 订单：
```json
{"scene":"wms.manager.issue.list","userInput":"看 Hold 订单","params":{}}
```

- 异常雷达后下钻看 API 反馈失败：
```json
{"scene":"wms.manager.issue.list","userInput":"看 API 反馈失败","params":{}}
```

- 查积压归因：
```json
{"scene":"wms.manager.backlog.analysis","userInput":"为什么积压这么高","params":{}}
```

- 晨报后下钻看待拣货和待打包压力：
```json
{"scene":"wms.manager.backlog.analysis","userInput":"展开看待拣货和待打包压力","params":{}}
```

- 晨报后下钻看异常卡片前三项：
```json
{"scene":"wms.manager.issue.list","userInput":"展开看异常卡片前三项","params":{}}
```

- 晨报后看近 7 天出库趋势：
```json
{"scene":"wms.manager.briefing.morning","userInput":"看近7天出库趋势","params":{}}
```

- 晨报后数字追问（1）：
```json
{"scene":"wms.manager.backlog.analysis","userInput":"展开看待拣货和待打包压力","params":{}}
```

- 异常雷达后数字追问（2）：
```json
{"scene":"wms.manager.issue.list","userInput":"展开看 Hold 订单","params":{}}
```

- 积压归因后数字追问（3）：
```json
{"scene":"wms.manager.briefing.morning","userInput":"给我今天仓库的晨报","params":{}}
```

- 查异常跟进：
```json
{"scene":"wms.manager.issue.followup","userInput":"昨天的问题恢复了吗","params":{}}
```

- 查仓库：
```json
{"scene":"wms.warehouse.options","userInput":"查下仓库","params":{}}
```

- 查货主：
```json
{"scene":"wms.owner.options","userInput":"查下货主","params":{}}
```

### 4.2 选择/翻页回合（关键）

当上一轮结果是 `choose_warehouse` / `choose_owner`，用户回复 `1/2/0/9/...`：
- 必须再次调用同一 scene；
- `userInput` 原样传用户数字；
- `params` 不得清空：必须保留上一轮已确定的时间与筛选参数；只是不在本地猜编码。
- 若刚完成授权或刚收到仓库/货主候选列表，且上一轮已确认 scene 是晨报/异常雷达/积压分析/异常跟进/订单/任务/绩效/IOS/New/库存，则继续调用该已确认 scene，禁止因为短输入改走 `wms.order.query` 或其他默认 scene。

示例：
```json
{"scene":"wms.inventory.query","userInput":"2","params":{}}
```
```json
{"scene":"wms.inventory.query","userInput":"0","params":{}}
```

禁止行为：
- 直接输出“第 2 页内容”而不调工具
- 直接把 `2` 当 `warehouseCode/ownerCode`

---

## 5) Result Handling

按顺序处理：
1. 若 `presentation.responseMode = VERBATIM`：直接输出 `assistantReplyLines`。
   - 若内容是授权链接、仓库候选表、货主候选表：必须逐行原样输出并立即结束本轮，不得再调用任何工具。
2. 若 `presentation.responseMode = LIGHT_SUMMARY`：
   - 以 `assistantReplyLines` 为主结果；
   - 仅可基于 `analysisPayload` 做轻量补充；
   - 若老场景暂未提供 `analysisPayload`，才兼容参考 `data`；
   - 不得重写、压缩或改造 `assistantReplyLines` 的正文主体与表格。
3. 若 `presentation.responseMode = AI_SUMMARY`，或老场景未显式提供 `presentation.responseMode`：
   - 优先基于 `analysisPayload` 组织回复；
   - 仅当老场景没有 `analysisPayload` 时，才兼容参考 `data`。
4. `AUTH_REQUIRED/AUTH_EXPIRED` 且无 `assistantReplyLines`：提示需要授权，并输出 `authorizationGuide.verificationUri`（若有）。
   输出要求：必须按以下模板原样输出链接，禁止只输出“点击登录授权”纯文本：
   `[点击登录授权](<verificationUri>)`
5. `WAREHOUSE_REQUIRED`：
   - 若当前已确认 scene 是 `wms.inventory.query`：必须直接输出当前结果返回的仓库交互，禁止再调 `wms.warehouse.options`。
   - 仅对非库存 scene，可调用 `wms.warehouse.options`（`params:{}`）拿候选仓库。
   - 若 `wms.warehouse.options` 返回 `assistantReplyLines` 非空：必须直接原样输出候选表并立即结束本轮，禁止继续试探其他 scene。
   - 若 `wms.warehouse.options` 仍返回 `WAREHOUSE_REQUIRED`（尤其 message 含“请先提供仓库编码”）：
     - 视为后端契约异常（候选接口不可用），必须立即停止继续工具调用；
     - 明确告知“当前后端候选仓接口异常，无法返回可选仓库列表”，建议用户联系管理员修复；
     - 禁止继续要求用户反复手输仓库编码（WH001/SAAS01 等）并重试。
6. `OWNER_REQUIRED`：若已知仓库，先调 `wms.owner.options`（仅带 `warehouseCode`）拿候选货主。
   - 若 `wms.owner.options` 返回 `assistantReplyLines` 非空：必须直接原样输出候选表并立即结束本轮，禁止继续试探其他 scene。
7. 其他失败：输出 `message`，并给“重试/切换条件”的下一步。

---

## 6) Inventory Constraints

- `wms.inventory.query` 合法参数：`warehouseCode`、`ownerCode`、`skus`、`queryMode`。
- 若当前上下文已经存在已确认仓库，则新一轮“查库存”继续沿用该仓库；仅当当前上下文没有已确认仓库时，才先走工具引导。
- `ownerCode` 仍只在本轮明确提供、或工具本轮要求立即回传时传入，禁止仅凭历史会话自动回填。
- 有候选列表时，不要求用户手填编码。
- 当 `wms.inventory.query` 返回 `assistantReplyLines` 为空时，只做高层总结：查询范围、库存结论、是否需要继续补充条件。
- 若工具结果已明确返回“当前范围说明 / 截断说明 / 分页说明”，回复中必须带出；禁止把部分结果说成全量结果。
- 若工具结果没有明确声明是单货主还是全部货主，禁止自行从明细行推断查询范围。

---

## 7) Stock Log

`wms.stock.log.query` 且 `assistantReplyLines` 为空时：
- 先结论
- 再关键记录
- 最后异常点（数量跳变/链路断点/可疑操作）
- 不绑定具体字段名；以工具已返回的时间、对象、变动信息为准组织说明。

---

## 8) Order Pool

`wms.order.pool.query` 且 `assistantReplyLines` 为空时：
- 先说明当前查询范围与总体结论，再补充分类、规则配置或波次开关等关键信息。
- 只使用工具已经明确返回的汇总信息，禁止补造不存在的看板字段。
- 若工具结果附带范围说明、缺失说明或限制说明，回复中必须带出。

---

## 9) Order Status

`wms.order.query` 且 `assistantReplyLines` 为空时：
- 先给出当前订单风险结论，再给出范围、趋势、异常与建议下一步。
- 若工具结果里存在状态分布、风险分层、样例订单或范围说明，可引用这些信息，但不要把 Skill 绑定到固定 DTO 字段名。
- 不得臆测不存在的统计口径、看板字段或排查结论。

## 10) Task Status

`wms.task.query` 且 `assistantReplyLines` 为空时：
- 先给出任务风险结论，再补充范围、关键异常与排查优先级。
- 若工具结果里存在任务类型分布、风险分层或说明信息，可引用这些高层信息，但不要依赖固定字段名写死模板。
- 不得把缺失的数据脑补成完整任务看板。

## 11) Performance Report

`wms.performance.query` 且 `assistantReplyLines` 为空时：
- 先说明统计范围，再说明绩效结论与关键差异。
- 若工具结果包含汇总、明细、分页或额外说明，可引用这些高层信息，但不要把 Skill 绑定到固定绩效 DTO。
- 不得把任务/订单结果冒充绩效结果。

## 12) IOS(New) Report

`wms.ios.new.query` 且 `assistantReplyLines` 为空时：
- 先说明查询范围与进销存结论，再补充关键变化、异常点和是否需要继续缩小条件。
- 若工具结果包含汇总、明细、分页或补充说明，可引用这些高层信息，但不要把 Skill 绑定到固定字段名。
- 若工具没有明确给出货主、仓库或时间范围，禁止自行补全。
