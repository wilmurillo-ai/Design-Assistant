---
name: news-impact-predictor
version: 1.0.0
description: Predict how news events will impact markets, stocks, and cryptocurrencies. Each call charges 0.001 USDT via SkillPay.
category: News
tags:
  - news
  - prediction
  - impact
  - market
author: moson
price: 0.001
currency: USDT
triggers:
  - "news impact"
  - "predict market"
  - "news prediction"
  - "market forecast"
config:
  OPENAI_API_KEY:
    type: string
    required: false
    secret: true
---

# News Impact Predictor

## 功能

- 预测新闻对市场的影响
- 分析价格走势
- 评估风险等级
- 提供交易建议

## 使用方法

```json
{
  "news": "Fed announces rate cut",
  "asset": "BTC",
  "timeframe": "24h"
}
```

## 输出

```json
{
  "success": true,
  "prediction": {
    "direction": "BULLISH",
    "confidence": 0.78,
    "price_change": "+3.5%",
    "risk_level": "MEDIUM"
  }
}
```

## 定价

每次调用: 0.001 USDT
