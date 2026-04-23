# CustomerInsights API 参考文档

## 概述

本文档详细介绍 CustomerInsights 开放 API 的所有端点、请求格式、响应格式和错误码。

## 认证方式

所有 API 请求需要在 HTTP 头中携带认证信息：

```
Authorization: Bearer {api_key}
Content-Type: application/json
```

> 注意：API Key 格式为 `sk_live_xxxxxxxxxxxxxxxx`

---

## 端点清单

### 1. 设备在线查询

**端点**: `POST /api/v1/external/device/status`

查询当前 API Key 绑定的用户设备是否在线。

**请求体**:
```json
{}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "online": true,
    "device_id": "device_xxx",
    "status": "idle"
  }
}
```

**字段说明**:
| 字段 | 类型 | 说明 |
|------|------|------|
| online | bool | 设备是否在线 |
| device_id | string | 设备ID |
| status | string | 设备状态 (idle/busy) |

---

### 2. 创建任务

**端点**: `POST /api/v1/external/task/create`

创建任务，下发到当前账号绑定的设备。

**请求体**:
```json
{
  "platform": "amazon",
  "site": "US",
  "submit_content": "B09V3KXJPB"
}
```

**参数说明**:
| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| platform | 否 | amazon | 平台名称 |
| site | 否 | US | 站点 |
| submit_content | 是 | - | 输入内容，支持 URL 或 ASIN |

**站点说明**:
| site | 语言 |
|------|------|
| US | 英语 |
| CA | 英语 |
| UK | 英语 |
| DE | 德语 |
| FR | 法语 |
| IT | 意大利语 |
| ES | 西班牙语 |
| JP | 日语 |

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "TSK_xxx",
    "name": "xxx",
    "status": "PENDING"
  }
}
```

---

### 3. 任务状态查询

**端点**: `POST /api/v1/external/task/detail`

查询任务详情和状态。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": "TSK_xxx",
    "user_id": "user_xxx",
    "name": "任务名称",
    "status": "SUCCESS",
    "platform": "amazon",
    "site": "US",
    "submit_content": "B09V3KXJPB",
    "parse_content": ["B09V3KXJPB"],
    "create_time": "2025-03-22 10:30:00",
    "update_time": "2025-03-22 10:35:00",
    "monitoring": false
  }
}
```

**任务状态说明**:
| 状态 | 说明 |
|------|------|
| PENDING | 待处理 |
| DISPATCHING | 分发中 |
| COLLECTING | 获取中 |
| PROCESSING | 处理中 |
| ANALYZING | 分析中 |
| SUCCESS | 完成 |
| FAILED | 失败 |
| CANCELLED | 已取消 |

---

### 4. 任务列表查询

**端点**: `POST /api/v1/external/task/list`

查询任务列表。

**请求体**:
```json
{
  "page": 1,
  "page_size": 20,
  "search_keyword": "B09",
  "filter_monitoring": false
}
```

**参数说明**:
| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| page | 否 | 1 | 页码 |
| page_size | 否 | 10 | 每页数量 |
| search_keyword | 否 | - | 搜索关键词 |
| filter_monitoring | 否 | false | 是否过滤监控任务 |

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 4.1 增量获取

**端点**: `POST /api/v1/external/task/incremental`

为终态任务（SUCCESS/FAILED/CANCELLED）创建增量获取，获取自上次获取后的新增评论。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**参数说明**:
| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| task_id | 是 | - | 任务ID，必须是终态任务 |

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "task_id": "TSK_xxx",
    "job_id": "JOB_xxx"
  }
}
```

**错误码**:
| 错误码 | 说明 |
|--------|------|
| -1 | 任务状态非终态，只有终态任务才能进行增量获取 |

**适用场景**：
- 已完成的任务需要更新最新评论数据
- 与创建新任务的区别：输入是已有的 ASIN（无需重复输入），自动获取增量数据
- 增量获取会触发完整的获取+分析流程，数据分析会扣除积分

---

### 5. AI 洞察查询

**端点**: `POST /api/v1/external/analysis/insights`

获取 AI 洞察摘要。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "executive_summary": [...],
    "key_problems": [...],
    "improvement_recommendations": [...],
    "priority_ranking": {},
    "insights_version": "1.0",
    "last_analyzed_at": "2025-03-22 10:35:00"
  }
}
```

---

### 6. 标签分布查询

**端点**: `POST /api/v1/external/analysis/tags`

获取标签分布统计。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "tag_categories": [
      {
        "category": "product",
        "category_name": "产品质量",
        "tags": [
          {"tag": "做工问题", "polarity": "negative", "count": 15}
        ],
        "total_count": 20
      }
    ]
  }
}
```

---

### 7. 问题维度统计查询

**端点**: `POST /api/v1/external/analysis/issue-statistics`

获取问题维度统计（产品、服务、体验三维模型）。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "product_count": 10,
    "product_rate": "6.7%",
    "service_count": 8,
    "service_rate": "5.3%",
    "experience_count": 5,
    "experience_rate": "3.3%"
  }
}
```

