## 目录

- [接口概述](#接口概述)
- [SDK Request 类字段](#sdk-request-类字段)
- [method_expand 各场景详解](#method_expand-各场景详解)
- [同步返回参数](#同步返回参数)
- [完整 SDK 调用示例](#完整-sdk-调用示例)
- [各场景前端处理](#各场景前端处理)
- [请求 JSON 示例](#请求-json-示例)
- [返回 JSON 示例](#返回-json-示例)
- [注意事项](#注意事项)

# 聚合支付下单

## 接口概述

| 属性 | 值 |
|-----|-----|
| 汇付 API 端点 | `v4/trade/payment/create` |
| 请求方式 | POST |
| SDK Request 类 | `TradePaymentCreateRequest` |
| SDK Client 方法 | `Factory.Payment.Common().create(request)` |
| 建议业务接口 | `POST /api/pay/create` |

## SDK Request 类字段

`TradePaymentCreateRequest` 的字段：

| 字段 | setter 方法 | 类型 | 必填 | 说明 |
|------|-----------|------|------|------|
| req_date | setReqDate() | String(8) | Y | 请求日期 yyyyMMdd |
| req_seq_id | setReqSeqId() | String(128) | Y | 请求流水号，当天唯一 |
| huifu_id | setHuifuId() | String(32) | Y | 商户号 |
| goods_desc | setGoodsDesc() | String(128) | Y | 商品描述 |
| trade_type | setTradeType() | String(16) | Y | 支付类型 |
| trans_amt | setTransAmt() | String(14) | Y | 交易金额 |
| method_expand | setMethodExpand() | String | C | 渠道扩展参数（JSON 字符串） |
| time_expire | setTimeExpire() | String(14) | N | 交易失效时间 |
| delay_acct_flag | setDelayAcctFlag() | String(1) | N | 延迟入账标记 |
| fee_flag | setFeeFlag() | String(1) | N | 手续费标记 |
| acct_split_bunch | setAcctSplitBunch() | String | N | 分账对象（JSON） |
| terminal_device_data | setTerminalDeviceData() | String | N | 设备信息（JSON） |
| notify_url | setNotifyUrl() | String(512) | N | 异步通知地址 |
| remark | setRemark() | String(255) | N | 备注 |

> **注意**：Lightning SDK 的 Request 类字段大多有独立 setter，与 dg-java-sdk 需要 extendInfoMap 不同。如果某个字段没有 setter，可通过 `client.optional(key, value)` 传入。

## method_expand 各场景详解

> **SDK 模型类**：SDK 提供了 `WxData`、`AlipayData`、`UnionpayData` 模型类（`com.huifu.dg.lightning.models.*`），可用于构建 method_expand JSON，比手写 JSON 字符串更安全。用 `JSON.toJSONString(wxData)` 转为 JSON 字符串后传入。

### 微信公众号支付（T_JSAPI）

```json
{
    "sub_appid": "wx1234567890abcdef",
    "sub_openid": "oUpF8uMuAJO_M2pxb1Q9zNjWeS6o"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| sub_appid | Y | 微信公众号 AppID，需已与商户绑定 |
| sub_openid | Y | 用户在该公众号下的 OpenID |

### 微信小程序支付（T_MINIAPP）

```json
{
    "sub_appid": "wx1234567890abcdef",
    "sub_openid": "oUpF8uMuAJO_M2pxb1Q9zNjWeS6o"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| sub_appid | Y | 微信小程序 AppID，需已与商户绑定 |
| sub_openid | Y | 用户在该小程序下的 OpenID |

### 微信APP支付（T_APP）

```json
{
    "sub_appid": "wx1234567890abcdef"
}
```

### 微信付款码（T_MICROPAY）

```json
{
    "auth_code": "134578907623468012"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| auth_code | Y | 用户微信付款码（18位数字），有效期约1分钟 |

### 支付宝JS支付（A_JSAPI）

```json
{
    "buyer_id": "2088012345678901"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| buyer_id | Y | 支付宝买家 ID（2088开头16位） |

### 支付宝正扫（A_NATIVE）

无需 method_expand 参数。

### 支付宝付款码（A_MICROPAY）

```json
{
    "auth_code": "286800000000000000"
}
```

### 银联JS支付（U_JSAPI）

无需 method_expand 参数（但 H5 页面需在银联备案）。

### 银联正扫（U_NATIVE）

无需 method_expand 参数。

### 银联付款码（U_MICROPAY）

```json
{
    "auth_code": "620000000000000000"
}
```

## 同步返回参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| resp_code | String(8) | Y | 业务响应码 |
| resp_desc | String(512) | Y | 业务响应信息 |
| huifu_id | String(32) | Y | 商户号 |
| req_date | String(8) | Y | 请求日期 |
| req_seq_id | String(128) | N | 请求流水号 |
| hf_seq_id | String(128) | N | 汇付全局流水号 |
| trade_type | String(16) | N | 支付类型 |
| trans_amt | String(14) | Y | 交易金额 |
| trans_stat | String(1) | N | 交易状态 P/S/F |
| qr_code | String | N | **二维码URL**（正扫场景：A_NATIVE、U_NATIVE） |
| pay_info | String | N | **JS支付调起参数**（JSAPI/MINIAPP/APP 场景） |
| party_order_id | String(64) | N | 微信/支付宝商户单号 |
| out_trans_id | String(64) | N | 微信/支付宝交易订单号 |
| delay_acct_flag | String(1) | Y | 是否延迟交易 |
| settlement_amt | String(14) | N | 结算金额 |
| bank_code | String | N | 外部通道返回码 |
| bank_message | String | N | 外部通道返回描述 |
| method_expand | String | N | 返回扩展参数（JSON） |

## 完整 SDK 调用示例

### 支付宝正扫（生成二维码）

```java
import com.huifu.dg.lightning.factory.Factory;
import com.huifu.dg.lightning.biz.client.CommonPayClient;
import com.huifu.dg.lightning.models.payment.TradePaymentCreateRequest;
import com.huifu.dg.lightning.utils.DateTools;
import com.huifu.dg.lightning.utils.SequenceTools;

// 1. 构建请求
TradePaymentCreateRequest request = new TradePaymentCreateRequest();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");
request.setGoodsDesc("测试商品");
request.setTradeType("A_NATIVE");                   // 支付宝正扫
request.setTransAmt("1.00");
request.setNotifyUrl("https://your-domain.com/notify");

// 2. 发起请求
CommonPayClient client = Factory.Payment.Common();
Map<String, Object> response = client.create(request);

// 3. 处理响应
String respCode = (String) response.get("resp_code");
if ("00000000".equals(respCode) || "00000100".equals(respCode)) {
    String qrCode = (String) response.get("qr_code");  // 二维码 URL
    String reqSeqId = (String) response.get("req_seq_id");
    String reqDate = (String) response.get("req_date");
    // 保存 reqSeqId 和 reqDate 用于后续查询/退款
    // 前端将 qrCode 生成二维码展示给用户
}
```

### 微信公众号支付（JS 调起）

```java
import com.huifu.dg.lightning.models.WxData;
import com.alibaba.fastjson.JSON;

TradePaymentCreateRequest request = new TradePaymentCreateRequest();
request.setReqDate(DateTools.getCurrentDateYYYYMMDD());
request.setReqSeqId(SequenceTools.getReqSeqId32());
request.setHuifuId("6666000123123123");
request.setGoodsDesc("测试商品");
request.setTradeType("T_JSAPI");
request.setTransAmt("1.00");
request.setNotifyUrl("https://your-domain.com/notify");

// 微信公众号需要 method_expand（推荐使用 WxData 模型类构建）
WxData wxData = new WxData();
wxData.setSubAppid("wx1234567890abcdef");
wxData.setSubOpenid("oUpF8uMuAJO_M2pxb1Q9zNjWeS6o");

CommonPayClient client = Factory.Payment.Common();
// method_expand 两种传入方式均可：
// 方式 1：通过 setter（推荐）
request.setMethodExpand(JSON.toJSONString(wxData));
Map<String, Object> response = client.create(request);
// 方式 2：通过 client.optional()（与 SDK demo 一致）
// Map<String, Object> response = client.optional("method_expand", JSON.toJSONString(wxData)).create(request);

String respCode = (String) response.get("resp_code");
if ("00000000".equals(respCode) || "00000100".equals(respCode)) {
    String payInfo = (String) response.get("pay_info");  // JS 调起参数
    // 返回给前端，前端使用 WeixinJSBridge.invoke('getBrandWCPayRequest', payInfo)
}
```

### 付款码支付（反扫，同步返回）

```java
TradePaymentCreateRequest request = new TradePaymentCreateRequest();
request.setReqDate("20250320");
request.setReqSeqId("20250320143000micropay001");
request.setHuifuId("6666000123123123");
request.setGoodsDesc("测试商品");
request.setTradeType("A_MICROPAY");                  // 支付宝反扫
request.setTransAmt("1.00");
request.setNotifyUrl("https://your-domain.com/notify");

// 付款码需要 auth_code
request.setMethodExpand("{\"auth_code\":\"286800000000000000\"}");

CommonPayClient client = Factory.Payment.Common();
Map<String, Object> response = client.create(request);

String respCode = (String) response.get("resp_code");
String transStat = (String) response.get("trans_stat");

if ("00000000".equals(respCode) && "S".equals(transStat)) {
    // 支付成功
} else if ("00000100".equals(respCode) || "P".equals(transStat)) {
    // 处理中，可能需要用户输入密码
    // 轮询查询接口确认最终状态
}
```

## 各场景前端处理

### 正扫场景（A_NATIVE / U_NATIVE）

```javascript
// 后端返回 qr_code URL，前端生成二维码展示
import QRCode from 'qrcode';
const canvas = document.getElementById('qrcode');
QRCode.toCanvas(canvas, response.qr_code);
// 前端轮询查询接口确认支付结果
```

### 微信公众号 JS 支付（T_JSAPI）

```javascript
// 后端返回 pay_info JSON 字符串
const payInfo = JSON.parse(response.pay_info);
WeixinJSBridge.invoke('getBrandWCPayRequest', payInfo, function(res) {
    if (res.err_msg === 'get_brand_wcpay_request:ok') {
        // 支付成功（仅前端提示，最终以后端查询为准）
    }
});
```

### 微信小程序支付（T_MINIAPP）

```javascript
// 后端返回 pay_info
const payInfo = JSON.parse(response.pay_info);
wx.requestPayment({
    ...payInfo,
    success(res) { /* 支付成功提示 */ },
    fail(res) { /* 支付失败提示 */ }
});
```

### 支付宝 JS 支付（A_JSAPI）

```javascript
// 后端返回 pay_info（trade_no）
ap.tradePay({
    tradeNO: response.pay_info
}, function(res) {
    if (res.resultCode === '9000') {
        // 支付成功提示
    }
});
```

## 请求 JSON 示例

### 支付宝正扫

```json
{
    "sys_id": "6666000003100616",
    "product_id": "MYPAY",
    "sign": "RSA签名（SDK自动生成）",
    "data": {
        "req_date": "20250320",
        "req_seq_id": "20250320143000alipay001",
        "huifu_id": "6666000003100616",
        "goods_desc": "测试商品",
        "trade_type": "A_NATIVE",
        "trans_amt": "1.00",
        "notify_url": "https://your-domain.com/notify"
    }
}
```

### 微信公众号

```json
{
    "sys_id": "6666000003100616",
    "product_id": "MYPAY",
    "sign": "RSA签名（SDK自动生成）",
    "data": {
        "req_date": "20250320",
        "req_seq_id": "20250320143000wechat001",
        "huifu_id": "6666000003100616",
        "goods_desc": "测试商品",
        "trade_type": "T_JSAPI",
        "trans_amt": "1.00",
        "method_expand": "{\"sub_appid\":\"wx1234567890abcdef\",\"sub_openid\":\"oUpF8uMuAJO_M2pxb1Q9zNjWeS6o\"}",
        "notify_url": "https://your-domain.com/notify"
    }
}
```

## 返回 JSON 示例

### 正扫返回（含二维码）

```json
{
    "data": {
        "resp_code": "00000000",
        "resp_desc": "交易成功",
        "huifu_id": "6666000003100616",
        "req_date": "20250320",
        "req_seq_id": "20250320143000alipay001",
        "hf_seq_id": "0029000topA250320143000P330c0a8200900000",
        "trade_type": "A_NATIVE",
        "trans_amt": "1.00",
        "trans_stat": "P",
        "qr_code": "https://qr.alipay.com/bax01234567890abcdef",
        "delay_acct_flag": "N"
    }
}
```

### 反扫返回（同步支付结果）

```json
{
    "data": {
        "resp_code": "00000000",
        "resp_desc": "交易成功",
        "huifu_id": "6666000003100616",
        "trade_type": "A_MICROPAY",
        "trans_amt": "0.03",
        "trans_stat": "S",
        "party_order_id": "2508046015554200132",
        "out_trans_id": "2025032022001478281403316633",
        "delay_acct_flag": "N"
    }
}
```

## 注意事项

1. **务必保存** `req_seq_id` 和 `req_date`，后续查询/退款/关单均需使用
2. **trade_type 决定返回字段**：正扫返回 qr_code，JS 支付返回 pay_info，反扫返回同步结果
3. **method_expand 必须与 trade_type 匹配**，传错会导致支付失败
4. 金额格式：`"1.00"`（保留两位小数，最低 0.01）
5. `notify_url` 必须为可公网访问的地址
6. 反扫支付（MICROPAY）可能返回 `trans_stat=P`（用户需输入密码），此时需轮询查询接口
7. 银联交易不支持关单，如需取消需走退款流程
8. `req_seq_id` 同一 huifu_id 下当天唯一，推荐格式：日期+业务标识+序号
