---
name: polymarket-copy-trade-bot
description: 自动跟随成功交易者的交易策略，复制鲸鱼仓位。每次调用自动扣费 0.001 USDT
version: 1.0.0
author: moson
tags:
  - polymarket
  - copy-trade
  - trading
  - whale
homepage: https://github.com/moson/polymarket-copy-trade-bot
metadata:
  clawdbot:
    requires:
      env:
        - SKILLPAY_API_KEY
        - PRIVATE_KEY
triggers:
  - "copy trade polymarket"
  - "follow traders"
config:
  SKILLPAY_API_KEY:
    type: string
    required: true
    secret: true
  PRIVATE_KEY:
    type: string
    required: true
    secret: true
---

# Polymarket Copy Trade Bot

## 功能
- 追踪成功交易者（鲸鱼）
- 自动复制高胜率交易
- 智能仓位管理
- 止盈止损设置

## 使用
```js
{ action: 'follow', trader: '0x...' }
{ action: 'status' }
{ action: 'execute', market: '...', side: 'YES', size: 100 }
```
