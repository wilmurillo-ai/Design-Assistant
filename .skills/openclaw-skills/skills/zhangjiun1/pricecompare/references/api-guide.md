# API 使用指南

## 概述

省钱购物助手 Skill 通过调用后端 API 实现商品搜索、链接转换、分享解析和价格对比功能。

---

## API 基础信息

- **API地址**: `http://op.squirrel2.cn` (生产环境)
- **API版本**: v1
- **API前缀**: `/api/v1`
- **请求方式**: POST
- **数据格式**: JSON
- **超时时间**: 10秒

---

## 核心接口

### 1. 商品搜索

**接口**: `/search`

**请求参数**:
```json
{
  "platform": "jd",           // 平台: jd/taobao/pinduoduo
  "keyword": "iPhone 16",     // 搜索关键词
  "page": 1,                  // 页码（可选，默认1）
  "page_size": 10             // 每页数量（可选，默认10）
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "goods_id": "10021724657015",
      "goods_name": "iPhone 16 Pro Max 256GB",
      "price": 7999.00,
      "original_price": 8999.00,
      "save_amount": 1000.00,
      "shop_name": "苹果官方旗舰店",
      "goods_link": "https://item.jd.com/10021724657015.html",
      "coupon_info": "满100减20"
    }
  ]
}
```

---

### 2. 链接转换

**接口**: `/convert`

**请求参数**:
```json
{
  "platform": "jd",           // 平台: jd/taobao/pinduoduo
  "url": "https://item.jd.com/10021724657015.html"
}
```

**响应示例**:
```json
{
  "success": true,
  "goods_name": "iPhone 16 Pro Max 256GB",
  "original_price": 8999.00,
  "final_price": 7999.00,
  "save_amount": 1000.00,
  "promotion_link": "https://u.jd.com/xxx",
  "coupon_info": "满100减20"
}
```

---

### 3. 分享解析

**接口**: `/parse_share`

**请求参数**:
```json
{
  "content": "【淘宝】假一赔四 https://e.tb.cn/h.iVW7Wnbs5Woz1ZI"
}
```

**响应示例**:
```json
{
  "success": true,
  "platform": "taobao",
  "data": {
    "goods_name": "白象火鸡面大辣娇韩式奶油咸蛋黄小龙虾干拌面",
    "original_price": 39.9,
    "final_price": 29.9,
    "save_amount": 10.0,
    "promotion_link": "https://uland.taobao.com/item/edetail?id=xxx",
    "coupon_info": "满30减10"
  }
}
```

---

### 4. 价格对比

**接口**: `/compare`

**请求参数**:
```json
{
  "keyword": "iPhone 16",     // 搜索关键词
  "platforms": ["jd", "taobao", "pinduoduo"]  // 对比平台（可选）
}
```

**响应示例**:
```json
{
  "success": true,
  "keyword": "iPhone 16",
  "comparison": [
    {
      "platform": "京东",
      "platform_code": "jd",
      "goods_name": "iPhone 16 Pro Max 256GB",
      "original_price": 8999.00,
      "final_price": 7999.00,
      "save_amount": 1000.00
    },
    {
      "platform": "淘宝",
      "platform_code": "taobao",
      "goods_name": "iPhone 16 Pro Max 256GB",
      "original_price": 8899.00,
      "final_price": 7899.00,
      "save_amount": 1000.00
    }
  ],
  "cheapest": {
    "platform": "淘宝",
    "price": 7899.00
  }
}
```

---

## 错误响应

所有接口在失败时返回统一格式：

```json
{
  "success": false,
  "error": "错误信息"
}
```

**常见错误**:
- `缺少必需参数`: 请求缺少必要参数
- `不支持的平台`: platform参数值无效
- `无法识别分享内容的平台`: 分享内容格式不支持
- `口令解析失败`: 口令已过期或无效
- `无法从链接中提取商品ID`: 链接格式不正确

---

## 调用示例

### Python

```python
import requests

# 商品搜索
response = requests.post(
    "http://op.squirrel2.cn/api/v1/search",
    json={
        "platform": "jd",
        "keyword": "iPhone 16"
    }
)
print(response.json())

# 链接转换
response = requests.post(
    "http://op.squirrel2.cn/api/v1/convert",
    json={
        "platform": "jd",
        "url": "https://item.jd.com/10021724657015.html"
    }
)
print(response.json())
```

### JavaScript

```javascript
// 商品搜索
fetch('http://op.squirrel2.cn/api/v1/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        platform: 'jd',
        keyword: 'iPhone 16'
    })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 注意事项

1. **请求频率**: 建议控制请求频率，避免频繁调用
2. **超时处理**: 设置合理的超时时间（建议10秒）
3. **错误处理**: 妥善处理API返回的错误信息
4. **数据缓存**: 可考虑缓存常用数据，减少API调用

---

## 环境配置

### 开发环境
```
API_BASE_URL=http://localhost:8000
API_TIMEOUT=10
```

### 生产环境
```
API_BASE_URL=http://op.squirrel2.cn
API_TIMEOUT=10
```
