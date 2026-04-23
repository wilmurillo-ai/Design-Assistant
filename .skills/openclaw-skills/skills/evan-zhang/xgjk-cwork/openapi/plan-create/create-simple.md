# POST https://cwork-web.mediportal.com.cn/cwork/report/save

## 作用
快速创建一个简单的“工作计划”汇报。

**Body**
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `title` | string | 是 | 计划标题 |
| `content` | string | 是 | 计划内容 |

## 脚本映射
- `../../scripts/plan-create/create-simple.py`
