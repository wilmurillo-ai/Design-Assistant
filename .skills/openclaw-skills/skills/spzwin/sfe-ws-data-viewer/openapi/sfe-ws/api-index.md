# SFE-WS API 索引

维盛专属数据查询接口索引。

**基 URL**: `https://erp-web.mediportal.com.cn/erp-open-api`

**认证**: 所有接口需要 `appKey` Header 鉴权。

---

## 接口列表

| 接口名称           | 接口地址                                                            | 文档链接                                | 脚本链接                                                   |
| ------------------ | ------------------------------------------------------------------- | --------------------------------------- | ---------------------------------------------------------- |
| 客户管理年度跟踪表 | `/bia/open/biz-service/sfe-ws-report/hcpManageYearlyTrackingReport` | [文档](./hcp-manage-yearly-tracking.md) | [脚本](../../scripts/sfe-ws/hcp-manage-yearly-tracking.py) |
| 医院管理年度跟踪表 | `/bia/open/biz-service/sfe-ws-report/hcoManageYearlyTrackingReport` | [文档](./hco-manage-yearly-tracking.md) | [脚本](../../scripts/sfe-ws/hco-manage-yearly-tracking.py) |
| 开发管理年度跟踪表 | `/bia/open/biz-service/sfe-ws-report/devManageYearlyTrackingReport` | [文档](./dev-manage-yearly-tracking.md) | [脚本](../../scripts/sfe-ws/dev-manage-yearly-tracking.py) |

---

## 通用说明

### 请求方式

所有接口使用 `POST` 方法，请求体为 JSON 格式。

### 认证 Header

```
appKey: <your_app_key>
Content-Type: application/json
```

### 分页

- 每页固定返回 1000 条记录
- 使用 `page` 参数控制页码（默认第 1 页）

### 查询总记录数

在接口地址后追加 `/count` 即可查询总记录数，返回格式：

```json
{
  "resultCode": "0",
  "resultMsg": "success",
  "data": 12345,
  "timestamp": 1234567890,
  "success": true
}
```

---

## 查询示例

### 查询客户管理年度跟踪表

```bash
python3 scripts/sfe-ws/hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
```

### 查询医院管理年度跟踪表

```bash
python3 scripts/sfe-ws/hco-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
```

### 查询开发管理年度跟踪表

```bash
python3 scripts/sfe-ws/dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --quarter 1
```
