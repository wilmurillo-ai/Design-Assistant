# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/coverage

## 作用

获取区划与客户画像的关联关系（覆盖分管关系）。需要先通过 zone 接口获取 `zoneId`，通过 customer-profile 接口获取 `customerProfileId`。

**Headers**

- `appKey` — API 密钥（必传）
- `Content-Type: application/json`
- `tenantId` — 租户 ID（可选）。默认无须传入，用户存在多个租户身份时须传入。如未传入具体 tenantId，会返回用户可选择的租户列表。

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `zoneId` | String | 否 | 区划 ID，来自 zone 接口返回的 `id` |
| `customerProfileId` | String | 否 | 客户画像 ID，来自 customer-profile 接口返回的 `id` |
| `status` | Integer | 否 | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "zoneId": { "type": "string", "description": "区划 ID" },
    "customerProfileId": { "type": "string", "description": "客户画像 ID" },
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
          "zoneId": { "type": "string" },
          "customerProfileId": { "type": "string" },
          "customerName": { "type": "string" },
          "productName": { "type": "string" },
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

- `../../scripts/sfe-user/coverage.py`
