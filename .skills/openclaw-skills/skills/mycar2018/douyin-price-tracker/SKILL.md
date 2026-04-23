# Douyin Price Tracker
Real-time price monitoring tool for Douyin e-commerce sellers.

## Core Features
- Auto resolve Douyin product links
- Real-time price drop alerts
- WeChat Work alert push
- Price trend tracking
- Multi task management

## Version Options
### Free Basic
- Up to 5 monitoring tasks
- 10 alerts per month
- Basic price tracking

### Pro Paid
- Up to 100 monitoring tasks
- Unlimited alerts
- Full feature access
- Priority support

### Enterprise Paid
- Unlimited tasks
- Multi store management
- Custom support
- Private deployment

## How to Install
Run this command to install:
npx clawhub@latest install douyin-price-tracker

## How to Use
- Monitor product: Monitor Douyin product, alert when price below 180 yuan
- View tasks: Show my monitoring tasks
- Get report: Generate product price analysis

## Contact
Email: 745934958@qq.com

## Configuration Guide
### How to set up
1. Open your agent's skill configuration page
2. Find the `SKILL_CONFIG` field
3. Paste the JSON below, replace with your own values:
```json
{
  "douyin_cookie": "your_douyin_web_cookie_here (optional)",
  "wechat_webhook": "your_wecom_webhook_url_here (optional)",
  "subscription_level": "basic"
}