# Web 产品资料访问说明

本文件只描述“产品推荐类问题”所使用的 Web 资料访问方式。
对于收益规则、节假日规则、政策解读、常见问答类问题，应优先从本地 `./qa` 目录中匹配文件名并读取内容回答。

## 访问原则

产品资料获取必须遵守以下规则：
- 只允许使用 **HTTPS**
- 只允许使用 **GET**
- **不带任何参数**
- 不拼接用户输入到 URL
- 仅访问本文件中声明的固定白名单地址
- 仅获取公开文本资料，不执行账户操作、交易动作或资金指令

## 固定白名单 URL

- 优选周报 → `https://static.hepei.club/better_weekly`
- 新品推荐 → `https://static.hepei.club/new_products`
- 产品排行榜 → `https://static.hepei.club/best_seller_list`
- 低回撤产品 → `https://static.hepei.club/no_drawdown`
- 理财产品全量列表 → `https://static.hepei.club/full_list`

## 使用约束

- 不允许修改协议、域名、路径
- 不允许拼接 query 参数
- 不允许添加 body
- 不允许把用户输入直接拼接进 URL
- 如果固定地址访问失败，则明确告知用户当前资料暂不可用，不要编造

## 返回使用规则

- 用户问事实问题时，优先使用本地 `qa/` 内容回答
- 用户问产品推荐时，按 `patterns.md` 中的 URL 路由规则选择主资料来源
- 如果返回内容中混有排行榜、介绍性文字、产品条目，推荐回答时必须先筛选出满足条件的产品，再组织输出
