# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-role

## 作用

获取用户在各模板下的操作权限。需要先通过 project-summary 接口获取 `projectId`。

**Headers**
- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `projectId` | String | 否 | 项目 ID，来自 project-summary 接口返回的 `id` |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "projectId": { "type": "string", "description": "项目 ID" }
  }
}
```

## 响应 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "resultCode": { "type": "integer" },
    "resultMsg": { "type": "string" },
    "data": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "projectId": { "type": "string" },
          "roles": { "type": "string", "description": "角色权限 JSON 字符串" }
        }
      }
    },
    "timestamp": { "type": "number" },
    "success": { "type": "boolean" }
  }
}
```

## 脚本映射

- `../../scripts/sfe-user/project-role.py`
