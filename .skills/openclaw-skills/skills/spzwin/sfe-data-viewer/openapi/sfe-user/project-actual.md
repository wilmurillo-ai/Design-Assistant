# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-actual

## 作用

获取用户在目标管理类项目中提交的实际结果数据。需要先通过 project-summary 接口获取 `projectId`。

**Headers**
- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `projectId` | String | 否 | 项目 ID，来自 project-summary 接口返回的 `id` |
| `periodStart` | String | 否 | 周期开始时间 |
| `periodEnd` | String | 否 | 周期结束时间 |
| `schemaCode` | String | 否 | 模板编码，来自 project-schema 接口返回的 `code` |
| `schemaVersion` | String | 否 | 模板版本 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
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

- `../../scripts/sfe-user/project-actual.py`
