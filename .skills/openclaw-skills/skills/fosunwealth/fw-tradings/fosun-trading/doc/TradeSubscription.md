# 交易订阅接口 - SubscriptionCreate / SubscriptionList / SubscriptionUpdate / SubscriptionDelete

> **POST**
>
> - `https://openapi.fosunxcz.com/api/v1/trade/SubscriptionCreate`
> - `https://openapi.fosunxcz.com/api/v1/trade/SubscriptionList`
> - `https://openapi.fosunxcz.com/api/v1/trade/SubscriptionUpdate`
> - `https://openapi.fosunxcz.com/api/v1/trade/SubscriptionDelete`

用于管理交易事件订阅。当前 SDK 暴露的事件类型仅有 `orderUpdate`，回调通道默认使用 `HTTP Webhook`。

---

## 适用范围

本文聚合说明以下 4 个接口：

| 接口 | 说明 |
|------|------|
| `SubscriptionCreate` | 创建交易订阅 |
| `SubscriptionList` | 查询订阅列表 |
| `SubscriptionUpdate` | 更新订阅回调地址 |
| `SubscriptionDelete` | 删除订阅 |

### 当前已知限制

| 项目 | 说明 |
|------|------|
| `eventType` | 当前仅支持 `orderUpdate` |
| `channelType` | 当前脚本和 SDK 默认使用 `1`，表示 `HTTP Webhook` |
| 回调地址 | `endpoint` 必须是非空字符串，通常应为可被服务端访问的公网 `HTTPS` 地址 |

---

## 请求

### Headers

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `X-api-key` | string | 是 | API Key，标识客户端 |
| `X-lang` | string | 是 | 语言，如 `zh-CN`、`en` |
| `X-request-id` | string | 是 | 请求追踪 ID，必填 |
| `X-session` | string | 是 | 会话 ID |
| `Content-Type` | string | 是 | 固定值 `application/json` |
| `Accept` | string | 是 | 固定值 `application/json` |

---

## 1. 创建订阅 - SubscriptionCreate

### Body（application/json）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `eventType` | string | 是 | 事件类型。当前仅支持 `orderUpdate` |
| `channelType` | integer | 是 | 通道类型。当前使用 `1` 表示 HTTP Webhook |
| `endpoint` | string | 是 | Webhook 回调地址 |

### 请求示例

```json
{
  "eventType": "orderUpdate",
  "channelType": 1,
  "endpoint": "https://example.com/webhook"
}
```

### 响应

#### 200 - 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "subscriptionId": 123456
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data.subscriptionId` | integer | 新创建的订阅 ID |

#### 400 - 请求错误

常见原因包括：

- 缺少 `eventType`、`channelType` 或 `endpoint`
- `eventType` 不为 `orderUpdate`
- `endpoint` 格式不合法或不可用

---

## 2. 查询订阅列表 - SubscriptionList

### Body（application/json）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `start` | integer | 是 | 分页偏移，通常从 `0` 开始 |
| `count` | integer | 是 | 返回条数 |
| `eventType` | string | 否 | 事件类型过滤。当前仅支持 `orderUpdate` |

### 请求示例

```json
{
  "start": 0,
  "count": 20,
  "eventType": "orderUpdate"
}
```

### 响应

#### 200 - 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "subscriptionId": 123456,
        "eventType": "orderUpdate",
        "channelType": 1,
        "endpoint": "https://example.com/webhook"
      }
    ],
    "start": 0,
    "count": 20
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data.list` | array[object] | 订阅列表 |
| `data.list[].subscriptionId` | integer | 订阅 ID |
| `data.list[].eventType` | string | 事件类型 |
| `data.list[].channelType` | integer | 通道类型 |
| `data.list[].endpoint` | string | 回调地址 |
| `data.start` | integer | 当前返回的起始偏移，常见于分页结果 |
| `data.count` | integer | 当前返回的条数，常见于分页结果 |

> 说明：
>
> - SDK 仅明确了请求字段，响应字段在公开示例中没有完整展开。
> - 上表和示例中的列表项结构依据 SDK 示例、管理脚本和常见返回习惯整理，实际响应如有更多字段，以线上接口返回为准。

#### 400 - 请求错误

常见原因包括：

- `start` 或 `count` 非法
- `eventType` 填写了当前不支持的值

---

## 3. 更新订阅 - SubscriptionUpdate

