# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-period

## 作用

获取项目下所有可用周期。需要先通过 project-summary 接口获取 `projectId`。返回的 `periods[].code` 可用于后续接口的 `periodCode` 参数。

**Headers**
- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `projectId` | String | 否 | 项目 ID，来自 project-summary 接口返回的 `id` |
| `periodCode` | String | 否 | 周期编码 |
| `periodName` | String | 否 | 周期名称 |
| `periodStart` | String | 否 | 周期开始时间 |
| `periodEnd` | String | 否 | 周期结束时间 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "projectId": { "type": "string", "description": "项目 ID" },
    "periodCode": { "type": "string", "description": "周期编码" },
    "periodName": { "type": "string", "description": "周期名称" },
    "periodStart": { "type": "string", "description": "周期开始时间" },
    "periodEnd": { "type": "string", "description": "周期结束时间" }
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
          "periods": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "code": { "type": "string" },
                "name": { "type": "string" },
                "cycleUnit": { "type": "string" },
                "startDate": { "type": "string" },
                "endDate": { "type": "string" }
              }
            }
          }
        }
      }
    },
    "timestamp": { "type": "number" },
    "success": { "type": "boolean" }
  }
}
```

## 脚本映射

- `../../scripts/sfe-user/project-period.py`
