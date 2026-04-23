# GET https://cwork-web.mediportal.com.cn/cwork/report/todo/list

## 作用
获取待办事项列表。

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 页码（默认 1） |
| `pageSize` | number | 否 | 每页条数（默认 10） |
| `status` | string | 否 | 筛选状态 (DONE, INIT) |

## 脚本映射
- `../../scripts/todos/get-list.py`
