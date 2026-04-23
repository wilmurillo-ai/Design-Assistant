# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/zone

## 作用

获取用户有权限访问的区划列表，通常作为数据查询的第一步，用于确定业务范围。返回的 `id` 可用于后续接口的 `zoneId` 参数。

**Headers**

- `appKey` — API 密钥（必传）
- `Content-Type: application/json`
- `tenantId` — 租户ID（可选），默认无须传入，用户存在多个租户身份时须传入。如未传入具体tenantId，会返回用户可选择的租户列表。

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | String | 否 | 区划 ID，用于精确查询 |
| `name` | String | 否 | 区划名称，支持模糊查询 |
| `level` | String | 否 | 区划层次：`hq`-总部，`region`-大区，`district`-片区，`area`-地区，`territory`-辖区 |
| `status` | Integer | 否 | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": { "type": "string", "description": "区划 ID" },
    "name": { "type": "string", "description": "区划名称" },
    "level": {
      "type": "string",
      "enum": ["hq", "region", "district", "area", "territory"]
    },
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
          "pathNames": { "type": "string" },
          "pathIds": { "type": "string" },
          "level": { "type": "string" },
          "isPrincipal": { "type": "integer" },
          "isDelegate": { "type": "integer" },
          "status": { "type": "integer" },
          "createTime": { "type": "string" },
          "updateTime": { "type": "string" }
        }
      }
    },
    "timestamp": { "type": "number" },
    "success": { "type": "boolean" }
  }
}
```

## 脚本映射

- `../../scripts/sfe-user/zone.py`
