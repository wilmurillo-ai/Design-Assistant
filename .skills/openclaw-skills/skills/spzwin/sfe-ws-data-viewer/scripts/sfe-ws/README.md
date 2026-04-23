# SFE-WS 脚本说明

维盛专属数据查询脚本。

## 环境要求

- Python 3.8+
- requests 库：`pip install requests`

## 环境变量

```bash
export XG_BIZ_API_KEY="your-app-key"
```

## 脚本列表

| 脚本                          | 说明               |
| ----------------------------- | ------------------ |
| hcp-manage-yearly-tracking.py | 客户管理年度跟踪表 |
| hco-manage-yearly-tracking.py | 医院管理年度跟踪表 |
| dev-manage-yearly-tracking.py | 开发管理年度跟踪表 |

## 使用示例

### 客户管理年度跟踪表

```bash
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --quarter 1
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```

### 医院管理年度跟踪表

```bash
python3 hco-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
python3 hco-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```

### 开发管理年度跟踪表

```bash
python3 dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
python3 dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --quarter 1
python3 dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```

## 参数说明

| 参数      | 必填 | 说明         |
| --------- | ---- | ------------ |
| --zoneId  | 是   | 区划ID       |
| --year    | 否   | 年度         |
| --quarter | 否   | 季度         |
| --page    | 否   | 页码，默认1  |
| --count   | 否   | 查询总记录数 |
