# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-user/project-summary

## 作用

获取用户参与的数据采集项目列表，包含项目基本信息与周期配置。返回的 `id` 可用于后续接口的 `projectId` 参数。

**Headers**

- `appKey` — API 密钥（必传）
- `Content-Type: application/json`
- `tenantId` — 租户ID（可选），默认无须传入，用户存在多个租户身份时须传入。如未传入具体tenantId，会返回用户可选择的租户列表。

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | String | 否 | 项目 ID，用于精确查询 |
| `code` | String | 否 | 项目编码 |
| `name` | String | 否 | 项目名称，支持模糊查询 |
| `status` | Integer | 否 | 状态：0-禁用，1-启用，默认查询 `status=1` 的启用数据 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "id": { "type": "string", "description": "项目 ID" },
    "code": { "type": "string", "description": "项目编码" },
    "name": { "type": "string", "description": "项目名称" },
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
          "code": { "type": "string" },
          "name": { "type": "string" },
          "type": { "type": "string" },
          "startDate": { "type": "string" },
          "endDate": { "type": "string" },
          "isRepeatCycle": { "type": "boolean" },
          "cycleUnit": { "type": "string" },
          "isExcludeNonWorkingDays": { "type": "boolean" },
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

- `../../scripts/sfe-user/project-summary.py`
