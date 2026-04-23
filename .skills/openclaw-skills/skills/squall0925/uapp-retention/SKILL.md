---
name: uapp-retention
version: 1.1.0
description: "友盟 App 留存率查询与对比分析 skill。当用户询问次日留存、第7日留存、版本/渠道维度留存对比时使用。触发词：留存、次日留存、7日留存30日留存、留存率、留存趋势、版本留存、渠道留存。"
entry: scripts/retention.py
---

## 使用流程

**Step 1：确认应用名称**
- 用户未提及应用名时，询问：「请问是哪个 App？」

**Step 2：确认留存参数**
- 留存天数（默认次日=1）：口语中“次日”→`1`，“7日”→`7`，“月”→`30`
- 留存类型：新增用户（默认）还是活跃用户？
- 时间范围：未提及则默认 `last_7_days`
- 版本/渠道筛选：如用户提及具体版本或渠道名，加入 `--version` / `--channel`

**Step 3：执行并解读输出**
- 返回留存率时，指出日均留存率、最高/最低点和整体走势
- 如有明显下降/上升，给出简短分析建议

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 用户未说 App 名 | 先询问，不要猜测 |
| App 名找不到 | 提示「可用 uapp-assets 查询应用列表」 |
| 返回数据为空 | 提示「留存数据通常延迟一天，建议查询 last_7_days 或更早日期」 |
| 查询今天/昨天留存 | 说明留存数据需要相应留存天数后才能生成，建议用 `last_7_days` 查询趋势 |
| 版本/渠道名不确定 | 建议先用 `--list-versions` / `--list-channels` 查询实际存在的列表 |
| 山张和 `last_7_days` 返回空表 | API `totalCount` 字段不可靠，无需告知用户分页细节，权当输出为准 |

## 典型问法与 CLI 参数映射

| 典型问法 | CLI 参数 |
|---------|---------|
| "昨天 DAU 的次日留存多少？" | `--retention-day 1 --range yesterday` |
| "过去7天的7日留存趋势？" | `--retention-day 7 --range last_7_days` |
| "最近一个月的30日留存？" | `--retention-day 30 --range last_30_days` |
| "活跃用户的次日留存？" | `--retention-type active --retention-day 1 --range yesterday` |
| "按周看的7日留存趋势？" | `--retention-day 7 --period week --range last_90_days` |
| "3.2版本的次日留存怎么样？" | `--retention-day 1 --version "3.2" --range last_7_days` |
| "GooglePlay渠道的7日留存？" | `--retention-day 7 --channel "GooglePlay" --range last_7_days` |
| "3.2版本在GooglePlay的次日留存？" | `--retention-day 1 --version "3.2" --channel "GooglePlay" --range last_7_days` |
| "有哪些版本？" | `--list-versions` |
| "有哪些渠道？" | `--list-channels` |
| "3.2和3.1版本的次日留存对比？" | `--retention-day 1 --compare-versions "3.2,3.1" --range last_7_days` |
| "GooglePlay和AppStore的7日留存对比？" | `--retention-day 7 --compare-channels "GooglePlay,AppStore" --range last_7_days` |

## 支持的留存类型

- `new`（默认）：新增用户留存
- `active`：活跃用户留存

## 支持的留存天数

- `1`：次日留存（默认）
- `3`：3日留存
- `7`：7日留存
- `14`：14日留存
- `30`：30日留存

## 支持的周期类型

- `day`（默认）：按日聚合
- `week`：按周聚合
- `month`：按月聚合

## 使用示例

```bash
# 基础留存查询
python3 scripts/retention.py --app "Android_Demo" --retention-day 7 --range last_30_days

# 活跃用户留存
python3 scripts/retention.py --app "Android_Demo" --retention-type active --retention-day 1 --range yesterday

# 版本筛选
python3 scripts/retention.py --app "Android_Demo" --version "2.0.11001" --retention-day 1 --range last_7_days

# 渠道筛选
python3 scripts/retention.py --app "Android_Demo" --channel "GooglePlay" --retention-day 7 --range last_7_days

# 二维组合筛选
python3 scripts/retention.py --app "Android_Demo" --version "2.0.11001" --channel "GooglePlay" --retention-day 1 --range last_7_days

# 版本列表
python3 scripts/retention.py --app "Android_Demo" --list-versions

# 版本对比
python3 scripts/retention.py --app "Android_Demo" --compare-versions "2.0.11001,1.0,1.1.1" --retention-day 1 --range last_7_days

# JSON 输出
python3 scripts/retention.py --app "Android_Demo" --retention-day 7 --range last_7_days --json
```

## 配置方式

配置文件路径优先级：
1. `--config /path/to/umeng-config.json`
2. 环境变量 `UMENG_CONFIG_PATH`
3. 当前目录下的 `umeng-config.json`

## 输出格式

### 文本模式（默认）

```
应用 Android_Demo 在 2026-02-28 至 2026-03-29 的 7日留存（新增用户，按日）
日均 14.01%，从 35.61% 变化到 6.19%，整体呈下降趋势，末期较初期下降 82.6%。
新增用户基数：日均 70 人。
```

### JSON 模式（--json）

```json
{
  "app": {
    "name": "Android_Demo",
    "appkey": "...",
    "platform": "Android"
  },
  "retention_type": "new",
  "retention_day": 7,
  "period": "day",
  "version": null,
  "channel": null,
  "start_date": "2026-02-28",
  "end_date": "2026-03-29",
  "series": [
    {
      "date": "2026-03-01",
      "retention_rate": 27.27,
      "total_install_user": 132,
      "raw": {...}
    }
  ]
}
```
