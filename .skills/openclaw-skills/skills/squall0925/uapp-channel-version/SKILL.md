---
name: uapp-channel-version
version: 1.1.0
description: "友盟 App 渠道/版本分析 skill。当用户想了解各渠道或版本表现对比、单个渠道/版本的趋势时使用。触发词：渠道分析、版本分析、渠道对比、版本对比、哪个渠道、哪个版本、渠道排名、版本表现。"
entry: scripts/channel_version.py
---

## 使用流程

**Step 1：确认应用名称**
- 用户未提及应用名时，询问：「请问是哪个 App？」

**Step 2：确认分析维度和模式**
- 维度：渠道（`--dimension channel`）还是版本（`--dimension version`）
- 模式：单日快照（返回当日排名）或趋势分析（需要指定渠道/版本 + 时间范围）
- 若用户说“某渠道过去一周趋势”→ 需要渠道名，用 `--filter-channel` 指定

**Step 3：执行并解读输出**
- 单日快照：指出排名第一的渠道/版本及其关键数据
- 趋势分析：指出指标最高/最低点和整体走势

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 用户未说 App 名 | 先询问，不要猜测 |
| App 名找不到 | 提示「找不到该 App；可用 uapp-assets 查询应用列表」 |
| 渠道/版本名找不到 | 提示可先不加 filter 查询全局排名，确认实际渠道/版本名 |
| 返回数据为空 | 提示「该日期暂无数据，建议换昨天或近期日期查询」 |
| `launches` 指标用于版本维度 | 告知用户「`launches`仅渠道维度支持，版本维度请用 `active_users` 或 `new_users`」 |

## 典型问法与 CLI 参数映射

| 典型问法 | CLI 参数 |
|---------|---------|
| "各渠道昨天的新增用户对比？" | `--dimension channel --date yesterday --sort-by new_users` |
| "各版本活跃用户排名？" | `--dimension version --sort-by active_users` |
| "华为渠道过去一周的活跃用户怎样？" | `--dimension channel --metric active_users --range last_7_days --filter-channel huawei` |
| "3.5版本上线后用户表现如何？" | `--dimension version --metric new_users --range last_7_days --filter-version 3.5` |
| "Top 5 渠道的启动次数对比" | `--dimension channel --top 5 --sort-by launches` |
| "Umeng渠道昨天表现如何？" | `--dimension channel --filter-channel Umeng` |

## 查询模式

### 单日快照模式（默认）

查询指定日期的渠道/版本表现排名：

```bash
# 渠道快照（默认昨天）
python3 scripts/channel_version.py --app "Android_Demo" --dimension channel

# 版本快照，按新增用户排序
python3 scripts/channel_version.py --app "Android_Demo" --dimension version --sort-by new_users

# 指定日期，Top 5
python3 scripts/channel_version.py --app "Android_Demo" --dimension channel --date 2026-03-29 --top 5
```

### 趋势分析模式

查询指定渠道/版本的指标趋势：

```bash
# 渠道趋势
python3 scripts/channel_version.py --app "Android_Demo" --dimension channel \
    --metric new_users --range last_7_days --filter-channel Umeng

# 版本趋势
python3 scripts/channel_version.py --app "Android_Demo" --dimension version \
    --metric active_users --range last_30_days --filter-version 2.0.11001
```

## 支持的分析维度

- `channel`（默认）：渠道维度
- `version`：版本维度

## 支持的指标类型

### 单日快照模式

- `active_users`（默认）：活跃用户
- `new_users`：新增用户
- `launches`：启动次数（仅渠道维度）
- `total_user`：总用户

### 趋势分析模式

- `new_users`：新增用户
- `active_users`：活跃用户
- `launches`：启动次数

## 支持的时间范围

- `yesterday`：昨天
- `last_7_days`：过去7天
- `last_30_days`：过去30天
- `last_90_days`：过去90天
- `yyyy-mm-dd`：指定日期

## 配置方式

配置文件路径优先级：
1. `--config /path/to/umeng-config.json`
2. 环境变量 `UMENG_CONFIG_PATH`
3. 当前目录下的 `umeng-config.json`

## 输出格式

### 文本模式（默认）

```
应用 Android_Demo 的 渠道 表现对比（2026-03-29）：

排名     渠道                   新增用户     活跃用户     启动次数     总用户
--------------------------------------------------------------------------------
1      Umeng                15           311          2,579        928,529
2      umeng                2            261          815          306,487
...
```

### JSON 模式（--json）

```json
{
  "app": {
    "name": "Android_Demo",
    "appkey": "...",
    "platform": "Android"
  },
  "dimension": "channel",
  "date": "2026-03-29",
  "sort_by": "active_users",
  "count": 5,
  "data": [...]
}
```
