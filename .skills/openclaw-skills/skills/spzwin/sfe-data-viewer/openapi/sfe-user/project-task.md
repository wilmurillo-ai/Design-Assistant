# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-task

## 作用

获取用户的待处理/已完成的任务列表。需要先通过 project-summary 接口获取 `projectId`。

**Headers**
- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `projectId` | String | 否 | 项目 ID，来自 project-summary 接口返回的 `id` |
| `periodStart` | String | 否 | 周期开始时间 |
| `periodEnd` | String | 否 | 周期结束时间 |
| `status` | Integer | 否 | 状态：0-待处理，1-已完成，2-已取消，3-过期关闭，4-手工关闭，默认查询全部数据 |
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
    "status": { "type": "integer", "enum": [0, 1, 2, 3, 4] },
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
          "projectId": { "type": "string" },
          "tasks": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "id": { "type": "string" },
                "name": { "type": "string" },
                "startDate": { "type": "string" },
                "endDate": { "type": "string" },
                "zoneId": { "type": "string" },
                "periodCode": { "type": "string" },
                "schemaCode": { "type": "string" },
                "status": { "type": "integer" },
                "createTime": { "type": "string" },
                "updateTime": { "type": "string" }
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

- `../../scripts/sfe-user/project-task.py`
