# GET https://cwork-web.mediportal.com.cn/cwork/report/template/list

## 作用
获取所有可用的汇报模板清单（如“日工作汇报”、“量化交易总结”等）。

**Query 参数**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `pageIndex` | number | 否 | 页码 (默认 1) |
| `pageSize` | number | 否 | 每页条数 (默认 50) |
| `searchKey` | string | 否 | 模板名称关键词搜索 |

## 脚本映射
- `../../scripts/templates/get-list.py`