---

### 8. 要点问题分布查询

**端点**: `POST /api/v1/external/analysis/top-issues`

获取各维度的 TopN 问题分布。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "top_issue_distribution": {
      "product": [...],
      "service": [...],
      "experience": [...]
    }
  }
}
```

---

### 9. 基础统计查询

**端点**: `POST /api/v1/external/analysis/statistics`

获取基础统计数据。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total_comments": 150,
    "negative_comments": 23,
    "negative_rate": "15%",
    "product_count": 10,
    "product_rate": "6.7%",
    "service_count": 8,
    "service_rate": "5.3%",
    "experience_count": 5,
    "experience_rate": "3.3%",
    "last_analyzed_at": "2025-03-22 10:35"
  }
}
```

---

### 10. 差评列表查询

**端点**: `POST /api/v1/external/analysis/negative-reviews`

获取差评列表。

**请求体**:
```json
{
  "task_id": "TSK_xxx",
  "page": 1,
  "page_size": 20
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [
      {
        "id": "comment_xxx",
        "content": "Shipping took forever!",
        "rating": 1,
        "date": "2025-03-15",
        "tags": ["物流问题", "时效差"]
      }
    ],
    "total": 23,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 11. 评论趋势查询

**端点**: `POST /api/v1/external/analysis/trend`

获取评论趋势数据。

**请求体**:
```json
{
  "task_id": "TSK_xxx",
  "filter_data": "30",
  "filter_product": "all"
}
```

**参数说明**:
| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| task_id | 是 | - | 任务ID |
| filter_data | 否 | 30 | 数据范围 (30/60/all) |
| filter_product | 否 | all | 商品筛选 |

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "trend_reviews": {
      "source": [["日期", "评论总数", "差评数量"], ["2025-03-01", 50, 8]]
    }
  }
}
```

---

### 12. 原始评论统计查询

**端点**: `POST /api/v1/external/analysis/comments-overview`

获取原始评论概览/统计数据。

**请求体**:
```json
{
  "task_id": "TSK_xxx"
}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "total_reviews": 150,
    "avg_rating": 4.2,
    "verified_count": 120,
    "image_count": 30,
    "video_count": 5
  }
}
```

---

### 13. 原始评论查询

**端点**: `POST /api/v1/external/analysis/comments`

获取原始评论列表。

**请求体**:
```json
{
  "task_id": "TSK_xxx",
  "page": 1,
  "page_size": 20,
  "filter_star": "all",
  "filter_verified": "all"
}
```

**参数说明**:
| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| task_id | 是 | - | 任务ID |
| page | 否 | 1 | 页码 |
| page_size | 否 | 20 | 每页数量 |
| filter_star | 否 | all | 评分筛选 (1-5/all) |
| filter_verified | 否 | all | 筛选已认证评论 |

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [...],
    "total": 150,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 14. 积分余额查询

**端点**: `POST /api/v1/external/account/points`

查询当前账号剩余积分。

**请求体**:
```json
{}
```

**响应**:
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "available_points": 1000
  }
}
```

---

## 错误码

| 错误码 | 说明 | 详细说明 |
|--------|------|----------|
| 0 | 成功 | - |
| -1 | 服务器内部错误 | 服务器内部异常 |
| 1001 | 设备不在线 | 桌面客户端未登录或设备离线 |
| 1002 | 积分不足 | 账户积分不足以执行操作 |
| 2001 | 无效的 API Key | Key 不存在或已失效 |
| 2002 | API Key 已禁用 | 用户主动禁用 |
| 2003 | API Key 已过期 | 超过 expires_at 设置的时间 |
| 2004 | 权限不足 | 缺少对应操作的权限 |
| 2005 | 请求频率超限 | 默认 100 次/分钟 |

---

## 速率限制

- 默认限制：100 次/分钟
- 超出限制返回错误码 2005，并包含 `Retry-After` 头

---

## 常见问题

### 积分规则

- **创建任务**：免费获取亚马逊评论，数据分析会扣除账户积分
- **查询结果**：查看已完成任务的分析结果，不扣积分，也无前置条件限制

### 前置条件（仅创建任务时需要）

创建任务前，需确保满足以下条件：

1. 星图 AI·跨境电商客户洞察 桌面客户端已登录
2. 桌面客户端已登录亚马逊买家账号
3. 确保亚马逊访问畅通

### 错误处理
1. 设备不在线 (1001)：检查桌面客户端是否登录
2. 积分不足 (1002)：提示用户充值积分
3. API Key 无效 (2001)：检查 API Key 是否正确
