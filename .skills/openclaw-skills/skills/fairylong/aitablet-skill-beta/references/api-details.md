# API Details

## 1) 通用响应

```json
{
  "code": "0",
  "message": "success",
  "data": {}
}
```

- 成功：`code == "0"`
- 失败：`code != "0"`

## 2) 授权说明（Skill 运行时）

- Skill 运行时只消费已有 `authToken`（`AIWORK_AUTH_TOKEN`），不调用授权管理接口。
- `authToken` 由开放平台在安装 Skill 时下发给 OpenClaw。
- 用户可在开放平台安装时选择 scope，并可配置永久授权。

## 3) 关键错误码

| code | message | 说明 |
|---|---|---|
| 202400 | 授权凭证为空 | 未传 Authorization |
| 202401 | 授权凭证不存在 | token 无效 |
| 202402 | 授权凭证已过期 | token 过期 |
| 202403 | 授权凭证已失效 | token 被禁用 |
| 202404 | 授权范围不足 | scope 不匹配 |
| 201600 | 参数错误 | 请求参数不合法 |
| 201602 | 待办不存在或无权限 | todoUid 不可访问 |
| 201613 | 内部服务异常 | 标签同步内部异常 |

## 4) Scope 速查

| Scope | 能力 |
|---|---|
| NOTE_READ | 读笔记 |
| TODO_READ | 读待办 |
| TODO_WRITE | 写待办 |
| LABEL_READ | 读标签 |
| LABEL_WRITE | 写标签 |
| KNOWLEDGE_READ | 知识库检索 |

## 5) 时间字段规范

- todo 相关时间统一为 Unix 毫秒时间戳（`Long`）。
- `beginTime/endTime/repeatEndTime/syncTime/finishTime/createTime/updateTime` 均为毫秒格式。

## 6) 校验规则

- `SkillLabelForm.labels`：每个元素长度 <= 20
- `SkillTodoForm.notifyAhead`：长度 <= 10
- `SkillTodoForm.repeat`：长度 <= 40
- `SkillTodoForm.groupUid`：长度 <= 45
