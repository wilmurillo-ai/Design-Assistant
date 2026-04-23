# Lota Football API 参考文档

## API 概览
Lota Football API 提供足球比赛数据查询服务，包括比赛列表、特征文本、预测结果等。

## 基础URL
```
http://deepdata.lota.tv/  # 默认值，可通过 LOTA_API_BASE_URL 环境变量覆盖
```

## 认证方式
支持三种认证方式（任选其一）：

1. **Header方式（推荐）**
```bash
curl -H "X-API-Key: your_api_key" ...
```

2. **Bearer Token方式**
```bash
curl -H "Authorization: Bearer your_api_key" ...
```

3. **查询参数方式**
```bash
curl "https://...?api_key=your_api_key"
```

## 比赛查询API
**接口路径**: `GET /predictions/api/v2/matches/`

### 参数说明
| 参数名 | 说明 | 必需 | 示例 | 默认值 |
|--------|------|------|------|--------|
| `league` | 联赛名称（模糊匹配） | 否 | `league=英超` | - |
| `start_date` | 开始日期（ISO格式） | 否 | `start_date=2025-03-15` | - |
| `end_date` | 结束日期（ISO格式） | 否 | `end_date=2025-03-16` | - |
| `limit` | 返回条数 | 否 | `limit=100` | 500 |
| `offset` | 偏移量 | 否 | `offset=50` | 0 |
| `is_beidan` | 是否北单比赛 | 否 | `is_beidan=true` | - |
| `is_jingcai` | 是否竞彩比赛 | 否 | `is_jingcai=true` | - |
| `status` | 比赛状态 | 否 | `status=未开始` | - |
| `lota_id` | 比赛ID | 否 | `lota_id=LotaXXXXXXX` | - |

**注意**：
1. 如不设定 `start_date` 和 `end_date`，默认返回未来10小时的比赛
2. 指定 `lota_id` 后其他参数都会失效，只返回该场比赛

### 响应格式
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "matches": [
      {
        "lota_id": "Lota4343308",
        "home_name": "曼联",
        "away_name": "切尔西",
        "league_name": "英超",
        "match_time": "2025-03-15T20:00:00",
        "state_name": "未开赛",
        "jingcai_id": "001",
        "beidan_id": "101"
      }
    ],
    "total": 1
  }
}
```

### 使用示例
```bash
# 查询今天英超比赛
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?league=英超&limit=50"

# 查询明天竞彩比赛
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?is_jingcai=true&limit=100"

# 查询指定日期范围的比赛
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/matches/?start_date=2024-01-01&end_date=2024-01-07"
```

## 紧凑版特征文本API
**⚠️ 重要提示**：必须使用**查询参数**格式，不支持路径参数格式！

**正确格式**: `GET /predictions/api/v2/compact-fet/?lota_id=LotaXXXXXXX`
**错误格式**: `GET /predictions/api/v2/compact-fet/LotaXXXXXXX/` （❌ 不支持）

### 参数说明
| 参数名 | 说明 | 必需 | 示例 |
|--------|------|------|------|
| `lota_id` | 比赛ID（以"Lota"开头） | ✅ | `lota_id=Lota4343308` |

### 响应格式
```json
{
  "success": true,
  "compact_fet": "比赛特征文本...",
  "lota_id": "Lota4343308"
}
```

### 使用示例
```bash
# 方式1：Header认证（推荐）
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=Lota4343308"

# 方式2：Bearer Token认证
curl -H "Authorization: Bearer $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=Lota4343308"

# 方式3：查询参数认证
curl "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=Lota4343308&api_key=$LOTA_API_KEY"

# 带详细输出的调试模式
curl -v -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/compact-fet/?lota_id=Lota4343308"
```

## 预测查询API
**接口路径**: `GET /predictions/api/v2/predictions/`

### 参数说明
| 参数名 | 说明 | 必需 | 示例 |
|--------|------|------|------|
| `lota_id` | 比赛ID | 否 | `lota_id=Lota4343308` |
| `model_name` | 模型名称 | 否 | `model_name=rf_v1` |
| `prediction_type` | 预测类型 | 否 | `prediction_type=eu_pred` |
| `date_from` | 开始日期 | 否 | `date_from=2024-01-01` |
| `date_to` | 结束日期 | 否 | `date_to=2024-01-31` |
| `limit` | 返回条数 | 否 | `limit=50` | 20 |
| `offset` | 偏移量 | 否 | `offset=10` | 0 |

### 使用示例
```bash
# 查询指定比赛的预测
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/predictions/?lota_id=Lota4343308"

# 查询指定模型的预测
curl -H "X-API-Key: $LOTA_API_KEY" \
  "$LOTA_API_BASE_URL/predictions/api/v2/predictions/?model_name=rf_v1&limit=100"
```

## 错误处理
API返回标准错误格式：
```json
{
  "code": 1,
  "message": "错误描述",
  "data": null
}
```

常见错误码：
- `1`: 参数错误
- `2`: 认证失败
- `3`: 未找到数据
- `4`: 服务器错误

## 环境变量
技能需要使用以下环境变量：
```bash
# 必需：API密钥
export LOTA_API_KEY="your_api_key_here"

# 可选：API基础URL（默认为 http://deepdata.lota.tv/）
export LOTA_API_BASE_URL="http://deepdata.lota.tv/"
```

## 使用限制
- 请遵守API调用频率限制
- 妥善保管API密钥
- 数据可能存在几分钟延迟