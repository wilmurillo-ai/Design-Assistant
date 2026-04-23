---
name: tencent-web-search
description: Search the web using TencentCloud Web Search API (WSA). Prioritize using it when you need to retrieve network information.
homepage: https://cloud.tencent.com/product/wsa
metadata: {"openclaw":{"emoji":"🔍︎","requires":{"bins":["python3"],"env":["TENCENTCLOUD_SECRET_ID","TENCENTCLOUD_SECRET_KEY"]}}}
---

# 腾讯云联网搜索

腾讯云联网搜索服务以互联网全网公开资源为基础，实现了从收录至召回排序全链路的智能搜索增强。
针对用户对话中的关键问题（query）实时搜索互联网内容，返回最新相关的、高质量网页的内容信息，包括文章标题、摘要、url地址、发布日期、发布站点，为大模型提供关键有效的决策信息，为用户提供更精准、更高质量的回答。

免费额度：https://console.cloud.tencent.com/wsapi/activity

产品官网：https://cloud.tencent.com/product/wsa

## 使用场景
通过接入腾讯云联网搜索skills，为大模型拓展互联网信息实时检索能力，突破大模型知识困局，帮助大模型准确理解并快速回应用户的多样化问题。
- **信息查询**：搜索特定主题的互联网信息
- **热点追踪**：获取最新的新闻、资讯
- **知识检索**：查找百科、教程等知识类内容

## 工具特性
- **毫秒级响应结果**
- **百亿索引内容库**
- **支持指定网址检索**
- **支持指定时间范围检索**
- **支持混合模式检索独家插件内容来源，如天气、股价、汇率等**
- **返回动态摘要，token消耗更友好**

## 快速开始

### 准备工作
配置腾讯云联网搜索skills前，您需要在腾讯云控制台上完成准备工作：

| 操作步骤 | 说明 |
| --- | --- |
| [步骤一：登陆注册](https://cloud.tencent.com/document/product/1806/121802#8270649a-f02c-4f88-ab02-656e5e92894a) | 注册腾讯云账号，完成实名认证并登录 |
| [步骤二：开通标准版服务](https://cloud.tencent.com/document/product/1806/121802#63b4e9ef-8c65-4a87-9169-627941e751a1) | 控制台自助开通联网搜索API 标准版服务 |
| [步骤三：获取云API密钥](https://cloud.tencent.com/document/product/1806/121802#21242563-b79b-4db5-962a-12a9a39ebc16) | 获取云 API 密钥的 SecretId 和 SecretKey |

### 配置密钥环境变量
安装skills后，您需要将腾讯云密钥以环境变量的方式配置在Open Claw中。

变量名称1：
TENCENTCLOUD_SECRET_ID

变量名称2：
TENCENTCLOUD_SECRET_KEY

eg:'~/.openclaw/.env'


## 使用方法

** 注意：需要切换到该 skill 同目录下执行**

### 基于关键词搜索
```bash
python3 scripts/websearch.py --query="搜索关键词"
```

### 指定时间范围搜索相关信息
```bash
python3 scripts/websearch.py --query="搜索关键词" --freshness='year'
```
freshness包含以下选项:

|选项|解释|
|-----|----|
| ''| 空或者不带freshness不强调时间范围|
| day | 搜索最近一天的内容|
| week| 搜索最近一周的内容|
| month| 搜索最近一个月的内容|
| year| 搜索最近一年的内容|

### 搜索天气、金价、股价、医疗、汇率、油价、贵金属相关高时效高精度的垂类信息，混合搜索独家插件内容来源。
```bash
python3 scripts/websearch.py --query="搜索关键词" --mode=2
```

### 指定网页站点搜索
```bash
python3 scripts/websearch.py --query="搜索关键词" --site="sogou.com"
```



## 输入参数说明

| 参数    | 必填 | 说明                     | 示例                                                                |
|-------| ---- |------------------------|-------------------------------------------------------------------|
| query | 是   | 搜索关键词                 | python3 scripts/websearch.py --query="搜索关键词"                      |
| site | 否 | 用于约束搜索内网的站点,要求是严格的站点格式 | python3 scripts/websearch.py --query="搜索关键词" --site="sogou.com"   |
| mode | 否| 0-自然检索结果(默认)，1-多模态VR结果（包括天气、金价、股价、医疗、汇率、油价、贵金属等相关信息），2-混合结果（多模态VR结果+自然检索结果)| python3 scripts/websearch.py --query="搜索关键词" --mode=2             |
| freshness| 否| 'day': 表示最近一天,'week': 表示最近一周,'month': 表示最近一个月,'year': 表示最近一年|python3 scripts/websearch.py --query="搜索关键词" --freshness='year'|
## 输出示例

```
🔍 搜索: 2026年两会
✅ 找到 2 个结果

【1】url:https://so.html5.qq.com/page/real/search_news?docid=70000021_26069b1993758352,title:2026年全国两会巡礼,snippet:2026年全国两会即将完成各项议程,圆满落下帷幕｡</p><p>这是一次凝心聚力､真抓实干､团结奋进的大会,出席会议的代表委员担当进取､同心同德､全力以赴,审议审查和讨论“十五五”规划纲要草案､政府工作报告等 重要遵循｡,date:2026-03-12 00:32:56,site:企鹅
【2】url:https://www.163.com/dy/article/KOD8C0FK05566NA8.html,title:30万亿砸向普通人!2026两会定调:不再只修路盖楼,国家要投资你大基建_网易订阅,snippet:别瞎撞了,2026年两会刚放的大招,直接把国家接下来的投资方向给你摆到明面上了｡以前国家砸钱爱搞修路盖楼大基建,现在思路直接大拐弯,30万亿财政支出史无前例,真金白银全 
往咱们普通人身上砸,就为了扶着大家长本事､多挣钱､日子过得更踏实｡今年两会直接把调子定死了,硬件还要搞,但更重要的是投“人”｡30万亿的财政支出创了历史纪录,光是教育､医保､养老､技能提升这四项民生相关的,占比就冲到了40%以上｡还有赤字率顶格提到4%,降息降准也跟上,钱真的是往老百姓口袋里流的｡,date:2026-03-19 16:39:29,site:网易
相关图片:https://nimg.ws.126.net/?url=http%3A%2F%2Fdingyue.ws.126.net%2F2026%2F0319%2Fd2402476j00tc51cm00ekd000ku00cip.jpg&thumbnail=660x2147483647&quality=80&type=jpg
```




