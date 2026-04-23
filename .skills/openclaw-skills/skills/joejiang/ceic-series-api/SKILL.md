---
name: ceic-series-api
description: CEIC 宏观经济数据 API 客户端。用于搜索数列、获取元数据和时间序列数据。仅覆盖三个核心 GET 接口：/series/search（搜索）、/series/{id}（元数据 + 数据）、/series/{id}/data（仅数据）。需要 API token 认证。
---

# CEIC Series API Skill

极简封装 CEIC API v2 的三个核心接口，用于获取宏观经济时间序列数据。

## 认证

所有请求需要 API token，通过以下方式之一提供：
- 查询参数：`?token=YOUR_API_KEY`
- HTTP Header：`Authorization: Bearer YOUR_API_KEY`

获取 token：登录 CEIC Insights → 用户菜单 → 生成 API Key

## 基础 URL

```
https://api.ceicdata.com/v2
```

## 三个核心接口

### 1. GET /series/search - 搜索数列

**功能**：按关键字和筛选条件搜索 CEIC 数据库中的时间序列。

**常用参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `keyword` | 关键字搜索 | `GDP`, `CPI`, `unemployment` |
| `country` | 国家代码（逗号分隔） | `CN`, `US`, `144`（中国） |
| `frequency` | 频率代码 | `A`(年), `Q`(季), `M`(月) |
| `indicator` | 指标分类代码 | 参见 `/dictionary/indicators` |
| `limit` | 返回数量上限 | `10`, `50`, `100` |
| `offset` | 分页偏移 | `0`, `50`, `100` |

**示例请求**：
```bash
curl "https://api.ceicdata.com/v2/series/search?keyword=GDP&country=CN&frequency=Q&limit=10&token=YOUR_TOKEN"
```

**响应结构**：
```json
{
  "series": [
    {
      "id": 123456,
      "name": "China GDP Quarterly Growth",
      "country": {"code": "CN", "name": "China"},
      "frequency": {"code": "Q", "name": "Quarterly"},
      "unit": {"code": "PC", "name": "Percent Change"},
      "source": {"name": "National Bureau of Statistics"},
      "startDate": "2010-03-31",
      "endDate": "2025-12-31"
    }
  ],
  "totalCount": 150
}
```

---

### 2. GET /series/{id} - 获取数列（元数据 + 数据）

**功能**：获取单个数列的完整信息，包括元数据和时间点数据。

**常用参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `seriesId` | 数列 ID（必填） | `123456` |
| `withObservations` | 是否包含数据点 | `true`/`false` |
| `observationsStartDateFilter` | 数据起始日期 | `2020-01-01` |
| `observationsEndDateFilter` | 数据结束日期 | `2025-12-31` |
| `blankObservations` | 是否包含空值 | `true`/`false` |

**示例请求**：
```bash
curl "https://api.ceicdata.com/v2/series/123456?withObservations=true&observationsStartDateFilter=2020-01-01&token=YOUR_TOKEN"
```

**响应结构**：
```json
{
  "series": {
    "id": 123456,
    "name": "China GDP Quarterly Growth",
    "frequency": {"code": "Q"},
    "observations": [
      {"date": "2020-03-31", "value": 6.8},
      {"date": "2020-06-30", "value": 3.2},
      {"date": "2020-09-30", "value": 4.9}
    ]
  }
}
```

---

### 3. GET /series/{id}/data - 仅获取数据点

**功能**：仅获取数列的时间点数据，不包含元数据（更轻量）。

**常用参数**：
| 参数 | 说明 | 示例 |
|------|------|------|
| `seriesId` | 数列 ID（必填） | `123456` |
| `observationsStartDateFilter` | 数据起始日期 | `2020-01-01` |
| `observationsEndDateFilter` | 数据结束日期 | `2025-12-31` |
| `blankObservations` | 是否包含空值 | `false` |

**示例请求**：
```bash
curl "https://api.ceicdata.com/v2/series/123456/data?observationsStartDateFilter=2020-01-01&token=YOUR_TOKEN"
```

**响应结构**：
```json
{
  "series": {
    "id": 123456,
    "observations": [
      {"date": "2020-03-31", "value": 6.8},
      {"date": "2020-06-30", "value": 3.2}
    ]
  }
}
```

---

## 使用场景

| 用户需求 | 推荐接口 |
|----------|----------|
| "查找中国 GDP 数据" | `/series/search?keyword=GDP&country=CN` |
| "获取某个数列的详细信息" | `/series/{id}` |
| "只想要数据，不要元数据" | `/series/{id}/data` |
| "获取 2020 年以来的数据" | `/series/{id}/data?observationsStartDateFilter=2020-01-01` |

## 辅助接口（字典查询）

获取筛选条件的有效代码值：

- `/dictionary/countries` - 国家列表
- `/dictionary/frequencies` - 频率列表（A/Q/M/W/D）
- `/dictionary/indicators` - 指标分类
- `/dictionary/sources` - 数据来源
- `/dictionary/units` - 单位

## 错误处理

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败（token 无效） |
| 403 | 权限不足（未订阅该数据） |
| 404 | 数列不存在 |
| 429 | 请求频率超限 |

## 注意事项

1. **日期格式**：ISO 8601 (`YYYY-MM-DD`)
2. **多值参数**：用逗号分隔，如 `country=CN,US,JP`
3. **分页**：使用 `limit` + `offset`
4. **订阅限制**：部分数据需要相应订阅权限