### Body（application/json）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `subscriptionId` | integer | 是 | 订阅 ID |
| `endpoint` | string | 是 | 新的 Webhook 回调地址 |

### 请求示例

```json
{
  "subscriptionId": 123456,
  "endpoint": "https://example.com/webhook/v2"
}
```

### 响应

#### 200 - 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "subscriptionId": 123456
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data.subscriptionId` | integer | 已更新的订阅 ID |

#### 400 - 请求错误

常见原因包括：

- `subscriptionId` 缺失或不存在
- `endpoint` 为空或格式不合法

---

## 4. 删除订阅 - SubscriptionDelete

### Body（application/json）

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `subscriptionId` | integer | 是 | 要删除的订阅 ID |

### 请求示例

```json
{
  "subscriptionId": 123456
}
```

### 响应

#### 200 - 成功

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "subscriptionId": 123456
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `code` | integer | 状态码，示例值 `0` |
| `message` | string | 状态消息，示例值 `success` |
| `data.subscriptionId` | integer | 已删除的订阅 ID |

#### 400 - 请求错误

常见原因包括：

- `subscriptionId` 缺失
- 指定的订阅不存在或当前不可删除

---

## 使用示例

### cURL

#### 创建订阅

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/SubscriptionCreate \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "eventType": "orderUpdate",
  "channelType": 1,
  "endpoint": "https://example.com/webhook"
}'
```

#### 查询订阅

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/SubscriptionList \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "start": 0,
  "count": 20,
  "eventType": "orderUpdate"
}'
```

#### 更新订阅

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/SubscriptionUpdate \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "subscriptionId": 123456,
  "endpoint": "https://example.com/webhook/v2"
}'
```

#### 删除订阅

```bash
curl --request POST \
  --url https://openapi.fosunxcz.com/api/v1/trade/SubscriptionDelete \
  --header 'Accept: application/json' \
  --header 'Content-Type: application/json' \
  --header 'X-api-key: YOUR_API_KEY' \
  --header 'X-lang: zh-CN' \
  --header 'X-request-id: UNIQUE_REQUEST_ID' \
  --header 'X-session: YOUR_SESSION_ID' \
  --data '{
  "subscriptionId": 123456
}'
```

### SDK 对应写法

```python
# 创建订阅
created = client.trade.create_subscription(
    event_type="orderUpdate",
    endpoint="https://example.com/webhook",
    channel_type=1,
)

# 查询订阅
items = client.trade.list_subscriptions(
    start=0,
    count=20,
    event_type="orderUpdate",
)

# 更新订阅
updated = client.trade.update_subscription(
    subscription_id=123456,
    endpoint="https://example.com/webhook/v2",
)

# 删除订阅
deleted = client.trade.delete_subscription(subscription_id=123456)
```

---

## 与脚本对应

当前仓库中的命令行脚本可直接调用这 4 个接口：

```bash
$FOSUN_PYTHON manage_subscription.py create --endpoint https://example.com/webhook
$FOSUN_PYTHON manage_subscription.py list
$FOSUN_PYTHON manage_subscription.py list --event-type orderUpdate
$FOSUN_PYTHON manage_subscription.py update --subscription-id 123456 --endpoint https://example.com/webhook/v2
$FOSUN_PYTHON manage_subscription.py delete --subscription-id 123456
```

脚本额外约定如下：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--event-type` | `orderUpdate` | 当前仅支持该值 |
| `--channel-type` | `1` | 当前默认 HTTP Webhook |
| `--start` | `0` | 查询分页偏移 |
| `--count` | `20` | 查询返回条数 |

---

## 推荐使用流程

1. 先调用 `SubscriptionCreate` 创建回调订阅。
2. 用 `SubscriptionList` 确认订阅是否已生效，并记录 `subscriptionId`。
3. 回调地址变更时调用 `SubscriptionUpdate`。
4. 不再需要时调用 `SubscriptionDelete` 清理订阅。

---

## 说明

- 当前仓库此前没有这 4 个接口的独立说明文档，本文为新增整理版。
- 本文主要依据 SDK 源码、SDK README 示例和仓库内 `manage_subscription.py` 脚本整理。
- 由于公开页面当前可见信息有限，`SubscriptionList` 的完整响应字段未完全展开；文中对返回结构做了保守归纳，实际以线上接口返回为准。
- 如果后续原始 OpenAPI 页面补全了 schema，可再把字段枚举和错误码细化。
