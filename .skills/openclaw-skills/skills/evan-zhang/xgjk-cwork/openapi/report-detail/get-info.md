# GET https://cwork-web.mediportal.com.cn/cwork/report/info

## 作用
获取指定汇报的完整结构化详情，包含汇报人、时间、各层级内容及结果。

**Headers**
- `access-token`

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `reportId` | string | 是 | 汇报 ID |

## 脚本映射
- `../../scripts/report-detail/get-info.py`
