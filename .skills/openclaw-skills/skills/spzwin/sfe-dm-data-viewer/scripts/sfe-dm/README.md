# 脚本清单 — sfe-dm

## 共享依赖

- `../common/toon_encoder.py` — TOON 编码器，所有脚本的 API 响应必须经过此编码器转换后再输出

## 脚本列表

| 脚本                                 | 对应接口                                            | 用途                       |
| ------------------------------------ | --------------------------------------------------- | -------------------------- |
| `balutamide-daily-feedback.py`       | `POST /balutamideDailyCollectionFeedback`           | 查询百卢妥日采集反馈数据   |
| `balutamide-statistics-by-region.py` | `POST /balutamideDailyCollectionStatisticsByRegion` | 查询百卢妥日采集按大区统计 |

## 使用方式

```bash
# 设置环境变量
export XG_BIZ_API_KEY="your-appkey"

# 查询百卢妥日采集反馈数据
python3 scripts/sfe-dm/balutamide-daily-feedback.py --periodStart 2025-01-01 --periodEnd 2025-01-31

# 查询总记录数
python3 scripts/sfe-dm/balutamide-daily-feedback.py --count --periodStart 2025-01-01 --periodEnd 2025-01-31

# 查询百卢妥日采集按大区统计
python3 scripts/sfe-dm/balutamide-statistics-by-region.py --periodStart 2025-01-01 --periodEnd 2025-01-31

# 查询总记录数
python3 scripts/sfe-dm/balutamide-statistics-by-region.py --count --periodStart 2025-01-01 --periodEnd 2025-01-31
```

## 输出说明

所有脚本的输出均为 **TOON 格式**（非原始 JSON），这是一种面向 LLM 的高密度压缩格式，可大幅节省 Token 消耗。

## 参数说明

### balutamide-daily-feedback

| 参数            | 类型    | 说明                         |
| --------------- | ------- | ---------------------------- |
| `--count`       | Flag    | 查询总记录数（不加则查列表） |
| `--zoneId`      | String  | 区划 ID                      |
| `--regionName`  | String  | 大区名称，支持模糊查询       |
| `--areaName`    | String  | 地区名称，支持模糊查询       |
| `--periodStart` | String  | 期间开始日期                 |
| `--periodEnd`   | String  | 期间结束日期                 |
| `--page`        | Integer | 页码，默认第 1 页            |

### balutamide-statistics-by-region

| 参数            | 类型    | 说明                         |
| --------------- | ------- | ---------------------------- |
| `--count`       | Flag    | 查询总记录数（不加则查列表） |
| `--regionName`  | String  | 大区名称，支持模糊查询       |
| `--periodStart` | String  | 期间开始日期                 |
| `--periodEnd`   | String  | 期间结束日期                 |
| `--page`        | Integer | 页码，默认第 1 页            |

## 规范

1. **必须使用 Python** 编写
2. **必须经过 toon_encoder** 处理后再输出
3. **鉴权遵循** `cms-auth-skills/SKILL.md` 规范
4. **入参定义以** `openapi/` 文档为准
