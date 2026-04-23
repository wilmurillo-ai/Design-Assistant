# GET https://cwork-web.mediportal.com.cn/user/search/emp

## 作用

根据姓名模糊搜索企业内部员工，返回员工基本信息（含 userId, personId, empName, deptName 等）。

**Headers**
- `access-token`
- `Content-Type: application/json`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `name` | string | 是 | 员工姓名关键词（如"张三"） |

## 请求 Schema
```json
{
 "$schema": "http://json-schema.org/draft-07/schema#",
 "type": "object",
 "required": ["name"],
 "properties": {
 "name": { "type": "string", "description": "搜索关键词" }
 }
}
```

## 响应 Schema
```json
{
 "$schema": "http://json-schema.org/draft-07/schema#",
 "type": "object",
 "properties": {
 "resultCode": { "type": "number" },
 "data": {
 "type": "array",
 "items": {
 "type": "object",
 "properties": {
 "empName": { "type": "string" },
 "deptName": { "type": "string" },
 "personId": { "type": "string" },
 "userId": { "type": "string" }
 }
 }
 }
 }
}
```

## 脚本映射

- `../../scripts/user-search/search-emp.py`
