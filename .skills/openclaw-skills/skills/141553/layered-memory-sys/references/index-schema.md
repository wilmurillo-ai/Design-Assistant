# Index Schema

memory/index.json 的完整结构定义。

## 完整示例

```json
{
  "version": 1,
  "updatedAt": "2026-04-17T21:24:00+08:00",
  "layers": {
    "flash": { "ttl": 3, "desc": "闪存层：临时查询/一次性问答" },
    "active": { "ttl": 7, "desc": "活跃层：正在进行的任务" },
    "attention": { "ttl": 30, "desc": "关注层：反复讨论的话题" },
    "settled": { "ttl": 90, "desc": "沉淀层：重要经验/决策记录" }
  },
  "upgradeRules": {
    "flash_to_active": "recallCount >= 3",
    "active_to_attention": "recallCount >= 5 且多天被召回",
    "attention_to_settled": "recallCount >= 10",
    "settled_to_core": "被频繁引用且有价值 → 写入MEMORY.md",
    "user_request": "用户说'记住这个' → 直接进settled层"
  },
  "taskTypes": {
    "short": { "startLayer": "active", "onComplete": "7天后归档" },
    "recurring": { "startLayer": "attention", "ttlRefresh": "每次执行刷新TTL" },
    "exploration": { "startLayer": "flash", "upgradeBy": "反复讨论才升级" }
  },
  "memories": [
    {
      "id": "unique-id-YYYYMMDD",
      "title": "记忆标题",
      "tags": ["标签1", "标签2"],
      "type": "short|recurring|exploration",
      "layer": "flash|active|attention|settled",
      "ttl": 7,
      "created": "YYYY-MM-DD",
      "lastActive": "YYYY-MM-DD",
      "recallCount": 0,
      "recallDays": [],
      "turns": 0,
      "status": "active|completed|archived",
      "summary": "一句话概括"
    }
  ]
}
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | ✅ | 唯一标识，建议格式 `topic-YYYYMMDD` |
| title | string | ✅ | 记忆标题 |
| tags | string[] | ✅ | 分类标签，用于语义匹配 |
| type | string | ✅ | 任务类型：short/recurring/exploration |
| layer | string | ✅ | 当前层级：flash/active/attention/settled |
| ttl | number | ✅ | 生存天数（对应层级默认值） |
| created | string | ✅ | 创建日期 YYYY-MM-DD |
| lastActive | string | ✅ | 最后活跃日期 YYYY-MM-DD |
| recallCount | number | ✅ | 被memory_search召回的次数 |
| recallDays | string[] | ✅ | 被召回的日期列表 |
| turns | number | ✅ | 产生此记忆的对话轮次 |
| status | string | ✅ | 状态：active/completed/archived |
| summary | string | ✅ | 一句话概括（归档时使用） |
| archivedAt | string | ❌ | 归档日期（仅归档后存在） |

## 层级与TTL默认值

| 层级 | TTL | 用途 |
|------|-----|------|
| flash | 3 | 一次性问答，过期直接删除 |
| active | 7 | 正在进行的任务 |
| attention | 30 | 反复讨论的话题 |
| settled | 90 | 重要经验和决策 |
