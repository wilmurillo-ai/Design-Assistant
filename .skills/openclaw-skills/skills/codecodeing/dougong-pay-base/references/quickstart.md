# dougong-pay-base — 汇付支付公共基座

所有汇付支付业务 Skill 的前置依赖，包含 SDK 安装初始化、技术规范、公共参数和错误码。

## 本 Skill 解决什么问题

在调用任何汇付支付接口之前，开发者需要完成：

1. 获取商户凭据（product_id、sys_id、RSA 密钥对）
2. 安装 dg-java-sdk 并在 Spring Boot 中初始化
3. 理解签名规则、异步通知机制、流水号规范等通用约定

本 Skill 将以上内容集中提供，避免在每个业务 Skill 中重复说明。

## 文件结构

```
dougong-pay-base/
├── SKILL.md                   # Skill 定义（触发词、接入流程、安全规则）
├── README.md                  # 本文件
└── references/
    ├── sdk-quickstart.md      # SDK 安装与初始化（Maven 依赖 + Spring Boot 配置类）
    ├── tech-spec.md           # 技术规范（签名、加密、异步通知、IP 白名单）
    ├── common-params.md       # 公共请求/返回参数、交易状态枚举、名词解释
    └── error-codes.md         # 网关返回码 + 业务返回码速查
```

## 5 分钟快速接入

### 第 1 步：获取商户配置

从汇付开放平台获取以下 4 项凭据：

| 配置项 | 环境变量 | 说明 |
|-------|---------|------|
| 产品号 | `HUIFU_PRODUCT_ID` | 汇付分配，如 `YYZY` |
| 系统号 | `HUIFU_SYS_ID` | 商户/渠道商的 huifu_id |
| RSA 私钥 | `HUIFU_RSA_PRIVATE_KEY` | 用于请求签名 |
| RSA 公钥 | `HUIFU_RSA_PUBLIC_KEY` | 用于响应验签 |

### 第 2 步：添加 Maven 依赖

```xml
<dependency>
    <groupId>com.huifu.bspay.sdk</groupId>
    <artifactId>dg-java-sdk</artifactId>
    <version>3.0.34</version>
</dependency>
```

### 第 3 步：配置环境变量

`application.yml`（通过环境变量注入，**严禁硬编码**）：

```yaml
huifu:
  product-id: ${HUIFU_PRODUCT_ID}
  sys-id: ${HUIFU_SYS_ID}
  rsa-private-key: ${HUIFU_RSA_PRIVATE_KEY}
  rsa-public-key: ${HUIFU_RSA_PUBLIC_KEY}
```

### 第 4 步：初始化 SDK

详见 [sdk-quickstart.md](references/sdk-quickstart.md) 中的 Spring Boot 配置类完整代码。

关键注意点：
- **Spring Boot 3.x** 用户需将 `javax.*` 替换为 `jakarta.*`
- SDK 方法名为 `setProcutId()`（不是 `setProductId`），这是 SDK 原生拼写

### 第 5 步：开始调用业务接口

初始化完成后，根据业务场景选择对应 Skill：

| 业务需求 | 下一步 |
|---------|-------|
| 发起支付 | [dougong-cashier-order](../dougong-cashier-order/) |
| 查询订单 / 关单 | [dougong-cashier-query](../dougong-cashier-query/) |
| 退款 | [dougong-cashier-refund](../dougong-cashier-refund/) |

## 联调环境

SDK 支持切换到联调（沙箱）环境进行测试，不会产生真实扣款：

```java
BasePay.prodMode = BasePay.MODE_TEST;  // 联调环境
```

- 联调商户号需联系汇付销售经理申请
- 本地 webhook 测试可使用 ngrok / frp 等内网穿透工具

详见 [SKILL.md 联调环境章节](SKILL.md#联调环境)。

## 参考资料索引

| 文档 | 你需要它当… |
|-----|------------|
| [sdk-quickstart.md](references/sdk-quickstart.md) | 第一次安装 SDK、写初始化代码 |
| [tech-spec.md](references/tech-spec.md) | 需要了解签名规则、接收异步通知、配置 IP 白名单 |
| [common-params.md](references/common-params.md) | 不确定 sys_id 和 huifu_id 填什么、交易状态 P/S/F 怎么处理 |
| [error-codes.md](references/error-codes.md) | 接口返回了非 00000000 的错误码 |
