# V-Train 饮食数据 API 参考

## 认证

所有 API 调用需要以下步骤：
1. 使用邮箱密码调用 `/api/agent/user-data` 获取 userId
2. 使用 userId 调用饮食数据接口

## API 端点

### 1. 用户鉴权

```http
POST https://puckg.fun/api/agent/user-data
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**成功响应:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "56537569-2607-42a9-89a4-65418a0d2edc",
      "email": "user@example.com",
      "profile": {
        "nickname": "健身达人",
        "height": "186",
        "weight": "86",
        "body_fat": "13",
        "eat_target": "增肌"
      }
    }
  }
}
```

### 2. 获取饮食数据

```http
POST https://www.puckg.xyz/api/food/analysis/by-date-range
Content-Type: application/json

{
  "userId": "56537569-2607-42a9-89a4-65418a0d2edc",
  "startDate": "2026-03-01",
  "endDate": "2026-03-31",
  "mealType": null
}
```

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| userId | string | 是 | 用户UUID |
| startDate | string | 否 | 开始日期 (yyyy-MM-dd) |
| endDate | string | 否 | 结束日期 (yyyy-MM-dd) |
| mealType | string | 否 | 餐型筛选，见下表 |

**餐型枚举:**
- `breakfast` / `早餐`
- `lunch` / `午餐`
- `dinner` / `晚餐`
- `snack` / `零食`
- `dessert` / `甜品`
- `midnight snack` / `夜宵`
- `mainMeal` / `正餐`

**成功响应:**
```json
{
  "success": true,
  "data": {
    "analyses": [
      {
        "id": "443",
        "user_id": "56537569-2607-42a9-89a4-65418a0d2edc",
        "meal_type": "lunch",
        "image_urls": ["https://...jpg"],
        "food_items": [
          {"name": "白米饭"},
          {"name": "炒豆角和肉片"},
          {"name": "蛋花汤"}
        ],
        "ai_analysis": {
          "protein": "中等含量，主要来自肉类",
          "carbohydrates": "较高，主要来源于白米饭",
          "fat": "适量",
          "fiber": "中等",
          "vitamins_and_minerals": "含有维生素A、C"
        },
        "next_meal_recommendation": ["建议下一餐增加深色蔬菜"],
        "created_at": "2026-03-13T05:01:09.011Z",
        "status": "completed",
        "calories": "780"
      }
    ],
    "stats": {
      "breakfast": {
        "count": 10,
        "totalCalories": 6500,
        "avgCalories": 650
      },
      "lunch": {
        "count": 12,
        "totalCalories": 9360,
        "avgCalories": 780
      }
    },
    "totalCount": 45,
    "totalCalories": 32450
  }
}
```

## 数据结构详解

### FoodAnalysis 对象

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录唯一ID |
| user_id | string | 用户ID |
| meal_type | string | 餐型 |
| image_urls | string[] | 食物照片URL数组 |
| food_items | FoodItem[] | 食物列表 |
| ai_analysis | AIAnalysis | AI营养分析结果 |
| calories | string | 估算热量(千卡) |
| created_at | string | 创建时间 ISO8601 |
| status | string | 状态: completed/processing/failed |
| next_meal_recommendation | string[] | AI下一餐建议 |
| description | string | 用户备注 |

### FoodItem 对象

```json
{
  "name": "白米饭"
}
```

### AIAnalysis 对象

```json
{
  "protein": "中等含量，主要来自肉类和蛋花汤",
  "carbohydrates": "较高，主要来源于白米饭",
  "fat": "适量，来自炒菜用油",
  "fiber": "中等，来自豆角和黄瓜",
  "vitamins_and_minerals": "含有维生素A、C、钾和少量铁"
}
```

### Stats 统计对象

```json
{
  "breakfast": {
    "count": 10,           // 记录数
    "totalCalories": 6500, // 总热量
    "avgCalories": 650     // 平均热量
  }
}
```

## 完整 Python 示例

```python
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://puckg.fun"

def get_food_report(email, password, start_date=None, end_date=None):
    """获取饮食报告完整流程"""

    # 1. 登录获取用户信息
    auth_resp = requests.post(
        f"{BASE_URL}/api/agent/user-data",
        json={"email": email, "password": password}
    ).json()

    if not auth_resp.get("success"):
        raise Exception(f"登录失败: {auth_resp.get('message')}")

    user_id = auth_resp["data"]["user"]["id"]

    # 2. 获取饮食数据
    if not start_date:
        start_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        next_month = datetime.now().replace(day=28) + timedelta(days=4)
        end_date = (next_month - timedelta(days=next_month.day)).strftime("%Y-%m-%d")

    food_resp = requests.post(
        f"{BASE_URL}/api/food/analysis/by-date-range",
        json={
            "userId": user_id,
            "startDate": start_date,
            "endDate": end_date
        }
    ).json()

    if not food_resp.get("success"):
        raise Exception(f"获取数据失败: {food_resp.get('message')}")

    return food_resp["data"]

# 使用示例
data = get_food_report("user@example.com", "password123")
print(f"总记录: {data['totalCount']}")
print(f"总热量: {data['totalCalories']} kcal")
```

## 错误处理

**登录失败:**
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

**参数错误:**
```json
{
  "success": false,
  "message": "Missing required field: userId"
}
```

**无数据:**
```json
{
  "success": true,
  "data": {
    "analyses": [],
    "stats": {},
    "totalCount": 0,
    "totalCalories": 0
  }
}
```
