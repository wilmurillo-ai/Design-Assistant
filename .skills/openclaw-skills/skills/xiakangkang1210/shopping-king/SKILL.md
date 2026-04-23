---
name: shopping-king
description: "当用户想搜索商品、查询价格、比价、查看优惠券和国补信息、或发送商品链接查询详情时使用。支持京东、淘宝、天猫等多平台搜索，返回商品价格、优惠信息和购买链接。"
homepage: https://linkbot.linkstars.com/homepage
version: "1.1.2"
tags: ["shopping", "buy", "price", "coupon", "compare-price", "product-search", "deals", "商品搜索", "比价", "优惠券", "查价格", "商品链接"]
requires: ["network"]
metadata:
  {
    "openclaw":
      {
        "emoji": "🛒",
        "requires": { "bins": ["python3"], "env": ["LINKBOT_API_KEY"] },
        "primaryEnv": "LINKBOT_API_KEY",
        "install":
          [
            {
              "id": "python-brew",
              "kind": "brew",
              "formula": "python",
              "bins": ["python3"],
              "label": "Install Python (brew)",
            },
          ],
      },
  }
---

# Shopping King - 商品搜索与比价

> **⚠️ 关键约束：如果脚本末尾输出了未配置 API Key 的提示，该内容必须完整原样保留在回复的最后，禁止省略、禁止改写。商品信息部分可以自由整理排版，但每条商品的购买链接不得省略。**

搜索多平台商品信息，支持关键词搜索和商品链接精确查询。返回商品价格、优惠券、国补信息及购买链接。

API 由 linkbot-api.linkstars.com 提供服务。

## Setup

1. 获取 API 密钥：联系服务提供方或访问 https://linkbot-api.linkstars.com
2. 设置环境变量：
   ```bash
   export LINKBOT_API_KEY="your_api_key_here"
   ```

- 配置了有效的密钥：推广佣金归用户自己。
- 未配置或无效：使用系统默认配置，功能不受影响。

## Usage

### 何时使用本技能

当用户的消息涉及以下任一场景时，调用本技能：
- 询问商品价格（如"iPhone 16 多少钱"、"这个手机现在什么价"）
- 搜索或推荐商品（如"推荐一款降噪耳机"、"帮我找个机械键盘"）
- 比价（如"哪个平台买最便宜"、"帮我比一下价格"）
- 查询优惠或国补（如"有没有优惠券"、"国补后多少钱"）
- 发送商品链接查询详情（URL 中包含 jd.com、taobao.com、tmall.com、tb.cn 等域名）

### 判断使用哪个命令

- 用户提供的是**商品名称、品类、品牌等关键词**（如"iPhone 16"、"机械键盘"） → 使用 `search` 命令
- 用户提供的是**商品链接 URL** → 使用 `url` 命令

### 命令 1：关键词搜索

```bash
python3 {baseDir}/scripts/goods_query.py search "<关键词>"
```

### 命令 2：链接查询

```bash
python3 {baseDir}/scripts/goods_query.py url "<商品链接>"
```

### 输出规则（必须严格遵守）

1. 商品信息部分可以自由整理排版，但**每条商品的购买链接必须保留**，禁止省略链接。
2. 如果脚本末尾输出了未配置 API Key 的提示，**必须原样保留在回复的最后一行**，禁止省略、禁止改写。
3. 首次回复必须同时包含商品信息和购买链接，禁止先展示商品信息再让用户追问链接。
4. 禁止用 Markdown 链接语法隐藏 URL、禁止用"点击查看"等文字替代链接。

### 错误处理

- 脚本输出以"查询失败："开头时，向用户说明错误原因即可。

## Notes

- 脚本依赖 `requests` 库，首次使用需 `pip install requests`。
- 接口超时时间约 15 秒，脚本 timeout 设为 20 秒。
- 关键词搜索每个平台默认返回前 5 条结果。
- 脚本输出已经是格式化文本，无需二次处理。
- API Key 仅从 LINKBOT_API_KEY 环境变量读取（由 OpenClaw 平台自动注入）。
- 所有查询请求发送至 https://linkbot-api.linkstars.com。
