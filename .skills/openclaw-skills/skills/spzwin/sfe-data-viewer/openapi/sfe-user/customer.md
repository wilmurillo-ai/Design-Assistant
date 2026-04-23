# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/customer

## 作用

获取用户有权限访问的客户列表。返回的 `id` 可用于查询客户画像的 `customerId` 参数。

**Headers**
- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | String | 否 | 客户 ID，用于精确查询 |
| `name` | String | 否 | 客户名称，支持模糊查询 |
| `type` | String | 否 | 客户类型 |
| `sourceType` | String | 否 | 来源类型 |
| `sourceId` | String | 否 | 来源 ID |
| `status` | Integer | 否 | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": { "type": "string", "description": "客户 ID" },
    "name": { "type": "string", "description": "客户名称" },
    "type": { "type": "string", "description": "客户类型" },
    "sourceType": { "type": "string", "description": "来源类型" },
    "sourceId": { "type": "string", "description": "来源 ID" },
    "status": { "type": "integer", "enum": [0, 1] },
    "page": { "type": "integer", "minimum": 1 }
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
          "id": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string" },
          "sourceType": { "type": "string" },
          "sourceId": { "type": "string" },
          "status": { "type": "integer" }
        }
      }
    },
    "timestamp": { "type": "number" },
    "success": { "type": "boolean" }
  }
}
```

## 脚本映射

- `../../scripts/sfe-user/customer.py`
