# POST https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionFeedback

## 作用

查询百卢妥日采集反馈数据（德镁专属）。

**Headers**

- `appKey` — API 密钥（必传）
- `Content-Type: application/json`

**Body 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `zoneId` | String | 否 | 区划 ID |
| `regionName` | String | 否 | 大区名称，支持模糊查询 |
| `areaName` | String | 否 | 地区名称，支持模糊查询 |
| `periodStart` | String | 否 | 期间开始日期 |
| `periodEnd` | String | 否 | 期间结束日期 |
| `page` | Integer | 否 | 页码，默认第 1 页 |

## 请求 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "zoneId": { "type": "string", "description": "区划 ID" },
    "regionName": { "type": "string", "description": "大区名称，支持模糊查询" },
    "areaName": { "type": "string", "description": "地区名称，支持模糊查询" },
    "periodStart": { "type": "string", "description": "期间开始日期" },
    "periodEnd": { "type": "string", "description": "期间结束日期" },
    "page": {
      "type": "integer",
      "minimum": 1,
      "description": "页码，默认第 1 页"
    }
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
          "regionName": { "type": "string", "description": "大区" },
          "areaName": { "type": "string", "description": "地区" },
          "date": { "type": "string", "description": "日期" },
          "newPatientReservesProCount": {
            "type": "number",
            "description": "新增患者储备PRO拉新人数"
          },
          "newPatientReservesWeComCount": {
            "type": "number",
            "description": "新增患者储备企微拉新人数"
          },
          "newPatientReservesTotal": {
            "type": "number",
            "description": "新增患者储备总数"
          },
          "onlinePrescriptionCount": {
            "type": "number",
            "description": "线上处方支数"
          },
          "offlinePrescriptionCount": {
            "type": "number",
            "description": "线下处方支数"
          },
          "prescriptionTotal": {
            "type": "number",
            "description": "处方支数总数"
          }
        }
      }
    },
    "timestamp": { "type": "number" },
    "success": { "type": "boolean" }
  }
}
```

## 响应字段说明

| 字段名                         | 类型   | 说明                     |
| ------------------------------ | ------ | ------------------------ |
| `regionName`                   | String | 大区                     |
| `areaName`                     | String | 地区                     |
| `date`                         | Date   | 日期                     |
| `newPatientReservesProCount`   | Number | 新增患者储备PRO拉新人数  |
| `newPatientReservesWeComCount` | Number | 新增患者储备企微拉新人数 |
| `newPatientReservesTotal`      | Number | 新增患者储备总数         |
| `onlinePrescriptionCount`      | Number | 线上处方支数             |
| `offlinePrescriptionCount`     | Number | 线下处方支数             |
| `prescriptionTotal`            | Number | 处方支数总数             |

## 请求示例

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionFeedback' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

## 响应示例

```json
{
  "resultCode": 1,
  "resultMsg": "操作成功",
  "data": [
    {
      "regionName": "华东大区",
      "areaName": "上海地区",
      "date": "2025-01-15",
      "newPatientReservesProCount": 10,
      "newPatientReservesWeComCount": 8,
      "newPatientReservesTotal": 18,
      "onlinePrescriptionCount": 20,
      "offlinePrescriptionCount": 12,
      "prescriptionTotal": 32
    }
  ],
  "timestamp": 1774003758844,
  "success": true
}
```

## 查询总记录数

可在 URL 后添加 `/count` 查询总记录数：

```bash
curl -X POST 'https://erp-web.mediportal.com.cn/erp-open-api/bia/open/biz-service/sfe-dm-report/balutamideDailyCollectionFeedback/count' \
  -H 'appKey: XXXXXXXX' \
  -H 'Content-Type: application/json' \
  -d '{
    "periodStart": "2025-01-01",
    "periodEnd": "2025-01-31"
  }'
```

## 脚本映射

- `../../scripts/sfe-dm/balutamide-daily-feedback.py`
