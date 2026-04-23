# -*- coding: utf-8 -*-
"""
国密加密模块使用说明

本模块提供与 Java 版本兼容的 SM2/SM4 加密加签功能。

## 依赖安装

```bash
pip install gmssl
```

## 核心组件

### 1. gm_crypto.py - 基础加密工具

提供 SM2 和 SM4 的基础加密操作：

- `SM2Util` - SM2 非对称加密
  - `en_code()`: 加密（公钥加密）
  - `de_code()`: 解密（私钥解密）
  - `sign()`: 签名
  - `verify()`: 验签

- `SM4Util` - SM4 对称加密
  - `generate_key()`: 生成随机密钥
  - `encrypt_ecb()`: ECB 模式加密
  - `decrypt_ecb()`: ECB 模式解密

### 2. message_processor.py - 报文处理器

提供完整的报文加密加签流程：

- `MessageProcessor`: 报文处理器类
  - `parse_client_message()`: 解析请求报文（解密、验签）
  - `build_client_message()`: 组装响应报文（加密、加签）

- 便捷函数:
  - `parse_request_message()`: 快速解析请求
  - `build_response_message()`: 快速组装响应

## 使用示例

### 服务端处理请求

```python
from zlpay_skill.security.message_processor import MessageProcessor

# 初始化处理器（使用服务端私钥和客户端公钥）
processor = MessageProcessor(
    server_private_key="你的服务端私钥(16进制)",
    client_public_key="你的客户端公钥(16进制)"
)

# 解析请求报文
business_data = processor.parse_client_message(
    app_id="APP001",
    version="1.0",
    seq_id="202403270001",
    timestamp="20240327093000",
    interface_id="/api/payment",
    encrypted_data="Base64编码的加密数据",
    signature="Base64编码的签名",
    encrypted_sm4_key="Base64编码的加密密钥",
    session_token="可选的会话令牌",
    trx_devc_inf="可选的设备信息",
    source="可选的来源标识"
)

# business_data 是解密后的业务数据字典
print(business_data)
```

### 服务端组装响应

```python
# 准备响应业务数据
response_data = {
    "code": "SUCCESS",
    "message": "处理成功",
    "data": {
        "orderId": "ORDER001",
        "amount": 100.00
    }
}

# 组装响应报文
response_message = processor.build_client_message(
    app_id="APP001",
    version="1.0",
    seq_id="202403270001",
    interface_id="/api/payment",
    response_data=response_data
)

# response_message 是包含加密数据和签名的响应报文字典
print(response_message)
```

### 便捷函数使用

```python
from zlpay_skill.security.message_processor import (
    parse_request_message,
    build_response_message
)

# 快速解析请求
business_data = parse_request_message(
    server_private_key="服务端私钥",
    client_public_key="客户端公钥",
    request_message=request_dict
)

# 快速组装响应
response_message = build_response_message(
    server_private_key="服务端私钥",
    client_public_key="客户端公钥",
    request_message=request_dict,
    response_data=response_data
)
```

## 报文格式说明

### 请求报文结构

```json
{
    "appId": "应用ID",
    "version": "版本号",
    "seqId": "流水号",
    "timeStamp": "时间戳(yyyyMMddHHmmss)",
    "interfaceId": "接口标识",
    "secret": "SM2加密的SM4密钥(Base64)",
    "data": "SM4加密的业务数据(Base64)",
    "sign": "SM2签名(Base64)",
    "sessionToken": "会话令牌(可选)",
    "trxDevcInf": "交易设备信息(可选)",
    "source": "来源标识(可选)"
}
```

### 响应报文结构

与请求报文结构相同，包含加密的数据和签名。

## 签名原文构造规则

签名原文 = verify_bo JSON + sm4_key

其中 verify_bo 包含的字段：
- 基础字段：`appId`, `version`, `seqId`, `timeStamp`, `interfaceId`, `secret`, `data`
- 可选字段：`sessionToken`, `trxDevcInf`, `source`

### ZL 应用特殊处理

对于 ZL 应用（source 字段存在），签名字段列表会包含 `source`。

## 密钥格式

所有密钥使用 16 进制字符串格式：
- SM2 私钥：32 字节（64 个 16 进制字符）
- SM2 公钥：64 字节（128 个 16 进制字符，不含 04 前缀）
- SM4 密钥：16 字节（32 个 16 进制字符）

## 注意事项

1. 本模块使用 `gmssl` 库实现国密算法
2. SM4 使用 ECB 模式，与 Java 版本保持一致
3. JSON 序列化使用紧凑格式（无空格），确保签名一致性
4. 时间戳格式：`yyyyMMddHHmmss`
5. 所有加密结果使用 Base64 编码

## 兼容性说明

本实现与 Java 版本的 sm2.java 逻辑对应：
- `parseClientMessage` → `MessageProcessor.parse_client_message`
- `buildClientMessage` → `MessageProcessor.build_client_message`
- `SM2Util.enCode/deCode/sign/verify` → `SM2Util.en_code/de_code/sign/verify`
- `SM4Util.encrypt_ECB/decrypt_ECB` → `SM4Util.encrypt_ecb/decrypt_ecb`
- `SM4Util.generatorSM4key` → `SM4Util.generate_key`
