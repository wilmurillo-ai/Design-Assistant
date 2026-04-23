---
name: uapp-core-index
version: 1.1.0
description: "友盟 App 核心指标问答入口 skill。当用户询问 App 的 DAU、日活、新增用户、启动次数、使用时长等核心运营指标时使用。触发词：DAU、日活、新增用户、活跃用户、启动次数、使用时长、核心指标、昨天数据、过去7天、上周、最近30天。"
entry: scripts/core_index.py
---

## 使用流程

**Step 1：确认 App 名称**
- 用户未提及 App 名时，询问：「请问是哪个 App？」
- App 名称支持模糊匹配（去除空格后不区分大小写），不需要完全精确

**Step 2：确认指标与时间范围**
- 根据用户问法，从下方参数表中选取对应的 `--metric` 和 `--range`
- 若问法模糊（如「最近的数据」），默认使用 `--range yesterday`

**Step 3：执行命令并解读输出**
- 执行命令后，用自然语言总结关键数字（不要直接贴原始输出）
- 有趋势数据时，指出最高/最低点和整体走势

## 参数速查

### 指标类型（--metric）

| 值 | 含义 |
|---|------|
| `dau` | 活跃用户数 |
| `new_users` | 新增用户数 |
| `launches` | 启动次数 |
| `duration` | 平均使用时长（秒） |

### 时间范围（--range）

| 值 | 含义 |
|---|------|
| `yesterday` | 昨天 |
| `last_7_days` | 过去7天（含昨天） |
| `last_30_days` | 过去30天（含昨天） |
| `last_week` | 上周（周一至周日） |
| `today_yesterday` | 今天 vs 昨天对比 |
| `yyyy-mm-dd` | 指定日期，如 `2026-03-25` |

### 典型问法与参数对照

| 典型问法 | CLI 参数 |
|---------|----------|
| "昨天 DAU 多少？" | `--metric dau --range yesterday` |
| "过去7天新增用户趋势" | `--metric new_users --range last_7_days` |
| "上周日均启动次数" | `--metric launches --range last_week` |
| "最近30天使用时长变化" | `--metric duration --range last_30_days` |
| "今天和昨天 DAU 对比" | `--metric dau --range today_yesterday` |

## 边界条件与异常处理

| 情形 | 处理方式 |
|------|----------|
| 用户未说 App 名 | 先询问，不要猜测 |
| App 名找不到匹配 | 提示「找不到该 App，请确认名称；可用 uapp-assets 查询所有 App 列表」 |
| 返回数据为空 | 提示「该时段暂无数据，可能是当天数据还未同步，建议查询昨天或更早的日期」 |
| 日期格式错误 | 提示正确格式为 `yyyy-mm-dd`，如 `2026-03-25` |
| 今天数据为0或极低 | 说明友盟数据存在延迟，今日数据通常次日才完整 |

## 调用示例

```bash
# 昨天 DAU（文本输出）
python3 scripts/core_index.py --metric dau --range yesterday --app "Android_Demo"

# 过去7天新增用户（JSON 输出）
python3 scripts/core_index.py --metric new_users --range last_7_days --app "Android_Demo" --json

# 上周日均启动次数
python3 scripts/core_index.py --metric launches --range last_week --app "Android_Demo"

# 今天 vs 昨天 DAU 对比
python3 scripts/core_index.py --metric dau --range today_yesterday --app "Android_Demo"
```

## 配置方式

1. `--config /path/to/umeng-config.json`：显式指定配置文件
2. `export UMENG_CONFIG_PATH=/path/to/umeng-config.json`：环境变量
3. 在当前目录创建 `umeng-config.json`：默认查找

配置文件格式参见项目根目录 `umeng-config.json` 示例。
