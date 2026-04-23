# API 接口文档

## Base URL
`https://h5.wintaocloud.com/prod-api/api/invoke`

## 认证
所有请求都需要携带 Bearer Token 认证：
```
Authorization: Bearer {api_key}
```

---

## 1. /fuzzy-search-org - 企业模糊搜索

### 功能说明
根据企业名称关键词模糊搜索企业，返回企业列表，其中返回orgId和orgName用于后续接口调用。

### 请求方式
`GET`

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| searchKey | string | 是 | 搜索关键词，最少 2 个字符 |
| pageNum | integer | 否 | 分页页码，默认 `1`，每页固定返回 5 条数据 |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "orgId": "xxxxxxxx",
        "orgName": "腾讯科技(深圳)有限公司",
        "creditCode": "91440300710933597U",
        "establishDate": "1998-11-11",
        "region": "广东省深圳市"
      }
    ],
    "total": 10,
    "pageNum": 1,
    "pageSize": 5
  }
}
```

### 说明
- 如果搜索结果为空，提示用户增加关键字或调整搜索词
- 如果搜索结果有多条，列出所有结果让用户选择确认
- 如果总条数超过当前页，提示用户可以查询下一页

---

## 2. /get-punishments - 查询行政处罚

### 功能说明
根据企业名称查询该企业的行政处罚记录。

### 请求方式
`GET`

### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| searchKey | string | 是 | 企业名称，从 `/fuzzy-search-org` 搜索结果中获取 |
| pageNum | integer | 否 | 分页起始页，默认 `1` |
| pageSize | integer | 否 | 每页条数，最大 `20`，默认 `10` |

### 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "punishNo": "银保监银罚决字〔2018〕XX号",
        "illegalFact": "贷款业务严重违反审慎经营规则。",
        "punishResult": "处罚结果",
        "unitName": "XXXXXX局",
        "punishTime": "2018-11-09",
        "punishAmount": "处罚金额"
      }
    ],
    "total": 10,
    "pageNum": 1,
    "pageSize": 10
  }
}
```

---

## 后续接口

更多接口将陆续接入，更新此文档保持同步。
