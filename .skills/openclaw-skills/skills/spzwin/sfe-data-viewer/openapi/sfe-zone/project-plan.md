# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-zone/project-plan

## 作用

按区划维度查询计划编制数据。需要先通过 zone 接口获取 `zoneId`，通过 project-summary 接口获取 `projectId`。

**Headers**

- `appKey` — API 密钥（必传）
- `Content-Type: application/json`
- `tenantId` — 租户ID（可选），默认无须传入，用户存在多个租户身份时须传入。如未传入具体tenantId，会返回用户可选择的租户列表。

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `zoneId` | String | 是 | 区划 ID，来自 zone 接口返回的 `id` |
| `projectId` | String | 是 | 项目 ID，来自 project-summary 接口返回的 `id` |
| `periodStart` | String | 是 | 周期开始时间 |
| `periodEnd` | String | 是 | 周期结束时间 |
| `schemaCode` | String | 否 | 模板编码 |
| `schemaVersion` | String | 否 | 模板版本 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["zoneId", "projectId", "periodStart", "periodEnd"],
  "properties": {
    "zoneId": { "type": "string", "description": "区划 ID" },
    "projectId": { "type": "string", "description": "项目 ID" },
    "periodStart": { "type": "string", "description": "周期开始时间" },
    "periodEnd": { "type": "string", "description": "周期结束时间" },
    "schemaCode": { "type": "string", "description": "模板编码" },
    "schemaVersion": { "type": "string", "description": "模板版本" },
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
          "zoneId": { "type": "string" },
          "zoneName": { "type": "string" },
          "pathIds": { "type": "string" },
          "pathNames": { "type": "string" },
          "projectId": { "type": "string" },
          "projectCode": { "type": "string" },
          "projectName": { "type": "string" },
          "periodCode": { "type": "string" },
          "periodName": { "type": "string" },
          "periodStart": { "type": "string" },
          "periodEnd": { "type": "string" },
          "schemaCode": { "type": "string" },
          "schemaName": { "type": "string" },
          "schemaVersion": { "type": "string" },
          "fieldValue": { "type": "object" },
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

- `../../scripts/sfe-zone/project-plan.py`
