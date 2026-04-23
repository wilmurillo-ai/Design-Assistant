# POST /ai-huiji/meetingChat/getChatFromShareId

## 作用

通过分享链接中的 `shareId` 获取一条 AI 慧记聊天记录详情，包含可用于纪要分析的原文内容（`srcText`）。

## 鉴权

只需 `appKey`，无需 access-token。

## 请求参数

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `shareId` | String | 是 | 分享链接中的 ID（UUID） |

## 响应说明

接口返回标准结构：`resultCode` / `resultMsg` / `data`。

常见 `data` 字段（以实际返回为准）：

| 字段 | 说明 |
|---|---|
| `_id` | 慧记记录 ID（可能包含后缀） |
| `name` | 会议标题 |
| `createTime` | 创建时间（毫秒时间戳） |
| `updateTime` | 更新时间（毫秒时间戳） |
| `meetingLength` | 会议时长（毫秒） |
| `simpleSummary` | 简要摘要 |
| `srcText` | 转写原文（可直接用于 AI 纪要） |
| `srcUser` | 分享者/来源用户信息 |

## 使用说明

- 当用户消息里出现分享链接时，先提取 `shareId` 再调用本接口。
- 支持三种链接形态（域名可变）：
  - 短链：`http://s.medihub.cn/p/xxxxx`（需先跟随跳转）
  - 长链：`https://<任意域名>/#/shareLinkPage?shareId=...`
  - 新版长链：`https://<任意域名>/#/meetingChatNew?shareId=...`
- 可携带附加参数（如 `userName`、`personId`），解析时仅使用 `shareId`，其它参数忽略。
- 短链解析建议在 Skill 层执行：先用 `web_fetch` 跟随跳转拿到 `finalUrl`，再提取 `shareId` 传给脚本。
- 返回后优先使用 `srcText` 做总结、待办提取、专题分析。

## 请求示例

```bash
python3 scripts/huiji/get-chat-from-share-id.py f12505e3-3ecb-47f1-87e4-277b2b1a243e

python3 scripts/huiji/get-chat-from-share-id.py --body '{"shareId":"f12505e3-3ecb-47f1-87e4-277b2b1a243e"}'
```

## 脚本映射

- `../../scripts/huiji/get-chat-from-share-id.py`
