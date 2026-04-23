# POST https://cwork-web.mediportal.com.cn/cwork/report/todo/complete

## 作用
完成或撤销完成一个待办事项。

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `todoId` | string | 是 | 待办 ID |
| `isComplete` | boolean | 是 | 完成状态 (true/false) |

## 脚本映射
- `../../scripts/todos/complete.py`
