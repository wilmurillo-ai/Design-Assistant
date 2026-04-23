# GET https://cwork-web.mediportal.com.cn/cwork/report/task/page

## 作用
按页获取工作任务列表。

**Headers**
- `access-token`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 默认 1 |
| `pageSize` | number | 否 | 默认 10 |
| `searchKey` | string | 否 | 搜索关键词 |
| `status` | string | 否 | 状态 (INIT, RUNNING, DONE, CANCELLED) |

## 脚本映射
- `../../scripts/tasks/get-page.py`
