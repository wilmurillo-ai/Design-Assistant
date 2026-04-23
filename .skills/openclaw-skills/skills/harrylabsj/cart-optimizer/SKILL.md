---
name: cart-optimizer
description: Optimize ecommerce cart top-up plans across promotions such as full-reduction, discounts, and coupons. Use when the user asks to 凑单、计算满减最优方案、比较多档优惠、推荐最低成本补单策略 or improve cart savings.
---

# Cart Optimizer - 凑单优化器

智能凑单助手，自动计算最优凑单方案。

## 功能特性

- 🎯 支持多种优惠类型：满减、折扣、优惠券
- 🧮 智能算法：最小额外支出、最大优惠利用率
- 🛒 多平台支持：淘宝、京东、拼多多
- 📊 实时计算：输入商品自动推荐凑单
- 💡 智能建议：推荐高性价比凑单品

## 使用方式

### 基础凑单
```
凑单 250 满 300 减 30
```

### 带购物车商品
```
购物车 250，凑满 300 减 30
```

### 多档优惠对比
```
对比凑单方案 250：满200减20 vs 满300减40
```

## 核心算法

- 背包问题变种
- 动态规划优化
- 贪心算法备选
