---
name: sp-service-weather
description: 用户询问天气（今天天气怎么样、天气怎么样、某城市/某日期天气）、或查询天气服务订单/额度/调用明细时触发
tags: [weather, service, api, payment]
---

# 天气服务 Skill (sp-service-weather)

本 Skill 通过本地天气服务 (``) 查询天气，并支持用户认证初始化、订单查询、额度查询等功能。

**脚本路径**: `scripts/sp-weather-cli.js`（相对于 skill 目录）
**运行方式**: `node scripts/sp-weather-cli.js <command> [options]`

---

## 触发条件

以下任意情况触发本 Skill：
- 用户询问天气：「今天天气怎么样」「北京天气」「明天上海天气」「天气怎么样」
- 用户查询订单：「查询天气服务订单」「查充值记录」
- 用户查询额度：「查询天气服务余额」「还有多少额度」
- 用户查询调用明细：「查看API调用记录」「查用量」

---

## 工作流程

### 第一步：确保用户配置存在

**每次执行前必须先运行**：
```bash
node scripts/sp-weather-cli.js userConfig
```

- 返回 `"action": "exists"` → 配置已存在，直接进入第二步
- 返回 `"action": "created"` → 已自动生成 EC/secp256r1 密钥并保存到 `${CLAUDE_SKILL_DIR}/sp-weather-config.json`，继续第二步
- 返回失败 → 告知用户错误信息,禁止把其他json配置文件拷贝过来重命名使用

### 第二步：根据用户意图执行对应命令

---

## 命令说明

### 1. 天气查询 `queryWeather`

**触发**：用户询问任何天气相关问题

**参数提取**：
- 从用户输入中提取**日期**，若无日期则使用当天日期（通过 `new Date().toISOString().split('T')[0]` 获取）
- 从用户输入中提取**城市名**；若用户未提供城市，**必须主动询问用户**直到获得城市名，不可使用默认值

**执行**：
```bash
node scripts/sp-weather-cli.js queryWeather --city <城市> --date <日期>
```

示例：
```bash
node scripts/sp-weather-cli.js queryWeather --city 北京 --date 2026-03-20
node scripts/sp-weather-cli.js queryWeather --city 上海
```

**处理结果**：
- `success: true` → 将 `data` 中的天气信息整理后展示给用户
- **当返回 `error: "FORBIDDEN"` 或 `detail` 包含"未购买"时**：
  转交 `dxm-agent-wallet` Skill 处理，传入：
  - `cliCommand`: `node scripts/sp-weather-cli.js queryPurchaseDetail`
  - `sender_id`: 当前飞书用户 open_id
- `needCity: true` → 询问用户城市名后重新执行

---

### 2. 查询充值订单列表 `queryOrders`

**触发**：用户查询充值记录、订单列表

```bash
node scripts/sp-weather-cli.js queryOrders
# 分页（可选）
node scripts/sp-weather-cli.js queryOrders --page 1 --page-size 20
```

**接口**：`GET /api/skill/orders?uid=<userId>&page=1&page_size=20`

---

### 3. 查询指定订单 `queryOrder`

**触发**：用户提供了具体订单号

```bash
node scripts/sp-weather-cli.js queryOrder --orderId SP202603192029449B6A4893
```

**接口**：`GET /api/skill/orders/<orderId>?uid=<userId>`

---

### 4. 查询天气服务额度 `queryQuota`

**触发**：用户询问余额、额度、还能用多少次

```bash
node scripts/sp-weather-cli.js queryQuota
```

**接口**：`GET /api/skill/quota?uid=<userId>&skill_id=skill_001`

---

### 5. 查询 API 调用明细 `queryCallLogs`

**触发**：用户查询调用记录、用量明细

```bash
node scripts/sp-weather-cli.js queryCallLogs
# 分页（可选）
node scripts/sp-weather-cli.js queryCallLogs --page 1 --page-size 20
```

**接口**：`GET /api/skill/call-logs?uid=<userId>&skill_id=skill_001&page=1&page_size=20`

### 6. 查询商品信息 `queryPurchaseDetail`

**触发**：余额不足时自动调用；或用户询问充值套餐、商品价格

```bash
node scripts/sp-weather-cli.js queryPurchaseDetail
```

**接口**：`GET /api/skill/purchase/detail?uid=<userId>&skill_id=skill_001`

**处理结果**：展示商品名称、价格、描述等信息，以及充值二维码（使用 `data.payUrl`）

---


---

## 配置文件说明

脚本自动将用户配置保存在 `${CLAUDE_SKILL_DIR}/sp-weather-config.json`，内容包括：
```json
{
  "userId": "32位十六进制字符串（公钥SHA256前32位）",
  "publicKey": "-----BEGIN PUBLIC KEY-----\n...",
  "privateKey": "-----BEGIN PRIVATE KEY-----\n..."
}
```

密钥算法：EC / secp256r1（prime256v1），签名算法：SHA256withECDSA。

---

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SP_WEATHER_BASE` | 天气服务 base URL | `` |

---

## 故障排查

| 现象 | 处理 |
|------|------|
| `连接天气服务失败` | 确认服务 `` 是否可达 |
| `余额不足` / `payRequired: true` | 扫码充值后重试 |
| 二维码不显示 | 手动打开 `payUrl` 完成支付；可安装 `brew install qrencode` 改善体验 |
| `用户配置不存在` | 先执行 `userConfig` 命令初始化 |
| `未知命令` | 检查命令名拼写，可用命令：`userConfig` / `queryWeather` / `queryOrders` / `queryOrder` / `queryQuota` / `queryPurchaseDetail` / `queryCallLogs` |

---

## 版本历史

- **v1.0.0**：初始版本，支持用户认证、天气查询、订单/额度/调用明细查询、二维码支付引导
