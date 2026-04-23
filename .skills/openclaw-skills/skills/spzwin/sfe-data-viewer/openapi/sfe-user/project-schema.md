# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-schema

## 作用

获取项目数据字段的 JSON Schema 定义。需要先通过 project-summary 接口获取 `projectId`。返回的 `schemas[].code` 可用于后续接口的 `schemaCode` 参数。

**Headers**
- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `projectId` | String | 否 | 项目 ID，来自 project-summary 接口返回的 `id` |
| `schemaCode` | String | 否 | 模板编码 |
| `schemaName` | String | 否 | 模板名称 |
| `schemaVersion` | String | 否 | 模板版本 |

## 请求 Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "projectId": { "type": "string", "description": "项目 ID" },
    "schemaCode": { "type": "string", "description": "模板编码" },
    "schemaName": { "type": "string", "description": "模板名称" },
    "schemaVersion": { "type": "string", "description": "模板版本" }
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
          "schemas": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "code": { "type": "string" },
                "name": { "type": "string" },
                "version": { "type": "string" },
                "field": { "type": "object" }
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

- `../../scripts/sfe-user/project-schema.py`
