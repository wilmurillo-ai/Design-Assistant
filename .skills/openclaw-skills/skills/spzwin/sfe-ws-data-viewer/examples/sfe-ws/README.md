# SFE-WS 示例说明

维盛专属数据查询示例。

## 前置条件

1. 已配置环境变量 `XG_BIZ_API_KEY`
2. 已安装 Python 3.8+ 和 requests 库

## 快速开始

### 1. 客户管理年度跟踪表

查询2025年Q1季度数据：

```bash
cd scripts/sfe-ws
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --quarter 1
```

查询总记录数：

```bash
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --count
```

### 2. 医院管理年度跟踪表

查询2025年数据：

```bash
python3 hco-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025
```

### 3. 开发管理年度跟踪表

查询2025年Q1季度数据：

```bash
python3 dev-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --quarter 1
```

## 分页查询

每页返回1000条记录，大数据量需要分页：

```bash
# 第1页
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --page 1

# 第2页
python3 hcp-manage-yearly-tracking.py --zoneId "your-zone-id" --year 2025 --page 2
```

## 输出格式

脚本输出采用 TOON 编码格式，便于大语言模型阅读和处理。
