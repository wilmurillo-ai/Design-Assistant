# 脚本清单 — user-search

## 脚本列表

| 脚本 | 对应接口 | 用途 |
|---|---|---|
| `search-emp.py` | `GET /user/search/emp` | 根据姓名搜索员工 |

## 使用方式
```bash
export XG_USER_TOKEN="your-token"
python3 scripts/user-search/search-emp.py "张三"
```
