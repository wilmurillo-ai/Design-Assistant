# GET https://cwork-web.mediportal.com.cn/cwork/report/inbox/list

## 作用
获取当前用户的收件箱汇报列表。

**Headers**
- `access-token`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 默认 1 |
| `pageSize` | number | 否 | 默认 10 |
| `searchKey` | string | 否 | 搜索关键词 |

## 脚本映射
- `../../scripts/inbox/get-list.py`
