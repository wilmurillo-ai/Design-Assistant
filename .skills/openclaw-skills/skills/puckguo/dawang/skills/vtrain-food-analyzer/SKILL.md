---
name: vtrain-food-analyzer
description: V-Train 饮食数据分析器。用于获取用户饮食记录并生成可视化报告。使用场景：(1) 用户要求查看/分析饮食记录，(2) 生成饮食报告，(3) 获取特定日期范围的饮食数据，(4) 分析营养摄入情况。需要用户提供邮箱和密码进行鉴权。
---

# V-Train 饮食数据分析器

## 快速开始

### 完整工作流程

```
1. 获取用户凭证（邮箱+密码）
2. 调用 API 鉴权获取 userId
3. 获取指定日期范围的饮食数据
4. 生成 HTML 可视化报告
5. 保存 JSON 原始数据
```

### 核心 API

**鉴权获取用户信息**
```python
POST https://www.puckg.xyz/api/agent/user-data
{
  "email": "user@example.com",
  "password": "password123"
}
```

**获取饮食数据**
```python
POST https://puckg.fun/api/food/analysis/by-date-range
{
  "userId": "user_uuid",
  "startDate": "2026-03-01",
  "endDate": "2026-03-31",
  "mealType": null  # 可选: breakfast/lunch/dinner/snack/dessert
}
```

## 使用方法

### 方式1：使用脚本（推荐）

运行封装好的脚本：

```bash
# 生成本月报告
node scripts/generate_food_report.js user@example.com password123

# 指定日期范围
node scripts/generate_food_report.js user@example.com password123 2026-03-01 2026-03-15
```

### 方式2：Python 代码

参考 [references/api_guide.md](references/api_guide.md) 获取完整代码示例。

### 方式3：直接调用

根据上述 API 文档直接构造请求。

## 数据字段说明

### 饮食记录字段

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 记录ID |
| meal_type | string | 餐型: breakfast/lunch/dinner/snack/dessert |
| food_items | array | 食物列表 [{name: "米饭"}, ...] |
| ai_analysis | object | AI营养分析 {protein, carbohydrates, fat, fiber, vitamins_and_minerals} |
| calories | string | 估算热量(kcal) |
| created_at | string | 记录时间 ISO8601 |
| image_urls | array | 食物照片URL列表 |
| next_meal_recommendation | array | AI下一餐建议 |

## 报告模板

HTML报告模板位于 `assets/food_report_template.html`，包含：
- 热量趋势图表
- 营养素分布饼图
- 餐型统计
- 每日详细记录
- 食物图片展示

## 输出文件

脚本默认生成：
- `food_report_YYYY-MM.html` - 可视化HTML报告
- `food_data_YYYY-MM.json` - 原始JSON数据

## 注意事项

1. 用户必须提供有效的 V-Train 账号邮箱和密码
2. 日期格式：yyyy-MM-dd
3. 餐型参数可选，不传则返回所有类型
4. 报告中的图片需要联网才能显示
