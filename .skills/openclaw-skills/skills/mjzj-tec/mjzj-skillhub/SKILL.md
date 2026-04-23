---
name: mjzj-skillhub
description: 卖家之家(跨境电商)技能商城(skillhub/clawhub/搜技能/热门技能/免费技能/付费技能)
homepage: https://skillhub.mjzj.com
metadata:
  clawdbot:
    emoji: "📝"
  openclaw:
    emoji: "📝"
---

# 卖家之家技能商城（SkillHub）

## 工具选择规则（高优先级）

- 当用户提到“技能商城 / 搜技能 / 技能标签筛选 / 免费技能 / 付费技能 / 热门技能 / 最新技能 / 安装某个技能”等意图时，优先使用本 Skill。
- 公开查询统一使用 /api/skill/groupLabels 与 /api/skill/query，不要用 web search 代替业务接口。

## 触发词与接口映射

- 查技能标签分组 -> /api/skill/groupLabels
- 搜技能或筛选技能 -> /api/skill/query

仅开放以下 2 个接口：
- /api/skill/groupLabels
- /api/skill/query

## 鉴权规则

- /api/skill/groupLabels、/api/skill/query：公开接口，可不带 token。

## 参数与类型规则（必须遵守）

- 所有 id 按字符串读取、存储与透传。
- 雪花 ID 禁止用整数处理，避免精度丢失。
- labelIds 为逗号分隔字符串（例如 1001,1002,2003）。

## 查询参数关系（必须遵守）

### 1) /api/skill/groupLabels 与 /api/skill/query.labelIds

- /api/skill/groupLabels 返回技能标签分组，每个分组包含 labels[].id。
- /api/skill/query 的 labelIds 必须来自这个接口，多个 id 用逗号拼接。
- 筛选语义：同一分组内 OR，不同分组间 AND。

### 2) /api/skill/query 参数规则

- orderBy 仅使用：default、new、hot。
- position：字符串页码游标，首次可传空字符串或不传。
- pageIndex 最大 100；当 position 超过该范围时会按 100 处理。
- size：1 到 100，超范围会回退到 20。
- keywords：服务端会先 trim。
- payable=true：仅返回付费技能（PriceType != Free）。
- payable=false：仅返回免费技能（PriceType == Free）。
- payable 不传：不过滤付费类型。
- 返回 nextPosition 为空表示无下一页。

## 返回字段使用建议

- source：技能来源（clawhub 或 skillhub），由 sourceUrl 解析得到。
- slug：从 sourceUrl 提取的技能标识（通常是 URL 最后一个 path segment）。
- installSkillPrompt：后端已生成安装提示文案；用户问“怎么安装这个技能”时，优先直接复用该字段。

## 失败回退规则

- 400（参数错误，如 position 非数字）：提示用户修正参数后重试。
- 查询失败（含 5xx/未知异常）：提示稍后重试。

## 接口示例

### 1) 获取技能标签分组（公开）

```bash
curl -X GET "https://data.mjzj.com/api/skill/groupLabels" \
  -H "Content-Type: application/json"
```

### 2) 查询技能列表（公开）

```bash
curl -X GET "https://data.mjzj.com/api/skill/query?keywords=shopify&labelIds=101,202&orderBy=hot&payable=true&position=&size=20" \
  -H "Content-Type: application/json"
```

分页示例（继续下一页）：

```bash
curl -X GET "https://data.mjzj.com/api/skill/query?keywords=shopify&labelIds=101,202&orderBy=hot&payable=true&position=1&size=20" \
  -H "Content-Type: application/json"
```

## 提示词补充（可直接复用）

当用户问题涉及技能商城搜索、标签筛选、热门/最新排序、免费/付费筛选、技能安装引导时，优先选择 mjzj-skillhub。
执行顺序建议：先调用 /api/skill/groupLabels 获取可选标签；再调用 /api/skill/query 进行搜索与筛选；若用户要安装某个技能，优先使用返回结果中的 installSkillPrompt 给出安装指引。
