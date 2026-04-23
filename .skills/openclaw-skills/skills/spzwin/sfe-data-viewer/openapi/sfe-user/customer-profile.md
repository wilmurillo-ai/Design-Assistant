# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/customer-profile

## 作用

获取客户的属性标签信息（画像）。需要先通过 customer 接口获取 `customerId`。

**Headers**

- `appKey` — API 密钥（必传）
- `Content-Type: application/json`
- `tenantId` — 租户 ID（可选）。默认无须传入，用户存在多个租户身份时须传入。如未传入具体 tenantId，会返回用户可选择的租户列表。

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `customerId` | String | 否 | 客户 ID，来自 customer 接口返回的 `id` |
| `productId` | String | 否 | 产品 ID，来自 product 接口返回的 `id` |
| `drugFormName` | String | 否 | 剂型名称 |
| `status` | Integer | 否 | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "customerId": { "type": "string", "description": "客户 ID" },
    "productId": { "type": "string", "description": "产品 ID" },
    "drugFormName": { "type": "string", "description": "剂型名称" },
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
          "customerId": { "type": "string" },
          "customerName": { "type": "string" },
          "productId": { "type": "string" },
          "productName": { "type": "string" },
          "drugFormName": { "type": "string" },
          "tags": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "type": { "type": "string" },
                "name": { "type": "string" }
              }
            }
          },
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

- `../../scripts/sfe-user/customer-profile.py`
